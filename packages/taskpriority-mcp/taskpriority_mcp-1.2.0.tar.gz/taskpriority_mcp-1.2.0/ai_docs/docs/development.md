# Development Guide

This guide covers development setup, contributing guidelines, and technical details for the TaskPriority MCP Server.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Testing](#testing)
- [Code Style](#code-style)
- [Contributing](#contributing)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- TaskPriority API key (for integration testing)

### Local Development Environment

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/mcp-priority.git
cd mcp-priority
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

4. **Configure Environment**

Create a `.env` file in the project root:

```env
TASKPRIORITY_API_KEY=tp_live_your_test_api_key
TASKPRIORITY_API_URL=http://localhost:3000
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

5. **Run the Server**

```bash
# Run directly
python -m src.server

# Or with Claude Desktop (see README.md)
```

## Project Structure

```
mcp-priority/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # MCP server implementation
│   ├── config.py            # Configuration management
│   ├── auth.py              # Authentication handling
│   ├── models.py            # Pydantic data models
│   ├── priority_client.py   # TaskPriority API client
│   ├── errors.py            # Custom exceptions
│   └── logging_config.py    # Logging configuration
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Test fixtures
├── ai_docs/
│   ├── docs/                # Documentation
│   └── logs/                # Development logs
├── examples/                # Usage examples
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Development dependencies
├── pytest.ini              # Test configuration
├── .env.example            # Environment template
└── README.md               # Project documentation
```

## Architecture Overview

### Component Diagram

```
┌─────────────────┐     ┌──────────────────┐
│  Claude Desktop │────▶│   MCP Protocol   │
└─────────────────┘     └──────────────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │  TaskPriority MCP   │
                     │      Server          │
                     └─────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │  Auth Manager   │   │  Config Manager │
          └─────────────────┘   └─────────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │ Priority Client │
          └─────────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │ TaskPriority API │
          └─────────────────┘
```

### Key Components

#### MCP Server (`server.py`)

The main server class that:
- Registers MCP tools
- Handles tool invocations
- Manages client lifecycle
- Formats responses

#### Priority Client (`priority_client.py`)

HTTP client that:
- Makes API requests
- Handles retries and errors
- Manages connection pooling
- Implements rate limiting

#### Authentication (`auth.py`)

Manages API authentication:
- Validates API keys
- Generates auth headers
- Caches validation state

#### Configuration (`config.py`)

Centralized configuration using Pydantic:
- Environment variable loading
- Validation and defaults
- Type-safe settings

#### Models (`models.py`)

Pydantic models for:
- Request/response validation
- Type safety
- JSON serialization
- API documentation

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v
```

### Test Structure

```python
# tests/unit/test_priority_client.py
import pytest
from unittest.mock import AsyncMock, Mock

@pytest.mark.asyncio
async def test_create_task_success(mock_client):
    """Test successful task creation."""
    # Arrange
    mock_client.create_task.return_value = sample_task
    
    # Act
    result = await client.create_task(request)
    
    # Assert
    assert result.id == sample_task.id
```

### Testing Best Practices

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Mocking**: Use mocks for external dependencies
4. **Fixtures**: Share test data using pytest fixtures
5. **Coverage**: Aim for >90% code coverage

## Code Style

### Python Style Guide

We follow PEP 8 with these additions:

- Line length: 88 characters (Black default)
- Imports: Sorted with isort
- Type hints: Required for all public APIs
- Docstrings: Google style

### Tools

```bash
# Format code
black src tests

# Check linting
ruff check src tests

# Type checking
mypy src
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Contributing

### Development Workflow

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation
4. **Run Tests**
   ```bash
   pytest
   black src tests
   ruff check src tests
   ```
5. **Commit Changes**
   ```bash
   git commit -m "feat: add new feature"
   ```
6. **Push and Create PR**

### Commit Message Format

We use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build process or auxiliary tool changes

### Pull Request Guidelines

1. **Title**: Use conventional commit format
2. **Description**: Explain what and why
3. **Tests**: Include tests for new features
4. **Documentation**: Update relevant docs
5. **Breaking Changes**: Clearly document

## Debugging

### Enable Debug Logging

```python
# In .env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### Common Issues

#### API Key Errors

```python
# Check API key format
assert api_key.startswith("tp_live_")
assert len(api_key) >= 16
```

#### Connection Errors

```python
# Check API URL
print(f"Connecting to: {settings.api_base_url}")

# Test connection
curl -H "Authorization: Bearer $TASKPRIORITY_API_KEY" \
     https://api.taskpriority.ai/api/v1/tasks
```

#### MCP Tool Errors

```python
# Add logging to tool handlers
logger.debug(f"Tool called: {tool_name}")
logger.debug(f"Arguments: {arguments}")
```

### Debug Tips

1. **Use Logging**: Add strategic log statements
2. **Check Environment**: Verify all env vars are set
3. **Test Locally**: Run server outside Claude Desktop
4. **Inspect Requests**: Use HTTP debugging proxy
5. **Read Traces**: Check full error stack traces

## Performance Optimization

### Connection Pooling

```python
# Configure in settings
CONNECTION_POOL_SIZE=10
CONNECTION_POOL_TIMEOUT=30
```

### Caching Strategy

- Settings: Cached on first access
- Auth: Validation cached for 1 hour
- AI Analysis: Poll efficiently with backoff

### Async Best Practices

```python
# Use asyncio effectively
async def batch_operations():
    tasks = [
        client.get_task(id1),
        client.get_task(id2),
        client.get_task(id3)
    ]
    results = await asyncio.gather(*tasks)
```

### Rate Limiting

```python
# Implement exponential backoff
async def retry_with_backoff():
    for attempt in range(max_retries):
        try:
            return await make_request()
        except RateLimitError:
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
```

## Advanced Topics

### Custom MCP Tools

To add a new MCP tool:

1. **Define Tool Schema**
```python
analyze_multiple_tasks = Tool(
    name="analyze_multiple_tasks",
    description="Analyze multiple tasks at once",
    inputSchema={
        "type": "object",
        "properties": {
            "task_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of task IDs"
            }
        },
        "required": ["task_ids"]
    }
)
```

2. **Implement Handler**
```python
async def _handle_analyze_multiple_tasks(self, arguments):
    task_ids = arguments["task_ids"]
    # Implementation
```

3. **Register Tool**
```python
async def setup_tools(self):
    await self._server.add_tool(analyze_multiple_tasks, self._handle_analyze_multiple_tasks)
```

### Custom Error Types

```python
class TaskLimitExceeded(APIError):
    """Raised when user exceeds task limits."""
    pass
```

### Performance Monitoring

```python
import time

async def timed_operation():
    start = time.time()
    result = await operation()
    duration = time.time() - start
    logger.info(f"Operation took {duration:.2f}s")
    return result
```

---

For more information, see:
- [API Reference](api-reference.md)
- [Deployment Guide](deployment.md)
- [Examples](../examples/)