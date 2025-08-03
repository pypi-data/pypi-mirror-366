"""
Base manager classes for AI Project Builder.

This module provides abstract base classes for manager components
that orchestrate different aspects of the project generation workflow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..core.interfaces import (
    ProjectManagerInterface, StateManagerInterface,
    FileSystemManagerInterface, DependencyAnalyzerInterface
)
from ..core.models import ValidationResult, ProjectPhase


class BaseManager(ABC):
    """
    Abstract base class for all manager components.
    
    Provides common functionality for project path management
    and component coordination.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the base manager.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path).resolve()
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the manager with required dependencies."""
        self._initialized = True
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate that all prerequisites are met for operation."""
        issues = []
        warnings = []
        
        if not self._initialized:
            issues.append("Manager has not been initialized")
        
        if not self.project_path.exists():
            warnings.append(f"Project path does not exist: {self.project_path}")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    def _ensure_initialized(self) -> None:
        """Ensure the manager is properly initialized before operations."""
        if not self._initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before use")


class BaseProjectManager(BaseManager, ProjectManagerInterface):
    """Base class for project manager implementations."""
    
    def __init__(self, project_path: str, state_manager: Optional[StateManagerInterface] = None):
        """
        Initialize the project manager.
        
        Args:
            project_path: Path to the project directory
            state_manager: Manager for project state persistence
        """
        super().__init__(project_path)
        self.state_manager = state_manager
        self._current_phase = ProjectPhase.PLANNING
    
    def get_current_phase(self) -> ProjectPhase:
        """Get the current phase of project generation."""
        return self._current_phase
    
    def _set_current_phase(self, phase: ProjectPhase) -> None:
        """Set the current phase (internal use only)."""
        self._current_phase = phase
        if self.state_manager:
            self.state_manager.save_progress(phase, {"phase_started": True})


class BaseStateManager(BaseManager, StateManagerInterface):
    """Base class for state manager implementations."""
    
    def __init__(self, project_path: str):
        """
        Initialize the state manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        self.a3_dir = self.project_path / ".A3"
    
    def initialize(self) -> None:
        """Initialize the state manager and create necessary directories."""
        super().initialize()
        self.a3_dir.mkdir(exist_ok=True)
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate state manager prerequisites."""
        result = super().validate_prerequisites()
        
        if self._initialized and not self.a3_dir.exists():
            result.issues.append(f".A3 directory does not exist: {self.a3_dir}")
        
        return result


class BaseFileSystemManager(BaseManager, FileSystemManagerInterface):
    """Base class for file system manager implementations."""
    
    def __init__(self, project_path: str):
        """
        Initialize the file system manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
    
    def validate_permissions(self, path: str) -> bool:
        """Validate that we have necessary permissions for operations."""
        target_path = Path(path)
        
        # Check if we can read the parent directory
        parent = target_path.parent
        if parent.exists():
            return parent.is_dir() and parent.stat().st_mode & 0o200  # Write permission
        
        return True  # Assume we can create if parent doesn't exist


class BaseDependencyAnalyzer(BaseManager, DependencyAnalyzerInterface):
    """Base class for dependency analyzer implementations."""
    
    def __init__(self, project_path: str):
        """
        Initialize the dependency analyzer.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)


class BasePackageManager(BaseManager):
    """Base class for package manager implementations."""
    
    def __init__(self, project_path: str):
        """
        Initialize the package manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
    
    @abstractmethod
    def register_package_usage(self, package_name: str, alias: str, module: str):
        """Register package usage in a module."""
        pass
    
    @abstractmethod
    def get_standard_import_alias(self, package_name: str) -> str:
        """Get the standard import alias for a package."""
        pass
    
    @abstractmethod
    def generate_imports_for_module(self, module):
        """Generate import statements for a module."""
        pass
    
    @abstractmethod
    def update_requirements_file(self, project_path: str):
        """Update the requirements.txt file."""
        pass


class BaseDataSourceManager(BaseManager):
    """Base class for data source manager implementations."""
    
    def __init__(self, project_path: str):
        """
        Initialize the data source manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
    
    @abstractmethod
    def analyze_data_file(self, file_path):
        """Analyze a data file and extract metadata."""
        pass
    
    @abstractmethod
    def scan_project_data_sources(self, project_path: str):
        """Scan project for data source files."""
        pass