"""MCP (Model Context Protocol) Client integration for msgflux library.
A lightweight implementation using HTTPx that integrates with the executor system.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional

import httpx

from msgflux._private.executor import Executor

from .exceptions import MCPError, MCPTimeoutError, MCPToolError
from .loglevels import LogLevel
from .types import MCPContent, MCPPrompt, MCPResource, MCPTool, MCPToolResult


class MCPClient:
    """Lightweight MCP client using HTTPx.

    Features:
    - SSE (Server-Sent Events) transport for real-time communication
    - Async/sync API compatible with msgflux.Executor
    - Tool execution with structured outputs
    - Resource and prompt management
    - Progress tracking and logging
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        client_info: Optional[Dict[str, Any]] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.client_info = client_info or {
            "name": "msgflux-mcp-client",
            "version": "1.0.0"
        }

        self._http_client: Optional[httpx.AsyncClient] = None
        self._session_id: Optional[str] = None
        self._initialized = False
        self._request_id_counter = 0
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._tools_cache: Optional[List[MCPTool]] = None
        self._resources_cache: Optional[List[MCPResource]] = None
        self._prompts_cache: Optional[List[MCPPrompt]] = None

    def _get_next_request_id(self) -> str:
        """Generate next request ID."""
        self._request_id_counter += 1
        return str(self._request_id_counter)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self):
        """Establish connection to MCP server."""
        if self._http_client is not None:
            return

        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self.headers
        )

        # Initialize session
        await self._initialize_session()

    async def disconnect(self):
        """Close connection to MCP server."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        self._initialized = False
        self._session_id = None
        self._clear_caches()

    def _clear_caches(self):
        """Clear all cached data."""
        self._tools_cache = None
        self._resources_cache = None
        self._prompts_cache = None

    async def _initialize_session(self):
        """Initialize MCP session with server."""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "logging": {},
                    "sampling": {},
                    "roots": {
                        "listChanged": True
                    }
                },
                "clientInfo": self.client_info
            }
        }

        response = await self._send_request("/initialize", request_data)

        if "error" in response:
            raise MCPError(f"Failed to initialize: {response['error']}")

        self._initialized = True

        # Send initialized notification
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self._send_notification("/initialized", notification)

    async def _send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send HTTP request to MCP server."""
        if not self._http_client:
            raise MCPError("Client not connected")

        try:
            response = await self._http_client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise MCPTimeoutError(f"Request to {endpoint} timed out")
        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP error {e.response.status_code}: {e.response.text}")

    async def _send_notification(self, endpoint: str, data: Dict[str, Any]):
        """Send notification to MCP server (no response expected)."""
        if not self._http_client:
            raise MCPError("Client not connected")

        try:
            await self._http_client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
        except Exception:
            # Notifications are fire-and-forget, log but don't raise
            pass

    # Resource Methods
    async def list_resources(self, use_cache: bool = True) -> List[MCPResource]:
        """List available resources."""
        if use_cache and self._resources_cache is not None:
            return self._resources_cache

        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "resources/list"
        }

        response = await self._send_request("/resources/list", request_data)

        if "error" in response:
            raise MCPError(f"Failed to list resources: {response['error']}")

        resources = []
        for resource_data in response.get("result", {}).get("resources", []):
            resources.append(MCPResource(
                uri=resource_data["uri"],
                name=resource_data["name"],
                description=resource_data.get("description"),
                mimeType=resource_data.get("mimeType"),
                annotations=resource_data.get("annotations")
            ))

        self._resources_cache = resources
        return resources

    async def read_resource(self, uri: str) -> List[MCPContent]:
        """Read content from a resource."""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "resources/read",
            "params": {"uri": uri}
        }

        response = await self._send_request("/resources/read", request_data)

        if "error" in response:
            raise MCPError(f"Failed to read resource {uri}: {response['error']}")

        contents = []
        for content_data in response.get("result", {}).get("contents", []):
            contents.append(MCPContent(
                type=content_data["type"],
                text=content_data.get("text"),
                data=content_data.get("data"),
                mimeType=content_data.get("mimeType")
            ))

        return contents

    # Tool Methods
    async def list_tools(self, use_cache: bool = True) -> List[MCPTool]:
        """List available tools."""
        if use_cache and self._tools_cache is not None:
            return self._tools_cache

        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "tools/list"
        }

        response = await self._send_request("/tools/list", request_data)

        if "error" in response:
            raise MCPError(f"Failed to list tools: {response['error']}")

        tools = []
        for tool_data in response.get("result", {}).get("tools", []):
            tools.append(MCPTool(
                name=tool_data["name"],
                description=tool_data["description"],
                inputSchema=tool_data.get("inputSchema", {})
            ))

        self._tools_cache = tools
        return tools

    async def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[float, Optional[str]], None]] = None
    ) -> MCPToolResult:
        """Execute a tool."""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        }

        response = await self._send_request("/tools/call", request_data)

        if "error" in response:
            raise MCPToolError(f"Tool {name} failed: {response['error']}")

        result = response.get("result", {})
        contents = []

        for content_data in result.get("content", []):
            contents.append(MCPContent(
                type=content_data["type"],
                text=content_data.get("text"),
                data=content_data.get("data"),
                mimeType=content_data.get("mimeType")
            ))

        return MCPToolResult(
            content=contents,
            isError=result.get("isError", False)
        )

    # Prompt Methods
    async def list_prompts(self, use_cache: bool = True) -> List[MCPPrompt]:
        """List available prompts."""
        if use_cache and self._prompts_cache is not None:
            return self._prompts_cache

        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "prompts/list"
        }

        response = await self._send_request("/prompts/list", request_data)

        if "error" in response:
            raise MCPError(f"Failed to list prompts: {response['error']}")

        prompts = []
        for prompt_data in response.get("result", {}).get("prompts", []):
            prompts.append(MCPPrompt(
                name=prompt_data["name"],
                description=prompt_data["description"],
                arguments=prompt_data.get("arguments")
            ))

        self._prompts_cache = prompts
        return prompts

    async def get_prompt(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> List[MCPContent]:
        """Get a prompt with optional arguments."""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "prompts/get",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        }

        response = await self._send_request("/prompts/get", request_data)

        if "error" in response:
            raise MCPError(f"Failed to get prompt {name}: {response['error']}")

        contents = []
        for message in response.get("result", {}).get("messages", []):
            if "content" in message:
                if isinstance(message["content"], str):
                    contents.append(MCPContent(type="text", text=message["content"]))
                elif isinstance(message["content"], list):
                    for content_data in message["content"]:
                        contents.append(MCPContent(
                            type=content_data["type"],
                            text=content_data.get("text"),
                            data=content_data.get("data"),
                            mimeType=content_data.get("mimeType")
                        ))

        return contents

    # Utility Methods
    async def ping(self) -> bool:
        """Send ping to check server connectivity."""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "ping"
        }

        try:
            response = await self._send_request("/ping", request_data)
            return "result" in response
        except Exception:
            return False

    async def set_logging_level(self, level: LogLevel):
        """Set server logging level."""
        notification = {
            "jsonrpc": "2.0",
            "method": "logging/setLevel",
            "params": {"level": level.value}
        }
        await self._send_notification("/logging/setLevel", notification)

    # Sync API using executor
    def connect_sync(self):
        """Synchronous version of connect."""
        executor = Executor.get_instance()
        future = executor.submit(self.connect)
        return future.result()

    def disconnect_sync(self):
        """Synchronous version of disconnect."""
        executor = Executor.get_instance()
        future = executor.submit(self.disconnect)
        return future.result()

    def list_tools_sync(self, use_cache: bool = True) -> List[MCPTool]:
        """Synchronous version of list_tools."""
        executor = Executor.get_instance()
        future = executor.submit(self.list_tools, use_cache)
        return future.result()

    def call_tool_sync(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> MCPToolResult:
        """Synchronous version of call_tool."""
        executor = Executor.get_instance()
        future = executor.submit(self.call_tool, name, arguments)
        return future.result()

    def list_resources_sync(self, use_cache: bool = True) -> List[MCPResource]:
        """Synchronous version of list_resources."""
        executor = Executor.get_instance()
        future = executor.submit(self.list_resources, use_cache)
        return future.result()

    def read_resource_sync(self, uri: str) -> List[MCPContent]:
        """Synchronous version of read_resource."""
        executor = Executor.get_instance()
        future = executor.submit(self.read_resource, uri)
        return future.result()

    def list_prompts_sync(self, use_cache: bool = True) -> List[MCPPrompt]:
        """Synchronous version of list_prompts."""
        executor = Executor.get_instance()
        future = executor.submit(self.list_prompts, use_cache)
        return future.result()

    def get_prompt_sync(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> List[MCPContent]:
        """Synchronous version of get_prompt."""
        executor = Executor.get_instance()
        future = executor.submit(self.get_prompt, name, arguments)
        return future.result()
