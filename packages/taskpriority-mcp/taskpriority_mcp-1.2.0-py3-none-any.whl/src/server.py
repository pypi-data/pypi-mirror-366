#!/usr/bin/env python3
"""TaskPriority MCP Server implementation."""

import asyncio
import signal
import sys
from typing import Any, Dict, List, Optional

from mcp import server
from mcp.types import Tool
from mcp.server.stdio import stdio_server
from pydantic import ValidationError

from .config import get_settings
from .logging_config import setup_logging, get_logger
from .auth import get_auth_manager, AuthenticationError
from .priority_client import (
    TaskPriorityClient,
    APIError,
    APINotFoundError,
    APIValidationError,
)
from .models import (
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    TaskStatus,
    TaskCategory,
    TaskWithAnalysis,
    AIAnalysis,
)

# Logger will be initialized after imports
logger = None

def init_logging():
    """Initialize logging when needed."""
    global logger
    if logger is None:
        setup_logging()
        logger = get_logger(__name__)


class TaskPriorityMCPServer(server.Server):
    """MCP server for TaskPriority integration."""
    
    def __init__(self):
        """Initialize the MCP server."""
        init_logging()  # Initialize logging first
        
        self.settings = get_settings()
        
        # Initialize parent Server class
        super().__init__(self.settings.mcp_server_name)
        
        self.auth_manager = get_auth_manager()
        self.client: Optional[TaskPriorityClient] = None
        self._shutdown_event = asyncio.Event()
        self._tools = {}  # Store tools by name
        self._tool_handlers = {}  # Store tool handlers separately
        
        # Server metadata
        self.version = self.settings.mcp_server_version
        
        logger.info(
            f"Initializing {self.name} v{self.version}",
            extra={
                "api_url": self.settings.api_base_url,
                "debug_mode": self.settings.debug_mode
            }
        )
    
    async def start(self):
        """Start the MCP server."""
        try:
            # Initialize API client
            self.client = TaskPriorityClient()
            await self.client.start()
            
            # Validate authentication
            if not self.auth_manager.is_authenticated():
                raise AuthenticationError("Failed to authenticate with TaskPriority API")
            
            # Test API connection with graceful fallback
            try:
                health_ok = await self.client.health_check()
                if health_ok:
                    logger.info("TaskPriority API health check passed")
                else:
                    logger.warning("Health check failed, proceeding in degraded mode")
            except Exception as e:
                logger.warning(f"Health check unavailable: {e}, continuing anyway")
            
            logger.info("TaskPriority API client initialized and authenticated")
            
            # Initialize all tools
            self._initialize_tools()
            
            # Register handlers using decorators
            self._register_handlers()
            
            logger.info(f"MCP server '{self.name}' started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def stop(self):
        """Stop the MCP server and cleanup resources."""
        logger.info("Shutting down MCP server...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cleanup API client
        if self.client:
            await self.client.close()
            
        logger.info("MCP server shutdown complete")
    
    def _initialize_tools(self):
        """Initialize all TaskPriority tools."""
        # Create tool definitions and store handlers separately
        tools_config = [
            (self._create_tool_create_task(), self._handle_create_task),
            (self._create_tool_list_tasks(), self._handle_list_tasks),
            (self._create_tool_get_task_details(), self._handle_get_task_details),
            (self._create_tool_update_task(), self._handle_update_task),
            (self._create_tool_delete_task(), self._handle_delete_task),
            (self._create_tool_get_ai_analysis(), self._handle_get_ai_analysis),
        ]
        
        for tool, handler in tools_config:
            self._tools[tool.name] = tool
            self._tool_handlers[tool.name] = handler
            logger.debug(f"Initialized tool: {tool.name}")
        
        logger.info(f"Initialized {len(tools_config)} tools")
    
    def _register_handlers(self):
        """Register method handlers using decorators."""
        
        @self.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return all available tools."""
            return list(self._tools.values())
        
        @self.call_tool()
        async def handle_call_tool(name: str, arguments: Any) -> Any:
            """Call a tool by name with arguments."""
            if name not in self._tool_handlers:
                raise ValueError(f"Unknown tool: {name}")
            
            # Get the handler function
            handler = self._tool_handlers[name]
            
            # Call the handler with the arguments
            result = await handler(arguments)
            
            return result
    
    # Tool definitions
    
    def _create_tool_create_task(self) -> Tool:
        """Create the create_task tool."""
        return Tool(
            name="create_task",
            description=(
                "Create a new task in TaskPriority. The task will be automatically "
                "analyzed by AI to determine priority, complexity, and time estimates."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Task description (required)",
                        "minLength": 1,
                        "maxLength": 1000
                    },
                    "source": {
                        "type": "string",
                        "description": "Origin of the task (default: 'internal')",
                        "default": "internal",
                        "maxLength": 100
                    },
                    "customer_info": {
                        "type": "string",
                        "description": "Additional context about the task",
                        "maxLength": 5000
                    }
                },
                "required": ["description"]
            }
        )
    
    def _create_tool_list_tasks(self) -> Tool:
        """Create the list_tasks tool."""
        return Tool(
            name="list_tasks",
            description=(
                "List tasks with optional filtering by status or category. "
                "Returns paginated results sorted by creation date (newest first)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by task status",
                        "enum": ["pending", "in_progress", "completed", "blocked"]
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by AI-assigned category",
                        "enum": ["bug", "feature", "improvement", "business", "other"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1-100, default: 50)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Pagination offset (default: 0)",
                        "minimum": 0,
                        "default": 0
                    }
                },
                "required": []
            }
        )
    
    def _create_tool_get_task_details(self) -> Tool:
        """Create the get_task_details tool."""
        return Tool(
            name="get_task_details",
            description=(
                "Get complete details for a specific task, including AI analysis "
                "with priority, complexity, and time estimates."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID (UUID format)",
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                    }
                },
                "required": ["task_id"]
            }
        )
    
    def _create_tool_update_task(self) -> Tool:
        """Create the update_task tool."""
        return Tool(
            name="update_task",
            description=(
                "Update an existing task. You can change the status, description, "
                "or customer information. AI analysis is preserved."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to update (UUID format)",
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                    },
                    "status": {
                        "type": "string",
                        "description": "New task status",
                        "enum": ["pending", "in_progress", "completed", "blocked"]
                    },
                    "description": {
                        "type": "string",
                        "description": "Updated task description",
                        "minLength": 1,
                        "maxLength": 1000
                    },
                    "customer_info": {
                        "type": "string",
                        "description": "Updated customer context",
                        "maxLength": 5000
                    }
                },
                "required": ["task_id"]
            }
        )
    
    def _create_tool_delete_task(self) -> Tool:
        """Create the delete_task tool."""
        return Tool(
            name="delete_task",
            description="Permanently delete a task from TaskPriority.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to delete (UUID format)",
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                    }
                },
                "required": ["task_id"]
            }
        )
    
    def _create_tool_get_ai_analysis(self) -> Tool:
        """Create the get_ai_analysis tool."""
        return Tool(
            name="get_ai_analysis",
            description=(
                "Get or wait for AI analysis of a task. Returns priority (1-10), "
                "complexity (easy/medium/hard), time estimates, and similar tasks. "
                "Will poll for up to 30 seconds if analysis is still processing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to get analysis for (UUID format)",
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max seconds to wait for analysis (default: 30)",
                        "minimum": 1,
                        "maximum": 60,
                        "default": 30
                    }
                },
                "required": ["task_id"]
            }
        )
    
    # Tool handlers
    
    async def _handle_create_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_task tool invocation."""
        try:
            # Create request from arguments
            request = CreateTaskRequest(**arguments)
            
            # Call API
            task = await self.client.create_task(request)
            
            # Format response
            return self._format_task_response(task, "Task created successfully")
            
        except ValidationError as e:
            logger.error(f"Validation error in create_task: {e}")
            return self._format_error("Invalid parameters", str(e))
        except APIValidationError as e:
            return self._format_error("Validation failed", str(e))
        except APIError as e:
            logger.error(f"API error in create_task: {e}")
            return self._format_error("Failed to create task", str(e))
        except Exception as e:
            logger.error(f"Unexpected error in create_task: {e}", exc_info=True)
            return self._format_error("Internal error", "An unexpected error occurred")
    
    async def _handle_list_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tasks tool invocation."""
        try:
            # Convert string status/category to enums if provided
            if "status" in arguments:
                arguments["status"] = TaskStatus(arguments["status"])
            if "category" in arguments:
                arguments["category"] = TaskCategory(arguments["category"])
            
            # Create request from arguments
            request = ListTasksRequest(**arguments)
            
            # Call API
            result = await self.client.list_tasks(request)
            
            # Format response
            tasks = result.get("tasks", [])
            total = result.get("total", len(tasks))
            
            return {
                "success": True,
                "tasks": [self._format_task_summary(task) for task in tasks],
                "total": total,
                "showing": len(tasks),
                "has_more": request.offset + len(tasks) < total
            }
            
        except ValidationError as e:
            logger.error(f"Validation error in list_tasks: {e}")
            return self._format_error("Invalid parameters", str(e))
        except APIError as e:
            logger.error(f"API error in list_tasks: {e}")
            return self._format_error("Failed to list tasks", str(e))
        except Exception as e:
            logger.error(f"Unexpected error in list_tasks: {e}", exc_info=True)
            return self._format_error("Internal error", "An unexpected error occurred")
    
    async def _handle_get_task_details(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task_details tool invocation."""
        try:
            task_id = arguments["task_id"]
            
            # Call API
            task = await self.client.get_task(task_id)
            
            # Format response with full details
            return self._format_task_response(task, "Task retrieved successfully", full_details=True)
            
        except APINotFoundError:
            return self._format_error("Task not found", f"No task found with ID: {arguments.get('task_id')}")
        except APIError as e:
            logger.error(f"API error in get_task_details: {e}")
            return self._format_error("Failed to get task", str(e))
        except Exception as e:
            logger.error(f"Unexpected error in get_task_details: {e}", exc_info=True)
            return self._format_error("Internal error", "An unexpected error occurred")
    
    async def _handle_update_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_task tool invocation."""
        try:
            task_id = arguments.pop("task_id")
            
            # Convert status string to enum if provided
            if "status" in arguments:
                arguments["status"] = TaskStatus(arguments["status"])
            
            # Create update request
            request = UpdateTaskRequest(**arguments)
            
            # Check if there are any updates
            if not request.has_updates():
                return self._format_error("No updates provided", "At least one field must be specified to update")
            
            # Call API
            task = await self.client.update_task(task_id, request)
            
            # Format response
            return self._format_task_response(task, "Task updated successfully")
            
        except ValidationError as e:
            logger.error(f"Validation error in update_task: {e}")
            return self._format_error("Invalid parameters", str(e))
        except APINotFoundError:
            return self._format_error("Task not found", f"No task found with ID: {task_id}")
        except APIValidationError as e:
            return self._format_error("Validation failed", str(e))
        except APIError as e:
            logger.error(f"API error in update_task: {e}")
            return self._format_error("Failed to update task", str(e))
        except Exception as e:
            logger.error(f"Unexpected error in update_task: {e}", exc_info=True)
            return self._format_error("Internal error", "An unexpected error occurred")
    
    async def _handle_delete_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_task tool invocation."""
        try:
            task_id = arguments["task_id"]
            
            # Call API
            await self.client.delete_task(task_id)
            
            # Format response
            return {
                "success": True,
                "message": "Task deleted successfully",
                "task_id": task_id
            }
            
        except APINotFoundError:
            return self._format_error("Task not found", f"No task found with ID: {arguments.get('task_id')}")
        except APIError as e:
            logger.error(f"API error in delete_task: {e}")
            return self._format_error("Failed to delete task", str(e))
        except Exception as e:
            logger.error(f"Unexpected error in delete_task: {e}", exc_info=True)
            return self._format_error("Internal error", "An unexpected error occurred")
    
    async def _handle_get_ai_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_ai_analysis tool invocation."""
        try:
            task_id = arguments["task_id"]
            timeout = arguments.get("timeout", 30)
            
            # Call API with polling
            analysis = await self.client.get_ai_analysis(task_id, timeout)
            
            if analysis:
                return {
                    "success": True,
                    "message": "AI analysis retrieved successfully",
                    "task_id": task_id,
                    "analysis": self._format_ai_analysis(analysis)
                }
            else:
                return {
                    "success": False,
                    "message": "AI analysis not ready within timeout period",
                    "task_id": task_id,
                    "timeout": timeout
                }
                
        except APINotFoundError:
            return self._format_error("Task not found", f"No task found with ID: {arguments.get('task_id')}")
        except APIError as e:
            logger.error(f"API error in get_ai_analysis: {e}")
            return self._format_error("Failed to get AI analysis", str(e))
        except Exception as e:
            logger.error(f"Unexpected error in get_ai_analysis: {e}", exc_info=True)
            return self._format_error("Internal error", "An unexpected error occurred")
    
    # Response formatting helpers
    
    def _format_task_response(
        self, 
        task: TaskWithAnalysis, 
        message: str,
        full_details: bool = False
    ) -> Dict[str, Any]:
        """Format a task response for MCP."""
        response = {
            "success": True,
            "message": message,
            "task": {
                "id": str(task.id),
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
        }
        
        # Add optional fields if present
        if task.source:
            response["task"]["source"] = task.source
        if task.customer_info:
            response["task"]["customer_info"] = task.customer_info
        if task.group_id:
            response["task"]["group_id"] = str(task.group_id)
            
        # Add AI analysis if available
        if task.task_analyses:
            response["task"]["ai_analysis"] = self._format_ai_analysis(task.task_analyses)
            
        return response
    
    def _format_task_summary(self, task: TaskWithAnalysis) -> Dict[str, Any]:
        """Format a task summary for list responses."""
        summary = {
            "id": str(task.id),
            "description": task.description,
            "status": task.status.value,
            "created_at": task.created_at.isoformat()
        }
        
        # Add AI priority if available
        if task.task_analyses and task.task_analyses.priority:
            summary["priority"] = task.task_analyses.priority
            summary["category"] = task.task_analyses.category.value if task.task_analyses.category else None
            
        return summary
    
    def _format_ai_analysis(self, analysis: AIAnalysis) -> Dict[str, Any]:
        """Format AI analysis for responses."""
        result = {
            "analyzed_at": analysis.analyzed_at.isoformat()
        }
        
        # Add all available fields
        if analysis.priority is not None:
            result["priority"] = analysis.priority
        if analysis.category:
            result["category"] = analysis.category.value
        if analysis.complexity:
            result["complexity"] = analysis.complexity.value
        if analysis.estimated_hours is not None:
            result["estimated_hours"] = analysis.estimated_hours
        if analysis.confidence_score is not None:
            result["confidence_score"] = analysis.confidence_score
        if analysis.implementation_spec:
            result["implementation_spec"] = analysis.implementation_spec
        if analysis.duplicate_of:
            result["duplicate_of"] = str(analysis.duplicate_of)
        if analysis.similar_tasks:
            result["similar_tasks"] = [str(task_id) for task_id in analysis.similar_tasks]
            
        return result
    
    def _format_error(self, error_type: str, message: str) -> Dict[str, Any]:
        """Format an error response for MCP with helpful context."""
        error_response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message
            }
        }
        
        # Add helpful context for common errors
        help_messages = {
            "Invalid parameters": "Check that all required fields are provided and properly formatted",
            "Validation failed": "Ensure your input meets the requirements (e.g., description length, valid status)",
            "Task not found": "Verify the task ID is correct and the task exists",
            "Authentication failed": "Check your API key is valid and properly configured",
            "Internal error": "An unexpected error occurred. Please try again or check the logs"
        }
        
        if error_type in help_messages:
            error_response["error"]["help"] = help_messages[error_type]
            
        return error_response
    
    async def run_server(self):
        """Run the MCP server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            try:
                # Initialize server
                await self.start()
                
                # Run MCP server with stdio transport
                await self.run(
                    read_stream,
                    write_stream,
                    self.create_initialization_options()
                )
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
            except Exception as e:
                logger.error(f"Server error: {e}", exc_info=True)
            finally:
                await self.stop()


# Signal handlers for graceful shutdown
def setup_signal_handlers(server_instance: TaskPriorityMCPServer):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        if logger:
            logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(server_instance.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point for the MCP server."""
    # Create server instance
    server = TaskPriorityMCPServer()
    
    # Set up signal handlers
    setup_signal_handlers(server)
    
    # Run the server
    try:
        asyncio.run(server.run_server())
    except KeyboardInterrupt:
        if logger:
            logger.info("Server stopped by user")
    except Exception as e:
        if logger:
            logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()