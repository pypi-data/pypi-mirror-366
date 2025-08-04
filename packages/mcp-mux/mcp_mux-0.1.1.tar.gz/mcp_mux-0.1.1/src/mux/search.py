"""Semantic search engine for tool discovery."""

import re
from typing import Any

import numpy as np
from fastembed import TextEmbedding

from .config import SearchConfig

# Recommended embedding models with their characteristics
RECOMMENDED_MODELS = [
    {
        "name": "BAAI/bge-small-en-v1.5",
        "description": "Balanced model with good performance and speed",
        "dimensions": 384,
        "speed": "fast",
    },
    {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "description": "Lightweight model optimized for speed",
        "dimensions": 384,
        "speed": "very fast",
    },
    {
        "name": "BAAI/bge-base-en-v1.5",
        "description": "Higher accuracy with more dimensions",
        "dimensions": 768,
        "speed": "moderate",
    },
    {
        "name": "BAAI/bge-large-en-v1.5",
        "description": "Best accuracy but slower performance",
        "dimensions": 1024,
        "speed": "slow",
    },
]


class SearchEngine:
    """Semantic search engine for finding tools."""

    def __init__(self, config: SearchConfig):
        self.config = config
        self._models: dict[str, TextEmbedding] = {}  # Cache for different models
        self.tools: list[dict[str, Any]] = []
        self.embeddings: np.ndarray | None = None
        self._embedding_cache: dict[str, np.ndarray] = {}
        self._current_model_name = config.model

    def _get_model(self) -> TextEmbedding:
        """Get or create the embedding model."""
        model_name = self.config.model

        # Check if model changed and clear embeddings if so
        if model_name != self._current_model_name:
            self._current_model_name = model_name
            self.embeddings = None  # Force re-indexing with new model
            self._embedding_cache.clear()

        # Get or create model
        if model_name not in self._models:
            self._models[model_name] = TextEmbedding(model_name=model_name)

        return self._models[model_name]

    def _create_tool_text(self, tool: dict[str, Any]) -> str:
        """Create searchable text representation of a tool."""
        tool_name = tool["tool"]

        # Convert snake_case or camelCase to natural language
        expanded_name = self._expand_tool_name(tool_name)

        # Weight tool name heavily by repeating it
        parts = [
            f"Tool: {tool_name}",
            f"{tool_name}",  # Repeat for emphasis
            f"{tool_name}",  # Triple weight
            f"{expanded_name}",  # Natural language version
            f"Description: {tool['description']}",
            f"Server: {tool['server']}",  # Include server for context
        ]

        return " ".join(parts)

    def _expand_tool_name(self, tool_name: str) -> str:
        """Convert tool name from snake_case or camelCase to natural language."""
        # Handle snake_case
        if "_" in tool_name:
            return tool_name.replace("_", " ")

        # Handle camelCase
        # Insert spaces before capital letters
        expanded = re.sub(r"(?<!^)(?=[A-Z])", " ", tool_name)
        return expanded.lower()

    async def index_tools(self, tools: list[dict[str, Any]]) -> None:
        """Index tools for semantic search."""
        self.tools = tools

        if not tools:
            self.embeddings = np.array([])
            return

        # Create text representations
        texts = [self._create_tool_text(tool) for tool in tools]

        # Generate embeddings
        model = self._get_model()
        embeddings_list = list(model.embed(texts))
        self.embeddings = np.array(embeddings_list)

        # Cache embeddings if enabled
        if self.config.cache_embeddings:
            for tool, embedding in zip(tools, embeddings_list, strict=False):
                cache_key = f"{tool['server']}:{tool['tool']}"
                self._embedding_cache[cache_key] = embedding

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search for tools matching the query."""
        if not self.tools or self.embeddings is None:
            return []

        # Expand query for better matching
        expanded_query = self._expand_query(query)

        # Generate query embedding
        model = self._get_model()
        query_embedding = next(iter(model.embed([expanded_query])))

        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Boost scores for exact matches
        query_terms = query.lower().split()
        for i, tool in enumerate(self.tools):
            tool_name_lower = tool["tool"].lower()

            # Exact tool name match gets massive boost
            if query.lower() == tool_name_lower:
                similarities[i] = min(similarities[i] + 0.5, 1.0)
            # Tool name contains query or vice versa
            elif tool_name_lower in query.lower() or query.lower() in tool_name_lower:
                similarities[i] = min(similarities[i] + 0.3, 1.0)
            # Any query term matches tool name
            elif any(term in tool_name_lower for term in query_terms):
                similarities[i] = min(similarities[i] + 0.1, 1.0)

        # Get top results
        top_indices = np.argsort(similarities)[::-1][:max_results]

        results = []
        for idx in top_indices:
            tool = self.tools[idx].copy()
            tool["score"] = float(similarities[idx])
            results.append(tool)

        return results

    def add_tool(self, tool: dict[str, Any]) -> None:
        """Add a single tool to the index."""
        # This method can be used for incremental updates
        # For now, we'll re-index everything
        self.tools.append(tool)
        # In a production system, you'd want to update embeddings incrementally

    def remove_tool(self, server: str, tool_name: str) -> None:
        """Remove a tool from the index."""
        self.tools = [
            t
            for t in self.tools
            if not (t["server"] == server and t["tool"] == tool_name)
        ]
        # Re-index after removal
        # In a production system, you'd want to update embeddings incrementally

    def _expand_query(self, query: str) -> str:
        """Expand query to improve semantic matching."""
        query_lower = query.lower()
        expansions = []

        # Detect action verbs and expand them
        action_verbs = {
            "read": "read reading get fetch retrieve",
            "write": "write writing save store put",
            "list": "list listing show display enumerate",
            "create": "create creating make new add",
            "delete": "delete deleting remove rm",
            "update": "update updating modify edit change",
            "run": "run running execute exec",
            "get": "get getting fetch retrieve read",
            "set": "set setting update configure",
        }

        for verb, expansion in action_verbs.items():
            if verb in query_lower:
                expansions.append(expansion)
                break

        # Add domain-specific keywords
        if any(
            word in query_lower
            for word in ["file", "files", "folder", "directory", "dir"]
        ):
            expansions.append("filesystem file")

        if any(
            word in query_lower
            for word in ["web", "webpage", "website", "url", "http", "fetch"]
        ):
            expansions.append("http url web")

        if any(word in query_lower for word in ["screen", "screenshot", "capture"]):
            expansions.append("screenshot screen capture")

        if any(
            word in query_lower for word in ["code", "python", "javascript", "script"]
        ):
            expansions.append("execute code run")

        if any(word in query_lower for word in ["database", "sql", "db", "query"]):
            expansions.append("database sql query")

        # Combine original query with expansions
        if expansions:
            return f"{query} {' '.join(expansions)}"
        return query
