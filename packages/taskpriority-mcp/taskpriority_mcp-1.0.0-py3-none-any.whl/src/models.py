"""Data models for TaskPriority MCP Server."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


# Enums

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    
    @classmethod
    def _missing_(cls, value: str) -> Optional["TaskStatus"]:
        """Handle case-insensitive status values."""
        for status in cls:
            if status.value.lower() == value.lower():
                return status
        return None


class TaskCategory(str, Enum):
    """Task category enumeration."""
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    BUSINESS = "business"
    OTHER = "other"
    
    @classmethod
    def _missing_(cls, value: str) -> Optional["TaskCategory"]:
        """Handle case-insensitive category values."""
        for category in cls:
            if category.value.lower() == value.lower():
                return category
        return None


class ComplexityLevel(str, Enum):
    """Task complexity level enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    
    @classmethod
    def _missing_(cls, value: str) -> Optional["ComplexityLevel"]:
        """Handle case-insensitive complexity values."""
        for level in cls:
            if level.value.lower() == value.lower():
                return level
        return None


# Core Models

class AIAnalysis(BaseModel):
    """AI analysis data for a task."""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        validate_assignment=True,
        extra="forbid"
    )
    
    id: UUID = Field(..., description="Unique identifier for the analysis")
    task_id: UUID = Field(..., description="Associated task ID")
    category: Optional[TaskCategory] = Field(
        None, 
        description="AI-assigned task category"
    )
    priority: Optional[int] = Field(
        None,
        description="AI-assigned priority (1-10 scale)",
        ge=1,
        le=10,
        examples=[1, 5, 10]
    )
    complexity: Optional[ComplexityLevel] = Field(
        None,
        description="AI-assessed complexity level"
    )
    estimated_hours: Optional[float] = Field(
        None,
        description="AI-estimated hours to complete",
        ge=0.0,
        le=1000.0,
        examples=[0.5, 2.0, 8.0]
    )
    confidence_score: Optional[int] = Field(
        None,
        description="AI confidence in analysis (0-100)",
        ge=0,
        le=100,
        examples=[75, 90, 100]
    )
    implementation_spec: Optional[str] = Field(
        None,
        description="AI-generated implementation specification",
        max_length=10000
    )
    duplicate_of: Optional[UUID] = Field(
        None,
        description="Task ID if this is a duplicate"
    )
    similar_tasks: Optional[List[UUID]] = Field(
        None,
        description="List of similar task IDs"
    )
    analyzed_at: datetime = Field(
        ...,
        description="Timestamp when analysis was completed"
    )
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        """Ensure priority is within valid range."""
        if v is not None and not 1 <= v <= 10:
            raise ValueError("Priority must be between 1 and 10")
        return v
    
    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: Optional[int]) -> Optional[int]:
        """Ensure confidence score is within valid range."""
        if v is not None and not 0 <= v <= 100:
            raise ValueError("Confidence score must be between 0 and 100")
        return v


class Task(BaseModel):
    """Task data model."""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        validate_assignment=True,
        extra="forbid"
    )
    
    id: UUID = Field(..., description="Unique task identifier")
    user_id: UUID = Field(..., description="Owner user ID")
    description: str = Field(
        ...,
        description="Task description",
        min_length=1,
        max_length=1000,
        examples=["Fix login bug", "Add user authentication", "Improve performance"]
    )
    source: Optional[str] = Field(
        None,
        description="Origin system of the task",
        max_length=100,
        examples=["github", "email", "internal", "customer"]
    )
    customer_info: Optional[str] = Field(
        None,
        description="Additional customer context",
        max_length=5000
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status"
    )
    group_id: Optional[UUID] = Field(
        None,
        description="Task group reference for related tasks"
    )
    created_at: datetime = Field(
        ...,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is not empty or just whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v


class TaskWithAnalysis(Task):
    """Task with nested AI analysis data."""
    
    task_analyses: Optional[AIAnalysis] = Field(
        None,
        description="Nested AI analysis data",
        alias="task_analyses"
    )


# Request Models

class CreateTaskRequest(BaseModel):
    """Request model for creating a task."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    description: str = Field(
        ...,
        description="Task description",
        min_length=1,
        max_length=1000,
        examples=["Fix login bug on mobile devices"]
    )
    source: Optional[str] = Field(
        default="internal",
        description="Origin of the task",
        max_length=100,
        examples=["github", "email", "internal", "customer"]
    )
    customer_info: Optional[str] = Field(
        None,
        description="Additional context about the task",
        max_length=5000,
        examples=["Reported by user@example.com via support ticket #1234"]
    )
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is not empty or just whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    status: Optional[TaskStatus] = Field(
        None,
        description="New task status"
    )
    description: Optional[str] = Field(
        None,
        description="Updated task description",
        min_length=1,
        max_length=1000
    )
    customer_info: Optional[str] = Field(
        None,
        description="Updated customer context",
        max_length=5000
    )
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Ensure description is not empty or just whitespace if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Description cannot be empty")
        return v
    
    def has_updates(self) -> bool:
        """Check if any fields are set for update."""
        return any(
            getattr(self, field) is not None 
            for field in self.model_fields
        )


class ListTasksRequest(BaseModel):
    """Request model for listing tasks."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    status: Optional[TaskStatus] = Field(
        None,
        description="Filter by task status"
    )
    category: Optional[TaskCategory] = Field(
        None,
        description="Filter by AI-assigned category"
    )
    limit: int = Field(
        default=50,
        description="Number of results to return",
        ge=1,
        le=100
    )
    offset: int = Field(
        default=0,
        description="Pagination offset",
        ge=0
    )


# Response Models

class TaskResponse(BaseModel):
    """Response model for a single task."""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        extra="forbid"
    )
    
    task: TaskWithAnalysis = Field(..., description="Task data with analysis")
    

class TaskListResponse(BaseModel):
    """Response model for multiple tasks."""
    
    model_config = ConfigDict(extra="forbid")
    
    tasks: List[TaskWithAnalysis] = Field(
        ...,
        description="List of tasks with analyses"
    )
    total: int = Field(
        ...,
        description="Total number of tasks matching criteria",
        ge=0
    )
    limit: int = Field(..., description="Results per page", ge=1)
    offset: int = Field(..., description="Pagination offset", ge=0)
    
    @property
    def has_more(self) -> bool:
        """Check if there are more results available."""
        return self.offset + len(self.tasks) < self.total


class DeleteTaskResponse(BaseModel):
    """Response model for task deletion."""
    
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(..., description="Whether deletion was successful")
    task_id: UUID = Field(..., description="ID of the deleted task")
    message: str = Field(
        default="Task deleted successfully",
        description="Confirmation message"
    )


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    model_config = ConfigDict(extra="allow")
    
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    model_config = ConfigDict(extra="forbid")
    
    error: Dict[str, Any] = Field(..., description="Error information")
    
    @classmethod
    def create(
        cls, 
        error_type: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> "ErrorResponse":
        """Create an error response with the standard format."""
        error_data = {
            "type": error_type,
            "message": message
        }
        if details:
            error_data["details"] = details
        return cls(error=error_data)


# MCP Tool Response Models

class MCPToolResponse(BaseModel):
    """Base model for MCP tool responses."""
    
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(..., description="Whether the operation succeeded")
    

class CreateTaskResponse(MCPToolResponse):
    """Response from create_task MCP tool."""
    
    task: TaskWithAnalysis = Field(..., description="Created task with ID")
    message: str = Field(
        default="Task created successfully",
        description="Success message"
    )


class UpdateTaskResponse(MCPToolResponse):
    """Response from update_task MCP tool."""
    
    task: TaskWithAnalysis = Field(..., description="Updated task")
    message: str = Field(
        default="Task updated successfully",
        description="Success message"
    )


class GetTaskDetailsResponse(MCPToolResponse):
    """Response from get_task_details MCP tool."""
    
    task: TaskWithAnalysis = Field(..., description="Complete task details")


class GetAIAnalysisResponse(MCPToolResponse):
    """Response from get_ai_analysis MCP tool."""
    
    analysis: AIAnalysis = Field(..., description="AI analysis data")
    task_id: UUID = Field(..., description="Associated task ID")


# Export all models
__all__ = [
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
]