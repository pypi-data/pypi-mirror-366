# Claude Desktop Configuration Examples

This directory contains example configurations for different installation methods and platforms.

## File Locations

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## Configuration Examples

### 1. Standard pip Installation
Use `claude_config_pip.json` - Works after `pip install taskpriority-mcp`

### 2. Python Module
Use `claude_config_python.json` - Works with any Python installation

### 3. Node.js/npx
Use `claude_config_npm.json` - Works with Node.js installed

### 4. Docker
Use `claude_config_docker.json` - Works with Docker installed

### 5. Development Mode
Use `claude_config_dev.json` - For developers working on the source

## Important Notes

1. **API Key**: Replace `tp_live_YOUR_API_KEY_HERE` with your actual API key
2. **Restart Required**: Always restart Claude Desktop after changing configuration
3. **One Server**: Only use one configuration method at a time
4. **JSON Syntax**: Ensure proper JSON formatting (no trailing commas!)

## Quick Setup

1. Choose the config file that matches your installation method
2. Copy its contents
3. Replace/merge with your existing claude_desktop_config.json
4. Update the API key
5. Restart Claude Desktop

## Verification

After setup, ask Claude:
```
What MCP servers do you have access to?
```

Claude should mention the TaskPriority server.