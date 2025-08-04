"""Authentication management for TaskPriority MCP Server."""

from typing import Dict, Optional
from datetime import datetime, timedelta

from .config import get_settings
from .logging_config import get_logger

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthManager:
    """Manages authentication for TaskPriority API requests."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the authentication manager.
        
        Args:
            api_key: Optional API key. If not provided, will use settings.
        """
        self._api_key = api_key
        self._validated = False
        self._validation_time: Optional[datetime] = None
        self._validation_ttl = timedelta(hours=1)  # Re-validate after 1 hour
        
    @property
    def api_key(self) -> str:
        """
        Get the API key.
        
        Returns:
            The API key from initialization or settings
            
        Raises:
            AuthenticationError: If no API key is available
        """
        if self._api_key:
            return self._api_key
            
        # Get from settings
        settings = get_settings()
        try:
            return settings.taskpriority_api_key.get_secret_value()
        except Exception as e:
            logger.error("Failed to retrieve API key from settings", extra={"error": str(e)})
            raise AuthenticationError("No API key available. Please configure TASKPRIORITY_API_KEY")
    
    def validate_api_key(self) -> bool:
        """
        Validate the API key format.
        
        Returns:
            True if the API key format is valid
            
        Raises:
            AuthenticationError: If the API key format is invalid
        """
        try:
            key = self.api_key
        except AuthenticationError:
            return False
            
        # Check format
        if not key.startswith("tp_live_"):
            raise AuthenticationError(
                "Invalid API key format. TaskPriority API keys must start with 'tp_live_'"
            )
            
        # Check minimum length
        if len(key) < 16:
            raise AuthenticationError(
                "Invalid API key format. API key appears to be too short"
            )
            
        # Mark as validated
        self._validated = True
        self._validation_time = datetime.utcnow()
        
        logger.info("API key validated successfully")
        return True
    
    def get_auth_header(self) -> Dict[str, str]:
        """
        Get the authorization header for API requests.
        
        Returns:
            Dictionary with Authorization header
            
        Raises:
            AuthenticationError: If the API key is invalid
        """
        # Check if we need to re-validate
        if self._validated and self._validation_time:
            if datetime.utcnow() - self._validation_time > self._validation_ttl:
                self._validated = False
                logger.debug("API key validation expired, re-validating")
        
        # Validate if not already done
        if not self._validated:
            self.validate_api_key()
            
        return {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get all required headers for API requests.
        
        Returns:
            Dictionary with all required headers including auth
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TaskPriority-MCP/1.0.0"
        }
        
        # Add auth header
        headers.update(self.get_auth_header())
        
        return headers
    
    def is_authenticated(self) -> bool:
        """
        Check if we have valid authentication.
        
        Returns:
            True if authenticated and validated
        """
        try:
            # This will trigger validation if needed
            self.get_auth_header()
            return True
        except AuthenticationError:
            return False
    
    def clear_validation(self) -> None:
        """Clear the validation state, forcing re-validation on next request."""
        self._validated = False
        self._validation_time = None
        logger.debug("Cleared API key validation state")


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager(api_key: Optional[str] = None) -> AuthManager:
    """
    Get the global auth manager instance.
    
    Args:
        api_key: Optional API key to use. Only used on first call.
        
    Returns:
        The global AuthManager instance
    """
    global _auth_manager
    
    if _auth_manager is None:
        _auth_manager = AuthManager(api_key)
    elif api_key and not _auth_manager._api_key:
        # Update API key if provided and not already set
        _auth_manager._api_key = api_key
        _auth_manager.clear_validation()
        
    return _auth_manager


def reset_auth_manager() -> None:
    """Reset the global auth manager (useful for testing)."""
    global _auth_manager
    _auth_manager = None
    logger.debug("Reset global auth manager")


# Export main components
__all__ = [
    "AuthManager",
    "AuthenticationError",
    "get_auth_manager",
    "reset_auth_manager"
]