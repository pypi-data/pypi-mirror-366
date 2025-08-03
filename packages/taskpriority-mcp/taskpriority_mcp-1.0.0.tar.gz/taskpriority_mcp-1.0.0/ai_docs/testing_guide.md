# TaskPriority MCP Server Testing Guide

This guide will walk you through testing your MCP server implementation step by step.

## Prerequisites

Before testing, ensure you have:
- Python 3.10+ installed
- A TaskPriority API key (get one from https://taskpriority.ai)
- Claude Desktop installed
- Git repository cloned locally

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
cd /Users/alexgreenblat/startups/mcp-priority
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Create Environment File

Create a `.env` file in the project root:

```bash
cat > .env << EOF
TASKPRIORITY_API_KEY=tp_live_your_actual_api_key_here
TASKPRIORITY_API_URL=https://api.taskpriority.ai
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
EOF
```

**Important**: Replace `tp_live_your_actual_api_key_here` with your actual API key!

## Step 2: Test Server Locally (Without Claude)

### 2.1 Test Direct Python Execution

```bash
# Test if the server starts
python -m src.server
```

You should see output like:
```
2025-01-01 12:00:00 - src.server - INFO - Starting TaskPriority MCP Server...
2025-01-01 12:00:00 - src.server - INFO - Server version: 1.0.0
```

Press `Ctrl+C` to stop.

### 2.2 Test API Client Directly

Create a test script `test_client.py`:

```python
import asyncio
from src.priority_client import create_client
from src.models import CreateTaskRequest

async def test_client():
    # Create client
    client = await create_client()
    
    try:
        # Test health check
        print("Testing health check...")
        health = await client.health_check()
        print(f"✓ Health check: {health}")
        
        # Test creating a task
        print("\nTesting task creation...")
        request = CreateTaskRequest(
            description="Test task from MCP server",
            source="test"
        )
        task = await client.create_task(request)
        print(f"✓ Created task: {task.id}")
        print(f"  Description: {task.description}")
        print(f"  Status: {task.status}")
        
        if task.task_analyses:
            print(f"  AI Priority: {task.task_analyses.priority}/10")
            print(f"  Category: {task.task_analyses.category}")
        
        # Test listing tasks
        print("\nTesting task listing...")
        result = await client.list_tasks()
        print(f"✓ Found {result['total']} tasks")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_client())
```

Run it:
```bash
python test_client.py
```

## Step 3: Configure Claude Desktop

### 3.1 Find Configuration File

**macOS**:
```bash
open ~/Library/Application\ Support/Claude/
```

**Windows**:
```
%APPDATA%\Claude\
```

### 3.2 Edit claude_desktop_config.json

```json
{
  "mcpServers": {
    "taskpriority": {
      "command": "/Users/alexgreenblat/startups/mcp-priority/venv/bin/python",
      "args": [
        "-m",
        "src.server"
      ],
      "cwd": "/Users/alexgreenblat/startups/mcp-priority",
      "env": {
        "TASKPRIORITY_API_KEY": "tp_live_your_actual_api_key_here",
        "TASKPRIORITY_API_URL": "https://api.taskpriority.ai",
        "DEBUG_MODE": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: 
- Update the paths to match your system
- Replace the API key with your actual key

### 3.3 Restart Claude Desktop

Completely quit and restart Claude Desktop for the configuration to take effect.

## Step 4: Test in Claude Desktop

### 4.1 Verify Server Connection

Start a new conversation and ask:

```
What MCP servers do you have access to?
```

Claude should mention the TaskPriority server.

### 4.2 Test Basic Operations

Try these commands in sequence:

#### Test 1: Create a Task

```
Create a task to implement user authentication with email and password
```

Expected response:
- Claude should use the `create_task` tool
- You should see task details including AI analysis
- Note the task ID for next tests

#### Test 2: List Tasks

```
Show me all my pending tasks
```

Expected response:
- Claude should use the `list_tasks` tool
- You should see a list of tasks including the one you just created

#### Test 3: Get Task Details

```
Show me details for task [use the ID from Test 1]
```

Expected response:
- Claude should use the `get_task_details` tool
- You should see complete task information

#### Test 4: Update Task

```
Update that task to in-progress status
```

Expected response:
- Claude should use the `update_task` tool
- Task status should change to "in_progress"

#### Test 5: Get AI Analysis

```
What's the AI analysis for that task?
```

Expected response:
- Claude should use the `get_ai_analysis` tool
- You should see priority, complexity, time estimates

#### Test 6: Delete Task

```
Delete the test task we created
```

Expected response:
- Claude should use the `delete_task` tool
- Task should be permanently removed

## Step 5: Debugging Common Issues

### 5.1 Check Server Logs

If things aren't working, check logs:

```bash
# Run server manually with debug output
DEBUG_MODE=true LOG_LEVEL=DEBUG python -m src.server
```

### 5.2 Common Errors and Solutions

#### "API key not found"
- Check your .env file exists
- Verify TASKPRIORITY_API_KEY is set correctly
- Ensure key starts with "tp_live_"

#### "Connection refused"
- Check TASKPRIORITY_API_URL is correct
- Verify internet connection
- Test API directly: `curl https://api.taskpriority.ai/health`

#### "Module not found"
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

#### Claude doesn't see the server
- Verify claude_desktop_config.json syntax
- Check file paths are absolute, not relative
- Restart Claude Desktop completely
- Look for syntax errors in JSON

### 5.3 Enable Verbose Logging

For maximum debugging info, update your .env:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

## Step 6: Advanced Testing

### 6.1 Performance Test

```python
# test_performance.py
import asyncio
import time
from src.priority_client import create_client
from src.models import CreateTaskRequest

async def performance_test():
    client = await create_client()
    
    try:
        # Create 10 tasks
        start = time.time()
        tasks = []
        
        for i in range(10):
            request = CreateTaskRequest(
                description=f"Performance test task {i+1}"
            )
            task = await client.create_task(request)
            tasks.append(task)
            print(f"Created task {i+1}/10")
        
        end = time.time()
        print(f"\nCreated 10 tasks in {end-start:.2f} seconds")
        print(f"Average: {(end-start)/10:.2f} seconds per task")
        
        # Clean up
        for task in tasks:
            await client.delete_task(str(task.id))
            
    finally:
        await client.close()

asyncio.run(performance_test())
```

### 6.2 Error Handling Test

Try these in Claude to test error handling:

```
# Test invalid task ID
Get details for task invalid-id-12345

# Test empty description
Create a task with description ""

# Test invalid status
Update task [valid-id] to status "flying"
```

## Step 7: Integration Test Checklist

Run through this checklist to ensure everything works:

- [ ] Server starts without errors
- [ ] API key validation works
- [ ] Can create tasks with AI analysis
- [ ] Can list tasks with filtering
- [ ] Can get specific task details
- [ ] Can update task status and description
- [ ] Can delete tasks
- [ ] Error messages are helpful
- [ ] Claude Desktop integration works
- [ ] Performance is acceptable (<2s per operation)

## Troubleshooting Resources

1. **Check API Status**: https://status.taskpriority.ai
2. **API Documentation**: https://docs.taskpriority.ai
3. **MCP Documentation**: https://github.com/modelcontextprotocol/servers
4. **Project Issues**: Check ai_docs/development_plan.md

## Success Criteria

Your MCP server is working correctly if:
1. ✅ All 6 MCP tools work in Claude Desktop
2. ✅ Tasks are created with AI analysis
3. ✅ Error handling provides clear messages
4. ✅ Performance is responsive
5. ✅ Server remains stable during use

---

Congratulations! If all tests pass, your TaskPriority MCP Server is fully operational! 🎉