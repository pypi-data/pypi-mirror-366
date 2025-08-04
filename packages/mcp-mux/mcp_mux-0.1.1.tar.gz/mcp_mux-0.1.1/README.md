# mcp-mux

A Model Context Protocol (MCP) multiplexer that simplifies tool access through semantic search.

## Overview

mcp-mux acts as a router between MCP clients and servers, providing a simplified interface that exposes only two tools (`search` and `execute`) instead of potentially hundreds. It uses semantic search to dynamically find and execute the right tools based on natural language queries.

## Quick Start

1. Initialize configuration:

```bash
uvx mcp-mux init
```

2. Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "mux": {
      "command": "uvx",
      "args": ["mcp-mux"]
    }
  }
}
```

## How It Works

Instead of exposing hundreds of tools from multiple servers, mcp-mux exposes just two:

1. **`search`** - Find tools using natural language
2. **`execute`** - Run a specific tool

## License

MIT

## Development Status

This project is in early development. Features may change.
