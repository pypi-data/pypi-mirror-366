import argparse
import os

from fastmcp.exceptions import ToolError
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from src.topology_client import TopologyClient


def add_tools(mcp: FastMCP, port: int):

    def topology_url():
        return os.getenv("TOPOLOGY_URL", f"http://localhost:{port}")

    @mcp.tool(name="get_topology_edges", description="Get topology edges from the topology service")
    def get_topology_edges() -> str:
        try:
            url = topology_url()
            return f"{TopologyClient(url).make_request('/edges')}"
        except Exception as ex:
            raise ToolError(ex)

    @mcp.tool(name="get_topology_graph", description="Get topology graph from the topology service")
    def get_topology_graph() -> str:
        try:
            url = topology_url()
            return f"{TopologyClient(url).make_request('/graph')}"
        except Exception as ex:
            raise ToolError(ex)

    @mcp.tool(name="get_topology_nodes", description="Get topology nodes from the topology service")
    def get_topology_nodes() -> str:
        try:
            url = topology_url()
            return f"{TopologyClient(url).make_request('/nodes')}"
        except Exception as ex:
            raise ToolError(ex)

    @mcp.tool(name="get_topology_events", description="Get topology events from the topology service")
    def get_topology_events() -> str:
        try:
            url = topology_url()
            return f"{TopologyClient(url).make_request('/events')}"
        except Exception as ex:
            raise ToolError(ex)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--transport", type=str, choices=["sse", "stdio", "streamable-http"], default="sse")
    parser.add_argument("-p", "--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")

    args = parser.parse_args()

    port = int(os.getenv("PORT", args.port))

    host = os.getenv("HOST", args.host)
    transport = os.getenv("TRANSPORT", args.transport)

    mcp = FastMCP("Topology MCP Server", port=port, host=host)
    add_tools(mcp=mcp, port=port)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main() 