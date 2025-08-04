"""Configuration management for MCP Mux."""

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings


class SearchConfig(BaseModel):
    """Configuration for the semantic search engine."""

    method: str = Field(
        default="local", description="Search method: 'local' or 'remote'"
    )
    model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description=(
            "Embedding model to use for semantic search "
            "(use 'mux model --list' to see options)"
        ),
    )
    cache_embeddings: bool = Field(
        default=True, description="Whether to cache embeddings"
    )
    max_results: int = Field(default=5, description="Maximum number of search results")


class MCPServerConfig(BaseModel):
    """Configuration for an individual MCP server."""

    # stdio server fields
    command: str | None = Field(None, description="Command to run the MCP server")
    args: list[str] = Field(
        default_factory=list, description="Arguments for the command"
    )
    env: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )

    # HTTP/SSE server fields
    url: str | None = Field(None, description="URL for HTTP/SSE MCP server")

    enabled: bool = Field(default=True, description="Whether this server is enabled")

    @model_validator(mode="after")
    def validate_server_type(self) -> "MCPServerConfig":
        """Ensure either command or url is provided, but not both."""
        if self.command and self.url:
            raise ValueError("Cannot specify both command and url")
        if not self.command and not self.url:
            raise ValueError("Must specify either command or url")
        return self


class Config(BaseSettings):
    """Main configuration for MCP Mux."""

    mcpServers: dict[str, MCPServerConfig] = Field(
        default_factory=dict, description="MCP servers to connect to"
    )
    search: SearchConfig = Field(
        default_factory=SearchConfig, description="Search configuration"
    )

    model_config = {
        "env_prefix": "MUX_",
        "env_nested_delimiter": "__",
    }


def get_config_path(path: str | Path | None = None) -> Path:
    """Get the path to the configuration file.

    Args:
        path: Optional explicit path to config file.
              If not provided, checks MUX_CONFIG_PATH env var,
              then falls back to ~/.mux/config.json

    Returns:
        Path to the configuration file
    """
    if path:
        return Path(path)

    # Check environment variable
    env_path = os.environ.get("MUX_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    # Default path
    return Path.home() / ".mux" / "config.json"


def load_config(path: str | Path | None = None) -> Config:
    """Load configuration from file.

    Args:
        path: Optional explicit path to config file.
              If not provided, uses get_config_path() logic.

    Returns:
        Loaded configuration
    """
    config_path = get_config_path(path)

    if not config_path.exists():
        # Return default config if file doesn't exist
        return Config()

    try:
        with open(config_path) as f:
            data = json.load(f)
        return Config(**data)
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}") from e


def save_config(config: Config, path: str | Path | None = None) -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save
        path: Optional explicit path to config file.
              If not provided, uses get_config_path() logic.
    """
    config_path = get_config_path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)


def init_config(path: str | Path | None = None) -> None:
    """Initialize a default configuration file.

    Args:
        path: Optional explicit path to config file.
              If not provided, uses get_config_path() logic.
    """
    default_config = Config(
        mcpServers={
            "fetch": MCPServerConfig(
                command="uvx",
                args=["mcp-server-fetch"],
                url=None,
                enabled=True,
            ),
            "time": MCPServerConfig(
                command="uvx",
                args=["mcp-server-time"],
                url=None,
                enabled=True,
            ),
            "ddg-search": MCPServerConfig(
                command="uvx",
                args=["duckduckgo-mcp-server"],
                url=None,
                enabled=True,
            ),
            "context7": MCPServerConfig(
                url="https://mcp.context7.com/mcp",
                enabled=True,
            ),
            "playwright": MCPServerConfig(
                command="npx",
                args=["@playwright/mcp@latest"],
                url=None,
                enabled=True,
            ),
        },
        search=SearchConfig(),
    )

    save_config(default_config, path)
