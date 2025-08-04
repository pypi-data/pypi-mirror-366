# MCP Mux

Mux acts as an MCP router. It acts as both MCP client and server. Instead of sending all 1000 tools you may have to the
model, we send just two: `search` and `execute`. Search allows the model to use semantic search to find the right tool
for the job, and mux will return the most likely tool(s) they will need, including their input schema. Then the model
will run `execute` in order to run the desired tool, passing in the input schema. Mux will take that input and pass it
through to the desired end MCP server, and then feed back the response.

## Starting the server

To add to your MCP host application, either pull the source locally and add:

```json
{
  "mcpServers": {
    "mux": {
      "command": "uv",
      "args": [
        "--directory",
        "~/workspace/mcp/mux",
        "run",
        "mux.py"
      ]
    }
  }
}
```

Or eventually, you'll be able to just run:

```json
{
  "mcpServers": {
    "mux": {
      "command": "uvx",
      "args": [
        "mux"
      ]
    }
  }
}
```

## Commands

- **mux** - Serve the MCP server
- **mux init** - Generates the config file at ~/.mux/config.json
- **mux ui** - Serves the configuration UI

## Config file

The configuration file largely follows the convention of other MCP clients.

```json5
{
  "mcpServers": {
    // MCP server configurations
  },
  "search": {
    "method": "local",
    "model": "..."
  }
}
```

## The process

When a user changes the MCP servers list, mux will spin up each server and inspect it to get its tools, and then
generate new embeddings (ideally we'll be smart about it and only inspect what has changed). Either immediately if doing
via the UI, or on the next run when done with direct file changes.
