"""
User feedback and error message utilities for AI Project Builder.

This module provides enhanced error messages, progress indicators,
and user-friendly feedback for various operations.
"""

import logging
import time
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from enum import Enum


class FeedbackLevel(Enum):
    """Levels of user feedback."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class ProgressIndicator:
    """
    Progress indicator for long-running operations.
    
    Provides user-friendly progress updates with time estimates
    and operation status.
    """
    
    def __init__(self, operation_name: str, total_items: int = 0, 
                 show_percentage: bool = True, show_eta: bool = True):
        """
        Initialize progress indicator.
        
        Args:
            operation_name: Name of the operation being tracked
            total_items: Total number of items to process
            show_percentage: Whether to show percentage completion
            show_eta: Whether to show estimated time to completion
        """
        self.operation_name = operation_name
        self.total_items = total_items
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        
        self.current_item = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.logger = logging.getLogger(__name__)
        
        # Track operation phases
        self.current_phase = "starting"
        self.phase_start_time = self.start_time
        
        self.logger.info(f"Starting {operation_name}...")
    
    def update(self, increment: int = 1, current_item_name: Optional[str] = None, 
               phase: Optional[str] = None) -> None:
        """
        Update progress indicator.
        
        Args:
            increment: Number of items completed
            current_item_name: Name of current item being processed
            phase: Current phase of the operation
        """
        self.current_item += increment
        current_time = time.time()
        
        # Update phase if provided
        if phase and phase != self.current_phase:
            phase_duration = current_time - self.phase_start_time
            self.logger.info(f"Completed phase '{self.current_phase}' in {phase_duration:.1f}s")
            self.current_phase = phase
            self.phase_start_time = current_time
        
        # Only show progress updates every few seconds to avoid spam
        if current_time - self.last_update_time >= 2.0 or self.current_item >= self.total_items:
            self._show_progress(current_item_name)
            self.last_update_time = current_time
    
    def _show_progress(self, current_item_name: Optional[str] = None) -> None:
        """Show current progress to user."""
        elapsed_time = time.time() - self.start_time
        
        # Build progress message
        message_parts = [f"{self.operation_name}"]
        
        if self.current_phase != "starting":
            message_parts.append(f"({self.current_phase})")
        
        if self.total_items > 0:
            if self.show_percentage:
                percentage = (self.current_item / self.total_items) * 100
                message_parts.append(f"{percentage:.1f}%")
            
            message_parts.append(f"({self.current_item}/{self.total_items})")
            
            if self.show_eta and self.current_item > 0:
                items_per_second = self.current_item / elapsed_time
                remaining_items = self.total_items - self.current_item
                eta_seconds = remaining_items / items_per_second if items_per_second > 0 else 0
                
                if eta_seconds > 60:
                    eta_str = f"{eta_seconds/60:.1f}m"
                else:
                    eta_str = f"{eta_seconds:.0f}s"
                
                message_parts.append(f"ETA: {eta_str}")
        
        if current_item_name:
            message_parts.append(f"- {current_item_name}")
        
        progress_message = " ".join(message_parts)
        self.logger.info(progress_message)
    
    def complete(self, success: bool = True, final_message: Optional[str] = None) -> None:
        """
        Mark operation as complete.
        
        Args:
            success: Whether operation completed successfully
            final_message: Optional final message to display
        """
        total_time = time.time() - self.start_time
        
        if success:
            if final_message:
                self.logger.info(f"✓ {self.operation_name} completed successfully: {final_message} (took {total_time:.1f}s)")
            else:
                self.logger.info(f"✓ {self.operation_name} completed successfully in {total_time:.1f}s")
        else:
            if final_message:
                self.logger.error(f"✗ {self.operation_name} failed: {final_message} (after {total_time:.1f}s)")
            else:
                self.logger.error(f"✗ {self.operation_name} failed after {total_time:.1f}s")


class UserFeedbackManager:
    """
    Manager for providing enhanced user feedback and error messages.
    
    Centralizes user communication with context-aware messages,
    suggestions, and progress tracking.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize feedback manager.
        
        Args:
            logger: Logger instance to use for output
        """
        self.logger = logger or logging.getLogger(__name__)
        self.active_operations: Dict[str, ProgressIndicator] = {}
    
    def start_operation(self, operation_id: str, operation_name: str, 
                       total_items: int = 0, **kwargs) -> ProgressIndicator:
        """
        Start tracking a long-running operation.
        
        Args:
            operation_id: Unique identifier for the operation
            operation_name: User-friendly name for the operation
            total_items: Total number of items to process
            **kwargs: Additional arguments for ProgressIndicator
            
        Returns:
            ProgressIndicator instance for the operation
        """
        indicator = ProgressIndicator(operation_name, total_items, **kwargs)
        self.active_operations[operation_id] = indicator
        return indicator
    
    def update_operation(self, operation_id: str, increment: int = 1, 
                        current_item_name: Optional[str] = None, 
                        phase: Optional[str] = None) -> None:
        """
        Update progress for an active operation.
        
        Args:
            operation_id: ID of the operation to update
            increment: Number of items completed
            current_item_name: Name of current item being processed
            phase: Current phase of the operation
        """
        if operation_id in self.active_operations:
            self.active_operations[operation_id].update(increment, current_item_name, phase)
    
    def complete_operation(self, operation_id: str, success: bool = True, 
                          final_message: Optional[str] = None) -> None:
        """
        Mark an operation as complete.
        
        Args:
            operation_id: ID of the operation to complete
            success: Whether operation completed successfully
            final_message: Optional final message to display
        """
        if operation_id in self.active_operations:
            self.active_operations[operation_id].complete(success, final_message)
            del self.active_operations[operation_id]
    
    def show_model_error(self, model_name: str, error_message: str, 
                        available_models: Optional[List[str]] = None,
                        suggested_models: Optional[List[str]] = None) -> str:
        """
        Show enhanced error message for model-related issues.
        
        Args:
            model_name: Name of the model that failed
            error_message: Original error message
            available_models: List of available models
            suggested_models: List of suggested alternative models
            
        Returns:
            Enhanced error message with suggestions
        """
        enhanced_message = f"❌ Model Error: {error_message}\n"
        enhanced_message += f"   Requested model: '{model_name}'\n"
        
        if suggested_models:
            enhanced_message += f"   💡 Suggested alternatives:\n"
            for i, suggestion in enumerate(suggested_models[:3], 1):
                enhanced_message += f"      {i}. {suggestion}\n"
        
        if available_models and len(available_models) <= 10:
            enhanced_message += f"   📋 All available models:\n"
            for model in sorted(available_models):
                enhanced_message += f"      • {model}\n"
        elif available_models:
            enhanced_message += f"   📋 {len(available_models)} models available (use get_available_models() to see all)\n"
        
        enhanced_message += f"   🔧 To fix: Use a3.set_model('model_name') with a valid model\n"
        
        self.logger.error(enhanced_message.strip())
        return enhanced_message.strip()
    
    def show_test_generation_error(self, function_name: str, module_name: str, 
                                  error_type: str, error_details: str,
                                  fallback_used: bool = False,
                                  recovery_suggestions: Optional[List[str]] = None) -> str:
        """
        Show enhanced error message for test generation issues.
        
        Args:
            function_name: Name of the function that failed
            module_name: Name of the module containing the function
            error_type: Type of error that occurred
            error_details: Detailed error information
            fallback_used: Whether fallback generation was used
            recovery_suggestions: List of recovery suggestions
            
        Returns:
            Enhanced error message with recovery options
        """
        enhanced_message = f"⚠️  Test Generation Issue: {error_type}\n"
        enhanced_message += f"   Function: {module_name}.{function_name}\n"
        enhanced_message += f"   Details: {error_details}\n"
        
        if fallback_used:
            enhanced_message += f"   ✅ Fallback: Template-based tests generated instead\n"
        
        if recovery_suggestions:
            enhanced_message += f"   💡 Recovery options:\n"
            for i, suggestion in enumerate(recovery_suggestions, 1):
                enhanced_message += f"      {i}. {suggestion}\n"
        else:
            # Default recovery suggestions
            enhanced_message += f"   💡 Recovery options:\n"
            enhanced_message += f"      1. Check your API key and network connection\n"
            enhanced_message += f"      2. Try a different AI model with a3.set_model()\n"
            enhanced_message += f"      3. Review function docstring for clarity\n"
            enhanced_message += f"      4. Generate tests manually if needed\n"
        
        level = FeedbackLevel.WARNING if fallback_used else FeedbackLevel.ERROR
        self._log_message(enhanced_message.strip(), level)
        return enhanced_message.strip()
    
    def show_api_error(self, operation: str, error_message: str, 
                      error_code: Optional[str] = None,
                      retry_suggestions: Optional[List[str]] = None) -> str:
        """
        Show enhanced error message for API-related issues.
        
        Args:
            operation: Name of the operation that failed
            error_message: Original error message
            error_code: Error code if available
            retry_suggestions: List of retry suggestions
            
        Returns:
            Enhanced error message with retry guidance
        """
        enhanced_message = f"🌐 API Error during {operation}\n"
        enhanced_message += f"   Error: {error_message}\n"
        
        if error_code:
            enhanced_message += f"   Code: {error_code}\n"
        
        if retry_suggestions:
            enhanced_message += f"   🔄 Retry suggestions:\n"
            for i, suggestion in enumerate(retry_suggestions, 1):
                enhanced_message += f"      {i}. {suggestion}\n"
        else:
            # Default retry suggestions based on common API issues
            enhanced_message += f"   🔄 Retry suggestions:\n"
            enhanced_message += f"      1. Check your internet connection\n"
            enhanced_message += f"      2. Verify your API key is valid and active\n"
            enhanced_message += f"      3. Try again in a few minutes (may be rate limited)\n"
            enhanced_message += f"      4. Check API service status\n"
        
        self.logger.error(enhanced_message.strip())
        return enhanced_message.strip()
    
    def show_validation_error(self, item_type: str, item_name: str, 
                             validation_errors: List[str],
                             validation_warnings: Optional[List[str]] = None,
                             fix_suggestions: Optional[List[str]] = None) -> str:
        """
        Show enhanced error message for validation issues.
        
        Args:
            item_type: Type of item being validated (e.g., "model", "function")
            item_name: Name of the item that failed validation
            validation_errors: List of validation errors
            validation_warnings: List of validation warnings
            fix_suggestions: List of suggestions to fix the issues
            
        Returns:
            Enhanced error message with fix suggestions
        """
        enhanced_message = f"❌ Validation Error: Invalid {item_type}\n"
        enhanced_message += f"   {item_type.title()}: '{item_name}'\n"
        
        enhanced_message += f"   🚫 Errors:\n"
        for i, error in enumerate(validation_errors, 1):
            enhanced_message += f"      {i}. {error}\n"
        
        if validation_warnings:
            enhanced_message += f"   ⚠️  Warnings:\n"
            for i, warning in enumerate(validation_warnings, 1):
                enhanced_message += f"      {i}. {warning}\n"
        
        if fix_suggestions:
            enhanced_message += f"   🔧 How to fix:\n"
            for i, suggestion in enumerate(fix_suggestions, 1):
                enhanced_message += f"      {i}. {suggestion}\n"
        
        self.logger.error(enhanced_message.strip())
        return enhanced_message.strip()
    
    def show_success_message(self, operation: str, details: Optional[str] = None,
                           metrics: Optional[Dict[str, Any]] = None) -> str:
        """
        Show enhanced success message with metrics.
        
        Args:
            operation: Name of the successful operation
            details: Additional details about the success
            metrics: Dictionary of metrics to display
            
        Returns:
            Enhanced success message
        """
        enhanced_message = f"✅ Success: {operation} completed\n"
        
        if details:
            enhanced_message += f"   Details: {details}\n"
        
        if metrics:
            enhanced_message += f"   📊 Metrics:\n"
            for key, value in metrics.items():
                enhanced_message += f"      • {key}: {value}\n"
        
        self.logger.info(enhanced_message.strip())
        return enhanced_message.strip()
    
    def _log_message(self, message: str, level: FeedbackLevel) -> None:
        """Log message at appropriate level."""
        if level == FeedbackLevel.DEBUG:
            self.logger.debug(message)
        elif level == FeedbackLevel.INFO:
            self.logger.info(message)
        elif level == FeedbackLevel.WARNING:
            self.logger.warning(message)
        elif level == FeedbackLevel.ERROR:
            self.logger.error(message)
        elif level == FeedbackLevel.SUCCESS:
            self.logger.info(message)


# Global feedback manager instance
_global_feedback_manager: Optional[UserFeedbackManager] = None


def get_feedback_manager() -> UserFeedbackManager:
    """Get the global feedback manager instance."""
    global _global_feedback_manager
    if _global_feedback_manager is None:
        _global_feedback_manager = UserFeedbackManager()
    return _global_feedback_manager


def show_model_error(model_name: str, error_message: str, 
                    available_models: Optional[List[str]] = None,
                    suggested_models: Optional[List[str]] = None) -> str:
    """Convenience function to show model error."""
    return get_feedback_manager().show_model_error(
        model_name, error_message, available_models, suggested_models
    )


def show_test_generation_error(function_name: str, module_name: str, 
                              error_type: str, error_details: str,
                              fallback_used: bool = False,
                              recovery_suggestions: Optional[List[str]] = None) -> str:
    """Convenience function to show test generation error."""
    return get_feedback_manager().show_test_generation_error(
        function_name, module_name, error_type, error_details, 
        fallback_used, recovery_suggestions
    )


def start_operation_progress(operation_id: str, operation_name: str, 
                           total_items: int = 0, **kwargs) -> ProgressIndicator:
    """Convenience function to start operation progress tracking."""
    return get_feedback_manager().start_operation(
        operation_id, operation_name, total_items, **kwargs
    )


def update_operation_progress(operation_id: str, increment: int = 1, 
                            current_item_name: Optional[str] = None, 
                            phase: Optional[str] = None) -> None:
    """Convenience function to update operation progress."""
    get_feedback_manager().update_operation(
        operation_id, increment, current_item_name, phase
    )


def complete_operation_progress(operation_id: str, success: bool = True, 
                              final_message: Optional[str] = None) -> None:
    """Convenience function to complete operation progress."""
    get_feedback_manager().complete_operation(operation_id, success, final_message)