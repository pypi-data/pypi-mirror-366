"""TaskPriority API client implementation."""

import asyncio
import json
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime

import httpx
from pydantic import BaseModel

from .config import get_settings
from .auth import get_auth_manager, AuthenticationError
from .logging_config import get_logger, log_with_context
from .models import (
    Task,
    TaskWithAnalysis,
    AIAnalysis,
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    ErrorResponse,
    TaskStatus,
    TaskCategory
)

logger = get_logger(__name__)

# Type variable for generic response handling
T = TypeVar('T', bound=BaseModel)


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class APIConnectionError(APIError):
    """Raised when connection to API fails."""
    pass


class APIValidationError(APIError):
    """Raised when API returns validation errors."""
    pass


class APINotFoundError(APIError):
    """Raised when requested resource is not found."""
    pass


class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class TaskPriorityClient:
    """Async client for TaskPriority API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the TaskPriority API client.
        
        Args:
            api_key: Optional API key. If not provided, will use settings.
            base_url: Optional base URL. If not provided, will use settings.
        """
        self.settings = get_settings()
        self.auth_manager = get_auth_manager(api_key)
        
        # Use provided base_url or fall back to settings
        self._base_url = base_url or self.settings.api_base_url
        
        # HTTP client configuration
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = httpx.Timeout(
            timeout=self.settings.request_timeout,
            connect=5.0,
            read=self.settings.request_timeout,
            write=self.settings.request_timeout
        )
        
        # Retry configuration
        self._max_retries = self.settings.max_retries
        self._retry_backoff = self.settings.retry_backoff_factor
        
    async def __aenter__(self) -> "TaskPriorityClient":
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
        
    async def start(self) -> None:
        """Start the HTTP client with connection pooling."""
        if self._client is None:
            limits = httpx.Limits(
                max_keepalive_connections=self.settings.connection_pool_size,
                max_connections=self.settings.connection_pool_size * 2,
                keepalive_expiry=self.settings.connection_pool_timeout
            )
            
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                limits=limits,
                follow_redirects=True
            )
            
            logger.info(
                "TaskPriority client started",
                extra={
                    "base_url": self._base_url,
                    "timeout": self.settings.request_timeout,
                    "pool_size": self.settings.connection_pool_size
                }
            )
    
    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("TaskPriority client closed")
    
    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            await self.start()
        return self._client
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Union[Dict[str, Any], T]:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            json_data: Optional JSON data for request body
            params: Optional query parameters
            response_model: Optional Pydantic model to parse response
            
        Returns:
            Parsed response data or dictionary
            
        Raises:
            Various APIError subclasses based on response
        """
        client = await self._ensure_client()
        headers = self.auth_manager.get_headers()
        
        # Clean up params - remove None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        # Retry logic
        last_error: Optional[Exception] = None
        
        for attempt in range(self._max_retries + 1):
            try:
                # Log request
                log_with_context(
                    logger, "debug", "Making API request",
                    method=method,
                    endpoint=endpoint,
                    attempt=attempt + 1,
                    has_data=bool(json_data),
                    has_params=bool(params)
                )
                
                # Make request
                response = await client.request(
                    method=method,
                    url=endpoint,
                    headers=headers,
                    json=json_data,
                    params=params
                )
                
                # Log response
                log_with_context(
                    logger, "debug", "Received API response",
                    status_code=response.status_code,
                    endpoint=endpoint,
                    response_time_ms=response.elapsed.total_seconds() * 1000
                )
                
                # Handle response
                if response.status_code >= 200 and response.status_code < 300:
                    # Success
                    data = response.json() if response.content else {}
                    
                    # Parse with model if provided
                    if response_model:
                        return response_model(**data)
                    return data
                    
                # Handle errors
                await self._handle_error_response(response, endpoint)
                
            except httpx.ConnectError as e:
                last_error = APIConnectionError(
                    f"Failed to connect to TaskPriority API: {str(e)}"
                )
                logger.warning(
                    f"Connection failed (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"error": str(e), "endpoint": endpoint}
                )
                
            except httpx.TimeoutException as e:
                last_error = APIConnectionError(
                    f"Request to TaskPriority API timed out: {str(e)}"
                )
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"error": str(e), "endpoint": endpoint}
                )
                
            except httpx.HTTPError as e:
                last_error = APIError(f"HTTP error occurred: {str(e)}")
                logger.warning(
                    f"HTTP error (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"error": str(e), "endpoint": endpoint}
                )
                
            # Retry with exponential backoff
            if attempt < self._max_retries:
                wait_time = self._retry_backoff ** attempt
                logger.debug(f"Retrying in {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
        
        # All retries exhausted
        if last_error:
            logger.error(
                "All retry attempts exhausted",
                extra={"endpoint": endpoint, "final_error": str(last_error)}
            )
            raise last_error
        else:
            raise APIError("Request failed after all retry attempts")
    
    async def _handle_error_response(self, response: httpx.Response, endpoint: str) -> None:
        """
        Handle error responses from the API.
        
        Args:
            response: The HTTP response
            endpoint: The endpoint that was called
            
        Raises:
            Appropriate APIError subclass based on status code
        """
        try:
            error_data = response.json()
            error_response = ErrorResponse(**error_data)
            error_info = error_response.error
            message = error_info.get("message", "Unknown error")
            details = error_info.get("details", {})
        except Exception:
            # Fallback if response isn't valid JSON or doesn't match ErrorResponse
            message = f"API error: {response.status_code} {response.reason_phrase}"
            details = {"response_text": response.text[:500]}  # Limit text length
        
        # Log the error
        logger.error(
            f"API error response: {message}",
            extra={
                "status_code": response.status_code,
                "endpoint": endpoint,
                "details": details
            }
        )
        
        # Map status codes to specific exceptions
        if response.status_code == 400:
            raise APIValidationError(message, response.status_code, details)
        elif response.status_code == 401:
            # Clear auth validation on 401
            self.auth_manager.clear_validation()
            raise AuthenticationError(message)
        elif response.status_code == 404:
            raise APINotFoundError(message, response.status_code, details)
        elif response.status_code == 429:
            # Extract rate limit info if available
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                details["retry_after"] = retry_after
            raise APIRateLimitError(message, response.status_code, details)
        elif response.status_code >= 500:
            raise APIError(f"Server error: {message}", response.status_code, details)
        else:
            raise APIError(message, response.status_code, details)
    
    # Task Management Methods
    
    async def create_task(self, request: CreateTaskRequest) -> TaskWithAnalysis:
        """
        Create a new task.
        
        Args:
            request: Task creation request
            
        Returns:
            Created task with optional AI analysis
            
        Raises:
            APIError: If task creation fails
        """
        logger.info(f"Creating task: {request.description[:50]}...")
        
        response = await self._request(
            method="POST",
            endpoint="/tasks",
            json_data=request.model_dump(exclude_none=True),
            response_model=TaskWithAnalysis
        )
        
        logger.info(f"Task created successfully with ID: {response.id}")
        return response
    
    async def get_task(self, task_id: Union[str, UUID]) -> TaskWithAnalysis:
        """
        Get a specific task by ID.
        
        Args:
            task_id: Task ID (string or UUID)
            
        Returns:
            Task with optional AI analysis
            
        Raises:
            APINotFoundError: If task not found
            APIError: For other errors
        """
        logger.info(f"Fetching task: {task_id}")
        
        response = await self._request(
            method="GET",
            endpoint=f"/tasks/{task_id}",
            response_model=TaskWithAnalysis
        )
        
        return response
    
    async def update_task(
        self, 
        task_id: Union[str, UUID], 
        request: UpdateTaskRequest
    ) -> TaskWithAnalysis:
        """
        Update an existing task.
        
        Args:
            task_id: Task ID to update
            request: Update request with fields to change
            
        Returns:
            Updated task
            
        Raises:
            APINotFoundError: If task not found
            APIValidationError: If update data is invalid
        """
        if not request.has_updates():
            raise ValueError("No updates provided")
            
        logger.info(f"Updating task: {task_id}")
        
        response = await self._request(
            method="PUT",
            endpoint=f"/tasks/{task_id}",
            json_data=request.model_dump(exclude_none=True),
            response_model=TaskWithAnalysis
        )
        
        logger.info(f"Task {task_id} updated successfully")
        return response
    
    async def delete_task(self, task_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Delete a task.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            Deletion confirmation
            
        Raises:
            APINotFoundError: If task not found
        """
        logger.info(f"Deleting task: {task_id}")
        
        response = await self._request(
            method="DELETE",
            endpoint=f"/tasks/{task_id}"
        )
        
        logger.info(f"Task {task_id} deleted successfully")
        return response
    
    async def list_tasks(
        self, 
        request: Optional[ListTasksRequest] = None
    ) -> Dict[str, Any]:
        """
        List tasks with optional filtering.
        
        Args:
            request: Optional filter and pagination parameters
            
        Returns:
            Dictionary with tasks array and pagination info
        """
        params = {}
        if request:
            if request.status:
                params["status"] = request.status.value
            if request.category:
                params["category"] = request.category.value
            params["limit"] = request.limit
            params["offset"] = request.offset
        
        logger.info("Listing tasks", extra={"params": params})
        
        response = await self._request(
            method="GET",
            endpoint="/tasks",
            params=params
        )
        
        # Parse tasks in response
        if "tasks" in response:
            response["tasks"] = [
                TaskWithAnalysis(**task) for task in response["tasks"]
            ]
        
        return response
    
    async def get_ai_analysis(
        self, 
        task_id: Union[str, UUID], 
        timeout: Optional[int] = None
    ) -> Optional[AIAnalysis]:
        """
        Get or wait for AI analysis of a task.
        
        Args:
            task_id: Task ID to get analysis for
            timeout: Max seconds to wait for analysis (default from settings)
            
        Returns:
            AI analysis if available, None if timeout
            
        Raises:
            APINotFoundError: If task not found
        """
        if timeout is None:
            timeout = self.settings.ai_analysis_max_wait_time
            
        poll_interval = self.settings.ai_analysis_poll_interval
        start_time = datetime.utcnow()
        
        logger.info(
            f"Getting AI analysis for task {task_id}",
            extra={"timeout": timeout, "poll_interval": poll_interval}
        )
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            try:
                # Get task with analysis
                task = await self.get_task(task_id)
                
                if task.task_analyses:
                    logger.info(f"AI analysis ready for task {task_id}")
                    return task.task_analyses
                    
                # Analysis not ready yet, wait before polling again
                logger.debug(f"AI analysis not ready, waiting {poll_interval}s...")
                await asyncio.sleep(poll_interval)
                
            except APINotFoundError:
                # Task not found, re-raise
                raise
            except Exception as e:
                logger.warning(
                    f"Error polling for AI analysis: {e}",
                    extra={"task_id": task_id}
                )
                # Continue polling on transient errors
                await asyncio.sleep(poll_interval)
        
        logger.warning(
            f"AI analysis timeout for task {task_id} after {timeout}s"
        )
        return None
    
    # Health check
    
    async def health_check(self) -> bool:
        """
        Check if the API is reachable and authenticated.
        
        Returns:
            True if API is healthy and auth is valid
        """
        try:
            # Try to list tasks with limit=1 as a health check
            await self.list_tasks(ListTasksRequest(limit=1))
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Convenience function for one-off requests
async def create_client(
    api_key: Optional[str] = None, 
    base_url: Optional[str] = None
) -> TaskPriorityClient:
    """
    Create and start a TaskPriority client.
    
    Args:
        api_key: Optional API key
        base_url: Optional base URL
        
    Returns:
        Started TaskPriorityClient instance
    """
    client = TaskPriorityClient(api_key=api_key, base_url=base_url)
    await client.start()
    return client


# Export main components
__all__ = [
    "TaskPriorityClient",
    "create_client",
    "APIError",
    "APIConnectionError",
    "APIValidationError",
    "APINotFoundError",
    "APIRateLimitError"
]