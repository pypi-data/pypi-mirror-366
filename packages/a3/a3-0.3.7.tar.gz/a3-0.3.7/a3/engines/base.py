"""
Base engine classes for AI Project Builder.

This module provides abstract base classes that all engines inherit from,
ensuring consistent interfaces and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..core.interfaces import (
    PlanningEngineInterface, SpecificationGeneratorInterface,
    CodeGeneratorInterface, IntegrationEngineInterface,
    ProjectAnalyzerInterface, AIClientInterface, StateManagerInterface
)
from ..core.models import ValidationResult


class BaseEngine(ABC):
    """
    Abstract base class for all engine components.
    
    Provides common functionality and ensures consistent interfaces
    across all engine implementations.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        """
        Initialize the base engine.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
        """
        self.ai_client = ai_client
        self.state_manager = state_manager
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the engine with required dependencies."""
        if self.ai_client and hasattr(self.ai_client, 'validate_api_key'):
            if not self.ai_client.validate_api_key():
                raise RuntimeError("Invalid API key provided to engine")
        
        self._initialized = True
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate that all prerequisites are met for operation."""
        issues = []
        warnings = []
        
        if not self._initialized:
            issues.append("Engine has not been initialized")
        
        if self.ai_client is None:
            issues.append("AI client is required but not provided")
        
        if self.state_manager is None:
            warnings.append("State manager not provided - state will not be persisted")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    def _ensure_initialized(self) -> None:
        """Ensure the engine is properly initialized before operations."""
        if not self._initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before use")


class BasePlanningEngine(BaseEngine, PlanningEngineInterface):
    """Base class for planning engine implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)


class BaseSpecificationGenerator(BaseEngine, SpecificationGeneratorInterface):
    """Base class for specification generator implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)


class BaseCodeGenerator(BaseEngine, CodeGeneratorInterface):
    """Base class for code generator implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)


class BaseIntegrationEngine(BaseEngine, IntegrationEngineInterface):
    """Base class for integration engine implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)


class BaseProjectAnalyzer(BaseEngine):
    """Base class for project analyzer implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)


class BaseTestGenerator(BaseEngine):
    """Base class for test generator implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)
    
    @abstractmethod
    def generate_module_tests(self, module, **kwargs):
        """Generate unit tests for a module."""
        pass
    
    @abstractmethod
    def generate_integration_tests(self, modules, **kwargs):
        """Generate integration tests for multiple modules."""
        pass
    
    @abstractmethod
    def execute_generated_tests(self, test_files, **kwargs):
        """Execute generated test files."""
        pass


class BaseDatabaseAnalyzer(BaseEngine):
    """Base class for database analyzer implementations."""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        super().__init__(ai_client, state_manager)
    
    @abstractmethod
    def connect_to_database(self, connection_string, **kwargs):
        """Connect to a database."""
        pass
    
    @abstractmethod
    def analyze_database_schema(self, connection, **kwargs):
        """Analyze database schema."""
        pass
    
    @abstractmethod
    def generate_database_models(self, schema, **kwargs):
        """Generate database model classes."""
        pass