import asyncio
import json
import logging
from typing import Dict, Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from calita.utils.mcp_config_loader import load_mcp_servers_config


class WebAgent:
    def __init__(self) -> None:
        mcp_servers_config: Dict[str, Any] = load_mcp_servers_config("mcp_config/mcp_web_agent_server.json")
        logging.info("Loaded MCP servers: %s", list(mcp_servers_config.keys()))
        self.mcp_client = MultiServerMCPClient(mcp_servers_config.get("mcpServers", {}))


    def parse_result(self, response):
        result = {}
        try:
            _response = json.loads(response)
            if 'results' in _response  and  len(_response['results']) > 1:
                content = _response['results']
                short_content = content[:500] if len(content) >= 500 else content
                result = {"result": short_content}
            else:
                result = {'error': "search result is empty"}
        except json.JSONDecodeError:
            result = {'error': "search result is not valid JSON"}
        return result

    def search(self, query: str) -> Dict[str, Any]:
        return asyncio.run(self._async_search(query))

    async def _async_search(self, query: str) -> Dict[str, Any]:
        result = {}
        try:
            logging.info("Executing Exa MCP search for query: %s", query)

            async with self.mcp_client.session("exa") as session:
                tools = await load_mcp_tools(session)
                web_search_tool = next(t for t in tools if t.name == "web_search_exa")
                response = await web_search_tool.arun({"query": query, "numResults": 3})
                result = self.parse_result(response)
        except Exception as e:
            logging.error("Exception occurred during Exa MCP search for query '%s': %s", query, str(e))
            result['error'] = str(e)

        return result

if __name__ == "__main__":
    web_agent = WebAgent()
    result = web_agent.search("上周黄金的走势")
    print(result)