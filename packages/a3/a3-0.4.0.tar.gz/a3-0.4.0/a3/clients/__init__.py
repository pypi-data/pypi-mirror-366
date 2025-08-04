"""
Clients module for AI Project Builder.

This module contains client classes for external service integrations,
particularly AI API clients.
"""

from .base import BaseClient, BaseAIClient
from .openrouter import OpenRouterClient, OpenRouterError, OpenRouterAuthenticationError, OpenRouterRateLimitError, OpenRouterAPIError

__all__ = [
    "BaseClient", 
    "BaseAIClient", 
    "OpenRouterClient",
    "OpenRouterError",
    "OpenRouterAuthenticationError", 
    "OpenRouterRateLimitError",
    "OpenRouterAPIError"
]