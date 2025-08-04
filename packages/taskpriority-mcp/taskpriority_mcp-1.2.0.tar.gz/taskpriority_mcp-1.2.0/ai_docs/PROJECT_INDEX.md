# TaskPriority MCP Server - Project Index

## Overview
TaskPriority MCP Server is a Model Context Protocol (MCP) server that enables AI assistants like Claude Desktop to interact with the TaskPriority task management system. It provides a bridge between AI-powered development environments and TaskPriority's API.

**Version**: 1.0.0  
**Status**: Implementation complete, authentication setup required  
**Language**: Python 3.8+  
**Protocol**: MCP (Model Context Protocol)

## Project Structure

```
mcp-priority/
├── src/                      # Core server implementation
│   ├── server.py            # Main MCP server with tool handlers
│   ├── priority_client.py   # TaskPriority API client wrapper
│   ├── auth.py             # Authentication management
│   ├── config.py           # Configuration and settings
│   ├── logging_config.py   # Logging setup (stderr for MCP)
│   └── models.py           # Pydantic models for data validation
│
├── npm-wrapper/            # NPM package wrapper
│   ├── package.json       # NPM package configuration
│   └── bin/              # Executable scripts
│
├── ai_docs/               # AI assistant documentation
│   ├── README.md         # Main documentation
│   ├── prd.md           # Product Requirements Document
│   ├── development_plan.md
│   ├── go_to_market_strategy.md
│   ├── publishing_guide.md
│   ├── testing_guide.md
│   └── logs/            # Implementation logs
│       ├── claude_desktop_setup_troubleshooting.md
│       └── setup_quick_reference.md
│
├── tests/                # Test suite (pending)
├── docker/              # Docker configuration
├── scripts/            # Utility scripts
└── Configuration Files
    ├── .env.template   # Environment variable template
    ├── requirements.txt # Python dependencies
    ├── pyproject.toml  # Python project config
    └── package.json    # Root NPM package

```

## Core Components

### 1. MCP Server (`src/server.py`)
- **Class**: `TaskPriorityMCPServer(server.Server)`
- **Purpose**: Main server handling MCP protocol communication
- **Key Features**:
  - Inherits from MCP's `server.Server` class
  - Uses decorator pattern for tool registration
  - Separates Tool objects from handlers for serialization
  - Implements 6 TaskPriority tools

### 2. API Client (`src/priority_client.py`)
- **Class**: `TaskPriorityClient`
- **Purpose**: Async HTTP client for TaskPriority API
- **Features**:
  - Connection pooling with httpx
  - Retry logic with exponential backoff
  - Comprehensive error handling
  - Type-safe with Pydantic models

### 3. Authentication (`src/auth.py`)
- **Class**: `AuthManager`
- **Purpose**: Manages API key authentication
- **Features**:
  - API key validation (format: `tp_live_*`)
  - Bearer token header generation
  - Validation caching with TTL

### 4. Configuration (`src/config.py`)
- **Class**: `Settings` (Pydantic BaseSettings)
- **Purpose**: Centralized configuration management
- **Sources**: Environment variables, .env file
- **Key Settings**:
  - `TASKPRIORITY_API_KEY`: API authentication key
  - `TASKPRIORITY_API_URL`: Backend URL (default: http://localhost:3000)
  - `LOG_LEVEL`: Logging verbosity
  - `LOG_FORMAT`: JSON or text logging

### 5. Models (`src/models.py`)
- **Purpose**: Type-safe data models
- **Key Models**:
  - `CreateTaskRequest`: New task creation
  - `UpdateTaskRequest`: Task updates
  - `TaskWithAnalysis`: Task with AI analysis
  - `AIAnalysis`: AI-generated insights

## Available MCP Tools

### 1. `create_task`
Create a new task with automatic AI analysis.
```json
{
  "description": "Task description",
  "source": "internal",
  "customer_info": "Additional context"
}
```

### 2. `list_tasks`
List tasks with optional filtering.
```json
{
  "status": "pending|in_progress|completed|blocked",
  "category": "bug|feature|improvement|business|other",
  "limit": 50,
  "offset": 0
}
```

### 3. `get_task_details`
Get complete task information including AI analysis.
```json
{
  "task_id": "uuid-format-task-id"
}
```

### 4. `update_task`
Update task properties.
```json
{
  "task_id": "uuid-format-task-id",
  "status": "new-status",
  "description": "updated description",
  "customer_info": "updated context"
}
```

### 5. `delete_task`
Permanently remove a task.
```json
{
  "task_id": "uuid-format-task-id"
}
```

### 6. `get_ai_analysis`
Get or wait for AI analysis with polling.
```json
{
  "task_id": "uuid-format-task-id",
  "timeout": 30
}
```

## Setup Requirements

### Prerequisites
- Python 3.8 or higher
- TaskPriority backend running (default: localhost:3000)
- Valid TaskPriority API key
- Claude Desktop application

### Environment Variables
```env
TASKPRIORITY_API_KEY=tp_live_your_actual_key_here
TASKPRIORITY_API_URL=http://localhost:3000
LOG_LEVEL=WARNING
LOG_FORMAT=text
DEBUG_MODE=false
```

### Claude Desktop Configuration
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "taskpriority": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-priority",
      "env": {
        "TASKPRIORITY_API_KEY": "your-api-key",
        "TASKPRIORITY_API_URL": "http://localhost:3000",
        "LOG_LEVEL": "WARNING",
        "LOG_FORMAT": "text"
      }
    }
  }
}
```

## Current Issues & Solutions

### Issue: 401 Unauthorized
**Problem**: API key doesn't exist in TaskPriority database  
**Solution**: Create API key via TaskPriority UI (Settings → API Keys)

### Issue: MCP Protocol Interference
**Problem**: JSON logs on stdout interfere with MCP  
**Solution**: Logging redirected to stderr

### Issue: Serialization Errors
**Problem**: Tool handlers not serializable  
**Solution**: Separate Tool objects from handler functions

## Development Status

### ✅ Completed
- Core MCP server implementation
- All 6 TaskPriority tools
- API client with retry logic
- Authentication system
- Error handling
- Logging configuration
- Claude Desktop integration

### ⏳ Pending
- API key creation in TaskPriority
- Health check endpoint fix
- Comprehensive test suite
- Resources/prompts MCP methods
- Production deployment guide

## Testing

### Manual Testing
```bash
# Test server directly
cd /Users/alexgreenblat/startups/mcp-priority
source venv/bin/activate
python -m src.server

# Check logs
tail -f ~/Library/Logs/Claude/mcp-server-taskpriority.log

# Test API directly
curl http://localhost:3000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### Integration Testing
1. Open Claude Desktop
2. Check for TaskPriority tools in tool list
3. Test tool execution

## Troubleshooting

### Common Commands
```bash
# Restart Claude Desktop
osascript -e 'quit app "Claude"' && sleep 2 && open -a "Claude"

# View server logs
tail -n 50 ~/Library/Logs/Claude/mcp-server-taskpriority.log

# Check for errors
grep -i error ~/Library/Logs/Claude/mcp-server-taskpriority.log
```

### Debug Checklist
1. ✓ Virtual environment activated?
2. ✓ Dependencies installed?
3. ✓ .env file configured?
4. ✓ API key valid in TaskPriority?
5. ✓ Backend running on localhost:3000?
6. ✓ Claude Desktop config updated?
7. ✓ Claude Desktop restarted?

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Document with docstrings
- Handle errors gracefully

### Testing Requirements
- Unit tests for all components
- Integration tests for API calls
- Mock external dependencies
- Maintain >80% coverage

## Resources

### Documentation
- [MCP Specification](https://modelcontextprotocol.org)
- [TaskPriority API Docs](http://localhost:3000/docs)
- [Project README](./README.md)

### Support
- GitHub Issues: [mcp-priority/issues](https://github.com/user/mcp-priority/issues)
- TaskPriority Support: support@taskpriority.ai

---
*Last Updated: 2025-08-04*  
*Generated with Claude Code*