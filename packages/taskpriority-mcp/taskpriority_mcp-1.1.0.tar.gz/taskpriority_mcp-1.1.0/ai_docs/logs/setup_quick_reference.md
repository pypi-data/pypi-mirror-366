# TaskPriority MCP Server - Quick Setup Reference

## Prerequisites
- Python 3.8+
- TaskPriority backend running on localhost:3000
- Valid TaskPriority API key (format: `tp_live_*`)

## Quick Setup Steps

### 1. Clone and Setup Environment
```bash
cd /Users/alexgreenblat/startups/mcp-priority
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create `.env` file:
```env
TASKPRIORITY_API_KEY=your_api_key_here
TASKPRIORITY_API_URL=http://localhost:3000
LOG_LEVEL=WARNING
LOG_FORMAT=text
```

### 3. Add to Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "taskpriority": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-priority",
      "env": {
        "TASKPRIORITY_API_KEY": "your_key",
        "TASKPRIORITY_API_URL": "http://localhost:3000",
        "LOG_LEVEL": "WARNING",
        "LOG_FORMAT": "text"
      }
    }
  }
}
```

### 4. Restart Claude Desktop
```bash
osascript -e 'quit app "Claude"' && sleep 2 && open -a "Claude"
```

## Common Issues

### Logs in Wrong Place
- **Fix**: Ensure logging uses stderr, not stdout
- **File**: `src/logging_config.py`
- **Code**: `console_handler = logging.StreamHandler(sys.stderr)`

### Pydantic Validation Errors
- **Fix**: Use camelCase `inputSchema` not `input_schema`
- **Check**: All Tool definitions in `server.py`

### Server Connection Issues
- **Fix**: Verify TaskPriority backend is running on localhost:3000
- **Check**: API key format starts with `tp_live_`

## Testing

### Check Logs
```bash
tail -f ~/Library/Logs/Claude/mcp-server-taskpriority.log
```

### Test Directly
```bash
cd /path/to/mcp-priority
source venv/bin/activate
python -m src.server
```

## Available Tools
- `create_task` - Create new tasks
- `list_tasks` - List tasks with filters
- `get_task_details` - Get task details
- `update_task` - Update task fields
- `delete_task` - Delete tasks
- `get_ai_analysis` - Get AI analysis