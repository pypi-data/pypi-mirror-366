#!/usr/bin/env python3
"""Test client for MCP Mux server."""
# ruff: noqa: T201, E501, SIM117
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# pyright: reportAttributeAccessIssue=false, reportUnknownArgumentType=false

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mux():
    """Test the MCP Mux server functionality."""
    # Connect to the mux server
    # Pass current environment to ensure LD_LIBRARY_PATH is preserved
    server_params = StdioServerParameters(
        command="mux",
        args=[],
        env=dict(os.environ),  # Pass all environment variables
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("✓ Connected to MCP Mux server")

            # List available tools
            tools = await session.list_tools()
            print(f"\n✓ Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Test the search tool
            print("\n✓ Testing search tool...")
            search_result = await session.call_tool(
                "search", arguments={"query": "echo print", "max_results": 3}
            )

            print(
                f"  Search results (content count: {len(search_result.content) if search_result.content else 0}):"
            )
            if search_result.content:
                for content in search_result.content:
                    if hasattr(content, "text"):
                        # The text might be the results directly as a list
                        try:
                            if content.text:
                                results = (
                                    json.loads(content.text)
                                    if isinstance(content.text, str)
                                    else content.text
                                )
                                for result in results:
                                    print(
                                        f"    - {result['server']}/{result['tool']} (score: {result['score']:.3f})"
                                    )
                                    print(f"      {result['description']}")
                            else:
                                print("    No results found")
                        except json.JSONDecodeError:
                            print(f"    Raw result: {content.text}")

            # Test the execute tool
            print("\n✓ Testing execute tool...")
            # First, let's execute a simple tool from the search results
            if search_result.content and hasattr(search_result.content[0], "text"):
                results = json.loads(search_result.content[0].text)
                if results:
                    first_result = results[0]
                    print(
                        f"  Executing {first_result['server']}/{first_result['tool']}..."
                    )

                    execute_result = await session.call_tool(
                        "execute",
                        arguments={
                            "server": first_result["server"],
                            "tool": first_result["tool"],
                            "arguments": {"message": "Hello from Mux!"},
                        },
                    )

                    if execute_result.content:
                        for content in execute_result.content:
                            if hasattr(content, "text"):
                                print(f"  Result: {content.text}")


if __name__ == "__main__":
    asyncio.run(test_mux())
