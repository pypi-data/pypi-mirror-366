# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MCP Mux is a Model Context Protocol (MCP) router that acts as both MCP client and server. It provides a simplified interface to models by exposing only two tools (`search` and `execute`) instead of potentially thousands, using semantic search to dynamically find and execute the right tools.

## Development Commands

### Environment Setup
```bash
# Create/activate virtual environment using uv
uv venv
uv pip sync
```

### Code Quality
```bash
# Run linter (configured with strict rules)
uv run ruff check .
uv run ruff format .

# Run type checker (strict mode enabled)
uv run pyright
```

### Running the Server
```bash
# Run the MCP server
uv run mux.py

# Initialize configuration
uv run mux.py init

# Launch configuration UI
uv run mux.py ui
```

## Architecture

### Core Components
- **mux.py**: Main entry point and server implementation
- **Configuration**: Stored at `~/.mux/config.json`, follows MCP client conventions
- **Tool Resolution**: Uses semantic search to match user requests to available tools from connected MCP servers

### Key Design Patterns
1. **Router Pattern**: Mux intercepts all tool requests and routes them to appropriate MCP servers
2. **Tool Discovery**: On startup or configuration change, Mux inspects all configured MCP servers to catalog their tools
3. **Semantic Search**: Uses embeddings to match user requests to the most relevant tools

### Configuration Structure
```json5
{
  "mcpServers": {
    // Standard MCP server configurations
  },
  "search": {
    "method": "local",  // Search implementation method
    "model": "..."      // Model for embeddings
  }
}
```

## Development Guidelines

### Python Version
- Requires Python >=3.13
- Uses modern Python features and type hints

### Code Standards
- Strict type checking with pyright
- Comprehensive linting with ruff (includes pyupgrade, flake8 plugins)
- Line length: 88 characters
- Use double quotes for strings

### Pre-commit Hooks
The project uses pre-commit hooks. Ensure changes pass all checks before committing.
