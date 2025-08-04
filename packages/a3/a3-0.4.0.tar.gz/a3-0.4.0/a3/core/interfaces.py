"""
Base interfaces and abstract classes for AI Project Builder components.

This module defines the contracts that all major components must implement,
ensuring consistency and enabling dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from .models import (
    ProjectPlan, ProjectStatus, ProjectProgress, ProjectResult,
    SpecificationSet, ImplementationResult, IntegrationResult,
    ValidationResult, Module, FunctionSpec, ProjectPhase,
    ExecutionResult, TestResult, ImportValidationResult, VerificationResult,
    TracebackAnalysis, FunctionInspection, ParsedDocstring, DebugContext, CodeRevision,
    ProjectStructure, ProjectDocumentation, CodePatterns, ModificationPlan, ModificationResult
)


class BaseEngine(ABC):
    """Base interface for all engine components."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the engine with required dependencies."""
        pass
    
    @abstractmethod
    def validate_prerequisites(self) -> ValidationResult:
        """Validate that all prerequisites are met for operation."""
        pass


class PlanningEngineInterface(BaseEngine):
    """Interface for the planning engine component."""
    
    @abstractmethod
    def generate_plan(self, objective: str) -> ProjectPlan:
        """Generate a complete project plan from an objective."""
        pass
    
    @abstractmethod
    def create_module_breakdown(self, plan: ProjectPlan) -> List[Module]:
        """Break down the plan into detailed modules."""
        pass
    
    @abstractmethod
    def identify_functions(self, modules: List[Module]) -> List[FunctionSpec]:
        """Identify all functions needed across modules."""
        pass


class SpecificationGeneratorInterface(BaseEngine):
    """Interface for the specification generator component."""
    
    @abstractmethod
    def generate_specifications(self, functions: List[FunctionSpec]) -> SpecificationSet:
        """Generate detailed specifications for all functions."""
        pass
    
    @abstractmethod
    def validate_specifications(self, specs: SpecificationSet) -> ValidationResult:
        """Validate generated specifications for consistency."""
        pass


class CodeGeneratorInterface(BaseEngine):
    """Interface for the code generator component."""
    
    @abstractmethod
    def implement_function(self, spec: FunctionSpec) -> str:
        """Generate implementation code for a single function."""
        pass
    
    @abstractmethod
    def implement_all(self, specs: SpecificationSet) -> ImplementationResult:
        """Generate implementations for all functions in the specification set."""
        pass
    
    @abstractmethod
    def retry_failed_implementations(self, failed_functions: List[str]) -> ImplementationResult:
        """Retry implementation for previously failed functions."""
        pass


class IntegrationEngineInterface(BaseEngine):
    """Interface for the integration engine component."""
    
    @abstractmethod
    def generate_imports(self, modules: List[Module]) -> Dict[str, List[str]]:
        """Generate import statements for all modules."""
        pass
    
    @abstractmethod
    def integrate_modules(self, modules: List[Module]) -> IntegrationResult:
        """Integrate all modules according to dependency graph."""
        pass
    
    @abstractmethod
    def verify_integration(self, modules: List[Module]) -> ValidationResult:
        """Verify that all imports resolve correctly."""
        pass


class StateManagerInterface(ABC):
    """Interface for project state management."""
    
    @abstractmethod
    def save_project_plan(self, plan: ProjectPlan) -> None:
        """Save project plan to persistent storage."""
        pass
    
    @abstractmethod
    def load_project_plan(self) -> Optional[ProjectPlan]:
        """Load project plan from persistent storage."""
        pass
    
    @abstractmethod
    def save_progress(self, phase: ProjectPhase, data: Dict[str, Any]) -> None:
        """Save progress information for a specific phase."""
        pass
    
    @abstractmethod
    def get_current_progress(self) -> Optional[ProjectProgress]:
        """Get current project progress information."""
        pass
    
    @abstractmethod
    def create_checkpoint(self) -> str:
        """Create a checkpoint of current project state."""
        pass
    
    @abstractmethod
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore project state from a checkpoint."""
        pass
    
    @abstractmethod
    def cleanup_state(self) -> None:
        """Clean up temporary state files."""
        pass


class ProjectManagerInterface(ABC):
    """Interface for the main project orchestration manager."""
    
    @abstractmethod
    def execute_pipeline(self, objective: str) -> ProjectResult:
        """Execute the complete project generation pipeline."""
        pass
    
    @abstractmethod
    def resume_pipeline(self) -> ProjectResult:
        """Resume an interrupted project generation pipeline."""
        pass
    
    @abstractmethod
    def get_current_phase(self) -> ProjectPhase:
        """Get the current phase of project generation."""
        pass
    
    @abstractmethod
    def validate_project_state(self) -> ValidationResult:
        """Validate the current project state for consistency."""
        pass


class AIClientInterface(ABC):
    """Interface for AI service clients."""
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Generate a chat completion response."""
        pass
    
    @abstractmethod
    def generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Generate response with automatic retry logic."""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is valid and active."""
        pass
    
    @abstractmethod
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for authentication."""
        pass


class FileSystemManagerInterface(ABC):
    """Interface for file system operations."""
    
    @abstractmethod
    def create_directory(self, path: str) -> bool:
        """Create a directory with proper error handling."""
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file with atomic operations."""
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file with error handling."""
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        pass
    
    @abstractmethod
    def validate_permissions(self, path: str) -> bool:
        """Validate that we have necessary permissions for operations."""
        pass


class DependencyAnalyzerInterface(ABC):
    """Interface for dependency analysis operations."""
    
    @abstractmethod
    def analyze_dependencies(self, modules: List[Module]) -> ValidationResult:
        """Analyze module dependencies for issues."""
        pass
    
    @abstractmethod
    def detect_circular_dependencies(self, modules: List[Module]) -> List[List[str]]:
        """Detect circular dependency chains."""
        pass
    
    @abstractmethod
    def get_build_order(self, modules: List[Module]) -> List[str]:
        """Get the optimal order for building/processing modules."""
        pass
    
    @abstractmethod
    def create_dependency_graph(self, modules: List[Module]) -> 'DependencyGraph':
        """Create a DependencyGraph object from modules."""
        pass
    
    @abstractmethod
    def validate_dependency_graph(self, graph: 'DependencyGraph') -> ValidationResult:
        """Validate a dependency graph for consistency."""
        pass


class CodeExecutorInterface(BaseEngine):
    """Interface for code execution and testing operations."""
    
    @abstractmethod
    def execute_function(self, function_spec: FunctionSpec, module_path: str) -> 'ExecutionResult':
        """Execute a specific function and capture results."""
        pass
    
    @abstractmethod
    def run_tests(self, test_files: List[str]) -> 'TestResult':
        """Run test files and return aggregated results."""
        pass
    
    @abstractmethod
    def validate_imports(self, module_path: str) -> 'ImportValidationResult':
        """Validate that all imports in a module resolve correctly."""
        pass
    
    @abstractmethod
    def capture_runtime_errors(self, execution_func) -> Optional[Exception]:
        """Capture and analyze runtime errors during execution."""
        pass
    
    @abstractmethod
    def verify_implementation(self, function_spec: FunctionSpec) -> 'VerificationResult':
        """Verify that a function implementation works correctly."""
        pass


class DebugAnalyzerInterface(BaseEngine):
    """Interface for comprehensive debug analysis and code revision."""
    
    @abstractmethod
    def analyze_traceback(self, exception: Exception) -> 'TracebackAnalysis':
        """Analyze a traceback and identify root causes."""
        pass
    
    @abstractmethod
    def inspect_function(self, function: Any) -> 'FunctionInspection':
        """Inspect a function using Python's inspect module."""
        pass
    
    @abstractmethod
    def parse_docstring(self, docstring: str) -> 'ParsedDocstring':
        """Parse a docstring using docstring_parser."""
        pass
    
    @abstractmethod
    def generate_debug_context(self, error: Exception, function_spec: FunctionSpec) -> 'DebugContext':
        """Generate comprehensive debug context for AI revision."""
        pass
    
    @abstractmethod
    def suggest_code_revision(self, debug_context: 'DebugContext') -> 'CodeRevision':
        """Generate AI-powered code revision suggestions."""
        pass
    
    @abstractmethod
    def apply_revision(self, revision: 'CodeRevision', module_path: str) -> bool:
        """Apply a code revision to the actual source file."""
        pass
    
    @abstractmethod
    def verify_revision(self, revision: 'CodeRevision', function_spec: FunctionSpec) -> 'VerificationResult':
        """Verify that a code revision resolves the original issue."""
        pass
    
    @abstractmethod
    def debug_and_revise_loop(self, error: Exception, function_spec: FunctionSpec, 
                             module_path: str, max_iterations: int = 3) -> List['CodeRevision']:
        """Perform a complete debug and revision loop with multiple attempts."""
        pass
    
    @abstractmethod
    def analyze_and_fix_function(self, function_spec: FunctionSpec, module_path: str, 
                                original_error: Optional[Exception] = None) -> Dict[str, Any]:
        """Complete analysis and fixing workflow for a function."""
        pass


class ProjectAnalyzerInterface(BaseEngine):
    """Interface for analyzing and modifying existing projects."""
    
    @abstractmethod
    def scan_project_folder(self, project_path: str) -> 'ProjectStructure':
        """Scan a project folder and identify all source files."""
        pass
    
    @abstractmethod
    def generate_project_documentation(self, project_structure: 'ProjectStructure') -> 'ProjectDocumentation':
        """Generate comprehensive documentation following the same standards as its own projects."""
        pass
    
    @abstractmethod
    def build_dependency_graph(self, project_structure: 'ProjectStructure') -> 'DependencyGraph':
        """Analyze import relationships and create visual dependency maps."""
        pass
    
    @abstractmethod
    def analyze_code_patterns(self, project_structure: 'ProjectStructure') -> 'CodePatterns':
        """Analyze code patterns and conventions in the project."""
        pass
    
    @abstractmethod
    def suggest_modifications(self, user_prompt: str, project_structure: 'ProjectStructure') -> 'ModificationPlan':
        """Make targeted changes based on the analyzed project structure."""
        pass
    
    @abstractmethod
    def apply_modifications(self, modification_plan: 'ModificationPlan') -> 'ModificationResult':
        """Apply the planned modifications to the project."""
        pass
    
    @abstractmethod
    def validate_style_consistency(self, project_structure: 'ProjectStructure', 
                                  modifications: 'ModificationPlan') -> ValidationResult:
        """Validate that modifications maintain consistency with existing codebase style."""
        pass