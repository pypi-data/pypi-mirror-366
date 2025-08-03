# TaskPriority MCP Server API Reference

This document provides a comprehensive reference for all MCP tools available in the TaskPriority server.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Tools](#tools)
  - [create_task](#create_task)
  - [list_tasks](#list_tasks)
  - [get_task_details](#get_task_details)
  - [update_task](#update_task)
  - [delete_task](#delete_task)
  - [get_ai_analysis](#get_ai_analysis)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Overview

The TaskPriority MCP Server provides intelligent task management capabilities through the Model Context Protocol. All operations are performed through MCP tools that Claude Desktop can invoke on your behalf.

### Base Configuration

- **API Version**: v1
- **Protocol**: MCP (Model Context Protocol)
- **Authentication**: Bearer token (API key)
- **Content Type**: application/json

## Authentication

All requests to the TaskPriority API require authentication using an API key. The key must:

- Start with `tp_live_`
- Be at least 16 characters long
- Be configured in your environment or Claude Desktop config

## Tools

### create_task

Creates a new task with automatic AI analysis.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | Task description (1-1000 characters) |
| `source` | string | No | Origin of the task. Default: "internal" |
| `customer_info` | string | No | Additional context (max 5000 characters) |

#### Response

```json
{
  "success": true,
  "message": "Task created successfully",
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "description": "Implement user authentication",
    "status": "pending",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z",
    "ai_analysis": {
      "priority": 8,
      "category": "feature",
      "complexity": "medium",
      "estimated_hours": 12.5,
      "confidence_score": 85,
      "implementation_spec": "1. Set up auth middleware\n2. Create login endpoint\n3. Implement JWT tokens",
      "similar_tasks": ["456e7890-e89b-12d3-a456-426614174001"]
    }
  }
}
```

#### Example Usage

```
"Create a task to implement OAuth2 authentication with Google"
```

### list_tasks

Lists tasks with optional filtering and pagination.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status: pending, in_progress, completed, blocked |
| `category` | string | No | Filter by category: bug, feature, improvement, business, other |
| `limit` | integer | No | Number of results (1-100). Default: 50 |
| `offset` | integer | No | Pagination offset. Default: 0 |

#### Response

```json
{
  "success": true,
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "description": "Implement user authentication",
      "status": "pending",
      "priority": 8,
      "category": "feature",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 150,
  "showing": 50,
  "has_more": true
}
```

#### Example Usage

```
"Show me all pending feature tasks"
"List high-priority bugs"
```

### get_task_details

Retrieves complete information about a specific task.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | The unique identifier of the task |

#### Response

```json
{
  "success": true,
  "message": "Task retrieved successfully",
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "456e7890-e89b-12d3-a456-426614174001",
    "description": "Implement user authentication",
    "status": "pending",
    "source": "internal",
    "customer_info": "Requested by product team",
    "group_id": null,
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z",
    "ai_analysis": {
      "priority": 8,
      "category": "feature",
      "complexity": "medium",
      "estimated_hours": 12.5,
      "confidence_score": 85,
      "implementation_spec": "Detailed implementation plan...",
      "duplicate_of": null,
      "similar_tasks": ["456e7890-e89b-12d3-a456-426614174001"],
      "analyzed_at": "2025-01-01T12:00:05Z"
    }
  }
}
```

### update_task

Updates an existing task. At least one field must be provided.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | The unique identifier of the task |
| `status` | string | No | New status: pending, in_progress, completed, blocked |
| `description` | string | No | Updated description (1-1000 characters) |
| `customer_info` | string | No | Updated customer information (max 5000 characters) |

#### Response

```json
{
  "success": true,
  "message": "Task updated successfully",
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "in_progress",
    "updated_at": "2025-01-01T13:00:00Z"
    // ... other task fields
  }
}
```

#### Example Usage

```
"Update task 123e4567 to in-progress"
"Mark the authentication task as completed"
```

### delete_task

Permanently deletes a task.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | The unique identifier of the task |

#### Response

```json
{
  "success": true,
  "message": "Task deleted successfully",
  "task_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Example Usage

```
"Delete task 123e4567"
"Remove the old authentication task"
```

### get_ai_analysis

Gets or waits for AI analysis of a task. Useful when a task was created but analysis is still processing.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | The unique identifier of the task |
| `timeout` | integer | No | Maximum seconds to wait for analysis. Default: 30 |

#### Response

```json
{
  "success": true,
  "message": "AI analysis retrieved successfully",
  "analysis": {
    "id": "789e0123-e89b-12d3-a456-426614174002",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "priority": 8,
    "category": "feature",
    "complexity": "medium",
    "estimated_hours": 12.5,
    "confidence_score": 85,
    "implementation_spec": "Detailed implementation plan...",
    "duplicate_of": null,
    "similar_tasks": ["456e7890-e89b-12d3-a456-426614174001"],
    "analyzed_at": "2025-01-01T12:00:05Z"
  }
}
```

## Data Models

### Task Status

- `pending` - Task is waiting to be started
- `in_progress` - Task is actively being worked on
- `completed` - Task has been finished
- `blocked` - Task cannot proceed due to dependencies

### Task Category

- `bug` - Defect or issue to be fixed
- `feature` - New functionality to be added
- `improvement` - Enhancement to existing functionality
- `business` - Business-related task
- `other` - Miscellaneous task

### Complexity Level

- `easy` - Simple task, minimal effort required
- `medium` - Moderate complexity, standard effort
- `hard` - Complex task, significant effort required

### AI Analysis Fields

| Field | Type | Description |
|-------|------|-------------|
| `priority` | integer | Priority score from 1 (lowest) to 10 (highest) |
| `category` | string | AI-assigned task category |
| `complexity` | string | Assessed complexity level |
| `estimated_hours` | float | Estimated hours to complete (0-1000) |
| `confidence_score` | integer | AI confidence in analysis (0-100) |
| `implementation_spec` | string | Detailed implementation suggestions |
| `duplicate_of` | UUID | Task ID if this is a duplicate |
| `similar_tasks` | array[UUID] | List of similar task IDs |

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "type": "error_type",
    "message": "Human-readable error message",
    "details": {
      // Optional additional error details
    }
  }
}
```

### Common Error Types

| Error Type | Description | Common Causes |
|------------|-------------|---------------|
| `Invalid parameters` | Request validation failed | Missing required fields, invalid values |
| `Task not found` | Task ID doesn't exist | Invalid UUID, deleted task |
| `Failed to create task` | Task creation failed | API error, server issue |
| `Failed to update task` | Update operation failed | Invalid status, API error |
| `No updates provided` | Update request empty | No fields specified for update |
| `API timeout` | Request timed out | Network issues, server overload |
| `Internal error` | Unexpected error | Server bug, unhandled case |

### HTTP Status Codes

While MCP abstracts HTTP details, the underlying API uses standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

The TaskPriority API implements rate limiting to ensure fair usage:

- **Default Limit**: 1000 requests per hour
- **Burst Limit**: 100 requests per minute
- **Per-Endpoint Limits**: Some endpoints may have stricter limits

When rate limited, you'll receive an error with retry information.

## Best Practices

1. **Batch Operations**: Use list_tasks with appropriate filters instead of multiple get_task_details calls
2. **Pagination**: Always paginate when listing large datasets
3. **Error Handling**: Implement proper error handling for all tool calls
4. **Timeout Management**: Set appropriate timeouts for get_ai_analysis based on your needs
5. **Description Quality**: Provide detailed task descriptions for better AI analysis
6. **Status Updates**: Keep task statuses current to maintain accurate project visibility

## Examples

### Creating a Feature Task

```
User: "Create a task to add dark mode support to the application"

Claude will invoke:
create_task({
  "description": "Add dark mode support to the application",
  "source": "internal"
})
```

### Finding Similar Tasks

```
User: "Show me tasks similar to implementing payment processing"

Claude will:
1. First create or find a payment processing task
2. Get its AI analysis to find similar_tasks
3. Retrieve details for those similar tasks
```

### Bulk Status Update

```
User: "Mark all my authentication-related tasks as completed"

Claude will:
1. List tasks with description matching "authentication"
2. Update each task's status to "completed"
```

---

For more information, see the [Development Guide](development.md) or [Examples](../examples/).