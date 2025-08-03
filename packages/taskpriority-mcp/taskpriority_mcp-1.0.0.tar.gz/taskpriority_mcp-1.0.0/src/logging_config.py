"""Logging configuration for TaskPriority MCP Server."""

import logging
import sys
import json
from typing import Any, Dict
from datetime import datetime
from pathlib import Path

from .config import get_settings, LogLevel, LogFormat


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "pathname", "process", "processName", "relativeCreated",
                          "thread", "threadName", "exc_info", "exc_text", "getMessage"]:
                log_data[key] = value
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color based on log level
        if record.levelname in self.COLORS:
            log_message = f"{self.COLORS[record.levelname]}{log_message}{self.RESET}"
        
        return log_message


def setup_logging() -> None:
    """
    Set up logging configuration based on settings.
    
    This function configures:
    - Log level from settings
    - Log format (JSON or text)
    - Console handler with appropriate formatter
    - Optional file handler for persistent logs
    """
    settings = get_settings()
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, settings.log_level.value)
    root_logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on format setting
    if settings.log_format == LogFormat.JSON:
        formatter = JSONFormatter()
    else:
        # Text format with colors for development
        if settings.is_development:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            formatter = ColoredFormatter(format_string)
        else:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            formatter = logging.Formatter(format_string)
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler in production
    if not settings.is_development:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"taskpriority-mcp-{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())  # Always use JSON for file logs
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    # Reduce noise from HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Enable debug logging for our modules in debug mode
    if settings.debug_mode:
        logging.getLogger("taskpriority_mcp").setLevel(logging.DEBUG)
    
    # Log initial configuration
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.log_level.value,
            "log_format": settings.log_format.value,
            "is_development": settings.is_development,
            "debug_mode": settings.debug_mode,
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding extra fields to log records."""
    
    def __init__(self, logger: logging.Logger, **kwargs: Any):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            **kwargs: Extra fields to add to log records
        """
        self.logger = logger
        self.extra = kwargs
        self._old_factory = None
    
    def __enter__(self) -> "LogContext":
        """Enter context and set up log record factory."""
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = old_factory(*args, **kwargs)
            for key, value in self.extra.items():
                setattr(record, key, value)
            return record
        
        self._old_factory = old_factory
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and restore log record factory."""
        if self._old_factory:
            logging.setLogRecordFactory(self._old_factory)


# Convenience function for structured logging
def log_with_context(logger: logging.Logger, level: str, message: str, **context: Any) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        **context: Additional context to include in the log
    """
    log_func = getattr(logger, level.lower())
    log_func(message, extra=context)


# Export main functions
__all__ = ["setup_logging", "get_logger", "LogContext", "log_with_context"]