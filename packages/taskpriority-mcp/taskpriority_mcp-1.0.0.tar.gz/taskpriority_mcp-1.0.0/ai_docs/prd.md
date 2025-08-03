# Product Requirements Document: TaskPriority AI MCP Server

## 1. Product Overview

### 1.1 Executive Summary

The TaskPriority AI MCP Server is a Python-based Model Context Protocol (MCP) server that enables seamless integration between TaskPriority AI and AI-powered development environments like Claude Desktop and Cursor. It eliminates context switching for developer-founders by providing direct task management capabilities within their AI coding assistants.

### 1.2 Problem Statement

Technical founders using TaskPriority AI currently lose 2-3 hours per week to context switching between their AI coding environment and the TaskPriority web interface. They cannot automate task creation, must manually copy information between systems, and break their flow state when managing tasks during development.

### 1.3 Solution

A lightweight MCP server that exposes TaskPriority's core functionality as tools within AI assistants, enabling developers to create, update, query, and manage tasks without leaving their development environment.

### 1.4 Key Business Metrics

- Target: 30% of existing customers adopt within 3 months
- Expected time savings: 3 hours/week per user
- New customer acquisition: 100 users via MCP-only tier
- Open source goal: 500+ GitHub stars

## 2. Target Audience

### Primary Users

- **Power users of TaskPriority AI** with 50+ tasks who want programmatic access
- **AI-native developers** using Claude Desktop, Cursor, or Continue.dev
- **Technical solo founders** building developer tools or SaaS products
- **Automation enthusiasts** connecting task management with other tools

### User Characteristics

- Already saving 5-10 hours/week with TaskPriority AI
- Comfortable with command-line tools and API integration
- Value deep integration over UI polish
- Actively using AI assistants for development

## 3. Core Features and Functionality

### 3.1 MCP Tools Specification

#### 3.1.1 create_task

Creates a new task in TaskPriority with automatic AI analysis.

**Parameters:**

- `description` (string, required): Task description
- `source` (string, optional): Origin of task (default: "internal")
- `customer_info` (string, optional): Additional context

**Returns:**

- Complete task object with ID
- Triggers automatic AI analysis
- Initial status: "pending"

**Example Usage:**

```
"Create a task to implement OAuth2 authentication for the admin panel"
```

#### 3.1.2 update_task

Updates an existing task's modifiable fields.

**Parameters:**

- `id` (string, required): Task ID
- `status` (string, optional): New status (pending|in_progress|completed|blocked)
- `description` (string, optional): Updated description
- `customer_info` (string, optional): Updated context

**Returns:**

- Updated task object
- Preserves AI analysis

#### 3.1.3 delete_task

Permanently removes a task.

**Parameters:**

- `id` (string, required): Task ID

**Returns:**

- Confirmation of deletion
- Deleted task ID

#### 3.1.4 list_tasks

Retrieves tasks with optional filtering.

**Parameters:**

- `status` (string, optional): Filter by status
- `category` (string, optional): Filter by AI-assigned category
- `limit` (integer, optional): Number of results
- `offset` (integer, optional): Pagination offset

**Returns:**

- Array of task objects
- Default: All tasks sorted by creation date (newest first)
- Includes AI analysis for each task

#### 3.1.5 get_task_details

Retrieves complete information for a specific task.

**Parameters:**

- `id` (string, required): Task ID

**Returns:**

- Complete task object with all fields
- Nested AI analysis data
- Implementation specifications

#### 3.1.6 get_ai_analysis

Retrieves or waits for AI analysis completion.

**Parameters:**

- `task_id` (string, required): Task ID
- `timeout` (integer, optional): Max wait time in seconds (default: 30)

**Returns:**

- AI analysis object with priority, complexity, estimates
- Implementation specification
- Similar/duplicate task detection
- Polls until analysis completes or timeout

### 3.2 Data Models

#### Task Object

```python
{
    "id": str,                    # UUID
    "user_id": str,              # UUID
    "description": str,          # Required
    "source": str | None,        # Origin system
    "customer_info": str | None, # Additional context
    "status": str,               # TaskStatus enum
    "group_id": str | None,      # Task group reference
    "created_at": str,           # ISO timestamp
    "updated_at": str,           # ISO timestamp
    "task_analyses": dict | None # Nested AI analysis
}
```

#### AI Analysis Object

```python
{
    "id": str,
    "task_id": str,
    "category": str | None,           # bug|feature|improvement|business|other
    "priority": int | None,           # 1-10 scale
    "complexity": str | None,         # easy|medium|hard
    "estimated_hours": float | None,  # Decimal hours
    "confidence_score": int | None,   # 0-100
    "implementation_spec": str | None,# AI-generated spec
    "duplicate_of": str | None,       # Task ID if duplicate
    "similar_tasks": list | None,     # Similar task IDs
    "analyzed_at": str               # ISO timestamp
}
```

## 4. Technical Architecture

### 4.1 Technology Stack

- **Language**: Python 3.9+
- **MCP SDK**: Official MCP Python SDK
- **HTTP Client**: aiohttp for async API calls
- **Configuration**: python-dotenv for environment variables
- **Testing**: pytest with pytest-asyncio
- **Packaging**: setuptools for pip installation

### 4.2 API Integration

#### Base Configuration

- Development URL: `http://localhost:3000`
- Production URL: Configurable via environment
- API Version: `/api/v1`
- Authentication: Bearer token with `tp_live_` prefix

#### HTTP Client Requirements

- Async/await pattern for all API calls
- Connection pooling for performance
- Automatic retry logic for network errors (max 3 attempts)
- Request timeout: 30 seconds
- Proper error propagation to MCP layer

### 4.3 Authentication Flow

1. API key stored in environment variable or config file
2. Validation occurs on first API call (lazy loading)
3. Bearer token included in all request headers
4. Invalid key returns clear error to AI assistant

### 4.4 Error Handling

#### API Error Responses

- 400 Bad Request → Clear parameter error message
- 401 Unauthorized → "Invalid API key" message
- 404 Not Found → "Task not found" with ID
- 429 Rate Limited → Show limits and reset time
- 500 Server Error → Generic error with retry suggestion

#### MCP Error Format

```python
{
    "error": {
        "type": "api_error",
        "message": "Human-readable error description",
        "details": {...}  # Optional additional context
    }
}
```

## 5. Development Phases

### Phase 1: Core MCP Server (Week 1-2)

**Deliverables:**

- Basic MCP server structure
- Configuration management
- API client with authentication
- Tools: create_task, list_tasks, get_task_details
- Basic error handling
- Unit tests for core functionality

**Acceptance Criteria:**

- Can create tasks from Claude/Cursor
- Lists tasks with proper formatting
- Handles API errors gracefully
- Passes all unit tests

### Phase 2: Advanced Operations (Week 3)

**Deliverables:**

- Tools: update_task, delete_task
- get_ai_analysis with polling mechanism
- Query parameter support for list_tasks
- Integration tests with mock API

**Acceptance Criteria:**

- Can update task status from AI assistant
- AI analysis polling completes within timeout
- Filtering works correctly
- 90% test coverage

### Phase 3: Production Polish (Week 4)

**Deliverables:**

- Comprehensive logging system
- Performance optimizations
- Installation documentation
- Usage examples for Claude/Cursor
- NPM packaging setup

**Acceptance Criteria:**

- Sub-second response times
- Clear installation instructions
- Working examples in documentation
- Published to npm registry

### Phase 4: Open Source Release (Week 5)

**Deliverables:**

- MIT license addition
- Contributing guidelines
- GitHub Actions CI/CD
- Issue templates
- Community documentation

**Acceptance Criteria:**

- Passes all automated checks
- Documentation complete
- Demo video recorded
- Listed in MCP directory

## 6. Security Considerations

### API Key Management

- Never log API keys
- Support environment variables and config files
- Clear documentation on secure storage
- Validate key format before use

### Data Privacy

- No local data caching
- No sensitive data in logs
- Respect TaskPriority's data retention policies
- HTTPS only for production

## 7. Performance Requirements

### Response Times

- List operations: < 500ms
- Single item operations: < 300ms
- AI analysis polling: Configurable timeout
- Connection establishment: < 1 second

### Scalability

- Support concurrent operations
- Connection pooling for efficiency
- Graceful degradation under load
- Memory usage < 50MB

## 8. Monitoring and Analytics

### Usage Metrics

- Track tool invocation counts
- Monitor error rates by type
- Measure response times
- Count unique users (hashed API keys)

### Integration Points

- Optional telemetry to TaskPriority
- Local usage statistics
- Error reporting (opt-in)

## 9. Documentation Requirements

### Developer Documentation

- Complete API reference
- MCP tool specifications
- Error handling guide
- Testing instructions

### End User Documentation

- Installation guide (npm, pip)
- Configuration tutorial
- Claude Desktop setup
- Cursor IDE setup
- Common use cases
- Troubleshooting guide

## 10. Testing Strategy

### Unit Tests

- Each MCP tool individually
- API client methods
- Error handling paths
- Configuration loading

### Integration Tests

- Full request/response cycles
- API error simulation
- Timeout handling
- Authentication flows

### End-to-End Tests

- Installation process
- Basic workflow completion
- Error recovery
- Performance benchmarks

## 11. Future Expansion Possibilities

### Near-term (3-6 months)

- GitHub integration for auto task creation
- Webhook support for external triggers
- Batch operations optimization
- Natural language task querying

### Long-term (6-12 months)

- Task dependencies management
- Time tracking integration
- Custom AI prompt templates
- Multi-workspace support
- Slack/Discord notifications

## 12. Success Metrics

### Technical Metrics

- Installation success rate > 95%
- Average response time < 400ms
- Error rate < 1%
- Test coverage > 90%

### Business Metrics

- 30% existing customer adoption in 3 months
- 100 new MCP-only customers
- 500+ GitHub stars
- Featured in MCP showcase

## 13. Implementation Notes

### MCP Protocol Compliance

- Follow official MCP server template
- Use standard tool response formats
- Support streaming responses where applicable
- Implement proper tool descriptions

### Python Package Structure

```
taskpriority-mcp/
├── src/
│   └── taskpriority_mcp/
│       ├── __init__.py
│       ├── server.py        # MCP server entry point
│       ├── api_client.py    # TaskPriority API wrapper
│       ├── tools.py         # MCP tool implementations
│       ├── models.py        # Data models
│       └── config.py        # Configuration management
├── tests/
├── examples/
├── setup.py
├── requirements.txt
└── README.md
```

### Example Usage in Claude

```
Human: Create a task to add user authentication to the admin panel
```
