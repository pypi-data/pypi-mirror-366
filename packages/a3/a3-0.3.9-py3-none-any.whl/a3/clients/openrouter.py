"""
OpenRouter client implementation for AI Project Builder.

This module provides the OpenRouterClient class that handles all interactions
with the OpenRouter API, including chat completions, retry logic, and error handling.
"""

import json
import logging
import time
import random
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseAIClient
from ..core.models import ValidationResult


class OpenRouterError(Exception):
    """Base exception for OpenRouter API errors."""
    pass


class OpenRouterAuthenticationError(OpenRouterError):
    """Exception raised for authentication failures."""
    pass


class OpenRouterRateLimitError(OpenRouterError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class OpenRouterAPIError(OpenRouterError):
    """Exception raised for general API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class OpenRouterClient(BaseAIClient):
    """
    Client for interacting with the OpenRouter API.
    
    Provides chat completion functionality with automatic retry logic,
    rate limiting handling, and comprehensive error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key for authentication
            default_model: Default model to use for completions
        """
        # Set default model before calling super().__init__
        default_model = default_model or "qwen/qwen-2.5-72b-instruct:free"
        super().__init__(api_key, default_model)
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.fallback_models = [
            "qwen/qwen-2.5-72b-instruct:free",
            "qwen/qwen3-coder:free",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku"
        ]
        self.timeout = 60  # seconds
        self.max_retries = 3
        self.base_delay = 1.0
        self.logger = logging.getLogger(__name__)
        
        # Track logged unavailable models to prevent spam
        self._logged_unavailable_models = set()
        
        # Configure requests session with retry strategy
        self._session = requests.Session()
        retry_strategy = Retry(
            total=0,  # We handle retries manually for more control
            backoff_factor=0,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        
        # Set up API key if provided
        if api_key:
            self.set_api_key(api_key)
            self.initialize()  # Auto-initialize when API key is provided
        
        # Validate default model format
        if not self.validate_model(self.default_model):
            raise ValueError(f"Invalid default model name: {self.default_model}")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for authentication.
        
        Args:
            api_key: OpenRouter API key
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        self._api_key = api_key.strip()
        
        # Update session headers
        self._session.headers.update({
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ai-project-builder/a3",
            "X-Title": "AI Project Builder"
        })
    
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is valid and active.
        
        Returns:
            True if API key is valid, False otherwise
        """
        if not self._api_key:
            return False
        
        try:
            # Make a simple request to validate the key
            response = self._session.get(
                f"{self.base_url}/models",
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def validate_prerequisites(self) -> ValidationResult:
        """
        Validate that all prerequisites are met for operation.
        
        Returns:
            ValidationResult with validation status and any issues
        """
        result = super().validate_prerequisites()
        
        if not self._api_key:
            result.issues.append("OpenRouter API key is required")
        elif not self.validate_api_key():
            result.issues.append("Invalid or inactive OpenRouter API key")
        
        # Check internet connectivity
        try:
            response = requests.get("https://openrouter.ai", timeout=5)
            if response.status_code != 200:
                result.warnings.append("OpenRouter service may be experiencing issues")
        except Exception:
            result.issues.append("Cannot reach OpenRouter service - check internet connection")
        
        result.is_valid = len(result.issues) == 0
        return result
    
    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """
        Generate a chat completion response with enhanced model validation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model to use for completion (defaults to default_model if None)
            
        Returns:
            Generated response text
            
        Raises:
            OpenRouterError: If the API request fails
            ValueError: If model validation fails
        """
        self._ensure_initialized()
        
        if model is None:
            model = self.default_model
        
        # Enhanced model validation using validation utilities
        from ..core.validation import validate_before_ai_operation
        validation_result = validate_before_ai_operation(model, self, "chat completion")
        
        if not validation_result.is_valid:
            # Provide helpful error message with suggestions
            error_msg = f"Model validation failed for '{model}': {'; '.join(validation_result.errors)}"
            
            # Try to suggest alternatives
            try:
                available_models = self.get_available_models()
                from ..core.validation import ModelValidator
                validator = ModelValidator(self)
                suggestions = validator.suggest_alternative_models(model, available_models)
                if suggestions:
                    error_msg += f"\n\nSuggested alternatives: {', '.join(suggestions[:3])}"
            except Exception:
                pass  # Don't fail if we can't get suggestions
            
            # Use enhanced error messaging for model validation failures
            from ..core.user_feedback import show_model_error
            try:
                available_models = self.get_available_models()
                from ..core.validation import ModelValidator
                validator = ModelValidator(self)
                suggestions = validator.suggest_alternative_models(model, available_models)
                
                enhanced_error = show_model_error(
                    model, 
                    "; ".join(validation_result.errors),
                    available_models,
                    suggestions
                )
            except Exception:
                pass  # Don't fail if we can't enhance the error message
            
            raise ValueError(error_msg)
        
        # Log warnings if any
        if validation_result.warnings:
            for warning in validation_result.warnings:
                self.logger.warning(f"Model validation warning: {warning}")
        
        # Prepare and validate messages
        formatted_messages = self._prepare_messages(messages)
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        try:
            response = self._session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            
            # Handle different response status codes
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    raise OpenRouterAPIError("No response content received from API")
            
            elif response.status_code == 401:
                raise OpenRouterAuthenticationError("Invalid API key or authentication failed")
            
            elif response.status_code == 429:
                # Extract retry-after header if present
                retry_after = None
                if "retry-after" in response.headers:
                    try:
                        retry_after = int(response.headers["retry-after"])
                    except ValueError:
                        pass
                
                raise OpenRouterRateLimitError(
                    "Rate limit exceeded", 
                    retry_after=retry_after
                )
            
            elif response.status_code >= 500:
                raise OpenRouterAPIError(
                    f"Server error: {response.status_code}", 
                    status_code=response.status_code
                )
            
            else:
                # Try to extract error message from response
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                except:
                    error_message = f"HTTP {response.status_code}"
                
                raise OpenRouterAPIError(error_message, status_code=response.status_code)
        
        except requests.exceptions.Timeout:
            raise OpenRouterAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise OpenRouterAPIError("Connection error - check internet connection")
        except requests.exceptions.RequestException as e:
            raise OpenRouterAPIError(f"Request failed: {str(e)}")
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3, model: Optional[str] = None, use_fallbacks: bool = True) -> str:
        """
        Generate response with automatic retry logic, fallback models, and enhanced validation.
        
        Args:
            prompt: The prompt to send to the AI service
            max_retries: Maximum number of retry attempts per model
            model: Model to use for completion (defaults to default_model if None)
            use_fallbacks: Whether to use fallback models if primary model fails
            
        Returns:
            Generated response text
            
        Raises:
            OpenRouterError: If all retry attempts and fallback models fail
            ValueError: If model validation fails
        """
        self._ensure_initialized()
        
        # Convert prompt to message format
        messages = [{"role": "user", "content": prompt}]
        
        # Use provided model or fall back to default, then try fallback models
        primary_model = model or self.default_model
        
        # Enhanced model selection with validation
        from ..core.validation import ModelValidator
        validator = ModelValidator(self)
        
        models_to_try = [primary_model]
        
        # Only add fallback models if explicitly requested
        if use_fallbacks:
            # Add configured fallback models
            for fallback_model in self.fallback_models:
                if fallback_model != primary_model:
                    # Validate fallback model before adding
                    is_available, _ = validator.check_model_availability(fallback_model)
                    if is_available:
                        models_to_try.append(fallback_model)
                    else:
                        # Only log once per model per client instance to reduce noise
                        if fallback_model not in self._logged_unavailable_models:
                            self.logger.warning(f"Fallback model '{fallback_model}' is not available, skipping")
                            self._logged_unavailable_models.add(fallback_model)
            
            # Add default fallbacks if needed
            if len(models_to_try) == 1:  # Only primary model
                for default_fallback in validator.default_fallback_models:
                    if default_fallback not in models_to_try:
                        is_available, _ = validator.check_model_availability(default_fallback)
                        if is_available:
                            models_to_try.append(default_fallback)
                            if len(models_to_try) >= 3:  # Limit to 3 models total
                                break
        
        last_error = None
        failed_models = []
        
        for model_to_try in models_to_try:
            self.logger.info(f"Attempting generation with model: {model_to_try}")
            
            for attempt in range(max_retries + 1):
                try:
                    return self.chat_completion(messages, model_to_try)
                
                except ValueError as e:
                    # Model validation error - don't retry with this model
                    self.logger.error(f"Model validation failed for '{model_to_try}': {e}")
                    failed_models.append(model_to_try)
                    last_error = e
                    break
                
                except OpenRouterRateLimitError as e:
                    last_error = e
                    if attempt < max_retries:
                        # Handle rate limiting with appropriate delay
                        delay = e.retry_after if e.retry_after else self.base_delay * (2 ** attempt)
                        delay += random.uniform(0, 1)  # Add jitter
                        self.logger.warning(f"Rate limited on model '{model_to_try}', waiting {delay:.1f}s")
                        time.sleep(delay)
                        continue
                    else:
                        # Try next model if available
                        self.logger.warning(f"Rate limit exceeded for model '{model_to_try}', trying next model")
                        failed_models.append(model_to_try)
                        break
                
                except OpenRouterAuthenticationError as e:
                    # Authentication errors won't be fixed by retrying
                    self.logger.error(f"Authentication failed: {e}")
                    raise e
                
                except (OpenRouterAPIError, OpenRouterError) as e:
                    last_error = e
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        self.logger.warning(f"API error on model '{model_to_try}' (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        # Try next model if available
                        self.logger.warning(f"All retries failed for model '{model_to_try}', trying next model")
                        failed_models.append(model_to_try)
                        break
                
                except Exception as e:
                    last_error = OpenRouterError(f"Unexpected error: {str(e)}")
                    if attempt < max_retries:
                        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        self.logger.warning(f"Unexpected error on model '{model_to_try}' (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"Unexpected error on model '{model_to_try}': {e}")
                        failed_models.append(model_to_try)
                        break
        
        # If we get here, all models and retries failed
        error_msg = (
            f"Failed to generate response after trying {len(models_to_try)} models "
            f"with {max_retries + 1} attempts each.\n"
            f"Failed models: {', '.join(failed_models)}\n"
            f"Last error: {last_error}"
        )
        
        # Try to provide helpful suggestions
        try:
            available_models = self.get_available_models()
            suggestions = validator.suggest_alternative_models(primary_model, available_models)
            if suggestions:
                error_msg += f"\n\nSuggested alternatives to try: {', '.join(suggestions[:3])}"
        except Exception:
            pass  # Don't fail if we can't get suggestions
        
        raise OpenRouterError(error_msg)
    
    def _handle_rate_limit(self, retry_after: Optional[int] = None) -> None:
        """
        Handle rate limiting by waiting appropriate amount of time.
        
        Args:
            retry_after: Seconds to wait as specified by the API
        """
        if retry_after and retry_after > 0:
            # Add small jitter to avoid thundering herd
            delay = retry_after + random.uniform(0, 2)
            time.sleep(delay)
        else:
            # Default exponential backoff
            delay = self.base_delay * 2 + random.uniform(0, 1)
            time.sleep(delay)
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available model names from OpenRouter.
        
        Returns:
            List of available model names
            
        Raises:
            OpenRouterError: If the request fails
        """
        self._ensure_initialized()
        
        try:
            response = self._session.get(
                f"{self.base_url}/models",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                models_data = data.get("data", [])
                # Extract model IDs and update cache
                model_names = [model.get("id", "") for model in models_data if model.get("id")]
                self._available_models = model_names
                return model_names
            else:
                raise OpenRouterAPIError(
                    f"Failed to fetch models: HTTP {response.status_code}",
                    status_code=response.status_code
                )
        
        except requests.exceptions.RequestException as e:
            raise OpenRouterAPIError(f"Request failed: {str(e)}")
    
    def get_available_models_detailed(self) -> List[Dict[str, Any]]:
        """
        Get detailed list of available models from OpenRouter.
        
        Returns:
            List of model information dictionaries
            
        Raises:
            OpenRouterError: If the request fails
        """
        self._ensure_initialized()
        
        try:
            response = self._session.get(
                f"{self.base_url}/models",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                raise OpenRouterAPIError(
                    f"Failed to fetch models: HTTP {response.status_code}",
                    status_code=response.status_code
                )
        
        except requests.exceptions.RequestException as e:
            raise OpenRouterAPIError(f"Request failed: {str(e)}")
    
    def refresh_available_models(self) -> None:
        """
        Refresh the list of available models from OpenRouter API.
        """
        try:
            self.get_available_models()  # This will update the cache
        except Exception:
            # If refresh fails, keep existing cache
            pass
    
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
        
        model = model.strip()
        
        # Validate model name format
        if not self.validate_model(model):
            raise ValueError(f"Invalid model name '{model}': must contain only alphanumeric characters, hyphens, underscores, colons, dots, and slashes")
        
        self.default_model = model
    
    def add_fallback_model(self, model: str) -> None:
        """
        Add a model to the fallback list.
        
        Args:
            model: Model identifier to add to fallbacks
            
        Raises:
            ValueError: If model name is invalid
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        
        model = model.strip()
        
        # Validate model name format
        if not self.validate_model(model):
            raise ValueError(f"Invalid model name '{model}': must contain only alphanumeric characters, hyphens, underscores, colons, dots, and slashes")
        
        if model not in self.fallback_models:
            self.fallback_models.append(model)
    
    def __del__(self):
        """Clean up resources when client is destroyed."""
        if hasattr(self, '_session'):
            self._session.close()