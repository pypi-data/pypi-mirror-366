# TaskPriority MCP Server - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Clone and Install
```bash
git clone https://github.com/yourusername/mcp-priority.git
cd mcp-priority
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get Your API Key
1. Open http://localhost:3000 in your browser
2. Sign in or create an account
3. Go to **Settings → API Keys**
4. Click **"Create New API Key"**
5. Copy the key immediately (it won't be shown again!)

### 3. Configure Environment
```bash
cp .env.template .env
# Edit .env and add your API key:
# TASKPRIORITY_API_KEY=tp_live_YOUR_KEY_HERE
```

### 4. Add to Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "taskpriority": {
      "command": "/path/to/mcp-priority/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-priority",
      "env": {
        "TASKPRIORITY_API_KEY": "tp_live_YOUR_KEY_HERE",
        "TASKPRIORITY_API_URL": "http://localhost:3000",
        "LOG_LEVEL": "WARNING",
        "LOG_FORMAT": "text"
      }
    }
  }
}
```

### 5. Restart Claude Desktop
```bash
osascript -e 'quit app "Claude"' && sleep 2 && open -a "Claude"
```

## ✅ Verify It's Working

In Claude Desktop, try:
- "Create a task to fix the login bug"
- "List all my pending tasks"
- "Show me details for task [task-id]"

## 🔧 Troubleshooting

### Check Logs
```bash
tail -f ~/Library/Logs/Claude/mcp-server-taskpriority.log
```

### Common Issues

**401 Unauthorized**
- Make sure your API key exists in TaskPriority
- Check that the key is in both .env AND Claude config
- Verify the key starts with `tp_live_`

**Connection Failed**
- Ensure TaskPriority backend is running on localhost:3000
- Check `TASKPRIORITY_API_URL` in your config

**Tools Not Showing**
- Restart Claude Desktop completely
- Check for errors in the logs
- Verify the Python path in config is correct

## 📚 Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `create_task` | Create new tasks | "Create a task to update the homepage" |
| `list_tasks` | List and filter tasks | "Show me all pending bug tasks" |
| `get_task_details` | Get full task info | "Get details for task abc-123" |
| `update_task` | Update task fields | "Mark task xyz as completed" |
| `delete_task` | Remove tasks | "Delete task def-456" |
| `get_ai_analysis` | Get AI insights | "Get AI analysis for task ghi-789" |

---
*Need help? Check the [full documentation](./PROJECT_INDEX.md) or [troubleshooting guide](./ai_docs/logs/claude_desktop_setup_troubleshooting.md)*