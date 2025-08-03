"""TaskPriority MCP Server package."""

from .models import (
    # Enums
    TaskStatus,
    TaskCategory,
    ComplexityLevel,
    # Core Models
    Task,
    AIAnalysis,
    TaskWithAnalysis,
    # Request Models
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    # Response Models
    TaskResponse,
    TaskListResponse,
    DeleteTaskResponse,
    ErrorResponse,
    ErrorDetail,
    # MCP Response Models
    MCPToolResponse,
    CreateTaskResponse,
    UpdateTaskResponse,
    GetTaskDetailsResponse,
    GetAIAnalysisResponse,
)

from .auth import (
    AuthManager,
    AuthenticationError,
    get_auth_manager,
    reset_auth_manager,
)

from .priority_client import (
    TaskPriorityClient,
    create_client,
    APIError,
    APIConnectionError,
    APIValidationError,
    APINotFoundError,
    APIRateLimitError,
)

__version__ = "1.0.0"
__author__ = "TaskPriority AI"
__email__ = "support@taskpriority.ai"

__all__ = [
    # Package info
    "__version__",
    "__author__",
    "__email__",
    # Enums
    "TaskStatus",
    "TaskCategory",
    "ComplexityLevel",
    # Core Models
    "Task",
    "AIAnalysis",
    "TaskWithAnalysis",
    # Request Models
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "ListTasksRequest",
    # Response Models
    "TaskResponse",
    "TaskListResponse",
    "DeleteTaskResponse",
    "ErrorResponse",
    "ErrorDetail",
    # MCP Response Models
    "MCPToolResponse",
    "CreateTaskResponse",
    "UpdateTaskResponse",
    "GetTaskDetailsResponse",
    "GetAIAnalysisResponse",
    # Auth
    "AuthManager",
    "AuthenticationError",
    "get_auth_manager",
    "reset_auth_manager",
    # API Client
    "TaskPriorityClient",
    "create_client",
    "APIError",
    "APIConnectionError",
    "APIValidationError",
    "APINotFoundError",
    "APIRateLimitError",
]