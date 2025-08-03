"""
Model validation utilities for AI Project Builder.

This module provides comprehensive validation functions for AI models,
including availability checks, format validation, and graceful degradation.
"""

import logging
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from .models import ModelConfiguration, ValidationResult
from ..clients.base import BaseAIClient


class ModelValidationError(Exception):
    """Exception raised for model validation failures."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message with suggestions."""
        msg = f"Model validation error: {self.message}"
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        if self.error_code:
            msg += f"\n\nError Code: {self.error_code}"
        return msg


class ModelValidator:
    """
    Comprehensive model validation utility class.
    
    Provides methods for validating model names, checking availability,
    and implementing graceful degradation strategies.
    """
    
    def __init__(self, ai_client: Optional[BaseAIClient] = None):
        """
        Initialize the model validator.
        
        Args:
            ai_client: AI client for checking model availability
        """
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
        
        # Cache for model availability checks
        self._availability_cache: Dict[str, Tuple[bool, datetime]] = {}
        self._cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        
        # Default fallback models in order of preference
        self.default_fallback_models = [
            "qwen/qwen-2.5-72b-instruct:free",
            "qwen/qwen3-coder:free",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku"
        ]
    
    def validate_model_name(self, model_name: str) -> ValidationResult:
        """
        Validate that a model name follows the correct format.
        
        Args:
            model_name: Model name to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        warnings = []
        
        if not model_name:
            errors.append("Model name cannot be empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        if not isinstance(model_name, str):
            errors.append("Model name must be a string")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        model_name = model_name.strip()
        if not model_name:
            errors.append("Model name cannot be empty or whitespace only")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Validate model name format (allow alphanumeric, hyphens, underscores, colons, slashes, dots, commas)
        if not re.match(r'^[a-zA-Z0-9_:/.,-]+$', model_name):
            errors.append(
                f"Invalid model name '{model_name}': must contain only alphanumeric characters, "
                "hyphens, underscores, colons, slashes, dots, and commas"
            )
        
        # Check for common format patterns
        if '/' not in model_name and ':' not in model_name:
            warnings.append(
                f"Model name '{model_name}' doesn't follow typical provider/model:version format. "
                "Consider using format like 'provider/model-name' or 'provider/model:version'"
            )
        
        # Check for suspicious patterns
        if model_name.startswith('/') or model_name.endswith('/'):
            errors.append("Model name cannot start or end with '/'")
        
        if model_name.startswith(':') or model_name.endswith(':'):
            errors.append("Model name cannot start or end with ':'")
        
        if '//' in model_name:
            errors.append("Model name cannot contain consecutive slashes")
        
        if '::' in model_name:
            errors.append("Model name cannot contain consecutive colons")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def check_model_availability(self, model_name: str, use_cache: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Check if a model is available for use.
        
        Args:
            model_name: Model name to check
            use_cache: Whether to use cached availability results
            
        Returns:
            Tuple of (is_available, error_message)
        """
        # First validate the model name format
        validation_result = self.validate_model_name(model_name)
        if not validation_result.is_valid:
            return False, f"Invalid model name: {'; '.join(validation_result.errors)}"
        
        # Check cache if enabled
        if use_cache and model_name in self._availability_cache:
            is_available, cached_time = self._availability_cache[model_name]
            if datetime.now() - cached_time < self._cache_duration:
                return is_available, None if is_available else "Model not available (cached result)"
        
        # Check availability through AI client if available
        if self.ai_client:
            try:
                available_models = self.ai_client.get_available_models()
                is_available = model_name in available_models
                
                # Cache the result
                self._availability_cache[model_name] = (is_available, datetime.now())
                
                if not is_available:
                    # Provide helpful suggestions
                    similar_models = self._find_similar_models(model_name, available_models)
                    error_msg = f"Model '{model_name}' is not available"
                    if similar_models:
                        error_msg += f". Similar available models: {', '.join(similar_models[:3])}"
                    return False, error_msg
                
                return True, None
                
            except Exception as e:
                self.logger.warning(f"Failed to check model availability for '{model_name}': {e}")
                # Don't cache failures, as they might be temporary
                return False, f"Unable to verify model availability: {str(e)}"
        
        # If no AI client, assume model is available (optimistic approach)
        self.logger.warning(f"No AI client available to verify model '{model_name}', assuming available")
        return True, None
    
    def validate_model_configuration(self, config: ModelConfiguration) -> ValidationResult:
        """
        Validate a complete model configuration.
        
        Args:
            config: ModelConfiguration to validate
            
        Returns:
            ValidationResult with comprehensive validation details
        """
        errors = []
        warnings = []
        
        try:
            # Use the built-in validation method
            config.validate()
        except Exception as e:
            errors.append(f"Configuration validation failed: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Additional availability checks
        if self.ai_client:
            # Check current model availability
            is_available, error_msg = self.check_model_availability(config.current_model)
            if not is_available:
                errors.append(f"Current model '{config.current_model}' is not available: {error_msg}")
            
            # Check fallback models availability
            unavailable_fallbacks = []
            for fallback_model in config.fallback_models:
                is_available, error_msg = self.check_model_availability(fallback_model)
                if not is_available:
                    unavailable_fallbacks.append(fallback_model)
            
            if unavailable_fallbacks:
                if len(unavailable_fallbacks) == len(config.fallback_models):
                    errors.append("All fallback models are unavailable")
                else:
                    warnings.append(
                        f"Some fallback models are unavailable: {', '.join(unavailable_fallbacks)}"
                    )
        
        # Check for configuration age
        if config.last_updated:
            age = datetime.now() - config.last_updated
            if age > timedelta(days=7):
                warnings.append(
                    f"Model configuration is {age.days} days old. "
                    "Consider refreshing available models list."
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def get_fallback_model(self, failed_model: str, config: ModelConfiguration) -> Optional[str]:
        """
        Get the next available fallback model when a model fails.
        
        Args:
            failed_model: Model that failed
            config: Model configuration with fallback options
            
        Returns:
            Next available fallback model or None if none available
        """
        # First try configured fallback models
        for fallback_model in config.fallback_models:
            if fallback_model != failed_model:
                is_available, _ = self.check_model_availability(fallback_model)
                if is_available:
                    self.logger.info(f"Using fallback model '{fallback_model}' after '{failed_model}' failed")
                    return fallback_model
        
        # If no configured fallbacks work, try default fallbacks
        for default_fallback in self.default_fallback_models:
            if default_fallback != failed_model and default_fallback not in config.fallback_models:
                is_available, _ = self.check_model_availability(default_fallback)
                if is_available:
                    self.logger.info(f"Using default fallback model '{default_fallback}' after '{failed_model}' failed")
                    return default_fallback
        
        self.logger.error(f"No fallback models available after '{failed_model}' failed")
        return None
    
    def validate_before_ai_operation(self, model: str, operation_name: str = "AI operation") -> ValidationResult:
        """
        Validate model before performing an AI operation.
        
        Args:
            model: Model to validate
            operation_name: Name of the operation for error messages
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Validate model name format
        name_validation = self.validate_model_name(model)
        if not name_validation.is_valid:
            errors.extend(name_validation.errors)
            warnings.extend(name_validation.warnings)
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check model availability
        is_available, error_msg = self.check_model_availability(model)
        if not is_available:
            errors.append(f"Cannot perform {operation_name}: {error_msg}")
        
        # Check AI client availability
        if not self.ai_client:
            warnings.append(f"No AI client available for {operation_name}")
        elif not hasattr(self.ai_client, '_api_key') or not self.ai_client._api_key:
            errors.append(f"Cannot perform {operation_name}: API key not configured")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def suggest_alternative_models(self, unavailable_model: str, available_models: List[str]) -> List[str]:
        """
        Suggest alternative models when a requested model is unavailable.
        
        Args:
            unavailable_model: Model that is not available
            available_models: List of available models
            
        Returns:
            List of suggested alternative models
        """
        suggestions = []
        
        # Find similar models by name
        similar_models = self._find_similar_models(unavailable_model, available_models)
        suggestions.extend(similar_models[:3])  # Top 3 similar models
        
        # Add default fallback models if not already included
        for fallback in self.default_fallback_models:
            if fallback in available_models and fallback not in suggestions:
                suggestions.append(fallback)
                if len(suggestions) >= 5:  # Limit to 5 suggestions
                    break
        
        return suggestions
    
    def _find_similar_models(self, target_model: str, available_models: List[str]) -> List[str]:
        """
        Find models similar to the target model based on name similarity.
        
        Args:
            target_model: Model to find similarities for
            available_models: List of available models to search
            
        Returns:
            List of similar models sorted by similarity
        """
        if not available_models:
            return []
        
        # Extract provider and model parts
        target_parts = target_model.lower().replace(':', '/').split('/')
        target_provider = target_parts[0] if len(target_parts) > 0 else ""
        target_name = target_parts[1] if len(target_parts) > 1 else ""
        
        similarities = []
        
        for model in available_models:
            model_parts = model.lower().replace(':', '/').split('/')
            model_provider = model_parts[0] if len(model_parts) > 0 else ""
            model_name = model_parts[1] if len(model_parts) > 1 else ""
            
            similarity_score = 0
            
            # Provider match
            if target_provider and model_provider:
                if target_provider == model_provider:
                    similarity_score += 3
                elif target_provider in model_provider or model_provider in target_provider:
                    similarity_score += 1
            
            # Model name similarity
            if target_name and model_name:
                if target_name == model_name:
                    similarity_score += 5
                elif target_name in model_name or model_name in target_name:
                    similarity_score += 2
                else:
                    # Check for common words
                    target_words = set(re.split(r'[-_.]', target_name))
                    model_words = set(re.split(r'[-_.]', model_name))
                    common_words = target_words.intersection(model_words)
                    similarity_score += len(common_words)
            
            if similarity_score > 0:
                similarities.append((model, similarity_score))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [model for model, _ in similarities]
    
    def clear_availability_cache(self) -> None:
        """Clear the model availability cache."""
        self._availability_cache.clear()
        self.logger.info("Model availability cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the availability cache.
        
        Returns:
            Dictionary with cache statistics
        """
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0
        
        for model_name, (is_available, cached_time) in self._availability_cache.items():
            if now - cached_time < self._cache_duration:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._availability_cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_duration_minutes': self._cache_duration.total_seconds() / 60
        }


# Convenience functions for common validation tasks

def validate_model_name(model_name: str) -> ValidationResult:
    """
    Convenience function to validate a model name.
    
    Args:
        model_name: Model name to validate
        
    Returns:
        ValidationResult with validation status
    """
    validator = ModelValidator()
    return validator.validate_model_name(model_name)


def check_model_availability(model_name: str, ai_client: Optional[BaseAIClient] = None) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to check model availability.
    
    Args:
        model_name: Model name to check
        ai_client: AI client for availability checking
        
    Returns:
        Tuple of (is_available, error_message)
    """
    validator = ModelValidator(ai_client)
    return validator.check_model_availability(model_name)


def validate_before_ai_operation(model: str, ai_client: Optional[BaseAIClient] = None, 
                                operation_name: str = "AI operation") -> ValidationResult:
    """
    Convenience function to validate model before AI operations.
    
    Args:
        model: Model to validate
        ai_client: AI client for validation
        operation_name: Name of the operation for error messages
        
    Returns:
        ValidationResult with validation status
    """
    validator = ModelValidator(ai_client)
    return validator.validate_before_ai_operation(model, operation_name)