from calita.manager_agent import ManagerAgent
from calita.mcp_creation.mcp_creation_agent import McpCreationAgent
from calita.utils.utils import get_global_config

if __name__ == "__main__":
    # Load configuration
    config = get_global_config("config.yaml")

    # Initialize the agent
    manager = ManagerAgent(config)

    # Process a task
    # result = manager.orchestrate("Create a function to sort a list of numbers")
    # print(result)
    # result = manager.orchestrate("video clipping")
    # print(result)
    # result = manager.generate("上周黄金的走势，输出格式{‘周一’: price}")
    # print(result)

    mcp_creation = McpCreationAgent(config)
    mcp_creation.generate("Create a function to sort a list of numbers", "")