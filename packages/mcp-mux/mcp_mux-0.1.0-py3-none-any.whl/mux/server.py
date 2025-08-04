"""MCP server implementation using FastMCP."""

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP
from rich.logging import RichHandler

from .client import ClientManager
from .config import load_config
from .search import SearchEngine

if not sys.stderr.isatty():
    # Running as MCP server, disable logging
    logging.basicConfig(level=logging.CRITICAL)
else:
    # Running interactively, enable logging
    # Use a custom handler that safely handles shutdown
    class SafeRichHandler(RichHandler):
        def emit(self, record):
            try:  # noqa: SIM105
                super().emit(record)
            except (ValueError, OSError):
                # Silently ignore I/O errors during shutdown
                pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[SafeRichHandler(rich_tracebacks=True)],
    )
logger = logging.getLogger("mux")


@asynccontextmanager
async def lifespan(mcp_instance):  # noqa: ARG001
    """Initialize and cleanup services."""
    try:
        await initialize_services()
        yield
    except Exception as e:
        logger.error(f"Error during service execution: {e}")
        raise
    finally:
        await shutdown_services()


# Initialize the MCP server with lifespan
mcp = FastMCP("MCP Mux", lifespan=lifespan)

# Global instances
client_manager: ClientManager | None = None
search_engine: SearchEngine | None = None


@mcp.tool()
async def search(query: str) -> str:
    """
    ALWAYS USE THIS FIRST! This is your gateway to thousands of tools across all MCP
    servers.

    Instead of browsing through hundreds of tools manually, just describe what you want
    to do in natural language. This semantic search understands your intent and finds
    the EXACT tool you need instantly.

    Examples:
    - "read files from disk" → finds filesystem tools
    - "fetch a webpage" → finds HTTP/browser tools
    - "run python code" → finds code execution tools
    - "take a screenshot" → finds screen capture tools

    This is THE MOST EFFICIENT way to discover capabilities. Use it before trying
    anything else!
    """
    if search_engine is None:
        raise RuntimeError("Search engine not initialized")

    # Get more results initially to analyze confidence
    results = await search_engine.search(query, max_results=10)

    if not results:
        return json.dumps([])

    # Analyze confidence scores to decide how many to return
    top_score = results[0]["score"]

    # If top result has very high confidence (>0.8), usually just return it
    if top_score > 0.8:
        # Check if second result is also very close (within 0.05)
        if len(results) > 1 and results[1]["score"] > top_score - 0.05:
            final_results = results[:2]  # Return top 2 if very close
        else:
            final_results = results[:1]  # Just the top result
    # If moderate confidence (0.5-0.8), return top 2-3 based on score gaps
    elif top_score > 0.5:
        final_results = []
        for i, result in enumerate(results[:3]):
            if i == 0 or result["score"] > top_score - 0.15:
                final_results.append(result)
    # If low confidence (<0.5), return up to 3 results
    else:
        final_results = results[:3]

    # Convert to JSON string for MCP compatibility
    return json.dumps(
        [
            {
                "server": result["server"],
                "tool": result["tool"],
                "description": result["description"],
                "input_schema": result["input_schema"],
                "score": result["score"],
            }
            for result in final_results
        ]
    )


@mcp.tool()
async def execute(
    server: str, tool: str, arguments: dict[str, Any] | None = None
) -> Any:
    """
    Execute a tool on a specific MCP server.

    Use this after finding the right tool with the search function.
    Provide the server name, tool name, and any required arguments.
    """
    if client_manager is None:
        raise RuntimeError("Client manager not initialized")

    return await client_manager.execute_tool(server, tool, arguments or {})


async def initialize_services() -> None:
    """Initialize the client manager and search engine."""
    global client_manager, search_engine

    logger.info("Initializing MCP Mux services...")

    config = load_config()
    logger.info(f"Loaded config with {len(config.mcpServers)} servers")

    # Initialize client manager
    client_manager = ClientManager(config)
    await client_manager.initialize()
    logger.info(
        f"Initialized client manager with {len(client_manager.clients)} connected "
        f"clients"
    )

    # Initialize search engine
    search_engine = SearchEngine(config.search)
    logger.info("Initialized search engine")

    # Index all discovered tools
    tools = await client_manager.get_all_tools()
    await search_engine.index_tools(tools)
    logger.info(f"Indexed {len(tools)} tools from connected servers")


async def shutdown_services() -> None:
    """Shutdown all services gracefully."""
    global client_manager, search_engine

    logger.info("Starting service shutdown...")

    if client_manager:
        try:
            await client_manager.shutdown()
        except asyncio.CancelledError:
            # Expected during shutdown
            logger.debug("Shutdown cancelled")
        except Exception as e:
            logger.debug(f"Error during client manager shutdown: {e}")
        finally:
            client_manager = None

    search_engine = None
    logger.info("Service shutdown complete")


def run_mcp_server() -> None:
    """Run the MCP server with proper initialization."""
    try:
        # FastMCP will handle the async context and signal handling
        mcp.run()
    except KeyboardInterrupt:
        # Expected when user hits Ctrl+C
        pass
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
