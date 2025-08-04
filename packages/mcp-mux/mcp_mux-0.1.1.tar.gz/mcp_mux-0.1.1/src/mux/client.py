"""MCP client connection management."""

import asyncio
import logging
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from .config import Config, MCPServerConfig

logger = logging.getLogger("mux.client")

if not sys.stderr.isatty():
    logger.setLevel(logging.CRITICAL)


class MCPClient:
    """Wrapper for an MCP client connection."""

    def __init__(self, name: str, config: MCPServerConfig):
        self.name = name
        self.config = config
        self.session: ClientSession | None = None
        self._transport_context = None  # Renamed for clarity
        self._session_context = None
        self._read = None
        self._write = None
        self.tools: list[dict[str, Any]] = []

    async def connect(self) -> None:
        """Connect to the MCP server."""
        if self.session is not None:
            return

        logger.info(f"Connecting to MCP server '{self.name}'...")

        try:
            if self.config.command:
                # stdio server
                server_params = StdioServerParameters(
                    command=self.config.command,
                    args=self.config.args,
                    env=self.config.env,
                )
                cmd_str = f"{self.config.command} {' '.join(self.config.args)}"
                logger.debug(f"Server command: {cmd_str}")
                self._transport_context = stdio_client(server_params)
                self._read, self._write = await self._transport_context.__aenter__()
            elif self.config.url:
                # HTTP server (streamable HTTP is the standard, SSE is deprecated)
                logger.debug(f"Server URL: {self.config.url}")
                self._transport_context = streamablehttp_client(self.config.url)
                # HTTP clients return (read, write, get_session_id)
                result = await self._transport_context.__aenter__()
                self._read, self._write = result[0], result[1]
            else:
                raise ValueError("No command or URL configured")

            # Create and start the session
            self._session_context = ClientSession(self._read, self._write)
            self.session = await self._session_context.__aenter__()

            # Initialize the connection
            await self.session.initialize()
            logger.info(f"Successfully connected to '{self.name}'")

            # Discover tools
            await self._discover_tools()
        except Exception as e:
            logger.error(f"Failed to connect to '{self.name}': {e}")
            await self.disconnect()
            raise

    async def _discover_tools(self) -> None:
        """Discover available tools from the server."""
        if self.session is None:
            return

        tools_response = await self.session.list_tools()
        self.tools = [
            {
                "server": self.name,
                "tool": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in tools_response.tools
        ]
        logger.info(f"Discovered {len(self.tools)} tools from '{self.name}'")

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool and return the result."""
        if self.session is None:
            raise RuntimeError(f"Client {self.name} is not connected")

        result = await self.session.call_tool(tool_name, arguments=arguments)

        # Extract the content from the result
        if result.content and len(result.content) > 0:
            content = result.content[0]
            if hasattr(content, "text"):
                return content.text  # type: ignore
            return content

        return None

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        logger.debug(f"Disconnecting from '{self.name}'...")

        # Close session first
        if self._session_context:
            try:
                await self._session_context.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing session for '{self.name}': {e}")
            finally:
                self._session_context = None
                self.session = None

        # Close transport connection (stdio/http)
        # This should properly terminate subprocesses
        if self._transport_context:
            try:
                await self._transport_context.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing transport for '{self.name}': {e}")
            finally:
                self._transport_context = None
                self._read = None
                self._write = None


class ClientManager:
    """Manages multiple MCP client connections."""

    def __init__(self, config: Config):
        self.config = config
        self.clients: dict[str, MCPClient] = {}

    async def initialize(self) -> None:
        """Initialize all configured MCP clients."""
        tasks = []
        client_names = []

        for name, server_config in self.config.mcpServers.items():
            if not server_config.enabled:
                continue

            client = MCPClient(name, server_config)
            self.clients[name] = client
            tasks.append(self._connect_client(client))
            client_names.append(name)

        # Connect to all servers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and remove failed clients
        failed_clients = []
        for name, result in zip(client_names, results, strict=False):
            if isinstance(result, Exception):
                logger.warning(f"Failed to connect to {name}: {result}")
                failed_clients.append(name)

        # Remove failed clients after iteration
        for name in failed_clients:
            del self.clients[name]

    async def _connect_client(self, client: MCPClient) -> None:
        """Connect a single client with error handling."""
        try:
            await client.connect()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {client.name}: {e}") from e

    async def get_all_tools(self) -> list[dict[str, Any]]:
        """Get all tools from all connected clients."""
        all_tools = []
        for client in self.clients.values():
            all_tools.extend(client.tools)
        return all_tools

    async def execute_tool(
        self, server: str, tool: str, arguments: dict[str, Any]
    ) -> Any:
        """Execute a tool on a specific server."""
        if server not in self.clients:
            raise ValueError(f"Server '{server}' not found or not connected")

        client = self.clients[server]
        return await client.execute_tool(tool, arguments)

    async def shutdown(self) -> None:
        """Shutdown all client connections gracefully."""
        if not self.clients:
            return

        logger.info(f"Shutting down {len(self.clients)} client connections...")

        # Disconnect all clients concurrently
        tasks = [client.disconnect() for client in self.clients.values()]

        # Wait for all disconnections with a shorter timeout
        if tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True), timeout=2.0
                )
            except TimeoutError:
                logger.debug("Some clients did not disconnect within timeout")
            except Exception as e:
                logger.debug(f"Error during shutdown: {e}")

        self.clients.clear()
        logger.info("All clients disconnected")
