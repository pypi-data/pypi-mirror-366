
import asyncio
import logging
from typing import Any, Dict, List, Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from calita.internal_agents.final_result_agent import FinalResultAgent
from calita.internal_agents.mcp_tool_agent import McpToolAgent
from calita.internal_agents.task_plan_agent import TaskPlanAgent
from calita.mcp_creation.mcp_creation_agent import McpCreationAgent
from calita.utils.mcp_config_loader import load_mcp_servers_config
from calita.utils.model_client import ModelClientFactory, ModelClient
from calita.utils.utils import handle_error
from calita.web_agent import WebAgent


class TaskState(TypedDict):
    """State definition for the agent orchestration graph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_input: str
    super_next: str
    tasks: List[Dict[str, Any]]
    current_task: Dict[str, Any]
    next_task: Dict[str, Any]
    formatted_result: str
    iteration_count: int

class ManagerAgent:
    def __init__(self, config: Dict[str, Any]) -> None:
        try:
            # API configuration
            model_config = {}
            api_config: Dict[str, Any] = config.get("api", {})
            model_config['temperature'] = float(api_config.get("temperature", 0.7))
            model_config['max_tokens'] = int(api_config.get("max_tokens", 16384))
            primary_llm = config.get("agent", {}).get("primary_llm")
            model_config['model'] = primary_llm
            reason_model = config.get("agent", {}).get("reason_llm")
            model_config['reason_model'] = reason_model if reason_model else primary_llm


            # Initialize model client using factory
            model_client: ModelClient = ModelClientFactory.create_client(config)

            # Load MCP servers configuration
            self.mcp_servers_config: Dict[str, Any] = load_mcp_servers_config("mcp_box_servers.json")

            # Initialize the graph (will be created when needed)
            self.max_iterations: int = 3
            self.graph = None

            self.mcp_creation_agent = McpCreationAgent(config)
            self.web_agent = WebAgent()
            self.task_plan_agent = TaskPlanAgent(model_client, model_config)
            self.mcp_tool_agent = McpToolAgent(model_client, model_config)
            self.final_result_agent = FinalResultAgent(model_client, model_config)
            self.mcp_tool_schemas = self.mcp_tool_agent.get_tool_schema()

            logging.info(f"ManagerAgent initialized ,max_iterations={self.max_iterations}")
        except Exception as e:
            handle_error(e)


    async def _create_graph(self) -> StateGraph:
        """
        Create and configure the LangGraph with MCP tools.

        Returns:
            StateGraph: Configured retrieval graph
        """
        try:
            # Create graph builder
            graph_builder = StateGraph(TaskState)

            # Add nodes
            graph_builder.add_node("supervisor", self._supervisor_node)
            graph_builder.add_node("task_plan_agent", self._task_plan_agent_node)
            graph_builder.add_node("web_agent", self._web_agent_node)
            graph_builder.add_node("tool_agent", self._tool_agent_node)
            graph_builder.add_node("mcp_creation_agent", self._mcp_creation_agent_node)
            graph_builder.add_node("eval_task", self._eval_task_node)
            graph_builder.add_node("final_result", self._final_result_node)

            # Add edges
            graph_builder.add_edge(START, "supervisor")
            graph_builder.add_conditional_edges(
                "supervisor",
                self._supervisor_router,
                {
                    "task_plan_agent": "task_plan_agent",
                    "web_agent": "web_agent",
                    "tool_agent": "tool_agent",
                    "mcp_creation_agent": "mcp_creation_agent",
                    "end": END,
                }
            )

            graph_builder.add_edge("task_plan_agent", "supervisor")
            graph_builder.add_edge("web_agent", "eval_task")
            graph_builder.add_edge("tool_agent", "eval_task")
            graph_builder.add_edge("mcp_creation_agent", "eval_task")

            graph_builder.add_conditional_edges(
                "eval_task",
                self._next_task_condition,
                {
                    "next_task": "supervisor",
                    "final_result": "final_result",
                }
            )

            graph_builder.add_conditional_edges(
                "eval_task",
                self._task_end_condition,
                {
                    "restart": "supervisor",
                    "task_end": END,
                }
            )

            graph_builder.add_edge("final_result", END)

            # Compile the graph with proper checkpointer configuration
            graph = graph_builder.compile(checkpointer=MemorySaver())
            graph.name = "Manager Agent"

            return graph
        except Exception as e:
            logging.error("Failed to create ManagerAgent graph: %s", str(e))
            raise

    def _supervisor_node(self, state: TaskState) -> Dict[str, Any]:
        super_next = "end"

        current_task = None
        tasks = state["tasks"]
        iteration_count = state["iteration_count"]

        if state["super_next"] is None: #First Time
            super_next = "task_plan_agent"
        elif state["super_next"]  == "task_plan_agent": #Task Plan Complete
            if len(tasks) > 0: #Task Plan Succeed
                first_task = tasks[0]
                current_task = first_task
                super_next = "end" if first_task["agent"] is None else first_task["agent"]
            else:
                logging.error(f"supervisor_node: task plan fail, user_input={state['user_input']}")
        elif state["next_task"] and len(state["next_task"]) > 0: #Begin Next Task
            current_task = state["next_task"]
            super_next = current_task["agent"]
        else: # Current Task Exec Fail or Final result is unsatisfy
            if iteration_count < self.max_iterations: # task 执行失败, 重新规划
                super_next = "task_plan_agent"
                iteration_count += 1
                tasks = []
                logging.warning(f"=== supervisor_node: begin next iteration, iteration_count={iteration_count} ===")
            else:
                logging.error(f"### supervisor_node: max_iteration is reached, iteration_count={iteration_count} ### ")

        logging.info(f"supervisor_node[{iteration_count}]： super_next={super_next}")
        return {
            "next_task": None,
            "super_next": super_next,
            "current_task": current_task,
            "iteration_count": iteration_count,
            "tasks": tasks,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _task_plan_agent_node(self, state: TaskState) -> Dict[str, Any]:
        logging.info(f"task_plan_agent_node： begin task plan, user_input={state['user_input']}")
        user_input = state['user_input']
        plan_tasks = self.task_plan_agent.task_plan(user_input, self.mcp_tool_schemas)

        return {
            "tasks" : plan_tasks,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _web_agent_node(self, state: TaskState) -> Dict[str, Any]:
        task = state["current_task"]
        logging.info(f"web_agent_node： begin web search, task={task}")

        search_result = self.web_agent.search(task["target"])
        task["result"] = search_result.get("result")
        task["error"] = search_result.get("error")

        return {
            "current_task": task,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _tool_agent_node(self, state: TaskState) -> Dict[str, Any]:
        task = state["current_task"]
        logging.info(f"tool_agent_node： begin use mcp tool, task={task}")

        tool_result = self.mcp_tool_agent.call(task["target"], "")
        task["result"] = tool_result.get("result")
        task["error"] = tool_result.get("error")

        return {
            "current_task": task,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _mcp_creation_agent_node(self, state: TaskState) -> Dict[str, Any]:
        task = state["current_task"]
        logging.info(f"mcp_creation_agent_node： begin create mcp tool, task={task}")

        generate_result = self.mcp_creation_agent.generate(task["target"], "")
        task["result"] = generate_result.get("result")
        task["error"] = generate_result.get("error")

        return {
            "current_task": task,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _eval_task_node(self, state: TaskState) -> Dict[str, Any]:
        current_task = state["current_task"]
        logging.info(f"evaluate_node： begin evaluate result, task={current_task}")
        tasks = state["tasks"]
        task_no = current_task["task_no"]

        next_task = None
        tasks[task_no]["result"] = current_task.get("result")
        tasks[task_no]["error"] = current_task.get("error")

        task_state = 1
        if current_task.get("error") is None:
            task_state = 0
            if task_no < len(tasks) -1: # Has next task
                next_task = tasks[task_no + 1]
            else: # All task is completed succeed
                next_task = {}
        elif state['iteration_count'] >= self.max_iterations: # max_iterations is reached， END
            logging.error(f"### evaluate_node: max_iteration is reached, iteration_count={state['iteration_count']} ### ")
            next_task = {}

        tasks[task_no]["state"] = task_state
        current_task["state"] = task_state

        return {
            "current_task": current_task,
            "next_task" : next_task,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _final_result_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state["user_input"]
        task_results = ""
        tasks = state["tasks"]
        for task in tasks:
            task_result = {
                "task_no": task["task_no"],
                "task": task["target"],
                "result" : task.get("result"),
                "error" : task.get("error"),
            }
            task_results += f"{task_result}\n"
        logging.info(f"final_result_node： begin formate result{task_results}")
        formatted_result = self.final_result_agent.final_result(user_input, task_results)

        logging.info(f"FINAL_RESULT： {formatted_result}")
        return {
            "formatted_result" : formatted_result,
            "messages": state["messages"] + [AIMessage(content=f"Supervisor: ")]
        }

    def _next_task_condition(self, state: TaskState) -> str:
        cond = "next_task"
        next_task = state["next_task"]
        if next_task is not None and len(next_task) == 0:
            cond = "final_result"
        return cond

    def _task_end_condition(self, state: TaskState) -> str:
        cond = "task_end"
        formatted_result = state["formatted_result"]
        if formatted_result is not None:
            final_result_type = int(formatted_result.get("final_result_type"))
            if final_result_type < 0 or final_result_type > 0:
                cond = "restart" if state['iteration_count'] < self.max_iterations else "task_end"
        else:
            cond = "restart" if state['iteration_count'] < self.max_iterations else "task_end"
        return cond

    def _supervisor_router(self, state: TaskState) -> str:
        return state['super_next']

    async def _agent_work(self, user_input: str) -> str:
        result = ""
        try:
            logging.info("Starting agent work for user_input: %s", user_input)

            # Create graph if not already created
            if self.graph is None:
                self.graph = await self._create_graph()

            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=f"information for: {user_input}")],
                "user_input": user_input,
                "super_next": None,
                "tasks": [],
                "current_task": None,
                "next_task": None,
                "formatted_result": None,
                "iteration_count": 1
            }

            # Run the retrieval graph with proper configuration
            config = {"recursion_limit": 90,
                      "configurable": {"thread_id": "manager_agent_work_thread"}}
            final_state = await self.graph.ainvoke(initial_state, config=config)

            # Parse and return formatted results
            result = final_state["formatted_result"]

            logging.info("ManagerAgent completed successfully for user question: %s", user_input)
            return result

        except Exception as e:
            logging.error("Error during ManagerAgent _agent_work for user_input '%s': %s", user_input, str(e))
            handle_error(e)
            return result

    def generate(self, request: str) -> str:
        result = "unknown"
        try:
            # Check if there"s already a running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we"re already in an async context, we can"t use run_until_complete
                # This is a limitation - the method should be called from sync context
                logging.warning("search() called from async context, returning empty results")
                return result
            except RuntimeError:
                # No running loop, we can create one
                pass

            # Use asyncio.run() which properly handles loop creation and cleanup
            result = asyncio.run(self._agent_work(request))
            return result
        except Exception as e:
            logging.error("Error in synchronous _agent_work wrapper: %s", str(e))
            return "execute error"


if __name__ == "__main__":
    from calita.utils.utils import get_global_config
    from calita.utils.utils import setup_logging

    config = get_global_config("config.yaml")

    # Setup logging configuration
    setup_logging(config)


    manager = ManagerAgent(config)

    # Test Mcp tool schema
    # asyncio.run(manager.refresh_mcp_box_tools())

    #result = asyncio.run(manager._agent_work("video clipping"))
    #result = asyncio.run(manager._agent_work("上周黄金的走势，输出格式{‘周一’: price}"))
    result = asyncio.run(manager._agent_work("Create a function to sort a list of numbers, sort [6,8,7,5]"))

    print(result)

