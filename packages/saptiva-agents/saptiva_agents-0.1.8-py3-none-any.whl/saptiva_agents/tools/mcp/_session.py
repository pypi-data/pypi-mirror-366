from contextlib import asynccontextmanager
from typing import AsyncGenerator

from autogen_ext.tools.mcp import McpServerParams
from mcp import ClientSession, stdio_client
from mcp.client.sse import sse_client

from saptiva_agents.tools.mcp import StdioServerParams, SseServerParams


@asynccontextmanager
async def create_mcp_server_session(
    server_params: McpServerParams,
) -> AsyncGenerator[ClientSession, None]:
    """Create an MCP client session for the given server parameters."""
    if isinstance(server_params, StdioServerParams):
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read_stream=read, write_stream=write) as session:
                yield session
    elif isinstance(server_params, SseServerParams):
        async with sse_client(**server_params.model_dump()) as (read, write):
            async with ClientSession(read_stream=read, write_stream=write) as session:
                yield session
