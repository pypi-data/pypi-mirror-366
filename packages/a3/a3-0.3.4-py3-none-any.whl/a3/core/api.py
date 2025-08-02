"""
Main API class for the AI Project Builder.

This module provides the primary user interface for interacting with
the AI Project Builder system.
"""

import logging
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path

from .models import (
    ProjectPlan, ProjectStatus, SpecificationSet, ImplementationResult, 
    IntegrationResult, ProjectResult, ProjectPhase, ProjectStructure,
    ProjectDocumentation, ExecutionResult, TestResult, DebugContext,
    CodeRevision, TracebackAnalysis, FunctionSpec, EnhancedDependencyGraph
)
from .interfaces import ProjectManagerInterface, StateManagerInterface
from ..managers.state import StateManager


# Custom exceptions for API errors
class A3Error(Exception):
    """Base exception for A3 API errors."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None, error_code: Optional[str] = None):
        """
        Initialize A3 error with user-friendly information.
        
        Args:
            message: Error message
            suggestion: Suggested solution for the user
            error_code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message with suggestions."""
        msg = f"Error: {self.message}"
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        if self.error_code:
            msg += f"\n\nError Code: {self.error_code}"
        return msg


class ConfigurationError(A3Error):
    """Exception raised for configuration issues."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Check your configuration and try again.",
            error_code="CONFIG_ERROR"
        )


class ProjectStateError(A3Error):
    """Exception raised for project state issues."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Check your project directory and ensure previous steps completed successfully.",
            error_code="STATE_ERROR"
        )


class OperationError(A3Error):
    """Exception raised for operation failures."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Try the operation again. If the problem persists, check your API key and network connection.",
            error_code="OPERATION_ERROR"
        )


class ValidationError(A3Error):
    """Exception raised for validation failures."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Review the input parameters and ensure they meet the requirements.",
            error_code="VALIDATION_ERROR"
        )


class A3:
    """
    Main API class for AI Project Builder.
    
    This class provides the primary interface for users to interact with
    the AI Project Builder system, orchestrating project creation from
    high-level objectives to complete implementations.
    """
    
    def __init__(self, project_path: str = "."):
        """
        Initialize the A3 instance.
        
        Args:
            project_path: Path to the project directory (default: current directory)
        """
        self.project_path = Path(project_path).resolve()
        self._api_key: Optional[str] = None
        self._project_manager: Optional[ProjectManagerInterface] = None
        self._state_manager: Optional[StateManagerInterface] = None
        self._logger = logging.getLogger(__name__)
        
        # Initialize state manager immediately
        self._state_manager = StateManager(str(self.project_path))
        self._state_manager.initialize()
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for AI service authentication.
        
        Args:
            api_key: The API key for OpenRouter or other AI services
            
        Raises:
            ConfigurationError: If the API key is invalid or empty
        """
        try:
            if not api_key or not api_key.strip():
                raise ConfigurationError(
                    "API key cannot be empty",
                    "Please provide a valid OpenRouter API key. You can get one from https://openrouter.ai/"
                )
            
            self._api_key = api_key.strip()
            
            # Validate API key by creating a client and testing it
            try:
                from ..clients.openrouter import OpenRouterClient
                client = OpenRouterClient(self._api_key)
                if not client.validate_api_key():
                    raise ConfigurationError(
                        "Invalid API key provided",
                        "Please check your API key and ensure it's active. You can verify it at https://openrouter.ai/keys"
                    )
            except Exception as e:
                if isinstance(e, ConfigurationError):
                    raise
                raise ConfigurationError(
                    f"Failed to validate API key: {e}",
                    "Check your internet connection and API key. If the problem persists, the API service may be temporarily unavailable."
                ) from e
            
            self._logger.info("API key set and validated successfully")
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            self._handle_unexpected_error("setting API key", e)
    
    def plan(self, objective: str, project_path: str = ".") -> ProjectPlan:
        """
        Generate a comprehensive project plan from a high-level objective.
        
        Args:
            objective: High-level description of what the project should accomplish
            project_path: Path where the project should be created
            
        Returns:
            ProjectPlan: Complete project plan with modules and dependencies
            
        Raises:
            ConfigurationError: If API key is not set
            OperationError: If planning fails
            ValidationError: If objective is empty or invalid
        """
        try:
            # Validate input
            if not objective or not objective.strip():
                raise ValidationError(
                    "Project objective cannot be empty",
                    "Please provide a clear description of what you want to build. For example: 'A web scraper for news articles' or 'A REST API for user management'"
                )
            
            if len(objective.strip()) < 10:
                raise ValidationError(
                    "Project objective is too short",
                    "Please provide a more detailed description (at least 10 characters) to generate a meaningful project plan."
                )
            
            self._ensure_initialized()
            
            # Validate and update project path
            try:
                if project_path != ".":
                    new_path = Path(project_path).resolve()
                    if not new_path.parent.exists():
                        raise ValidationError(
                            f"Parent directory does not exist: {new_path.parent}",
                            "Create the parent directory first or choose an existing location."
                        )
                    self.project_path = new_path
                    self._state_manager = StateManager(str(self.project_path))
                    self._state_manager.initialize()
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(
                    f"Invalid project path: {e}",
                    "Ensure the path is valid and you have write permissions to the directory."
                ) from e
            
            # Check if project already exists
            existing_status = self.status(project_path)
            if existing_status.is_active:
                raise ProjectStateError(
                    "A project already exists in this directory",
                    "Use resume() to continue the existing project, or choose a different directory for a new project."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info(f"Starting project planning for objective: {objective}")
            
            # Execute only the planning phase
            try:
                result = self._project_manager._execute_planning_phase(objective)
            except Exception as e:
                raise OperationError(
                    f"Planning engine failed: {e}",
                    "This could be due to API rate limits, network issues, or an unclear objective. Try again with a more specific objective."
                ) from e
            
            if not result.success:
                error_details = f"Planning failed: {result.message}"
                if result.errors:
                    error_details += f". Details: {'; '.join(result.errors)}"
                
                suggestion = "Try rephrasing your objective more clearly, check your API key, or try again later if there are service issues."
                raise OperationError(error_details, suggestion)
            
            # Load and validate the generated plan
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise OperationError(
                    "Planning completed but no plan was saved",
                    "This indicates a system error. Try running the plan() method again."
                )
            
            self._logger.info(f"Project planning completed successfully. Generated {len(plan.modules)} modules with {plan.estimated_functions} functions.")
            return plan
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, OperationError, ValidationError, ProjectStateError)):
                raise
            self._handle_unexpected_error("planning", e)
    
    def generate_specs(self, project_path: str = ".") -> SpecificationSet:
        """
        Generate detailed function specifications from the project plan.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            SpecificationSet: Complete set of function specifications
            
        Raises:
            ProjectStateError: If no project plan exists
            OperationError: If specification generation fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project plan exists
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info("Starting specification generation")
            
            # Get current progress to determine if we need to generate specs
            progress = self._state_manager.get_current_progress()
            if progress and progress.current_phase.value in ['specification', 'implementation', 'integration', 'completed']:
                self._logger.info("Specifications already generated, loading existing specs")
                # Load existing specifications from state
                # For now, create from current plan
                specs = SpecificationSet(
                    functions=[func for module in plan.modules for func in module.functions],
                    modules=plan.modules
                )
                return specs
            
            # Generate specifications using the specification generator
            from ..clients.openrouter import OpenRouterClient
            from ..engines.specification import SpecificationGenerator
            
            client = OpenRouterClient(self._api_key)
            spec_generator = SpecificationGenerator(client)
            spec_generator.initialize()
            
            # Extract all functions from the plan
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            specs = spec_generator.generate_specifications(all_functions)
            # Add modules to specs so CodeGenerator can find file paths
            specs.modules = plan.modules
            
            # Save progress
            self._state_manager.save_progress(
                ProjectPhase.SPECIFICATION,
                {
                    'total_functions': len(specs.functions),
                    'implemented_functions': 0,
                    'failed_functions': []
                }
            )
            
            self._logger.info("Specification generation completed successfully")
            return specs
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, OperationError)):
                raise
            self._handle_unexpected_error("specification generation", e)
    
    def implement(self, project_path: str = ".") -> ImplementationResult:
        """
        Implement all functions based on their specifications.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ImplementationResult: Results of the implementation process
            
        Raises:
            ProjectStateError: If specifications don't exist
            OperationError: If implementation fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project plan and specifications exist
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            progress = self._state_manager.get_current_progress()
            if not progress or progress.current_phase == ProjectPhase.PLANNING:
                raise ProjectStateError(
                    "No specifications found. Run generate_specs() first to create function specifications."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info("Starting function implementation")
            
            # Check if implementation is already complete
            if progress.current_phase.value in ['implementation', 'integration', 'completed']:
                if progress.current_phase.value in ['integration', 'completed']:
                    self._logger.info("Implementation already completed")
                    return ImplementationResult(
                        implemented_functions=[func.name for module in plan.modules for func in module.functions],
                        failed_functions=progress.failed_functions,
                        success_rate=1.0 - (len(progress.failed_functions) / max(progress.total_functions, 1))
                    )
            
            # Generate implementations using the code generator
            from ..clients.openrouter import OpenRouterClient
            from ..engines.code_generator import CodeGenerator
            
            client = OpenRouterClient(self._api_key)
            code_generator = CodeGenerator(client, self._state_manager, str(self.project_path))
            code_generator.initialize()
            
            # Create specification set from plan
            specs = SpecificationSet(
                functions=[func for module in plan.modules for func in module.functions],
                modules=plan.modules
            )
            
            result = code_generator.implement_all(specs)
            
            # Save progress
            self._state_manager.save_progress(
                ProjectPhase.IMPLEMENTATION,
                {
                    'total_functions': len(specs.functions),
                    'implemented_functions': len(result.implemented_functions),
                    'failed_functions': result.failed_functions
                }
            )
            
            self._logger.info(f"Implementation completed. Success rate: {result.success_rate:.2%}")
            return result
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, OperationError)):
                raise
            self._handle_unexpected_error("implementation", e)
    
    def integrate(self, project_path: str = ".", generate_tests: bool = False) -> IntegrationResult:
        """
        Integrate all modules and handle imports automatically.
        
        Args:
            project_path: Path to the project directory
            generate_tests: Whether to generate unit tests during integration
            
        Returns:
            IntegrationResult: Results of the integration process
            
        Raises:
            ProjectStateError: If implementations don't exist
            OperationError: If integration fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project plan and implementations exist
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            progress = self._state_manager.get_current_progress()
            if not progress or progress.current_phase.value in ['planning', 'specification']:
                raise ProjectStateError(
                    "No implementations found. Run implement() first to generate function implementations."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info("Starting module integration")
            
            # Check if integration is already complete
            if progress.current_phase == ProjectPhase.COMPLETED:
                self._logger.info("Integration already completed")
                return IntegrationResult(
                    integrated_modules=[module.name for module in plan.modules],
                    import_errors=[],
                    success=True
                )
            
            # Perform integration using the integration engine
            from ..clients.openrouter import OpenRouterClient
            from ..engines.integration import IntegrationEngine
            from ..managers.dependency import DependencyAnalyzer
            from ..managers.filesystem import FileSystemManager
            
            client = OpenRouterClient(self._api_key)
            dependency_analyzer = DependencyAnalyzer(str(self.project_path))
            filesystem_manager = FileSystemManager(str(self.project_path))
            integration_engine = IntegrationEngine(dependency_analyzer, filesystem_manager, client, self._state_manager)
            integration_engine.initialize()
            
            result = integration_engine.integrate_modules(plan.modules, generate_tests=generate_tests)
            
            # Enhanced result reporting
            if generate_tests and result.test_result:
                if result.test_result.success:
                    self._logger.info(f"Test generation completed successfully. Generated {len(result.test_result.generated_tests)} tests.")
                else:
                    self._logger.warning(f"Test generation encountered errors: {'; '.join(result.test_result.errors)}")
            
            # Enhanced error reporting
            if result.import_errors:
                self._logger.warning(f"Integration completed with import errors: {'; '.join(result.import_errors)}")
            
            if hasattr(result, 'warnings') and result.warnings:
                for warning in result.warnings:
                    self._logger.warning(f"Integration warning: {warning}")
            
            # Save progress
            if result.success:
                progress_data = {
                    'total_functions': progress.total_functions if progress else 0,
                    'implemented_functions': progress.implemented_functions if progress else 0,
                    'failed_functions': progress.failed_functions if progress else []
                }
                
                # Add test generation info to progress if applicable
                if generate_tests and result.test_result:
                    progress_data['test_generation'] = {
                        'enabled': True,
                        'success': result.test_result.success,
                        'tests_generated': len(result.test_result.generated_tests) if result.test_result.generated_tests else 0,
                        'test_files_created': len(result.test_result.test_files_created) if result.test_result.test_files_created else 0
                    }
                
                self._state_manager.save_progress(ProjectPhase.COMPLETED, progress_data)
            else:
                # Log detailed failure information
                error_msg = "Integration failed"
                if result.import_errors:
                    error_msg += f" with import errors: {'; '.join(result.import_errors)}"
                if generate_tests and result.test_result and not result.test_result.success:
                    error_msg += f" and test generation errors: {'; '.join(result.test_result.errors)}"
                
                raise OperationError(
                    error_msg,
                    "Check the error details above and ensure all dependencies are properly installed and accessible."
                )
            
            self._logger.info(f"Integration completed successfully. Integrated {len(result.integrated_modules)} modules.")
            return result
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, OperationError)):
                raise
            self._handle_unexpected_error("integration", e)
    
    def status(self, project_path: str = ".") -> ProjectStatus:
        """
        Get the current status of the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectStatus: Current project status and progress information
        """
        try:
            # Validate and update project path
            try:
                if project_path != ".":
                    new_path = Path(project_path).resolve()
                    if not new_path.exists():
                        return ProjectStatus(
                            is_active=False,
                            progress=None,
                            errors=[f"Project directory does not exist: {new_path}"],
                            can_resume=False,
                            next_action="Create the project directory or run plan() to start a new project"
                        )
                    self.project_path = new_path
                    # Create temporary state manager for status check
                    temp_state_manager = StateManager(str(self.project_path))
                    temp_state_manager.initialize()
                    status = temp_state_manager.get_project_status()
                else:
                    # Use existing state manager if available
                    if self._state_manager:
                        status = self._state_manager.get_project_status()
                    else:
                        # Create state manager if none exists
                        self._state_manager = StateManager(str(self.project_path))
                        self._state_manager.initialize()
                        status = self._state_manager.get_project_status()
                
                # Enhance status with user-friendly information
                status = self._enhance_status_with_guidance(status)
                return status
                
            except Exception as e:
                self._logger.error(f"Error accessing project directory: {e}")
                return ProjectStatus(
                    is_active=False,
                    progress=None,
                    errors=[f"Cannot access project directory: {e}"],
                    can_resume=False,
                    next_action="Check directory permissions and ensure the path is correct"
                )
            
        except Exception as e:
            self._logger.error(f"Unexpected error getting project status: {e}")
            return ProjectStatus(
                is_active=False,
                progress=None,
                errors=[f"Status check failed: {e}"],
                can_resume=False,
                next_action="Check project directory and try again"
            )
    
    def resume(self, project_path: str = ".") -> ProjectResult:
        """
        Resume an interrupted project from the last completed stage.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectResult: Result of the resumption operation
            
        Raises:
            ProjectStateError: If no resumable project state exists
            ConfigurationError: If API key is not set
            OperationError: If resumption fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if there's a resumable project
            status = self._state_manager.get_project_status()
            if not status.can_resume:
                raise ProjectStateError(
                    "No resumable project found. Either no project exists or the project is already complete."
                )
            
            # Check if project plan exists
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "Project state is corrupted: no project plan found despite resumable status."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info("Resuming interrupted project")
            
            # Resume the pipeline
            result = self._project_manager.resume_pipeline()
            
            if result.success:
                self._logger.info("Project resumed successfully")
            else:
                self._logger.error(f"Project resumption failed: {result.message}")
            
            return result
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, ConfigurationError, OperationError)):
                raise
            self._handle_unexpected_error("project resumption", e)
    
    def analyze_project(self, project_path: str = ".", database_connection: Optional[str] = None) -> ProjectStructure:
        """
        Analyze an existing project and generate comprehensive documentation.
        
        Args:
            project_path: Path to the project directory to analyze
            database_connection: Optional PostgreSQL connection string for database analysis
            
        Returns:
            ProjectStructure: Complete analysis of the project structure including data sources and database metadata
            
        Raises:
            ValidationError: If project path is invalid or inaccessible
            OperationError: If analysis fails
        """
        try:
            # Validate project path
            project_root = Path(project_path).resolve()
            if not project_root.exists():
                raise ValidationError(
                    f"Project directory does not exist: {project_root}",
                    "Ensure the path is correct and the directory exists."
                )
            
            if not project_root.is_dir():
                raise ValidationError(
                    f"Path is not a directory: {project_root}",
                    "Provide a path to a directory, not a file."
                )
            
            self._logger.info(f"Starting project analysis for: {project_root}")
            
            # Initialize project analyzer and enhanced components
            try:
                from ..clients.openrouter import OpenRouterClient
                from ..engines.project_analyzer import ProjectAnalyzer
                from ..engines.database_analyzer import DatabaseAnalyzer
                from ..managers.dependency import DependencyAnalyzer
                from ..managers.filesystem import FileSystemManager
                from ..managers.data_source_manager import DataSourceManager
                
                # Create components (API key not required for basic analysis)
                client = None
                if self._api_key:
                    client = OpenRouterClient(self._api_key)
                
                dependency_analyzer = DependencyAnalyzer(str(project_root))
                filesystem_manager = FileSystemManager(str(project_root))
                data_source_manager = DataSourceManager(str(project_root))
                
                analyzer = ProjectAnalyzer(
                    ai_client=client,
                    dependency_analyzer=dependency_analyzer,
                    filesystem_manager=filesystem_manager
                )
                analyzer.initialize()
                
                # Initialize database analyzer if connection string provided
                database_analyzer = None
                if database_connection:
                    try:
                        database_analyzer = DatabaseAnalyzer(ai_client=client, state_manager=self._state_manager)
                        database_analyzer.initialize()
                        self._logger.info("Database analyzer initialized for PostgreSQL analysis")
                    except Exception as e:
                        self._logger.warning(f"Failed to initialize database analyzer: {e}")
                        # Continue without database analysis
                
            except Exception as e:
                raise OperationError(
                    f"Failed to initialize project analyzer: {e}",
                    "Check your installation and try again."
                ) from e
            
            # Perform enhanced project analysis
            try:
                # Basic project structure analysis
                project_structure = analyzer.scan_project_folder(str(project_root))
                
                # Enhanced data source analysis
                try:
                    self._logger.info("Scanning for data sources...")
                    data_source_analysis = data_source_manager.scan_project_data_sources(str(project_root))
                    
                    project_structure.data_source_analysis = data_source_analysis
                    
                    if data_source_analysis.unified_metadata:
                        self._logger.info(f"Found {len(data_source_analysis.unified_metadata)} data sources: "
                                        f"{', '.join([ds.file_type for ds in data_source_analysis.unified_metadata])}")
                    else:
                        self._logger.info("No data sources found in project")
                        
                except Exception as e:
                    self._logger.warning(f"Data source analysis failed: {e}")
                    # Continue without data source analysis
                
                # Enhanced database analysis
                if database_connection and database_analyzer:
                    try:
                        self._logger.info("Analyzing database schema...")
                        database_connection_obj = database_analyzer.connect_to_database(database_connection)
                        database_schema = database_analyzer.analyze_database_schema(database_connection_obj)
                        
                        # Store database metadata in project structure
                        project_structure.database_analysis = database_schema
                        
                        self._logger.info(f"Database analysis completed. Found {len(database_schema.tables)} tables.")
                        
                        # Close database connection
                        if hasattr(database_connection_obj, 'close'):
                            database_connection_obj.close()
                            
                    except Exception as e:
                        self._logger.warning(f"Database analysis failed: {e}")
                        # Continue without database analysis
                
                # Generate enhanced documentation if AI client is available
                if client:
                    try:
                        documentation = analyzer.generate_project_documentation(project_structure)
                        project_structure.documentation = documentation
                        self._logger.info("Generated AI-powered project documentation")
                    except Exception as e:
                        self._logger.warning(f"Failed to generate AI documentation: {e}")
                        # Continue without AI documentation
                
                # Log comprehensive analysis results
                analysis_summary = f"Project analysis completed. Found {len(project_structure.source_files)} source files"
                if project_structure.data_source_analysis and project_structure.data_source_analysis.unified_metadata:
                    analysis_summary += f", {len(project_structure.data_source_analysis.unified_metadata)} data sources"
                if project_structure.database_analysis and project_structure.database_analysis.tables:
                    analysis_summary += f", database with {len(project_structure.database_analysis.tables)} tables"
                analysis_summary += "."
                
                self._logger.info(analysis_summary)
                return project_structure
                
            except Exception as e:
                raise OperationError(
                    f"Project analysis failed: {e}",
                    "Ensure the project directory contains valid Python files and you have read permissions."
                ) from e
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("project analysis", e)
    
    def analyze_dependencies(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Analyze project dependencies at both module and function level.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary with comprehensive dependency analysis
            
        Raises:
            ValidationError: If project path is invalid
            OperationError: If analysis fails
        """
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Load project plan
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ValidationError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Initialize dependency analyzer
            from ..managers.dependency import DependencyAnalyzer
            dependency_analyzer = DependencyAnalyzer(str(self.project_path))
            
            # Get implementation strategy
            strategy = dependency_analyzer.get_implementation_strategy(plan.modules)
            
            return strategy
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("dependency analysis", e)
    
    def get_implementation_strategy(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Get optimal implementation strategy based on enhanced dependency analysis.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary with implementation strategy details
            
        Raises:
            ValidationError: If project path is invalid
            OperationError: If analysis fails
        """
        try:
            # This is essentially the same as analyze_dependencies but with a clearer name
            return self.analyze_dependencies(project_path)
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("implementation strategy analysis", e)
    
    def get_enhanced_dependency_graph(self, project_path: str = ".") -> EnhancedDependencyGraph:
        """
        Get the enhanced dependency graph for the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            EnhancedDependencyGraph with function-level dependencies
            
        Raises:
            ValidationError: If project path is invalid
            OperationError: If analysis fails
        """
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Load project plan
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ValidationError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Return enhanced dependency graph if available
            if plan.enhanced_dependency_graph:
                return plan.enhanced_dependency_graph
            
            # Create enhanced dependency graph if not available
            from ..managers.dependency import DependencyAnalyzer
            dependency_analyzer = DependencyAnalyzer(str(self.project_path))
            enhanced_graph = dependency_analyzer.build_enhanced_dependency_graph(plan.modules)
            
            # Update the plan with the enhanced graph
            plan.enhanced_dependency_graph = enhanced_graph
            self._state_manager.save_project_plan(plan)
            
            return enhanced_graph
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("enhanced dependency graph retrieval", e)
    
    def debug_and_revise(self, error: Exception, function_spec: FunctionSpec, 
                        module_path: str, max_iterations: int = 3) -> List[CodeRevision]:
        """
        Debug a failed function implementation and generate revision suggestions.
        
        Args:
            error: The exception that occurred during execution
            function_spec: Specification of the function that failed
            module_path: Path to the module containing the function
            max_iterations: Maximum number of revision iterations
            
        Returns:
            List[CodeRevision]: List of code revision suggestions
            
        Raises:
            ConfigurationError: If API key is not set
            ValidationError: If inputs are invalid
            OperationError: If debugging fails
        """
        self._ensure_initialized()
        
        try:
            # Validate inputs
            if not isinstance(error, Exception):
                raise ValidationError(
                    "Error parameter must be an Exception instance",
                    "Pass the actual exception object that was caught."
                )
            
            if not function_spec or not function_spec.name:
                raise ValidationError(
                    "Function specification is required and must have a name",
                    "Provide a valid FunctionSpec object with at least the function name."
                )
            
            module_path_obj = Path(module_path)
            if not module_path_obj.exists():
                raise ValidationError(
                    f"Module file does not exist: {module_path}",
                    "Ensure the module file exists and the path is correct."
                )
            
            if max_iterations < 1 or max_iterations > 10:
                raise ValidationError(
                    "Max iterations must be between 1 and 10",
                    "Choose a reasonable number of revision attempts."
                )
            
            self._logger.info(f"Starting debug analysis for function: {function_spec.name}")
            
            # Initialize debug analyzer
            try:
                from ..clients.openrouter import OpenRouterClient
                from ..engines.debug_analyzer import DebugAnalyzer
                
                client = OpenRouterClient(self._api_key)
                debug_analyzer = DebugAnalyzer(
                    ai_client=client,
                    project_path=str(self.project_path)
                )
                debug_analyzer.initialize()
                
            except Exception as e:
                raise OperationError(
                    f"Failed to initialize debug analyzer: {e}",
                    "Check your API key and network connection."
                ) from e
            
            # Perform debug analysis and revision
            try:
                revisions = debug_analyzer.debug_and_revise_loop(
                    error=error,
                    function_spec=function_spec,
                    module_path=module_path,
                    max_iterations=max_iterations
                )
                
                self._logger.info(f"Debug analysis completed. Generated {len(revisions)} revision suggestions.")
                return revisions
                
            except Exception as e:
                raise OperationError(
                    f"Debug analysis failed: {e}",
                    "The error may be too complex to analyze automatically. Try simplifying the function or checking the error manually."
                ) from e
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("debug and revision", e)
    
    def execute_and_test(self, function_spec: FunctionSpec, module_path: Optional[str] = None, 
                        test_files: Optional[List[str]] = None) -> Tuple[ExecutionResult, Optional[TestResult]]:
        """
        Execute a function implementation and run associated tests.
        
        Args:
            function_spec: Specification of the function to execute
            module_path: Optional path to the module containing the function (inferred if not provided)
            test_files: Optional list of test files to run
            
        Returns:
            Tuple[ExecutionResult, Optional[TestResult]]: Execution and test results
            
        Raises:
            ValidationError: If inputs are invalid
            OperationError: If execution fails
        """
        try:
            # Validate inputs
            if not function_spec or not function_spec.name:
                raise ValidationError(
                    "Function specification is required and must have a name",
                    "Provide a valid FunctionSpec object with at least the function name."
                )
            
            # Infer module path if not provided
            if module_path is None:
                module_path = self._infer_module_path(function_spec)
                if module_path is None:
                    raise ValidationError(
                        f"Could not infer module path for function {function_spec.name} in module {function_spec.module}",
                        "Either provide module_path explicitly or ensure the project has been properly implemented."
                    )
            
            module_path_obj = Path(module_path)
            if not module_path_obj.exists():
                raise ValidationError(
                    f"Module file does not exist: {module_path}",
                    "Ensure the module file exists and the path is correct."
                )
            
            # Validate test files if provided
            if test_files:
                for test_file in test_files:
                    test_path = Path(test_file)
                    if not test_path.exists():
                        raise ValidationError(
                            f"Test file does not exist: {test_file}",
                            "Ensure all test files exist and paths are correct."
                        )
            
            self._logger.info(f"Starting execution and testing for function: {function_spec.name}")
            
            # Initialize code executor
            try:
                from ..engines.code_executor import CodeExecutor
                from ..managers.filesystem import FileSystemManager
                
                filesystem_manager = FileSystemManager(str(self.project_path))
                code_executor = CodeExecutor(
                    project_path=str(self.project_path),
                    file_manager=filesystem_manager
                )
                code_executor.initialize()
                
            except Exception as e:
                raise OperationError(
                    f"Failed to initialize code executor: {e}",
                    "Check your project setup and try again."
                ) from e
            
            # Execute the function
            try:
                execution_result = code_executor.execute_function(function_spec, module_path)
                self._logger.info(f"Function execution completed. Success: {execution_result.success}")
                
            except Exception as e:
                # Create failed execution result
                execution_result = ExecutionResult(
                    success=False,
                    output=None,
                    error=e,
                    execution_time=0.0,
                    memory_usage=None
                )
                self._logger.warning(f"Function execution failed: {e}")
            
            # Run tests if provided
            test_result = None
            if test_files:
                try:
                    test_result = code_executor.run_tests(test_files)
                    self._logger.info(f"Test execution completed. Passed: {test_result.passed_tests}/{test_result.total_tests}")
                    
                except Exception as e:
                    self._logger.warning(f"Test execution failed: {e}")
                    # Create failed test result
                    from ..core.models import TestResult, TestDetail
                    test_result = TestResult(
                        total_tests=0,
                        passed_tests=0,
                        failed_tests=0,
                        test_details=[],
                        coverage_report=None
                    )
            
            return execution_result, test_result
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("execution and testing", e)
    
    def _ensure_initialized(self) -> None:
        """Ensure that all required components are initialized."""
        if not self._api_key:
            raise ConfigurationError("API key must be set before performing operations. Call set_api_key() first.")
        
        if not self._state_manager:
            self._state_manager = StateManager(str(self.project_path))
            self._state_manager.initialize()
    
    def _initialize_project_manager(self) -> None:
        """Initialize the project manager with all required components."""
        if not self._api_key:
            raise ConfigurationError("API key must be set before initializing project manager")
        
        if not self._state_manager:
            self._state_manager = StateManager(str(self.project_path))
            self._state_manager.initialize()
        
        try:
            # Import components lazily to avoid circular imports
            from ..clients.openrouter import OpenRouterClient
            from ..engines.planning import PlanningEngine
            from ..engines.specification import SpecificationGenerator
            from ..engines.code_generator import CodeGenerator
            from ..engines.integration import IntegrationEngine
            from ..managers.project import ProjectManager
            
            # Create OpenRouter client
            client = OpenRouterClient(self._api_key)
            
            # Create all engine components
            planning_engine = PlanningEngine(client, self._state_manager, str(self.project_path))
            spec_generator = SpecificationGenerator(client, self._state_manager)
            code_generator = CodeGenerator(client, self._state_manager)
            integration_engine = IntegrationEngine(ai_client=client, state_manager=self._state_manager)
            
            # Initialize all engines
            planning_engine.initialize()
            spec_generator.initialize()
            code_generator.initialize()
            integration_engine.initialize()
            
            # Create project manager
            self._project_manager = ProjectManager(
                project_path=str(self.project_path),
                state_manager=self._state_manager,
                planning_engine=planning_engine,
                spec_generator=spec_generator,
                code_generator=code_generator,
                integration_engine=integration_engine
            )
            
            self._logger.info("Project manager initialized successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize project manager: {e}") from e
    
    def _handle_unexpected_error(self, operation: str, error: Exception) -> None:
        """
        Handle unexpected errors with user-friendly messages.
        
        Args:
            operation: The operation that failed
            error: The exception that occurred
            
        Raises:
            OperationError: Always raises with user-friendly message
        """
        self._logger.error(f"Unexpected error during {operation}: {error}")
        
        # Provide specific guidance based on error type
        if "network" in str(error).lower() or "connection" in str(error).lower():
            suggestion = "Check your internet connection and try again."
        elif "permission" in str(error).lower() or "access" in str(error).lower():
            suggestion = "Check file permissions and ensure you have write access to the project directory."
        elif "api" in str(error).lower() or "key" in str(error).lower():
            suggestion = "Verify your API key is correct and has sufficient credits."
        elif "timeout" in str(error).lower():
            suggestion = "The operation timed out. Try again or check your network connection."
        elif "analysis" in str(error).lower() or "scan" in str(error).lower():
            suggestion = "The project analysis failed. Ensure the project contains valid Python files and you have read permissions."
        elif "debug" in str(error).lower() or "revision" in str(error).lower():
            suggestion = "The debug analysis failed. The error may be too complex to analyze automatically."
        elif "execution" in str(error).lower() or "test" in str(error).lower():
            suggestion = "Code execution or testing failed. Check the function implementation and test files."
        else:
            suggestion = "This is an unexpected error. Please check the logs for more details and try again."
        
        raise OperationError(
            f"Unexpected error during {operation}: {error}",
            suggestion
        ) from error
    
    def _infer_module_path(self, function_spec: FunctionSpec) -> Optional[str]:
        """
        Infer the module file path from function specification.
        
        Args:
            function_spec: Function specification containing module information
            
        Returns:
            Inferred module path or None if not found
        """
        try:
            # Try to load project plan to get module information
            plan = self._state_manager.load_project_plan() if self._state_manager else None
            
            if plan:
                # Find the module in the plan
                for module in plan.modules:
                    if module.name == function_spec.module:
                        module_path = Path(module.file_path)
                        if not module_path.is_absolute():
                            module_path = self.project_path / module_path
                        if module_path.exists():
                            return str(module_path)
            
            # Fallback: construct path from module name
            if '.' in function_spec.module:
                # Convert dotted module name to path: 'parsers.html_parser' -> 'parsers/html_parser.py'
                module_file_path = function_spec.module.replace('.', '/') + '.py'
            else:
                module_file_path = f"{function_spec.module}.py"
            
            # Try relative to project path
            candidate_path = self.project_path / module_file_path
            if candidate_path.exists():
                return str(candidate_path)
            
            # Try in current directory
            candidate_path = Path(module_file_path)
            if candidate_path.exists():
                return str(candidate_path)
            
            return None
            
        except Exception:
            return None
    
    def _enhance_status_with_guidance(self, status: ProjectStatus) -> ProjectStatus:
        """
        Enhance project status with user-friendly guidance.
        
        Args:
            status: Original project status
            
        Returns:
            ProjectStatus: Enhanced status with guidance
        """
        if not status.progress:
            status.next_action = "Run plan() to start a new project"
            return status
        
        # Provide phase-specific guidance
        phase = status.progress.current_phase
        
        if phase == ProjectPhase.PLANNING:
            if status.progress.total_functions > 0:
                status.next_action = "Run generate_specs() to create function specifications"
            else:
                status.next_action = "Planning in progress or incomplete"
        
        elif phase == ProjectPhase.SPECIFICATION:
            status.next_action = "Run implement() to generate function implementations"
        
        elif phase == ProjectPhase.IMPLEMENTATION:
            if status.progress.failed_functions:
                failed_count = len(status.progress.failed_functions)
                status.next_action = f"Run integrate() to complete the project ({failed_count} functions failed)"
                if failed_count > status.progress.total_functions * 0.5:
                    status.next_action += ". Consider reviewing the objective or API key due to high failure rate."
            else:
                status.next_action = "Run integrate() to connect all modules"
        
        elif phase == ProjectPhase.INTEGRATION:
            status.next_action = "Integration in progress"
        
        elif phase == ProjectPhase.COMPLETED:
            status.next_action = "Project completed successfully! Check your project files."
        
        # Add progress information to next_action
        if status.progress.total_functions > 0:
            progress_pct = (status.progress.implemented_functions / status.progress.total_functions) * 100
            status.next_action += f" (Progress: {progress_pct:.1f}%)"
        
        return status
    
    def get_error_guidance(self, error: Exception) -> str:
        """
        Get user-friendly guidance for handling errors.
        
        Args:
            error: The exception that occurred
            
        Returns:
            str: User-friendly guidance message
        """
        if isinstance(error, A3Error):
            return error.get_user_message()
        
        # Provide guidance for common error patterns
        error_str = str(error).lower()
        
        if "api key" in error_str:
            return ("API Key Issue: Check that your API key is valid and has sufficient credits. "
                   "You can verify your key at https://openrouter.ai/keys")
        
        elif "network" in error_str or "connection" in error_str:
            return ("Network Issue: Check your internet connection and try again. "
                   "If the problem persists, the API service may be temporarily unavailable.")
        
        elif "permission" in error_str or "access" in error_str:
            return ("Permission Issue: Ensure you have write access to the project directory. "
                   "Try running with appropriate permissions or choose a different directory.")
        
        elif "not found" in error_str:
            return ("File Not Found: The required files may be missing or corrupted. "
                   "Try starting over with plan() or check your project directory.")
        
        elif "analysis" in error_str or "scan" in error_str:
            return ("Project Analysis Issue: The project structure could not be analyzed properly. "
                   "Ensure the directory contains valid Python files and you have read permissions.")
        
        elif "debug" in error_str or "revision" in error_str:
            return ("Debug Analysis Issue: The error could not be analyzed automatically. "
                   "Try simplifying the function or reviewing the error manually.")
        
        elif "execution" in error_str or "test" in error_str:
            return ("Execution/Testing Issue: The code could not be executed or tested properly. "
                   "Check the function implementation, dependencies, and test files.")
        
        else:
            return (f"Unexpected Error: {error}\n"
                   "Try the operation again. If the problem persists, check your configuration and network connection.")
    
    def print_status_report(self, project_path: str = ".") -> None:
        """
        Print a detailed, user-friendly status report.
        
        Args:
            project_path: Path to the project directory
        """
        try:
            status = self.status(project_path)
            
            print("\n" + "="*60)
            print("A3 PROJECT STATUS REPORT")
            print("="*60)
            
            if not status.is_active:
                print("Status: No active project")
                if status.errors:
                    print(f"Issues: {'; '.join(status.errors)}")
                print(f"Next Action: {status.next_action}")
                return
            
            print("Status: Active project found")
            
            if status.progress:
                progress = status.progress
                print(f"Current Phase: {progress.current_phase.value.title()}")
                print(f"Last Updated: {progress.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if progress.total_functions > 0:
                    success_rate = (progress.implemented_functions / progress.total_functions) * 100
                    print(f"Progress: {progress.implemented_functions}/{progress.total_functions} functions ({success_rate:.1f}%)")
                    
                    if progress.failed_functions:
                        print(f"Failed Functions: {len(progress.failed_functions)}")
                        if len(progress.failed_functions) <= 5:
                            print(f"  - {', '.join(progress.failed_functions)}")
                        else:
                            print(f"  - {', '.join(progress.failed_functions[:5])} and {len(progress.failed_functions)-5} more")
                
                print(f"Completed Phases: {', '.join([p.value.title() for p in progress.completed_phases])}")
            
            if status.errors:
                print(f"Current Issues: {'; '.join(status.errors)}")
            
            print(f"Next Action: {status.next_action}")
            print("="*60)
            
        except Exception as e:
            print(f"Error generating status report: {e}")
            print("Try checking your project directory and permissions.")
    
    def validate_environment(self) -> Dict[str, bool]:
        """
        Validate the environment for A3 operations.
        
        Returns:
            Dict[str, bool]: Validation results for different components
        """
        results = {
            "api_key_set": self._api_key is not None,
            "api_key_valid": False,
            "project_directory_writable": False,
            "state_manager_initialized": self._state_manager is not None,
            "project_manager_initialized": self._project_manager is not None
        }
        
        # Test API key validity
        if self._api_key:
            try:
                from ..clients.openrouter import OpenRouterClient
                client = OpenRouterClient(self._api_key)
                results["api_key_valid"] = client.validate_api_key()
            except Exception:
                results["api_key_valid"] = False
        
        # Test project directory writability
        try:
            test_file = self.project_path / ".a3_test"
            test_file.write_text("test")
            test_file.unlink()
            results["project_directory_writable"] = True
        except Exception:
            results["project_directory_writable"] = False
        
        return results
    
    def get_help_message(self, topic: Optional[str] = None) -> str:
        """
        Get help message for A3 usage.
        
        Args:
            topic: Specific topic to get help for
            
        Returns:
            str: Help message
        """
        if topic == "getting_started":
            return """
Getting Started with A3:

1. Set your API key:
   a3.set_api_key("your-openrouter-api-key")

2. Create a project plan:
   plan = a3.plan("Build a web scraper for news articles")

3. Generate specifications:
   specs = a3.generate_specs()

4. Implement the code:
   result = a3.implement()

5. Integrate modules:
   integration = a3.integrate()

6. Check status anytime:
   status = a3.status()
   a3.print_status_report()

For more help: a3.get_help_message("errors") or a3.get_help_message("troubleshooting")
"""
        
        elif topic == "errors":
            return """
Common A3 Errors and Solutions:

1. ConfigurationError:
   - Check your API key is valid
   - Ensure you have internet connection
   - Verify API key has sufficient credits

2. ProjectStateError:
   - Run operations in correct order: plan() → generate_specs() → implement() → integrate()
   - Check if project directory is corrupted
   - Use resume() for interrupted projects

3. OperationError:
   - Check network connection
   - Verify API service availability
   - Try the operation again

4. ValidationError:
   - Provide more detailed project objectives
   - Check input parameters
   - Ensure project directory is writable

Use a3.get_error_guidance(error) for specific error help.
"""
        
        elif topic == "troubleshooting":
            return """
A3 Troubleshooting Guide:

1. Project won't start:
   - Check API key: a3.validate_environment()
   - Verify directory permissions
   - Try a different project directory

2. Planning fails:
   - Make objective more specific and detailed
   - Check API key credits and validity
   - Ensure stable internet connection

3. Implementation has many failures:
   - Review generated specifications
   - Check if objective is too complex
   - Try breaking down into smaller projects

4. Integration issues:
   - Check for circular dependencies
   - Verify all implementations completed
   - Review module relationships

5. General debugging:
   - Use a3.print_status_report() for detailed status
   - Check logs for detailed error information
   - Use a3.status() to understand current state
"""
        
        else:
            return """
A3 - AI Project Builder Help

Available help topics:
- a3.get_help_message("getting_started") - Basic usage guide
- a3.get_help_message("errors") - Common errors and solutions  
- a3.get_help_message("troubleshooting") - Troubleshooting guide

Main methods:
- set_api_key(key) - Set your OpenRouter API key
- plan(objective) - Generate project plan from objective
- generate_specs() - Create function specifications
- implement() - Generate code implementations
- integrate() - Connect all modules
- status() - Get current project status
- resume() - Resume interrupted project
- print_status_report() - Detailed status display

Enhanced capabilities:
- analyze_project(path) - Analyze existing project structure
- debug_and_revise(error, func_spec, module_path) - Debug failed implementations
- execute_and_test(func_spec, module_path, test_files) - Execute and test code

Utility methods:
- validate_environment() - Check system readiness
- get_error_guidance(error) - Get help for specific errors

For detailed documentation, visit: https://github.com/your-repo/a3
"""