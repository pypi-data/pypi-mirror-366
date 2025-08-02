"""
Tests for model selection functionality in A3.

This module tests the model selection API methods to ensure:
1. set_model, get_current_model, and get_available_models methods work correctly
2. Model validation and error handling function properly
3. Configuration persistence and state management work as expected
4. Fallback mechanisms and error recovery work correctly
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Optional

from a3.core.api import A3, ConfigurationError, ValidationError, OperationError
from a3.core.models import ModelConfiguration
from a3.managers.state import StateManager


class TestModelSelectionAPI:
    """Test suite for A3 model selection API methods."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create temporary directory for test project
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Create A3 instance
        self.a3 = A3(str(self.project_path))
        self.a3.set_api_key("test-api-key")
        
        # Mock the OpenRouter client to avoid actual API calls
        self.mock_client_patcher = patch('a3.clients.openrouter.OpenRouterClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        
        # Configure mock client
        self.mock_client.validate_api_key.return_value = True
        self.mock_client.get_available_models.return_value = [
            "qwen/qwen-2.5-72b-instruct:free",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.mock_client_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_set_model_valid_model(self):
        """Test setting a valid model name."""
        model_name = "qwen/qwen-2.5-72b-instruct:free"
        
        # Mock model validation
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (True, None)
                mock_validator_class.return_value = mock_validator
                
                # Set the model
                self.a3.set_model(model_name)
                
                # Verify the model was set
                assert self.a3.get_current_model() == model_name
    
    def test_set_model_empty_name_raises_error(self):
        """Test that setting an empty model name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            self.a3.set_model("")
        
        assert "Model name cannot be empty" in str(exc_info.value)
        assert "get_available_models()" in exc_info.value.suggestion
    
    def test_set_model_whitespace_only_name_raises_error(self):
        """Test that setting a whitespace-only model name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            self.a3.set_model("   ")
        
        assert "Model name cannot be empty" in str(exc_info.value)
    
    def test_set_model_invalid_format_raises_error(self):
        """Test that setting an invalid model name format raises ValidationError."""
        invalid_model = "invalid-model-format"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(
                is_valid=False, 
                errors=["Invalid model name format"],
                warnings=[]
            )
            
            with pytest.raises(ValidationError) as exc_info:
                self.a3.set_model(invalid_model)
            
            assert f"Invalid model name '{invalid_model}'" in str(exc_info.value)
            assert "get_available_models()" in exc_info.value.suggestion
    
    def test_set_model_unavailable_model_raises_error(self):
        """Test that setting an unavailable model raises ValidationError."""
        unavailable_model = "provider/unavailable-model"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (False, "Model not found")
                mock_validator.suggest_alternative_models.return_value = ["qwen/qwen-2.5-72b-instruct:free"]
                mock_validator_class.return_value = mock_validator
                
                with pytest.raises(ValidationError) as exc_info:
                    self.a3.set_model(unavailable_model)
                
                assert f"Model '{unavailable_model}' is not available" in str(exc_info.value)
                assert "Suggested alternatives" in exc_info.value.suggestion
    
    def test_set_model_with_warnings(self):
        """Test setting a model that generates warnings."""
        model_name = "deprecated/old-model"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(
                is_valid=True, 
                errors=[], 
                warnings=["This model is deprecated"]
            )
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (True, None)
                mock_validator_class.return_value = mock_validator
                
                # Should succeed but log warnings
                self.a3.set_model(model_name)
                assert self.a3.get_current_model() == model_name
    
    def test_set_model_network_error_fallback(self):
        """Test that model setting works even when network validation fails."""
        model_name = "qwen/qwen-2.5-72b-instruct:free"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.side_effect = Exception("Network error")
                mock_validator_class.return_value = mock_validator
                
                # Should succeed despite network error
                self.a3.set_model(model_name)
                assert self.a3.get_current_model() == model_name
    
    def test_get_current_model_default(self):
        """Test getting current model returns default when none is set."""
        current_model = self.a3.get_current_model()
        assert current_model == "qwen/qwen-2.5-72b-instruct:free"  # Default model
    
    def test_get_current_model_after_setting(self):
        """Test getting current model after setting a specific model."""
        model_name = "openai/gpt-3.5-turbo"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (True, None)
                mock_validator_class.return_value = mock_validator
                
                self.a3.set_model(model_name)
                assert self.a3.get_current_model() == model_name
    
    def test_get_available_models_from_api(self):
        """Test getting available models from API."""
        expected_models = [
            "qwen/qwen-2.5-72b-instruct:free",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku"
        ]
        self.mock_client.get_available_models.return_value = expected_models
        
        models = self.a3.get_available_models()
        assert models == expected_models
        self.mock_client.get_available_models.assert_called_once()
    
    def test_get_available_models_api_failure_uses_cache(self):
        """Test that API failure falls back to cached models."""
        # First, populate cache with successful API call
        cached_models = ["qwen/qwen-2.5-72b-instruct:free", "openai/gpt-3.5-turbo"]
        self.mock_client.get_available_models.return_value = cached_models
        
        # Get models to populate cache
        self.a3.get_available_models()
        
        # Now make API fail and verify fallback to cache
        self.mock_client.get_available_models.side_effect = Exception("API Error")
        
        models = self.a3.get_available_models()
        assert models == cached_models
    
    def test_get_available_models_fallback_to_hardcoded(self):
        """Test that complete failure falls back to hardcoded model list."""
        # Make API fail
        self.mock_client.get_available_models.side_effect = Exception("API Error")
        
        # Create fresh A3 instance with no cache
        fresh_a3 = A3(str(self.project_path))
        fresh_a3.set_api_key("test-api-key")
        
        models = fresh_a3.get_available_models()
        
        # Should return hardcoded fallback list
        assert isinstance(models, list)
        assert len(models) > 0
        assert "qwen/qwen-2.5-72b-instruct:free" in models
    
    def test_model_configuration_persistence(self):
        """Test that model configuration is persisted across sessions."""
        model_name = "anthropic/claude-3-haiku"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (True, None)
                mock_validator_class.return_value = mock_validator
                
                # Set model in first instance
                self.a3.set_model(model_name)
                
                # Create new A3 instance and verify model persisted
                new_a3 = A3(str(self.project_path))
                new_a3.set_api_key("test-api-key")
                
                assert new_a3.get_current_model() == model_name
    
    def test_model_configuration_validation_on_load(self):
        """Test that invalid saved configuration is handled gracefully."""
        # Manually create invalid configuration file
        config_file = self.project_path / ".a3" / "model_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump({"invalid": "config"}, f)
        
        # Should handle invalid config gracefully and create default
        current_model = self.a3.get_current_model()
        assert current_model == "qwen/qwen-2.5-72b-instruct:free"  # Default
    
    def test_api_key_required_for_model_operations(self):
        """Test that API key is required for model operations."""
        # Create A3 instance without API key
        no_key_a3 = A3(str(self.project_path))
        
        with pytest.raises(ConfigurationError) as exc_info:
            no_key_a3.set_model("some-model")
        
        assert "API key" in str(exc_info.value).lower()
    
    def test_model_configuration_caching(self):
        """Test that available models are cached properly."""
        api_models = ["model1", "model2", "model3"]
        self.mock_client.get_available_models.return_value = api_models
        
        # First call should hit API
        models1 = self.a3.get_available_models()
        assert models1 == api_models
        
        # Verify models were cached in state
        config = self.a3._state_manager.load_model_configuration()
        assert config is not None
        assert config.available_models == api_models
        
        # Second call with API failure should use cache
        self.mock_client.get_available_models.side_effect = Exception("API Error")
        models2 = self.a3.get_available_models()
        assert models2 == api_models  # Should use cached models


class TestModelConfigurationStateManagement:
    """Test suite for model configuration state management."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.state_manager = StateManager(str(self.project_path))
        self.state_manager.initialize()
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_model_configuration(self):
        """Test saving and loading model configuration."""
        config = ModelConfiguration(
            current_model="test/model",
            available_models=["test/model", "other/model"],
            fallback_models=["other/model"],
            preferences={"auto_fallback": True}
        )
        
        # Save configuration
        self.state_manager.save_model_configuration(config)
        
        # Load configuration
        loaded_config = self.state_manager.load_model_configuration()
        
        assert loaded_config is not None
        assert loaded_config.current_model == config.current_model
        assert loaded_config.available_models == config.available_models
        assert loaded_config.fallback_models == config.fallback_models
        assert loaded_config.preferences == config.preferences
    
    def test_get_or_create_model_configuration_creates_default(self):
        """Test that get_or_create_model_configuration creates default when none exists."""
        config = self.state_manager.get_or_create_model_configuration()
        
        assert config is not None
        assert config.current_model == "qwen/qwen-2.5-72b-instruct:free"
        assert len(config.available_models) > 0
        assert len(config.fallback_models) > 0
        assert isinstance(config.preferences, dict)
    
    def test_get_or_create_model_configuration_returns_existing(self):
        """Test that get_or_create_model_configuration returns existing config."""
        # Create and save initial config
        initial_config = ModelConfiguration(
            current_model="custom/model",
            available_models=["custom/model"],
            fallback_models=["custom/model"]
        )
        self.state_manager.save_model_configuration(initial_config)
        
        # Get or create should return existing
        config = self.state_manager.get_or_create_model_configuration()
        
        assert config.current_model == "custom/model"
        assert config.available_models == ["custom/model"]
    
    def test_model_configuration_validation_on_save(self):
        """Test that invalid configuration is rejected on save."""
        invalid_config = ModelConfiguration(
            current_model="",  # Invalid: empty model name
            available_models=[],
            fallback_models=[]
        )
        
        with pytest.raises(Exception):  # Should raise validation error
            self.state_manager.save_model_configuration(invalid_config)
    
    def test_model_configuration_atomic_save(self):
        """Test that model configuration save is atomic."""
        config = ModelConfiguration(
            current_model="test/model",
            available_models=["test/model"]
        )
        
        # Mock file operations to simulate failure during save
        original_move = shutil.move
        
        def failing_move(*args, **kwargs):
            raise Exception("Simulated failure")
        
        with patch('shutil.move', side_effect=failing_move):
            with pytest.raises(Exception):
                self.state_manager.save_model_configuration(config)
        
        # Verify no partial state was saved
        loaded_config = self.state_manager.load_model_configuration()
        assert loaded_config is None  # Should be None since save failed
    
    def test_model_configuration_corrupted_file_handling(self):
        """Test handling of corrupted configuration file."""
        # Create corrupted config file
        config_file = self.project_path / ".a3" / "model_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle corruption gracefully
        with pytest.raises(Exception):  # Should raise StateCorruptionError
            self.state_manager.load_model_configuration()


class TestModelValidationAndErrorHandling:
    """Test suite for model validation and error handling."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.a3 = A3(str(self.project_path))
        self.a3.set_api_key("test-api-key")
        
        # Mock the OpenRouter client
        self.mock_client_patcher = patch('a3.clients.openrouter.OpenRouterClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        self.mock_client.validate_api_key.return_value = True
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.mock_client_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_model_validation_with_suggestions(self):
        """Test that model validation provides helpful suggestions."""
        invalid_model = "typo/gpt-3.5-turbo"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (False, "Model not found")
                mock_validator.suggest_alternative_models.return_value = ["openai/gpt-3.5-turbo"]
                mock_validator_class.return_value = mock_validator
                
                self.mock_client.get_available_models.return_value = ["openai/gpt-3.5-turbo"]
                
                with pytest.raises(ValidationError) as exc_info:
                    self.a3.set_model(invalid_model)
                
                assert "openai/gpt-3.5-turbo" in exc_info.value.suggestion
    
    def test_error_handling_with_user_friendly_messages(self):
        """Test that errors include user-friendly messages and suggestions."""
        with pytest.raises(ValidationError) as exc_info:
            self.a3.set_model("")
        
        error = exc_info.value
        assert hasattr(error, 'message')
        assert hasattr(error, 'suggestion')
        assert hasattr(error, 'error_code')
        assert error.suggestion is not None
        assert len(error.suggestion) > 0
    
    def test_fallback_model_selection(self):
        """Test fallback model selection when preferred model fails."""
        # This would be tested in integration with actual model switching logic
        # For now, test that configuration supports fallback models
        config = ModelConfiguration(
            current_model="primary/model",
            available_models=["primary/model", "fallback/model"],
            fallback_models=["fallback/model"]
        )
        
        # Test getting next fallback model
        next_fallback = config.get_next_fallback_model()
        assert next_fallback == "fallback/model"
    
    def test_model_availability_checking(self):
        """Test model availability checking logic."""
        config = ModelConfiguration(
            current_model="available/model",
            available_models=["available/model", "other/model"]
        )
        
        assert config.is_model_available("available/model") is True
        assert config.is_model_available("unavailable/model") is False
        
        # Test with empty available models (should return True)
        empty_config = ModelConfiguration(
            current_model="any/model",
            available_models=[]
        )
        assert empty_config.is_model_available("any/model") is True
    
    def test_concurrent_model_configuration_access(self):
        """Test that concurrent access to model configuration is handled safely."""
        # This is a basic test - in a real scenario, you'd test with threading
        config1 = self.a3._state_manager.get_or_create_model_configuration()
        config2 = self.a3._state_manager.get_or_create_model_configuration()
        
        # Both should return valid configurations
        assert config1 is not None
        assert config2 is not None
        assert config1.current_model == config2.current_model


class TestModelSelectionIntegration:
    """Integration tests for model selection with other A3 components."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.a3 = A3(str(self.project_path))
        self.a3.set_api_key("test-api-key")
        
        # Mock the OpenRouter client
        self.mock_client_patcher = patch('a3.clients.openrouter.OpenRouterClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        self.mock_client.validate_api_key.return_value = True
        self.mock_client.get_available_models.return_value = [
            "qwen/qwen-2.5-72b-instruct:free",
            "openai/gpt-3.5-turbo"
        ]
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.mock_client_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_model_selection_affects_ai_operations(self):
        """Test that model selection affects subsequent AI operations."""
        # This would require mocking the actual AI operations
        # For now, test that the model is properly stored and retrieved
        
        model_name = "openai/gpt-3.5-turbo"
        
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (True, None)
                mock_validator_class.return_value = mock_validator
                
                self.a3.set_model(model_name)
                
                # Verify that subsequent operations would use this model
                current_model = self.a3.get_current_model()
                assert current_model == model_name
    
    def test_model_configuration_migration_compatibility(self):
        """Test that projects without model config are handled gracefully."""
        # Create A3 instance in directory without existing model config
        fresh_a3 = A3(str(self.project_path))
        fresh_a3.set_api_key("test-api-key")
        
        # Should create default configuration
        current_model = fresh_a3.get_current_model()
        assert current_model == "qwen/qwen-2.5-72b-instruct:free"
        
        # Should be able to set new model
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.return_value = (True, None)
                mock_validator_class.return_value = mock_validator
                
                fresh_a3.set_model("openai/gpt-3.5-turbo")
                assert fresh_a3.get_current_model() == "openai/gpt-3.5-turbo"
    
    def test_model_selection_error_recovery(self):
        """Test error recovery in model selection operations."""
        # Test that system recovers gracefully from various error conditions
        
        # 1. Network errors during model validation
        with patch('a3.core.validation.validate_model_name') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
            
            with patch('a3.core.validation.ModelValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.check_model_availability.side_effect = Exception("Network error")
                mock_validator_class.return_value = mock_validator
                
                # Should succeed despite network error
                self.a3.set_model("qwen/qwen-2.5-72b-instruct:free")
                assert self.a3.get_current_model() == "qwen/qwen-2.5-72b-instruct:free"
        
        # 2. API errors during get_available_models
        self.mock_client.get_available_models.side_effect = Exception("API Error")
        
        # Should fall back to cached or hardcoded models
        models = self.a3.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0