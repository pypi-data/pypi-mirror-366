import sys

import click
from mcp.server.fastmcp import FastMCP

from calita.manager_agent import ManagerAgent
from calita.utils.utils import get_global_config


def run_mcp(host: str, port: int):
    mcp = FastMCP("Calita Server")
    config = get_global_config("config.yaml")
    mcp.settings.host = host
    mcp.settings.port = port

    @mcp.tool()
    def calita_generate(request: str)->str:
        manager = ManagerAgent(config)
        result = manager.generate(request)
        return result

    mcp.run(transport="sse")

def run_cli():
    config = get_global_config("config.yaml")
    manager_agent: ManagerAgent = ManagerAgent(config)

    # For single task mode, prompt the user for a natural language query.
    task: str = input("Enter a natural language query/task: ").strip()
    if not task:
        print("No task entered. Exiting.")
        sys.exit(0)
    # Process the task through ManagerAgent orchestration.
    result: str = manager_agent.generate(task)
    print("Result from ManagerAgent:")
    print(result)

@click.command()
@click.option("--mode", type=click.Choice(["sse", "cli"]),  default="cli", help="App Type：Human input cli or MCP sse")
@click.option("--host", default="localhost", help="Host to listen on for SSE")
@click.option("--port", default=57070, help="Port to listen on for SSE")
def main(mode: str, host: str, port: int) :
    try:
        if(mode == "cli"):
            run_cli()
        else:
            run_mcp(host, port)
    except Exception as e:
        print(f"An error occurred in the application: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    #run_mcp("localhost", 57070)
    run_cli()