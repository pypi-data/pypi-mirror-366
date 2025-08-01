"""
OpenRouter client implementation for AI Project Builder.

This module provides the OpenRouterClient class that handles all interactions
with the OpenRouter API, including chat completions, retry logic, and error handling.
"""

import json
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
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key for authentication
        """
        super().__init__(api_key)
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = "qwen/qwen-2.5-72b-instruct:free"
        self.fallback_models = [
            "qwen/qwen-2.5-72b-instruct:free",
            "qwen/qwen-2-72b-instruct:free",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku"
        ]
        self.timeout = 60  # seconds
        self.max_retries = 3
        self.base_delay = 1.0
        
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
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "default") -> str:
        """
        Generate a chat completion response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model to use for completion (defaults to default_model)
            
        Returns:
            Generated response text
            
        Raises:
            OpenRouterError: If the API request fails
        """
        self._ensure_initialized()
        
        if model == "default":
            model = self.default_model
        
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
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response with automatic retry logic and fallback models.
        
        Args:
            prompt: The prompt to send to the AI service
            max_retries: Maximum number of retry attempts per model
            
        Returns:
            Generated response text
            
        Raises:
            OpenRouterError: If all retry attempts and fallback models fail
        """
        self._ensure_initialized()
        
        # Convert prompt to message format
        messages = [{"role": "user", "content": prompt}]
        
        # Try primary model first, then fallback models
        models_to_try = [self.default_model] + [
            model for model in self.fallback_models 
            if model != self.default_model
        ]
        
        last_error = None
        
        for model in models_to_try:
            for attempt in range(max_retries + 1):
                try:
                    return self.chat_completion(messages, model)
                
                except OpenRouterRateLimitError as e:
                    last_error = e
                    if attempt < max_retries:
                        # Handle rate limiting with appropriate delay
                        delay = e.retry_after if e.retry_after else self.base_delay * (2 ** attempt)
                        delay += random.uniform(0, 1)  # Add jitter
                        time.sleep(delay)
                        continue
                    else:
                        # Try next model if available
                        break
                
                except OpenRouterAuthenticationError as e:
                    # Authentication errors won't be fixed by retrying
                    raise e
                
                except (OpenRouterAPIError, OpenRouterError) as e:
                    last_error = e
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                    else:
                        # Try next model if available
                        break
                
                except Exception as e:
                    last_error = OpenRouterError(f"Unexpected error: {str(e)}")
                    if attempt < max_retries:
                        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                    else:
                        break
        
        # If we get here, all models and retries failed
        raise OpenRouterError(
            f"Failed to generate response after trying {len(models_to_try)} models "
            f"with {max_retries + 1} attempts each. Last error: {last_error}"
        )
    
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
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from OpenRouter.
        
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
    
    def set_default_model(self, model: str) -> None:
        """
        Set the default model for completions.
        
        Args:
            model: Model identifier to use as default
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        
        self.default_model = model.strip()
    
    def add_fallback_model(self, model: str) -> None:
        """
        Add a model to the fallback list.
        
        Args:
            model: Model identifier to add to fallbacks
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        
        model = model.strip()
        if model not in self.fallback_models:
            self.fallback_models.append(model)
    
    def __del__(self):
        """Clean up resources when client is destroyed."""
        if hasattr(self, '_session'):
            self._session.close()