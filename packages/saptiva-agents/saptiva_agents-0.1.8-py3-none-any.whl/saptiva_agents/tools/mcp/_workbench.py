from autogen_ext.tools.mcp import McpWorkbench


class McpWorkbench(McpWorkbench):
    """
    A workbench that wraps an MCP server and provides an interface
    to list and call tools provided by the server.

    Args:
        server_params (McpServerParams): The parameters to connect to the MCP server.
            This can be either a: class:`StdioServerParams` or: class:`SseServerParams`.
    """
    pass
