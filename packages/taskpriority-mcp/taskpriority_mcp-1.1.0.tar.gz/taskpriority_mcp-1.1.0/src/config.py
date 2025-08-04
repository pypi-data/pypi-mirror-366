"""Configuration management for TaskPriority MCP Server."""

import os
from typing import Optional
from enum import Enum
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Supported log formats."""
    JSON = "json"
    TEXT = "text"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # TaskPriority API Configuration
    taskpriority_api_key: SecretStr = Field(
        ...,
        env="TASKPRIORITY_API_KEY",
        description="TaskPriority API key (must start with tp_live_)"
    )
    taskpriority_api_url: str = Field(
        default="http://localhost:3000",
        env="TASKPRIORITY_API_URL",
        description="TaskPriority API base URL"
    )
    taskpriority_api_version: str = Field(
        default="v1",
        env="TASKPRIORITY_API_VERSION",
        description="TaskPriority API version"
    )
    
    # Logging Configuration
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env="LOG_LEVEL",
        description="Logging level"
    )
    log_format: LogFormat = Field(
        default=LogFormat.JSON,
        env="LOG_FORMAT",
        description="Logging format"
    )
    
    # MCP Server Configuration
    mcp_server_name: str = Field(
        default="taskpriority-mcp",
        env="MCP_SERVER_NAME",
        description="MCP server name"
    )
    mcp_server_version: str = Field(
        default="1.0.0",
        env="MCP_SERVER_VERSION",
        description="MCP server version"
    )
    
    # Performance Settings
    request_timeout: int = Field(
        default=30,
        env="REQUEST_TIMEOUT",
        description="HTTP request timeout in seconds",
        gt=0,
        le=300
    )
    max_retries: int = Field(
        default=3,
        env="MAX_RETRIES",
        description="Maximum number of retry attempts",
        ge=0,
        le=10
    )
    retry_backoff_factor: float = Field(
        default=1.5,
        env="RETRY_BACKOFF_FACTOR",
        description="Exponential backoff factor for retries",
        gt=1.0,
        le=5.0
    )
    
    # Optional Features
    enable_telemetry: bool = Field(
        default=False,
        env="ENABLE_TELEMETRY",
        description="Enable telemetry for usage analytics"
    )
    debug_mode: bool = Field(
        default=False,
        env="DEBUG_MODE",
        description="Enable debug mode with verbose logging"
    )
    
    # Connection Pool Settings
    connection_pool_size: int = Field(
        default=10,
        env="CONNECTION_POOL_SIZE",
        description="HTTP connection pool size",
        gt=0,
        le=100
    )
    connection_pool_timeout: int = Field(
        default=5,
        env="CONNECTION_POOL_TIMEOUT",
        description="Connection pool timeout in seconds",
        gt=0,
        le=60
    )
    
    # AI Analysis Settings
    ai_analysis_poll_interval: int = Field(
        default=2,
        env="AI_ANALYSIS_POLL_INTERVAL",
        description="Polling interval for AI analysis in seconds",
        gt=0,
        le=10
    )
    ai_analysis_max_wait_time: int = Field(
        default=30,
        env="AI_ANALYSIS_MAX_WAIT_TIME",
        description="Maximum wait time for AI analysis in seconds",
        gt=0,
        le=300
    )
    
    @field_validator("taskpriority_api_key")
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Validate that the API key has the correct format."""
        key_value = v.get_secret_value()
        if not key_value.startswith("tp_live_"):
            raise ValueError("API key must start with 'tp_live_'")
        if len(key_value) < 16:  # Reasonable minimum length
            raise ValueError("API key appears to be too short")
        return v
    
    @field_validator("taskpriority_api_url")
    def validate_api_url(cls, v: str) -> str:
        """Validate and normalize the API URL."""
        # Remove trailing slash if present
        v = v.rstrip("/")
        # Ensure it starts with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("API URL must start with http:// or https://")
        return v
    
    @property
    def api_base_url(self) -> str:
        """Get the complete API base URL with version."""
        return f"{self.taskpriority_api_url}/api/{self.taskpriority_api_version}"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return "localhost" in self.taskpriority_api_url or "127.0.0.1" in self.taskpriority_api_url
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Creates a new instance on first call and caches it for subsequent calls.
    
    Returns:
        Settings: The application settings
        
    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None


# Convenience exports
__all__ = ["Settings", "get_settings", "reset_settings", "LogLevel", "LogFormat"]