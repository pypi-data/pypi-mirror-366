from typing import Callable, Dict, List, Optional

from .client import MCPClient, MCPToolError


# Integration with msgflux tool system
def create_mcp_tool_wrapper(client: MCPClient, tool_name: str):
    """Create a msgflux-compatible tool wrapper for MCP tools.

    This allows MCP tools to be used directly in the msgflux tool system.
    """

    async def mcp_tool_impl(**kwargs):
        """Implementation function for MCP tool."""
        result = await client.call_tool(tool_name, kwargs)

        if result.isError:
            error_msg = ""
            for content in result.content:
                if content.type == "text" and content.text:
                    error_msg += content.text
            raise MCPToolError(f"MCP tool {tool_name} failed: {error_msg}")

        # Return text content or structured data
        output = []
        for content in result.content:
            if content.type == "text" and content.text:
                output.append(content.text)
            elif content.type == "resource" and content.data:
                output.append(content.data)

        return "\n".join(output) if output else "Tool executed successfully"

    # Add metadata for msgflux tool system
    mcp_tool_impl.__name__ = f"mcp_{tool_name}"
    mcp_tool_impl.__doc__ = f"MCP tool: {tool_name}"

    return mcp_tool_impl


# Factory function for easy integration
async def create_mcp_tools_from_server(
    server_url: str,
    timeout: float = 30.0,
    headers: Optional[Dict[str, str]] = None
) -> List[Callable]:
    """Factory function to create msgflux tools from MCP server.

    Usage:
        tools = await create_mcp_tools_from_server("http://localhost:8080")
        library = ToolLibrary("mcp_tools", tools)
    """
    client = MCPClient(server_url, timeout=timeout, headers=headers)

    async with client:
        mcp_tools = await client.list_tools()

        msgflux_tools = []
        for mcp_tool in mcp_tools:
            tool_wrapper = create_mcp_tool_wrapper(client, mcp_tool.name)
            msgflux_tools.append(tool_wrapper)

        return msgflux_tools
