# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Veris AI Python SDK - a package that provides simulation capabilities through decorator-based function mocking and FastAPI MCP (Model Context Protocol) integration. The core functionality revolves around:
- `VerisSDK` class in `src/veris_ai/tool_mock.py:27` - enables environment-aware execution where functions can be mocked in simulation mode or executed normally in production
- `convert_to_type()` function in `src/veris_ai/utils.py:5` - handles sophisticated type conversion from mock responses
- `FastApiMCPParams` model in `src/veris_ai/models.py:1` - provides configuration for integrating FastAPI applications with the Model Context Protocol
- `set_fastapi_mcp()` method in `src/veris_ai/tool_mock.py:54` - configures FastAPI MCP server with automatic OAuth2-based session management

## Development Commands

This project uses `uv` as the package manager and follows modern Python tooling practices.

### Setup
```bash
# Install with development dependencies
uv add "veris-ai[dev]"

# Install with FastAPI MCP integration
uv add "veris-ai[fastapi]"

# Set Python version (requires 3.11+)
pyenv local 3.11.0
```

### Code Quality (Primary: Ruff)
```bash
# Lint code
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code  
ruff format .

# Check formatting only
ruff format --check .
```

### Type Checking
```bash
# Run static type checking
mypy src/veris_ai tests
```

### Testing
```bash
# Run all tests with coverage
pytest tests/ --cov=veris_ai --cov-report=xml --cov-report=term-missing

# Run specific test file
pytest tests/test_tool_mock.py

# Run tests with verbose output
pytest -v tests/
```

### Building
```bash
# Build package distributions
uv build
```

## Code Architecture

### Core Components

**VerisSDK Class** (`src/veris_ai/tool_mock.py:27`)
- Main SDK class that provides decorator functionality:
  - `@veris.mock()`: Dynamic mocking that calls external endpoints for responses
  - `@veris.stub()`: Simple stubbing with fixed return values
- Environment detection: Uses `ENV` environment variable to determine simulation vs production mode
- HTTP communication with mock endpoints via `httpx` (for mock decorator)
- Context extraction for session management via context variables
- Delegates type conversion to the utils module

**API Surface** (`src/veris_ai/__init__.py:5`)
- Exports single `veris` instance for public use
- Clean, minimal API design

**Type Conversion Utilities** (`src/veris_ai/utils.py:1`)
- `convert_to_type()` function handles sophisticated type conversion from mock responses
- Supports primitives, lists, dictionaries, unions, and custom types
- Modular design with separate conversion functions for each type category
- Uses Python's typing system for runtime type checking

**FastAPI MCP Integration** (`src/veris_ai/models.py:1`)
- `FastApiMCPParams` Pydantic model for configuring FastAPI MCP server integration
- Comprehensive configuration options including:
  - Custom server naming and descriptions
  - HTTP client configuration (base URL, headers, timeout)
  - Operation filtering (include/exclude by operation ID or tag)
  - Response schema documentation controls
  - Authentication configuration

### Environment Configuration

Required environment variables:
- `VERIS_MOCK_ENDPOINT_URL`: Mock endpoint URL (required)
- `VERIS_MOCK_TIMEOUT`: Request timeout in seconds (optional, default: 30.0)
- `ENV`: Set to "simulation" to enable mocking, anything else runs original functions

### Type System

The SDK handles sophisticated type conversion from mock responses:
- Type conversion is handled by the `convert_to_type()` function in `src/veris_ai/utils.py`
- Supports primitives, lists, dictionaries, unions, and custom types
- Modular design with separate handlers for different type categories
- Uses Python's typing system for runtime type checking

## Testing Strategy

**Test Structure**:
- `tests/conftest.py:1`: Pytest fixtures for environment mocking and context objects
- `tests/test_tool_mock.py:1`: Unit tests for the VerisSDK class and mock decorator functionality
- `tests/test_utils.py:1`: Comprehensive tests for type conversion utilities

**Key Test Fixtures**:
- `mock_context`: Provides mock context with session ID
- `simulation_env`: Sets up simulation environment variables  
- `production_env`: Sets up production environment variables

**Test Coverage Areas**:
- Environment-based behavior switching
- HTTP client interactions and error handling
- Type conversion scenarios (parametrized tests)
- Configuration validation

## Code Quality Standards

**Ruff Configuration** (80+ rules enabled):
- Line length: 100 characters
- Target: Python 3.11+
- Google-style docstring convention
- Comprehensive rule set covering style, bugs, security, and complexity
- Relaxed rules for test files (allows more flexibility in tests)

**Development Tools**:
- **Ruff**: Primary linter and formatter (replaces flake8, black, isort)
- **MyPy**: Static type checking
- **Pytest**: Testing with async support and coverage
- **Pre-commit**: Git hooks for code quality

## CI/CD Pipeline

**Testing Workflow** (`.github/workflows/test.yml`):
- Runs on Python 3.11, 3.12, 3.13
- Code quality checks (Ruff lint/format)
- Type checking (MyPy)  
- Unit tests with coverage

**Release Workflow** (`.github/workflows/release.yml`):
- Manual trigger for releases
- Semantic versioning with conventional commits
- Automated PyPI publishing
- Uses `uv build` for package building

## Key Implementation Details

- **Decorator Pattern**: Functions are wrapped to intercept calls in simulation mode
  - `mock()`: Sends function metadata to external endpoint for dynamic responses
  - `stub()`: Returns predetermined values without external calls
- **Session Management**: Extracts session ID from context for request correlation
- **Error Handling**: Comprehensive HTTP and type conversion error handling
- **Async Support**: Built with async/await pattern throughout
- **Type Safety**: Full type hints and runtime type conversion validation
- **Modular Architecture**: Type conversion logic separated into utils module for better maintainability

### FastAPI MCP Integration

The `set_fastapi_mcp()` method provides:
- **Automatic Session Handling**: OAuth2-based session ID extraction from bearer tokens
- **Context Management**: Session IDs are stored in context variables for cross-request correlation
- **Auth Config Merging**: User-provided auth configs are merged with internal session handling
- **MCP Server Access**: Configured server available via `veris.fastapi_mcp` property

Key implementation aspects:
- Creates internal OAuth2PasswordBearer scheme for token extraction
- Dependency injection for automatic session context setting
- Preserves user auth configurations while adding session management
- SSE (Server-Sent Events) support for streaming responses