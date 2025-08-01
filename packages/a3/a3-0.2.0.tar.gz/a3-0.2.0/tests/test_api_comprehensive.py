"""
Comprehensive unit tests for the main A3 API class.

This module provides complete test coverage for the primary user interface
of the AI Project Builder, including error handling, configuration, and workflow orchestration.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from a3.core.api import (
    A3, A3Error, ConfigurationError, ProjectStateError, 
    OperationError, ValidationError
)
from a3.core.models import (
    ProjectPlan, ProjectStatus, ProjectProgress, ProjectPhase,
    SpecificationSet, ImplementationResult, IntegrationResult,
    ProjectResult, Module, FunctionSpec, DependencyGraph
)


class TestA3Initialization:
    """Test A3 class initialization and basic setup."""
    
    def test_initialization_default_path(self):
        """Test A3 initialization with default project path."""
        api = A3()
        
        assert api.project_path == Path(".").resolve()
        assert api._api_key is None
        assert api._project_manager is None
        assert api._state_manager is not None
    
    def test_initialization_custom_path(self):
        """Test A3 initialization with custom project path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            
            assert api.project_path == Path(temp_dir).resolve()
            assert api._state_manager is not None
    
    def test_initialization_invalid_path(self):
        """Test A3 initialization with invalid path."""
        # Should raise error when trying to initialize state manager
        with pytest.raises(Exception):  # FileNotFoundError or similar
            A3("/nonexistent/path/that/should/not/exist")


class TestA3APIKeyManagement:
    """Test API key setting and validation."""
    
    @pytest.fixture
    def api(self):
        """Create A3 instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield A3(temp_dir)
    
    @patch('a3.clients.openrouter.OpenRouterClient.validate_api_key')
    def test_set_api_key_success(self, mock_validate, api):
        """Test successful API key setting."""
        mock_validate.return_value = True
        
        api.set_api_key("test-api-key-123")
        
        assert api._api_key == "test-api-key-123"
        mock_validate.assert_called_once()
    
    def test_set_api_key_empty(self, api):
        """Test setting empty API key raises error."""
        with pytest.raises(ConfigurationError) as exc_info:
            api.set_api_key("")
        
        assert "API key cannot be empty" in str(exc_info.value)
        assert "OpenRouter API key" in exc_info.value.suggestion
    
    def test_set_api_key_whitespace_only(self, api):
        """Test setting whitespace-only API key raises error."""
        with pytest.raises(ConfigurationError):
            api.set_api_key("   ")
    
    @patch('a3.clients.openrouter.OpenRouterClient.validate_api_key')
    def test_set_api_key_invalid(self, mock_validate, api):
        """Test setting invalid API key raises error."""
        mock_validate.return_value = False
        
        with pytest.raises(ConfigurationError) as exc_info:
            api.set_api_key("invalid-key")
        
        assert "Invalid API key provided" in str(exc_info.value)
        assert "verify it at https://openrouter.ai/keys" in exc_info.value.suggestion
    
    @patch('a3.clients.openrouter.OpenRouterClient')
    def test_set_api_key_validation_exception(self, mock_client_class, api):
        """Test API key validation with network exception."""
        mock_client = Mock()
        mock_client.validate_api_key.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ConfigurationError) as exc_info:
            api.set_api_key("test-key")
        
        assert "Failed to validate API key" in str(exc_info.value)
        assert "internet connection" in exc_info.value.suggestion


class TestA3Planning:
    """Test project planning functionality."""
    
    @pytest.fixture
    def api_with_key(self):
        """Create A3 instance with API key set."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            with patch('a3.clients.openrouter.OpenRouterClient.validate_api_key', return_value=True):
                api.set_api_key("test-key")
            yield api
    
    def test_plan_without_api_key(self):
        """Test planning without API key raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            
            with pytest.raises(ConfigurationError) as exc_info:
                api.plan("Build a web scraper")
            
            assert "API key must be set" in str(exc_info.value)
    
    def test_plan_empty_objective(self, api_with_key):
        """Test planning with empty objective raises error."""
        with pytest.raises(ValidationError) as exc_info:
            api_with_key.plan("")
        
        assert "Project objective cannot be empty" in str(exc_info.value)
    
    def test_plan_short_objective(self, api_with_key):
        """Test planning with too short objective raises error."""
        with pytest.raises(ValidationError) as exc_info:
            api_with_key.plan("short")
        
        assert "Project objective is too short" in str(exc_info.value)
    
    @patch('a3.managers.project.ProjectManager')
    def test_plan_success(self, mock_pm_class, api_with_key):
        """Test successful project planning."""
        # Mock project manager
        mock_pm = Mock()
        mock_pm.execute_pipeline.return_value = ProjectResult(
            success=True,
            message="Planning completed"
        )
        mock_pm_class.return_value = mock_pm
        
        # Mock state manager to return a plan
        sample_plan = ProjectPlan(
            objective="Build a web scraper",
            modules=[],
            dependency_graph=DependencyGraph(nodes=[], edges=[]),
            estimated_functions=5
        )
        api_with_key._state_manager.load_project_plan = Mock(return_value=sample_plan)
        
        result = api_with_key.plan("Build a web scraper for news articles")
        
        assert isinstance(result, ProjectPlan)
        assert result.objective == "Build a web scraper"
        mock_pm.execute_pipeline.assert_called_once()
    
    def test_plan_existing_project(self, api_with_key):
        """Test planning when project already exists."""
        # Mock status to show active project
        mock_status = ProjectStatus(
            is_active=True,
            progress=None,
            errors=[],
            can_resume=True
        )
        api_with_key._state_manager.get_project_status = Mock(return_value=mock_status)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_key.plan("New objective")
        
        assert "project already exists" in str(exc_info.value)
        assert "resume()" in exc_info.value.suggestion
    
    @patch('a3.managers.project.ProjectManager')
    def test_plan_engine_failure(self, mock_pm_class, api_with_key):
        """Test planning when engine fails."""
        mock_pm = Mock()
        mock_pm.execute_pipeline.side_effect = Exception("Planning engine error")
        mock_pm_class.return_value = mock_pm
        
        with pytest.raises(OperationError) as exc_info:
            api_with_key.plan("Build something")
        
        assert "Planning engine failed" in str(exc_info.value)
        assert "API rate limits" in exc_info.value.suggestion
    
    @patch('a3.managers.project.ProjectManager')
    def test_plan_pipeline_failure(self, mock_pm_class, api_with_key):
        """Test planning when pipeline returns failure."""
        mock_pm = Mock()
        mock_pm.execute_pipeline.return_value = ProjectResult(
            success=False,
            message="Planning failed",
            errors=["Specific error"]
        )
        mock_pm_class.return_value = mock_pm
        
        with pytest.raises(OperationError) as exc_info:
            api_with_key.plan("Build something")
        
        assert "Planning failed" in str(exc_info.value)
        assert "Specific error" in str(exc_info.value)
    
    def test_plan_invalid_project_path(self, api_with_key):
        """Test planning with invalid project path."""
        with pytest.raises(ValidationError) as exc_info:
            api_with_key.plan("Build something", "/nonexistent/parent/path")
        
        assert "Parent directory does not exist" in str(exc_info.value)


class TestA3SpecificationGeneration:
    """Test specification generation functionality."""
    
    @pytest.fixture
    def api_with_plan(self):
        """Create A3 instance with existing project plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            with patch('a3.clients.openrouter.OpenRouterClient.validate_api_key', return_value=True):
                api.set_api_key("test-key")
            
            # Mock existing plan
            sample_plan = ProjectPlan(
                objective="Test project",
                modules=[
                    Module(
                        name="test_module",
                        description="Test module",
                        file_path="test.py",
                        functions=[
                            FunctionSpec(
                                name="test_func",
                                module="test_module",
                                docstring="Test function"
                            )
                        ]
                    )
                ]
            )
            api._state_manager.load_project_plan = Mock(return_value=sample_plan)
            yield api
    
    def test_generate_specs_no_plan(self, api_with_plan):
        """Test spec generation without existing plan."""
        api_with_plan._state_manager.load_project_plan = Mock(return_value=None)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_plan.generate_specs()
        
        assert "No project plan found" in str(exc_info.value)
        assert "Run plan() first" in str(exc_info.value)
    
    @patch('a3.engines.specification.SpecificationGenerator')
    def test_generate_specs_success(self, mock_spec_gen_class, api_with_plan):
        """Test successful specification generation."""
        # Mock specification generator
        mock_spec_gen = Mock()
        mock_specs = SpecificationSet(
            functions=[
                FunctionSpec(
                    name="test_func",
                    module="test_module",
                    docstring="Enhanced test function"
                )
            ],
            modules=[]
        )
        mock_spec_gen.generate_specifications.return_value = mock_specs
        mock_spec_gen_class.return_value = mock_spec_gen
        
        result = api_with_plan.generate_specs()
        
        assert isinstance(result, SpecificationSet)
        assert len(result.functions) == 1
        mock_spec_gen.generate_specifications.assert_called_once()
    
    def test_generate_specs_already_generated(self, api_with_plan):
        """Test spec generation when specs already exist."""
        # Mock progress showing specs already generated
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.SPECIFICATION,
            completed_phases=[ProjectPhase.PLANNING],
            total_functions=1,
            implemented_functions=0
        )
        api_with_plan._state_manager.get_current_progress = Mock(return_value=mock_progress)
        
        result = api_with_plan.generate_specs()
        
        assert isinstance(result, SpecificationSet)


class TestA3Implementation:
    """Test implementation functionality."""
    
    @pytest.fixture
    def api_with_specs(self):
        """Create A3 instance with existing specifications."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            with patch('a3.clients.openrouter.OpenRouterClient.validate_api_key', return_value=True):
                api.set_api_key("test-key")
            
            # Mock existing plan and progress
            sample_plan = ProjectPlan(
                objective="Test project",
                modules=[
                    Module(
                        name="test_module",
                        description="Test module",
                        file_path="test.py",
                        functions=[
                            FunctionSpec(
                                name="test_func",
                                module="test_module",
                                docstring="Test function"
                            )
                        ]
                    )
                ]
            )
            mock_progress = ProjectProgress(
                current_phase=ProjectPhase.SPECIFICATION,
                completed_phases=[ProjectPhase.PLANNING],
                total_functions=1,
                implemented_functions=0
            )
            
            api._state_manager.load_project_plan = Mock(return_value=sample_plan)
            api._state_manager.get_current_progress = Mock(return_value=mock_progress)
            yield api
    
    def test_implement_no_plan(self, api_with_specs):
        """Test implementation without existing plan."""
        api_with_specs._state_manager.load_project_plan = Mock(return_value=None)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_specs.implement()
        
        assert "No project plan found" in str(exc_info.value)
    
    def test_implement_no_specs(self, api_with_specs):
        """Test implementation without specifications."""
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[],
            total_functions=1,
            implemented_functions=0
        )
        api_with_specs._state_manager.get_current_progress = Mock(return_value=mock_progress)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_specs.implement()
        
        assert "No specifications found" in str(exc_info.value)
        assert "generate_specs()" in str(exc_info.value)
    
    @patch('a3.engines.code_generator.CodeGenerator')
    def test_implement_success(self, mock_code_gen_class, api_with_specs):
        """Test successful implementation."""
        # Mock code generator
        mock_code_gen = Mock()
        mock_result = ImplementationResult(
            implemented_functions=["test_module.test_func"],
            failed_functions=[],
            success_rate=1.0
        )
        mock_code_gen.implement_all.return_value = mock_result
        mock_code_gen_class.return_value = mock_code_gen
        
        result = api_with_specs.implement()
        
        assert isinstance(result, ImplementationResult)
        assert result.success_rate == 1.0
        mock_code_gen.implement_all.assert_called_once()
    
    def test_implement_already_completed(self, api_with_specs):
        """Test implementation when already completed."""
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.COMPLETED,
            completed_phases=[ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION, ProjectPhase.IMPLEMENTATION],
            total_functions=1,
            implemented_functions=1,
            failed_functions=[]
        )
        api_with_specs._state_manager.get_current_progress = Mock(return_value=mock_progress)
        
        result = api_with_specs.implement()
        
        assert isinstance(result, ImplementationResult)
        assert result.success_rate == 1.0


class TestA3Integration:
    """Test integration functionality."""
    
    @pytest.fixture
    def api_with_implementation(self):
        """Create A3 instance with existing implementation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            with patch('a3.clients.openrouter.OpenRouterClient.validate_api_key', return_value=True):
                api.set_api_key("test-key")
            
            # Mock existing plan and progress
            sample_plan = ProjectPlan(
                objective="Test project",
                modules=[
                    Module(
                        name="test_module",
                        description="Test module",
                        file_path="test.py",
                        functions=[
                            FunctionSpec(
                                name="test_func",
                                module="test_module",
                                docstring="Test function"
                            )
                        ]
                    )
                ]
            )
            mock_progress = ProjectProgress(
                current_phase=ProjectPhase.IMPLEMENTATION,
                completed_phases=[ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION],
                total_functions=1,
                implemented_functions=1
            )
            
            api._state_manager.load_project_plan = Mock(return_value=sample_plan)
            api._state_manager.get_current_progress = Mock(return_value=mock_progress)
            yield api
    
    def test_integrate_no_plan(self, api_with_implementation):
        """Test integration without existing plan."""
        api_with_implementation._state_manager.load_project_plan = Mock(return_value=None)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_implementation.integrate()
        
        assert "No project plan found" in str(exc_info.value)
    
    def test_integrate_no_implementation(self, api_with_implementation):
        """Test integration without implementation."""
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.SPECIFICATION,
            completed_phases=[ProjectPhase.PLANNING],
            total_functions=1,
            implemented_functions=0
        )
        api_with_implementation._state_manager.get_current_progress = Mock(return_value=mock_progress)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_implementation.integrate()
        
        assert "No implementations found" in str(exc_info.value)
        assert "implement()" in str(exc_info.value)
    
    @patch('a3.engines.integration.IntegrationEngine')
    def test_integrate_success(self, mock_integration_class, api_with_implementation):
        """Test successful integration."""
        # Mock integration engine
        mock_integration = Mock()
        mock_result = IntegrationResult(
            integrated_modules=["test_module"],
            import_errors=[],
            success=True
        )
        mock_integration.integrate_modules.return_value = mock_result
        mock_integration_class.return_value = mock_integration
        
        result = api_with_implementation.integrate()
        
        assert isinstance(result, IntegrationResult)
        assert result.success is True
        mock_integration.integrate_modules.assert_called_once()
    
    def test_integrate_already_completed(self, api_with_implementation):
        """Test integration when already completed."""
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.COMPLETED,
            completed_phases=[ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION, ProjectPhase.IMPLEMENTATION],
            total_functions=1,
            implemented_functions=1
        )
        api_with_implementation._state_manager.get_current_progress = Mock(return_value=mock_progress)
        
        result = api_with_implementation.integrate()
        
        assert isinstance(result, IntegrationResult)
        assert result.success is True


class TestA3Status:
    """Test status functionality."""
    
    def test_status_nonexistent_directory(self):
        """Test status with nonexistent directory."""
        api = A3()
        
        status = api.status("/nonexistent/directory")
        
        assert not status.is_active
        assert not status.can_resume
        assert len(status.errors) > 0
        assert "does not exist" in status.errors[0]
    
    def test_status_existing_project(self):
        """Test status with existing project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            
            # Mock state manager to return active status
            mock_status = ProjectStatus(
                is_active=True,
                progress=ProjectProgress(
                    current_phase=ProjectPhase.PLANNING,
                    completed_phases=[],
                    total_functions=5,
                    implemented_functions=0
                ),
                errors=[],
                can_resume=True
            )
            api._state_manager.get_project_status = Mock(return_value=mock_status)
            
            status = api.status()
            
            assert status.is_active
            assert status.can_resume
    
    def test_status_error_handling(self):
        """Test status with error in state manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            
            # Mock state manager to raise exception
            api._state_manager.get_project_status = Mock(side_effect=Exception("State error"))
            
            status = api.status()
            
            assert not status.is_active
            assert not status.can_resume
            assert len(status.errors) > 0


class TestA3Resume:
    """Test resume functionality."""
    
    @pytest.fixture
    def api_with_resumable_project(self):
        """Create A3 instance with resumable project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            with patch('a3.clients.openrouter.OpenRouterClient.validate_api_key', return_value=True):
                api.set_api_key("test-key")
            
            # Mock resumable state
            mock_status = ProjectStatus(
                is_active=True,
                progress=ProjectProgress(
                    current_phase=ProjectPhase.SPECIFICATION,
                    completed_phases=[ProjectPhase.PLANNING],
                    total_functions=5,
                    implemented_functions=0
                ),
                errors=[],
                can_resume=True
            )
            sample_plan = ProjectPlan(
                objective="Test project",
                modules=[]
            )
            
            api._state_manager.get_project_status = Mock(return_value=mock_status)
            api._state_manager.load_project_plan = Mock(return_value=sample_plan)
            yield api
    
    def test_resume_no_resumable_project(self):
        """Test resume without resumable project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = A3(temp_dir)
            with patch('a3.clients.openrouter.OpenRouterClient.validate_api_key', return_value=True):
                api.set_api_key("test-key")
            
            mock_status = ProjectStatus(
                is_active=False,
                progress=None,
                errors=[],
                can_resume=False
            )
            api._state_manager.get_project_status = Mock(return_value=mock_status)
            
            with pytest.raises(ProjectStateError) as exc_info:
                api.resume()
            
            assert "No resumable project found" in str(exc_info.value)
    
    def test_resume_corrupted_state(self, api_with_resumable_project):
        """Test resume with corrupted project state."""
        api_with_resumable_project._state_manager.load_project_plan = Mock(return_value=None)
        
        with pytest.raises(ProjectStateError) as exc_info:
            api_with_resumable_project.resume()
        
        assert "Project state is corrupted" in str(exc_info.value)
    
    @patch('a3.managers.project.ProjectManager')
    def test_resume_success(self, mock_pm_class, api_with_resumable_project):
        """Test successful project resumption."""
        mock_pm = Mock()
        mock_pm.resume_pipeline.return_value = ProjectResult(
            success=True,
            message="Project resumed successfully"
        )
        mock_pm_class.return_value = mock_pm
        
        result = api_with_resumable_project.resume()
        
        assert isinstance(result, ProjectResult)
        assert result.success is True
        mock_pm.resume_pipeline.assert_called_once()
    
    @patch('a3.managers.project.ProjectManager')
    def test_resume_failure(self, mock_pm_class, api_with_resumable_project):
        """Test failed project resumption."""
        mock_pm = Mock()
        mock_pm.resume_pipeline.return_value = ProjectResult(
            success=False,
            message="Resume failed",
            errors=["Specific error"]
        )
        mock_pm_class.return_value = mock_pm
        
        result = api_with_resumable_project.resume()
        
        assert isinstance(result, ProjectResult)
        assert result.success is False


class TestA3ErrorHandling:
    """Test error handling and user-friendly messages."""
    
    def test_a3_error_user_message(self):
        """Test A3Error user message formatting."""
        error = A3Error(
            message="Something went wrong",
            suggestion="Try this solution",
            error_code="TEST_ERROR"
        )
        
        user_msg = error.get_user_message()
        
        assert "Error: Something went wrong" in user_msg
        assert "Suggestion: Try this solution" in user_msg
        assert "Error Code: TEST_ERROR" in user_msg
    
    def test_configuration_error_defaults(self):
        """Test ConfigurationError with default values."""
        error = ConfigurationError("Config issue")
        
        assert error.error_code == "CONFIG_ERROR"
        assert "Check your configuration" in error.suggestion
    
    def test_project_state_error_defaults(self):
        """Test ProjectStateError with default values."""
        error = ProjectStateError("State issue")
        
        assert error.error_code == "STATE_ERROR"
        assert "Check your project directory" in error.suggestion
    
    def test_operation_error_defaults(self):
        """Test OperationError with default values."""
        error = OperationError("Operation failed")
        
        assert error.error_code == "OPERATION_ERROR"
        assert "Try the operation again" in error.suggestion
    
    def test_validation_error_defaults(self):
        """Test ValidationError with default values."""
        error = ValidationError("Validation failed")
        
        assert error.error_code == "VALIDATION_ERROR"
        assert "Review the input parameters" in error.suggestion


class TestA3PrivateMethods:
    """Test private helper methods."""
    
    @pytest.fixture
    def api(self):
        """Create A3 instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield A3(temp_dir)
    
    def test_ensure_initialized_no_api_key(self, api):
        """Test _ensure_initialized without API key."""
        with pytest.raises(ConfigurationError):
            api._ensure_initialized()
    
    @patch('a3.clients.openrouter.OpenRouterClient.validate_api_key')
    def test_ensure_initialized_success(self, mock_validate, api):
        """Test successful _ensure_initialized."""
        mock_validate.return_value = True
        api.set_api_key("test-key")
        
        # Should not raise
        api._ensure_initialized()
    
    @patch('a3.clients.openrouter.OpenRouterClient.validate_api_key')
    def test_initialize_project_manager_success(self, mock_validate, api):
        """Test successful project manager initialization."""
        mock_validate.return_value = True
        api.set_api_key("test-key")
        
        with patch('a3.engines.planning.PlanningEngine') as mock_planning, \
             patch('a3.engines.specification.SpecificationGenerator') as mock_spec, \
             patch('a3.engines.code_generator.CodeGenerator') as mock_code, \
             patch('a3.engines.integration.IntegrationEngine') as mock_integration, \
             patch('a3.managers.project.ProjectManager') as mock_pm:
            
            api._initialize_project_manager()
            
            assert api._project_manager is not None
            mock_planning.assert_called_once()
            mock_spec.assert_called_once()
            mock_code.assert_called_once()
            mock_integration.assert_called_once()
            mock_pm.assert_called_once()
    
    def test_initialize_project_manager_no_api_key(self, api):
        """Test project manager initialization without API key."""
        with pytest.raises(ConfigurationError):
            api._initialize_project_manager()
    
    def test_handle_unexpected_error(self, api):
        """Test unexpected error handling."""
        test_error = Exception("Unexpected error")
        
        with pytest.raises(OperationError) as exc_info:
            api._handle_unexpected_error("test operation", test_error)
        
        assert "Unexpected error during test operation" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])