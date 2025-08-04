# Deployment Guide

This guide covers deployment options for the TaskPriority MCP Server in various environments.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Security Considerations](#security-considerations)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Deployment Options

The TaskPriority MCP Server can be deployed in several ways:

1. **Local Installation** - Direct installation on user's machine
2. **Docker Container** - Containerized deployment
3. **Cloud Service** - Hosted on cloud platforms
4. **Enterprise** - On-premise deployment

## Local Deployment

### System Requirements

- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application
- **Network**: Internet connection for API access

### Installation Steps

1. **Download Release**

```bash
# Download latest release
wget https://github.com/yourusername/mcp-priority/releases/latest/download/mcp-priority.tar.gz

# Extract
tar -xzf mcp-priority.tar.gz
cd mcp-priority
```

2. **Install Dependencies**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

3. **Configure Environment**

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

4. **Configure Claude Desktop**

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "taskpriority": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-priority",
      "env": {
        "TASKPRIORITY_API_KEY": "tp_live_your_api_key"
      }
    }
  }
}
```

### Service Management

#### Windows Service

Create `taskpriority-mcp.bat`:

```batch
@echo off
cd /d "C:\path\to\mcp-priority"
"venv\Scripts\python.exe" -m src.server
```

#### macOS LaunchAgent

Create `~/Library/LaunchAgents/com.taskpriority.mcp.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.taskpriority.mcp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>-m</string>
        <string>src.server</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/mcp-priority</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TASKPRIORITY_API_KEY</key>
        <string>tp_live_your_api_key</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

#### Linux Systemd

Create `/etc/systemd/system/taskpriority-mcp.service`:

```ini
[Unit]
Description=TaskPriority MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/mcp-priority
Environment="TASKPRIORITY_API_KEY=tp_live_your_api_key"
ExecStart=/path/to/venv/bin/python -m src.server
Restart=always

[Install]
WantedBy=multi-user.target
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run server
CMD ["python", "-m", "src.server"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  taskpriority-mcp:
    build: .
    container_name: taskpriority-mcp
    environment:
      - TASKPRIORITY_API_KEY=${TASKPRIORITY_API_KEY}
      - TASKPRIORITY_API_URL=https://api.taskpriority.ai
      - LOG_LEVEL=INFO
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

### Running with Docker

```bash
# Build image
docker build -t taskpriority-mcp .

# Run container
docker run -d \
  --name taskpriority-mcp \
  -e TASKPRIORITY_API_KEY=tp_live_your_api_key \
  taskpriority-mcp

# With Claude Desktop
# Update claude_desktop_config.json to use docker
{
  "mcpServers": {
    "taskpriority": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "taskpriority-mcp"],
      "env": {
        "TASKPRIORITY_API_KEY": "tp_live_your_api_key"
      }
    }
  }
}
```

## Cloud Deployment

### AWS Lambda

```python
# lambda_handler.py
import json
from src.server import TaskPriorityMCPServer

def lambda_handler(event, context):
    server = TaskPriorityMCPServer()
    # Handle MCP protocol over Lambda
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/taskpriority-mcp', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/taskpriority-mcp']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'taskpriority-mcp'
      - '--image=gcr.io/$PROJECT_ID/taskpriority-mcp'
      - '--platform=managed'
      - '--region=us-central1'
```

### Azure Container Instances

```bash
# Deploy to Azure
az container create \
  --resource-group myResourceGroup \
  --name taskpriority-mcp \
  --image taskpriority-mcp:latest \
  --environment-variables \
    TASKPRIORITY_API_KEY=tp_live_your_api_key
```

## Security Considerations

### API Key Management

1. **Never commit API keys** to version control
2. **Use environment variables** or secure key management
3. **Rotate keys regularly** (every 90 days recommended)
4. **Use different keys** for dev/staging/production

### Key Storage Options

#### Environment Variables

```bash
# .env file (git ignored)
TASKPRIORITY_API_KEY=tp_live_your_api_key
```

#### AWS Secrets Manager

```python
import boto3

def get_api_key():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='taskpriority-api-key')
    return response['SecretString']
```

#### Azure Key Vault

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_api_key():
    client = SecretClient(
        vault_url="https://myvault.vault.azure.net/",
        credential=DefaultAzureCredential()
    )
    return client.get_secret("taskpriority-api-key").value
```

### Network Security

1. **HTTPS Only**: Always use HTTPS for API communication
2. **Firewall Rules**: Restrict outbound to TaskPriority API
3. **VPN/Proxy**: Use corporate proxy if required

### Access Control

1. **User Permissions**: Limit who can access the server
2. **File Permissions**: Secure configuration files
   ```bash
   chmod 600 .env
   ```
3. **Process Isolation**: Run in separate user context

## Monitoring

### Health Checks

```python
# Health check endpoint
@app.route('/health')
async def health_check():
    try:
        # Check API connectivity
        await client.health_check()
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

### Logging

Configure structured logging:

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Metrics

Track key metrics:

- Request count and latency
- Error rates by type
- API quota usage
- Task creation/update rates

### Monitoring Tools

#### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

request_count = Counter('mcp_requests_total', 'Total MCP requests')
request_duration = Histogram('mcp_request_duration_seconds', 'Request duration')

@request_duration.time()
@request_count.count_exceptions()
async def handle_tool(tool_name, arguments):
    # Tool implementation
```

#### Application Insights

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient('YOUR_INSTRUMENTATION_KEY')

def track_event(name, properties=None):
    tc.track_event(name, properties=properties)
    tc.flush()
```

## Troubleshooting

### Common Issues

#### Connection Errors

```bash
# Test API connectivity
curl -I https://api.taskpriority.ai/api/v1/health

# Check DNS resolution
nslookup api.taskpriority.ai

# Test with API key
curl -H "Authorization: Bearer $TASKPRIORITY_API_KEY" \
     https://api.taskpriority.ai/api/v1/tasks
```

#### Permission Errors

```bash
# Check file permissions
ls -la .env

# Fix permissions
chmod 600 .env
chown $USER:$USER .env
```

#### Resource Limits

```bash
# Check memory usage
ps aux | grep python

# Increase limits if needed
ulimit -n 4096  # File descriptors
ulimit -m unlimited  # Memory
```

### Debug Mode

Enable detailed logging:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### Support Channels

1. **GitHub Issues**: Technical problems
2. **Discussions**: Questions and help
3. **Email**: support@taskpriority.ai
4. **Documentation**: Check docs first

## Best Practices

1. **Use Version Pinning**: Lock dependency versions
2. **Regular Updates**: Keep dependencies updated
3. **Backup Configuration**: Keep config backups
4. **Monitor Resources**: Track CPU/memory usage
5. **Log Rotation**: Implement log rotation
6. **Error Alerting**: Set up error notifications

---

For more information, see:
- [Configuration Guide](configuration.md)
- [API Reference](api-reference.md)
- [Development Guide](development.md)