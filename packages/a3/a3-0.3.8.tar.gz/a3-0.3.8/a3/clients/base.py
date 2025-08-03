"""
Base client classes for AI Project Builder.

This module provides abstract base classes for client components
that handle external service integrations.
"""

from abc import ABC
from typing import Optional, Dict, List
import time
import random

from ..core.interfaces import AIClientInterface
from ..core.models import ValidationResult


class BaseClient(ABC):
    """
    Abstract base class for all client components.
    
    Provides common functionality for external service interactions
    including error handling and retry logic.
    """
    
    def __init__(self):
        """Initialize the base client."""
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the client with required dependencies."""
        self._initialized = True
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate that all prerequisites are met for operation."""
        issues = []
        warnings = []
        
        if not self._initialized:
            issues.append("Client has not been initialized")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    def _ensure_initialized(self) -> None:
        """Ensure the client is properly initialized before operations."""
        if not self._initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before use")


class BaseAIClient(BaseClient, AIClientInterface):
    """
    Base class for AI service client implementations.
    
    Provides common functionality for AI API interactions including
    retry logic, rate limiting, and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialize the AI client.
        
        Args:
            api_key: API key for authentication
            default_model: Default model to use for completions
        """
        super().__init__()
        self._api_key = api_key
        self.default_model = default_model or "openai/gpt-3.5-turbo"
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay for exponential backoff
        self._available_models = []  # Cache for available models
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for authentication."""
        self._api_key = api_key
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is valid and active."""
        if not self._api_key:
            return False
        
        # Basic validation - actual implementation will be in concrete classes
        return len(self._api_key.strip()) > 0
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate AI client prerequisites."""
        result = super().validate_prerequisites()
        
        if not self._api_key:
            result.issues.append("API key is required but not provided")
        elif not self.validate_api_key():
            result.issues.append("Invalid API key provided")
        
        return result
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3, model: Optional[str] = None) -> str:
        """
        Generate response with automatic retry logic and model validation.
        
        Args:
            prompt: The prompt to send to the AI service
            max_retries: Maximum number of retry attempts
            model: Model to use for completion (defaults to default_model if None)
            
        Returns:
            Generated response text
            
        Raises:
            RuntimeError: If all retry attempts fail
            ValueError: If model validation fails
        """
        self._ensure_initialized()
        
        # Use provided model or fall back to default
        selected_model = model or self.default_model
        
        # Validate model before attempting generation
        from ..core.validation import validate_before_ai_operation
        validation_result = validate_before_ai_operation(selected_model, self, "text generation")
        
        if not validation_result.is_valid:
            error_msg = f"Model validation failed: {'; '.join(validation_result.errors)}"
            if validation_result.warnings:
                error_msg += f". Warnings: {'; '.join(validation_result.warnings)}"
            raise ValueError(error_msg)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Convert prompt to message format for chat completion
                messages = [{"role": "user", "content": prompt}]
                return self.chat_completion(messages, selected_model)
            
            except Exception as e:
                last_error = e
                
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                else:
                    break
        
        raise RuntimeError(f"Failed to generate response after {max_retries + 1} attempts: {last_error}")
    
    def _handle_rate_limit(self, retry_after: Optional[int] = None) -> None:
        """
        Handle rate limiting by waiting appropriate amount of time.
        
        Args:
            retry_after: Seconds to wait as specified by the API
        """
        if retry_after:
            time.sleep(retry_after)
        else:
            # Default backoff if no retry-after header
            time.sleep(self.base_delay * 2)
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Prepare messages for API call by validating format.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Validated and formatted messages
        """
        formatted_messages = []
        
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("Each message must be a dict with 'role' and 'content' keys")
            
            if msg["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Invalid message role: {msg['role']}")
            
            formatted_messages.append({
                "role": msg["role"],
                "content": str(msg["content"])
            })
        
        return formatted_messages
    
    def set_default_model(self, model: str) -> None:
        """
        Set the default model for completions.
        
        Args:
            model: Model identifier to use as default
            
        Raises:
            ValueError: If model name is invalid
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        
        # Validate model name format
        import re
        if not re.match(r'^[a-zA-Z0-9_:./-]+$', model):
            raise ValueError(f"Invalid model name '{model}': must contain only alphanumeric characters, hyphens, underscores, colons, dots, and slashes")
        
        self.default_model = model.strip()
    
    def validate_model(self, model: str) -> bool:
        """
        Validate that a model name is properly formatted.
        
        Args:
            model: Model name to validate
            
        Returns:
            True if model name is valid, False otherwise
        """
        if not model or not model.strip():
            return False
        
        import re
        return bool(re.match(r'^[a-zA-Z0-9_:./-]+$', model))
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of available model names
            
        Note:
            This is a base implementation that returns cached models.
            Concrete implementations should override this to fetch from API.
        """
        return self._available_models.copy()
    
    def refresh_available_models(self) -> None:
        """
        Refresh the list of available models.
        
        Note:
            This is a base implementation that does nothing.
            Concrete implementations should override this to fetch from API.
        """
        pass