#!/usr/bin/env python3
"""Simple test MCP server for testing mux functionality."""
# pyright: reportUnknownParameterType=false, reportUnknownVariableType=false

from typing import Any

from mcp.server.fastmcp import FastMCP

# Create a test server
mcp = FastMCP("Test Server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(x: float, y: float) -> float:
    """Multiply two numbers."""
    return x * y


@mcp.tool()
def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting."""
    return f"{greeting}, {name}!"


@mcp.tool()
def get_weather(city: str, units: str = "celsius") -> dict[str, Any]:
    """Get weather information for a city (mock data)."""
    return {
        "city": city,
        "temperature": 22 if units == "celsius" else 72,
        "units": units,
        "condition": "sunny",
        "humidity": 65,
    }


if __name__ == "__main__":
    mcp.run()
