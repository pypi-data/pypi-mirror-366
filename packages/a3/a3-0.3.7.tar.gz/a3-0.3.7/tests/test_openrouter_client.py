"""
Unit tests for OpenRouterClient with mocked API responses.

Tests cover retry logic, exponential backoff, rate limiting handling,
and fallback model support.
"""

import json
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

from a3.clients.openrouter import (
    OpenRouterClient, 
    OpenRouterError, 
    OpenRouterAuthenticationError,
    OpenRouterRateLimitError,
    OpenRouterAPIError
)
from a3.core.models import ValidationResult


class TestOpenRouterClient:
    """Test suite for OpenRouterClient class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test-api-key-12345"
        self.client = OpenRouterClient(self.api_key)
        self.client.initialize()
    
    def test_initialization(self):
        """Test client initialization with API key."""
        client = OpenRouterClient("test-key")
        assert client._api_key == "test-key"
        assert client.base_url == "https://openrouter.ai/api/v1"
        assert client.default_model == "qwen/qwen-2.5-72b-instruct:free"
        assert client.max_retries == 3
        assert client.base_delay == 1.0
    
    def test_initialization_without_api_key(self):
        """Test client initialization without API key."""
        client = OpenRouterClient()
        assert client._api_key is None
    
    def test_set_api_key(self):
        """Test setting API key and updating session headers."""
        client = OpenRouterClient()
        client.set_api_key("new-api-key")
        
        assert client._api_key == "new-api-key"
        assert "Authorization" in client._session.headers
        assert client._session.headers["Authorization"] == "Bearer new-api-key"
    
    def test_set_empty_api_key_raises_error(self):
        """Test that setting empty API key raises ValueError."""
        client = OpenRouterClient()
        
        with pytest.raises(ValueError, match="API key cannot be empty"):
            client.set_api_key("")
        
        with pytest.raises(ValueError, match="API key cannot be empty"):
            client.set_api_key("   ")
    
    @patch('requests.Session.get')
    def test_validate_api_key_success(self, mock_get):
        """Test successful API key validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert self.client.validate_api_key() is True
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_validate_api_key_failure(self, mock_get):
        """Test failed API key validation."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        assert self.client.validate_api_key() is False
    
    @patch('requests.Session.get')
    def test_validate_api_key_exception(self, mock_get):
        """Test API key validation with network exception."""
        mock_get.side_effect = ConnectionError("Network error")
        
        assert self.client.validate_api_key() is False
    
    def test_validate_api_key_no_key(self):
        """Test API key validation without key set."""
        client = OpenRouterClient()
        assert client.validate_api_key() is False
    
    @patch('requests.Session.get')
    @patch('requests.get')
    def test_validate_prerequisites_success(self, mock_requests_get, mock_session_get):
        """Test successful prerequisite validation."""
        # Mock API key validation
        mock_session_response = Mock()
        mock_session_response.status_code = 200
        mock_session_get.return_value = mock_session_response
        
        # Mock connectivity check
        mock_connectivity_response = Mock()
        mock_connectivity_response.status_code = 200
        mock_requests_get.return_value = mock_connectivity_response
        
        result = self.client.validate_prerequisites()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.issues) == 0
    
    @patch('requests.Session.get')
    def test_validate_prerequisites_invalid_key(self, mock_get):
        """Test prerequisite validation with invalid API key."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = self.client.validate_prerequisites()
        
        assert result.is_valid is False
        assert "Invalid or inactive OpenRouter API key" in result.issues
    
    @patch('requests.Session.post')
    def test_chat_completion_success(self, mock_post):
        """Test successful chat completion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Test response"}}
            ]
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = self.client.chat_completion(messages)
        
        assert result == "Test response"
        mock_post.assert_called_once()
        
        # Verify request payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == self.client.default_model
        assert payload['messages'] == messages
    
    @patch('requests.Session.post')
    def test_chat_completion_authentication_error(self, mock_post):
        """Test chat completion with authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(OpenRouterAuthenticationError):
            self.client.chat_completion(messages)
    
    @patch('requests.Session.post')
    def test_chat_completion_rate_limit_error(self, mock_post):
        """Test chat completion with rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "60"}
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(OpenRouterRateLimitError) as exc_info:
            self.client.chat_completion(messages)
        
        assert exc_info.value.retry_after == 60
    
    @patch('requests.Session.post')
    def test_chat_completion_server_error(self, mock_post):
        """Test chat completion with server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(OpenRouterAPIError) as exc_info:
            self.client.chat_completion(messages)
        
        assert exc_info.value.status_code == 500
    
    @patch('requests.Session.post')
    def test_chat_completion_timeout(self, mock_post):
        """Test chat completion with timeout."""
        mock_post.side_effect = Timeout("Request timed out")
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(OpenRouterAPIError, match="Request timed out"):
            self.client.chat_completion(messages)
    
    @patch('requests.Session.post')
    def test_chat_completion_connection_error(self, mock_post):
        """Test chat completion with connection error."""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(OpenRouterAPIError, match="Connection error"):
            self.client.chat_completion(messages)
    
    @patch('requests.Session.post')
    def test_chat_completion_no_content(self, mock_post):
        """Test chat completion with no content in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []}
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(OpenRouterAPIError, match="No response content received"):
            self.client.chat_completion(messages)
    
    @patch('time.sleep')
    @patch('requests.Session.post')
    def test_generate_with_retry_success_after_failure(self, mock_post, mock_sleep):
        """Test generate_with_retry succeeding after initial failure."""
        # First call fails with rate limit, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 429
        mock_response_fail.headers = {}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "choices": [{"message": {"content": "Success after retry"}}]
        }
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        result = self.client.generate_with_retry("Test prompt")
        
        assert result == "Success after retry"
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once()  # Should have slept between retries
    
    @patch('time.sleep')
    @patch('requests.Session.post')
    def test_generate_with_retry_exponential_backoff(self, mock_post, mock_sleep):
        """Test that retry logic uses exponential backoff."""
        # All calls fail with server error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(OpenRouterError):
            self.client.generate_with_retry("Test prompt", max_retries=2)
        
        # Should have made 3 attempts (initial + 2 retries) per model
        # With fallback models, total attempts will be higher
        assert mock_post.call_count >= 3
        
        # Should have slept between retries with increasing delays
        assert mock_sleep.call_count >= 2
        
        # Verify exponential backoff (delays should increase)
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        # First delay should be around base_delay (1.0), second should be larger
        assert sleep_calls[1] > sleep_calls[0]
    
    @patch('time.sleep')
    @patch('requests.Session.post')
    def test_generate_with_retry_fallback_models(self, mock_post, mock_sleep):
        """Test that retry logic tries fallback models."""
        # All calls fail with server error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Set up fallback models
        self.client.fallback_models = ["model1", "model2"]
        
        with pytest.raises(OpenRouterError):
            self.client.generate_with_retry("Test prompt", max_retries=1)
        
        # Should try primary model + fallback models
        # Each model gets max_retries + 1 attempts
        expected_calls = len([self.client.default_model] + self.client.fallback_models) * 2
        assert mock_post.call_count == expected_calls
    
    @patch('requests.Session.post')
    def test_generate_with_retry_authentication_error_no_retry(self, mock_post):
        """Test that authentication errors are not retried."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        with pytest.raises(OpenRouterAuthenticationError):
            self.client.generate_with_retry("Test prompt", max_retries=3)
        
        # Should only make one attempt since auth errors aren't retried
        assert mock_post.call_count == 1
    
    @patch('time.sleep')
    @patch('requests.Session.post')
    def test_generate_with_retry_rate_limit_with_retry_after(self, mock_post, mock_sleep):
        """Test rate limit handling with retry-after header."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "5"}
        mock_post.return_value = mock_response
        
        with pytest.raises(OpenRouterError):
            self.client.generate_with_retry("Test prompt", max_retries=1)
        
        # Should respect retry-after header
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        # First sleep should be around 5 seconds (retry-after) plus jitter
        assert 5 <= sleep_calls[0] <= 7
    
    @patch('requests.Session.get')
    def test_get_available_models_success(self, mock_get):
        """Test successful retrieval of available models."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "name": "Model 1"},
                {"id": "model2", "name": "Model 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        models = self.client.get_available_models()
        
        assert len(models) == 2
        assert models[0] == "model1"
        assert models[1] == "model2"
    
    @patch('requests.Session.get')
    def test_get_available_models_error(self, mock_get):
        """Test error handling when retrieving available models."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(OpenRouterAPIError) as exc_info:
            self.client.get_available_models()
        
        assert exc_info.value.status_code == 500
    
    def test_set_default_model(self):
        """Test setting default model."""
        self.client.set_default_model("new-model")
        assert self.client.default_model == "new-model"
    
    def test_set_default_model_empty_raises_error(self):
        """Test that setting empty model name raises error."""
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            self.client.set_default_model("")
    
    def test_add_fallback_model(self):
        """Test adding fallback model."""
        initial_count = len(self.client.fallback_models)
        self.client.add_fallback_model("new-fallback-model")
        
        assert len(self.client.fallback_models) == initial_count + 1
        assert "new-fallback-model" in self.client.fallback_models
    
    def test_add_fallback_model_duplicate(self):
        """Test adding duplicate fallback model."""
        existing_model = self.client.fallback_models[0]
        initial_count = len(self.client.fallback_models)
        
        self.client.add_fallback_model(existing_model)
        
        # Should not add duplicate
        assert len(self.client.fallback_models) == initial_count
    
    def test_add_fallback_model_empty_raises_error(self):
        """Test that adding empty fallback model raises error."""
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            self.client.add_fallback_model("")
    
    def test_prepare_messages_valid(self):
        """Test message preparation with valid messages."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        result = self.client._prepare_messages(messages)
        
        assert len(result) == 3
        assert all(isinstance(msg["content"], str) for msg in result)
    
    def test_prepare_messages_invalid_format(self):
        """Test message preparation with invalid message format."""
        messages = [{"invalid": "message"}]
        
        with pytest.raises(ValueError, match="must be a dict with 'role' and 'content' keys"):
            self.client._prepare_messages(messages)
    
    def test_prepare_messages_invalid_role(self):
        """Test message preparation with invalid role."""
        messages = [{"role": "invalid", "content": "test"}]
        
        with pytest.raises(ValueError, match="Invalid message role"):
            self.client._prepare_messages(messages)
    
    def test_handle_rate_limit_with_retry_after(self):
        """Test rate limit handling with retry-after value."""
        with patch('time.sleep') as mock_sleep:
            self.client._handle_rate_limit(retry_after=10)
            
            # Should sleep for retry_after + jitter (10-12 seconds)
            sleep_time = mock_sleep.call_args[0][0]
            assert 10 <= sleep_time <= 12
    
    def test_handle_rate_limit_without_retry_after(self):
        """Test rate limit handling without retry-after value."""
        with patch('time.sleep') as mock_sleep:
            self.client._handle_rate_limit()
            
            # Should use default backoff
            sleep_time = mock_sleep.call_args[0][0]
            assert 2 <= sleep_time <= 4  # base_delay * 2 + jitter


class TestOpenRouterClientIntegration:
    """Integration tests for OpenRouterClient (require network access)."""
    
    @pytest.mark.integration
    def test_real_api_key_validation(self):
        """Test API key validation with real network call."""
        # This test requires a real API key and network access
        # Skip if no API key is provided
        import os
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            pytest.skip("No OPENROUTER_API_KEY environment variable set")
        
        client = OpenRouterClient(api_key)
        client.initialize()
        
        # This should succeed with a valid key
        assert client.validate_api_key() is True
    
    @pytest.mark.integration
    def test_real_models_retrieval(self):
        """Test retrieving real models from OpenRouter."""
        import os
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            pytest.skip("No OPENROUTER_API_KEY environment variable set")
        
        client = OpenRouterClient(api_key)
        client.initialize()
        
        models = client.get_available_models()
        
        # Should return a list of models
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Each model should have required fields
        for model in models[:5]:  # Check first 5 models
            assert "id" in model
            assert isinstance(model["id"], str)


if __name__ == "__main__":
    pytest.main([__file__])