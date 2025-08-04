# Comprehensive Testing Plan for MCP Mux

## Testing Framework Setup

1. **Add pytest and related dependencies** to the dev dependency group:
   - pytest (core testing framework)
   - pytest-asyncio (for async test support)
   - pytest-cov (for coverage reporting)
   - pytest-mock (for mocking)
   - pytest-timeout (for test timeouts)
   - httpx (for testing HTTP clients, already included)

2. **Create test configuration**:
   - pytest.ini with asyncio mode configuration
   - .coveragerc for coverage settings
   - tests/__init__.py

## Code Refactoring for Testability

As we implement tests, we'll make the following changes to improve testability:

1. **Configurable paths**:
   - Make config path configurable via environment variable or parameter
   - Current: `Path.home() / ".mux" / "config.json"`
   - New: Support `MUX_CONFIG_PATH` env var or parameter to load_config()

2. **Dependency injection**:
   - Allow passing custom SearchEngine to ClientManager
   - Allow passing custom ClientManager to server initialization
   - Make it easier to inject mocks for testing

3. **Better separation of concerns**:
   - Extract subprocess management into a separate class
   - Make HTTP client creation configurable
   - Separate config loading from config usage

## Test Structure and Organization

### 1. Unit Tests (tests/unit/)

**tests/unit/test_config.py**
- Test Config, SearchConfig, MCPServerConfig models
- Test validation (command vs URL exclusivity)
- Test config loading/saving with custom paths
- Test environment variable handling
- Test default values
- Test missing config file behavior

**tests/unit/test_search.py**
- Test SearchEngine initialization
- Test embedding generation
- Test tool indexing
- Test semantic search with various queries
- Test query expansion logic
- Test scoring and ranking
- Test exact match boosting
- Test model switching

**tests/unit/test_utils.py**
- Test format_tool_info with various tool schemas
- Test validate_tool_arguments with valid/invalid arguments
- Test validate_type for all JSON schema types
- Test edge cases (missing schemas, unknown types)

**tests/unit/test_client.py**
- Test MCPClient connection/disconnection
- Test tool discovery
- Test execute_tool
- Mock stdio and HTTP transports
- Test error handling and retries
- Test ClientManager with multiple clients
- Test concurrent operations
- Test shutdown/cleanup

**tests/unit/test_server.py**
- Test FastMCP tool definitions
- Test search tool with various queries
- Test execute tool with mocked clients
- Test lifespan management
- Test error handling in tools

### 2. Integration Tests (tests/integration/)

**tests/integration/test_stdio_integration.py**
- Test real stdio MCP server connection
- Use a simple test MCP server
- Test full flow: connect → discover → search → execute

**tests/integration/test_http_integration.py**
- Test HTTP/SSE MCP server connection
- Mock HTTP server with httpx
- Test connection handling

**tests/integration/test_end_to_end.py**
- Full system test with multiple servers
- Test search across multiple servers
- Test execution routing
- Test error propagation

### 3. Real End-to-End Integration Test (tests/integration/test_real_servers.py)

This will be the ultimate test that actually spins up:
1. **The MCP Mux server itself** as a subprocess
2. **Real MCP servers** like:
   - @modelcontextprotocol/server-everything (stdio)
   - sequential-thinking (stdio)
   - A simple HTTP MCP server if available
3. **A test client** that connects to Mux and:
   - Searches for tools across all servers
   - Executes tools and verifies results
   - Tests edge cases like server disconnection
   - Verifies proper cleanup on shutdown

**Real Integration Test Flow**:
```python
async def test_real_mux_integration(tmp_path):
    # 1. Create test config in tmp_path
    config_path = tmp_path / "test_config.json"

    # 2. Start mux server with custom config path
    env = {"MUX_CONFIG_PATH": str(config_path)}

    # 3. Connect as MCP client
    # 4. Search for "echo" - should find echo tool
    # 5. Execute echo tool - verify response
    # 6. Search for "list files" - should find filesystem tool
    # 7. Execute file listing - verify response
    # 8. Test error handling (invalid tool, bad arguments)
    # 9. Shutdown gracefully and verify cleanup
```

### 4. Fixtures and Utilities (tests/conftest.py)

**Shared Fixtures**:
- Mock MCP servers (stdio and HTTP)
- Sample tool definitions
- Test configurations with temporary paths
- Async event loop setup
- Temporary directories for config files
- Mock embedding models
- Real server management utilities

**Test Utilities**:
- Helper to create test tool definitions
- Helper to create mock MCP responses
- Assertion helpers for async operations
- Process management for real servers
- Config file creation helpers

## Test Coverage Goals

1. **Core Functionality** (>90% coverage):
   - All public methods in client.py, server.py, search.py
   - All validation logic in utils.py
   - Configuration loading/saving

2. **Edge Cases**:
   - Empty tool lists
   - Malformed tool schemas
   - Network failures
   - Timeout scenarios
   - Invalid configurations
   - Concurrent access

3. **Error Paths**:
   - Connection failures
   - Invalid tool execution
   - Search with no results
   - Shutdown during operations

## Mock Strategy

1. **External Dependencies**:
   - Mock FastEmbed for unit tests (avoid downloading models)
   - Mock MCP client connections
   - Mock subprocess for stdio servers
   - Mock HTTP calls with httpx

2. **Test Doubles**:
   - Create a TestMCPServer class for integration tests
   - Create predictable embeddings for search tests

## CI/CD Integration

1. **Pre-commit hooks**:
   - Run pytest on staged files
   - Check coverage thresholds

2. **GitHub Actions** (future):
   - Run full test suite on push
   - Generate coverage reports
   - Test matrix (Python versions)

## Testing Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mux --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_search.py

# Run with verbose output
uv run pytest -vv

# Run only unit tests
uv run pytest tests/unit/

# Run real integration tests (may be slower)
uv run pytest tests/integration/test_real_servers.py -v
```

## Implementation Order

1. First, refactor code for testability (config paths, dependency injection)
2. Set up pytest infrastructure and fixtures
3. Write unit tests (high coverage, fast execution)
4. Write integration tests (test component interactions)
5. Write real end-to-end test (confidence in full system)

## Progress Tracking

- [x] Add pytest dependencies to pyproject.toml
- [x] Create pytest.ini and test structure
- [x] Refactor config.py for configurable paths
- [x] Write tests/unit/test_config.py (19 tests)
- [x] Write tests/unit/test_utils.py (22 tests)
- [x] Create tests/conftest.py with fixtures
- [x] Write tests/unit/test_search.py (19 tests)
- [x] Write tests/unit/test_client.py (20 tests)
- [x] Write tests/unit/test_server.py (17 tests)
- [x] Achieve 96%+ coverage for core modules
- [ ] Write tests/integration/test_stdio_integration.py
- [ ] Write tests/integration/test_http_integration.py
- [ ] Write tests/integration/test_end_to_end.py
- [ ] Write tests/integration/test_real_servers.py
- [ ] Add testing to pre-commit hooks
- [ ] Document testing approach in README

This comprehensive testing approach will ensure MCP Mux is reliable, maintainable, and ready for production use. The refactoring for testability will make the codebase more flexible and easier to test in different environments.
