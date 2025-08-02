"""
Unit tests for the ProjectManager class.

This module tests the project manager functionality including pipeline execution,
resumption capabilities, and state validation.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from pathlib import Path

from a3.managers.project import ProjectManager, ProjectManagerError
from a3.core.models import (
    ProjectPlan, ProjectProgress, ProjectPhase, ProjectResult,
    SpecificationSet, ImplementationResult, IntegrationResult,
    ValidationResult, Module, FunctionSpec, DependencyGraph
)
from a3.core.interfaces import (
    StateManagerInterface, PlanningEngineInterface,
    SpecificationGeneratorInterface, CodeGeneratorInterface,
    IntegrationEngineInterface
)


class TestProjectManagerInitialization:
    """Test ProjectManager initialization."""
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components for ProjectManager."""
        return {
            'state_manager': Mock(spec=StateManagerInterface),
            'planning_engine': Mock(spec=PlanningEngineInterface),
            'spec_generator': Mock(spec=SpecificationGeneratorInterface),
            'code_generator': Mock(spec=CodeGeneratorInterface),
            'integration_engine': Mock(spec=IntegrationEngineInterface)
        }
    
    def test_initialization(self, mock_components):
        """Test ProjectManager initialization with all components."""
        pm = ProjectManager(
            project_path="/test/path",
            state_manager=mock_components['state_manager'],
            planning_engine=mock_components['planning_engine'],
            spec_generator=mock_components['spec_generator'],
            code_generator=mock_components['code_generator'],
            integration_engine=mock_components['integration_engine']
        )
        
        assert str(pm.project_path) == str(Path("/test/path").resolve())
        assert pm.state_manager == mock_components['state_manager']
        assert pm.planning_engine == mock_components['planning_engine']
        assert pm.spec_generator == mock_components['spec_generator']
        assert pm.code_generator == mock_components['code_generator']
        assert pm.integration_engine == mock_components['integration_engine']
    
    def test_initialization_inherits_from_base(self, mock_components):
        """Test that ProjectManager inherits from BaseProjectManager."""
        pm = ProjectManager(
            project_path="/test/path",
            state_manager=mock_components['state_manager'],
            planning_engine=mock_components['planning_engine'],
            spec_generator=mock_components['spec_generator'],
            code_generator=mock_components['code_generator'],
            integration_engine=mock_components['integration_engine']
        )
        
        # Should have base class attributes
        assert hasattr(pm, 'project_path')
        assert hasattr(pm, 'state_manager')


class TestProjectManagerPipelineExecution:
    """Test pipeline execution functionality."""
    
    @pytest.fixture
    def project_manager(self):
        """Create ProjectManager with mocked components."""
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        return ProjectManager(
            project_path="/test/path",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
    
    def test_execute_pipeline_success(self, project_manager):
        """Test successful pipeline execution."""
        # Mock planning engine to return a plan
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
            ],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1
        )
        
        project_manager.planning_engine.generate_plan.return_value = sample_plan
        
        # Mock other phases to return success
        from a3.core.models import SpecificationSet, ImplementationResult, IntegrationResult
        
        spec_set = SpecificationSet(functions=sample_plan.modules[0].functions)
        project_manager.spec_generator.generate_specifications.return_value = spec_set
        
        impl_result = ImplementationResult(
            implemented_functions=["test_func"],
            failed_functions=[],
            success_rate=1.0
        )
        project_manager.code_generator.implement_all.return_value = impl_result
        
        integration_result = IntegrationResult(
            success=True,
            integrated_modules=["test_module"],
            import_errors=[]
        )
        project_manager.integration_engine.integrate_modules.return_value = integration_result
        
        # Mock state manager to return the plan when needed
        project_manager.state_manager.load_project_plan.return_value = sample_plan
        
        # Execute pipeline
        result = project_manager.execute_pipeline("Build a test project")
        
        # Verify results
        assert isinstance(result, ProjectResult)
        assert result.success is True
        assert "Pipeline execution completed successfully" in result.message
        assert result.data['phase'] == 'completed'
        
        # Verify all phases were called
        project_manager.planning_engine.generate_plan.assert_called_once_with("Build a test project")
        project_manager.spec_generator.generate_specifications.assert_called_once()
        project_manager.code_generator.implement_all.assert_called_once()
        project_manager.integration_engine.integrate_modules.assert_called_once()
        
        # Verify state was saved for all phases
        project_manager.state_manager.save_project_plan.assert_called_once_with(sample_plan)
        assert project_manager.state_manager.save_progress.call_count >= 4  # At least 4 phases
    
    def test_execute_pipeline_planning_failure(self, project_manager):
        """Test pipeline execution with planning failure."""
        # Mock planning engine to raise exception
        project_manager.planning_engine.generate_plan.side_effect = Exception("Planning failed")
        
        # Execute pipeline
        result = project_manager.execute_pipeline("Build a test project")
        
        # Verify failure result
        assert isinstance(result, ProjectResult)
        assert result.success is False
        assert "Planning phase failed" in result.message
        assert "Planning failed" in result.message
        assert len(result.errors) == 1
        assert "Planning failed" in result.errors[0]
    
    def test_execute_pipeline_state_save_failure(self, project_manager):
        """Test pipeline execution with state save failure."""
        # Mock planning engine to return a plan
        sample_plan = ProjectPlan(
            objective="Test project",
            modules=[],
            dependency_graph=DependencyGraph(nodes=[], edges=[]),
            estimated_functions=0
        )
        project_manager.planning_engine.generate_plan.return_value = sample_plan
        
        # Mock state manager to raise exception on save
        project_manager.state_manager.save_project_plan.side_effect = Exception("Save failed")
        
        # Execute pipeline
        result = project_manager.execute_pipeline("Build a test project")
        
        # Verify failure result
        assert isinstance(result, ProjectResult)
        assert result.success is False
        assert "Save failed" in result.message
    
    def test_execute_pipeline_empty_objective(self, project_manager):
        """Test pipeline execution with empty objective."""
        # Mock planning engine to raise exception for empty objective
        project_manager.planning_engine.generate_plan.side_effect = ValueError("Empty objective")
        
        # Execute pipeline
        result = project_manager.execute_pipeline("")
        
        # Verify failure result
        assert isinstance(result, ProjectResult)
        assert result.success is False
        assert "Empty objective" in result.message


class TestProjectManagerResumption:
    """Test pipeline resumption functionality."""
    
    @pytest.fixture
    def project_manager_with_progress(self):
        """Create ProjectManager with existing progress."""
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        pm = ProjectManager(
            project_path="/test/path",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
        
        return pm
    
    def test_resume_pipeline_success(self, project_manager_with_progress):
        """Test successful pipeline resumption."""
        # Mock existing progress
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.SPECIFICATION,
            completed_phases=[ProjectPhase.PLANNING],
            total_functions=5,
            implemented_functions=0
        )
        project_manager_with_progress.state_manager.get_current_progress.return_value = mock_progress

        # Mock project plan
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
            ],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1
        )
        project_manager_with_progress.state_manager.load_project_plan.return_value = sample_plan

        # Mock other phases to return success
        from a3.core.models import SpecificationSet, ImplementationResult, IntegrationResult
        
        spec_set = SpecificationSet(functions=sample_plan.modules[0].functions)
        project_manager_with_progress.spec_generator.generate_specifications.return_value = spec_set
        
        impl_result = ImplementationResult(
            implemented_functions=["test_func"],
            failed_functions=[],
            success_rate=1.0
        )
        project_manager_with_progress.code_generator.implement_all.return_value = impl_result
        
        integration_result = IntegrationResult(
            success=True,
            integrated_modules=["test_module"],
            import_errors=[]
        )
        project_manager_with_progress.integration_engine.integrate_modules.return_value = integration_result
        
        # Resume pipeline
        result = project_manager_with_progress.resume_pipeline()
        
        # Verify results
        assert isinstance(result, ProjectResult)
        assert result.success is True
        assert "Pipeline resumed and completed successfully" in result.message
        assert result.data['phase'] == 'completed'
    
    def test_resume_pipeline_no_progress(self, project_manager_with_progress):
        """Test pipeline resumption with no existing progress."""
        # Mock no existing progress
        project_manager_with_progress.state_manager.get_current_progress.return_value = None
        
        # Resume pipeline
        result = project_manager_with_progress.resume_pipeline()
        
        # Verify failure result
        assert isinstance(result, ProjectResult)
        assert result.success is False
        assert "No progress found to resume" in result.message
        assert "No resumable state found" in result.errors
    
    def test_resume_pipeline_state_manager_error(self, project_manager_with_progress):
        """Test pipeline resumption with state manager error."""
        # Mock state manager to raise exception
        project_manager_with_progress.state_manager.get_current_progress.side_effect = Exception("State error")
        
        # Resume pipeline
        result = project_manager_with_progress.resume_pipeline()
        
        # Verify failure result
        assert isinstance(result, ProjectResult)
        assert result.success is False
        assert "Pipeline execution failed" in result.message
        assert "State error" in result.message
    
    def test_resume_pipeline_different_phases(self, project_manager_with_progress):
        """Test pipeline resumption from different phases."""
        # Mock project plan for phases that need it
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
            ],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1
        )
        project_manager_with_progress.state_manager.load_project_plan.return_value = sample_plan

        # Mock other phases to return success
        from a3.core.models import SpecificationSet, ImplementationResult, IntegrationResult
        
        spec_set = SpecificationSet(functions=sample_plan.modules[0].functions)
        project_manager_with_progress.spec_generator.generate_specifications.return_value = spec_set
        
        impl_result = ImplementationResult(
            implemented_functions=["test_func"],
            failed_functions=[],
            success_rate=1.0
        )
        project_manager_with_progress.code_generator.implement_all.return_value = impl_result
        
        integration_result = IntegrationResult(
            success=True,
            integrated_modules=["test_module"],
            import_errors=[]
        )
        project_manager_with_progress.integration_engine.integrate_modules.return_value = integration_result
        
        # Test PLANNING phase (should fail)
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[],
            total_functions=1,
            implemented_functions=0
        )
        project_manager_with_progress.state_manager.get_current_progress.return_value = mock_progress
        
        result = project_manager_with_progress.resume_pipeline()
        assert isinstance(result, ProjectResult)
        assert result.success is False
        assert "Cannot resume from planning phase" in result.message
        
        # Test other phases (should succeed)
        phases_to_test = [
            ProjectPhase.SPECIFICATION,
            ProjectPhase.IMPLEMENTATION,
            ProjectPhase.INTEGRATION,
            ProjectPhase.COMPLETED
        ]
        
        for phase in phases_to_test:
            mock_progress = ProjectProgress(
                current_phase=phase,
                completed_phases=[],
                total_functions=1,
                implemented_functions=0
            )
            project_manager_with_progress.state_manager.get_current_progress.return_value = mock_progress
            
            result = project_manager_with_progress.resume_pipeline()
            
            assert isinstance(result, ProjectResult)
            assert result.success is True
            if phase == ProjectPhase.COMPLETED:
                assert "already completed" in result.message
                assert result.data['phase'] == 'completed'
            else:
                assert "Pipeline resumed and completed successfully" in result.message
                assert result.data['phase'] == 'completed'


class TestProjectManagerPhaseManagement:
    """Test phase management functionality."""
    
    @pytest.fixture
    def project_manager(self):
        """Create ProjectManager with mocked components."""
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        return ProjectManager(
            project_path="/test/path",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
    
    def test_get_current_phase_with_progress(self, project_manager):
        """Test getting current phase when progress exists."""
        mock_progress = ProjectProgress(
            current_phase=ProjectPhase.IMPLEMENTATION,
            completed_phases=[ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION],
            total_functions=10,
            implemented_functions=5
        )
        project_manager.state_manager.get_current_progress.return_value = mock_progress
        
        current_phase = project_manager.get_current_phase()
        
        assert current_phase == ProjectPhase.IMPLEMENTATION
    
    def test_get_current_phase_no_progress(self, project_manager):
        """Test getting current phase when no progress exists."""
        project_manager.state_manager.get_current_progress.return_value = None
        
        current_phase = project_manager.get_current_phase()
        
        assert current_phase == ProjectPhase.PLANNING
    
    def test_get_current_phase_state_manager_error(self, project_manager):
        """Test getting current phase with state manager error."""
        project_manager.state_manager.get_current_progress.side_effect = Exception("State error")
        
        # Should raise the exception since the implementation doesn't catch it
        with pytest.raises(Exception, match="State error"):
            project_manager.get_current_phase()


class TestProjectManagerValidation:
    """Test project state validation functionality."""
    
    @pytest.fixture
    def project_manager(self):
        """Create ProjectManager with mocked components."""
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        return ProjectManager(
            project_path="/test/path",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
    
    def test_validate_project_state_success(self, project_manager):
        """Test successful project state validation."""
        # Mock valid project plan
        sample_plan = ProjectPlan(
            objective="Test project",
            modules=[],
            dependency_graph=DependencyGraph(nodes=[], edges=[]),
            estimated_functions=0
        )
        sample_plan.validate = Mock()  # Mock validate method
        project_manager.state_manager.load_project_plan.return_value = sample_plan
        
        # Mock valid progress
        sample_progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[],
            total_functions=0,
            implemented_functions=0
        )
        sample_progress.validate = Mock()  # Mock validate method
        project_manager.state_manager.get_current_progress.return_value = sample_progress
        
        # Validate project state
        result = project_manager.validate_project_state()
        
        # Verify results
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.issues) == 0
        assert len(result.warnings) == 0
        
        # Verify validation methods were called
        sample_plan.validate.assert_called_once()
        sample_progress.validate.assert_called_once()
    
    def test_validate_project_state_no_plan(self, project_manager):
        """Test project state validation with no project plan."""
        project_manager.state_manager.load_project_plan.return_value = None
        project_manager.state_manager.get_current_progress.return_value = None
        
        result = project_manager.validate_project_state()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert "No project plan found" in result.issues[0]
    
    def test_validate_project_state_invalid_plan(self, project_manager):
        """Test project state validation with invalid project plan."""
        # Mock invalid project plan
        sample_plan = ProjectPlan(
            objective="",  # Invalid empty objective
            modules=[],
            dependency_graph=DependencyGraph(nodes=[], edges=[]),
            estimated_functions=0
        )
        sample_plan.validate = Mock(side_effect=ValueError("Invalid plan"))
        project_manager.state_manager.load_project_plan.return_value = sample_plan
        project_manager.state_manager.get_current_progress.return_value = None
        
        result = project_manager.validate_project_state()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert "Project plan validation failed" in result.issues[0]
        assert "Invalid plan" in result.issues[0]
    
    def test_validate_project_state_invalid_progress(self, project_manager):
        """Test project state validation with invalid progress."""
        # Mock valid project plan
        sample_plan = ProjectPlan(
            objective="Test project",
            modules=[],
            dependency_graph=DependencyGraph(nodes=[], edges=[]),
            estimated_functions=0
        )
        sample_plan.validate = Mock()
        project_manager.state_manager.load_project_plan.return_value = sample_plan
        
        # Mock invalid progress
        sample_progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[],
            total_functions=-1,  # Invalid negative value
            implemented_functions=0
        )
        sample_progress.validate = Mock(side_effect=ValueError("Invalid progress"))
        project_manager.state_manager.get_current_progress.return_value = sample_progress
        
        result = project_manager.validate_project_state()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert "Progress validation failed" in result.issues[0]
        assert "Invalid progress" in result.issues[0]
    
    def test_validate_project_state_state_manager_error(self, project_manager):
        """Test project state validation with state manager error."""
        project_manager.state_manager.load_project_plan.side_effect = Exception("State manager error")
        
        result = project_manager.validate_project_state()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert "Validation error" in result.issues[0]
        assert "State manager error" in result.issues[0]
    
    def test_validate_project_state_mixed_results(self, project_manager):
        """Test project state validation with mixed valid/invalid components."""
        # Mock valid project plan
        sample_plan = ProjectPlan(
            objective="Test project",
            modules=[],
            dependency_graph=DependencyGraph(nodes=[], edges=[]),
            estimated_functions=0
        )
        sample_plan.validate = Mock()
        project_manager.state_manager.load_project_plan.return_value = sample_plan
        
        # Mock invalid progress
        sample_progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[],
            total_functions=0,
            implemented_functions=0
        )
        sample_progress.validate = Mock(side_effect=ValueError("Progress issue"))
        project_manager.state_manager.get_current_progress.return_value = sample_progress
        
        result = project_manager.validate_project_state()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert "Progress validation failed" in result.issues[0]


class TestProjectManagerErrorHandling:
    """Test error handling in ProjectManager."""
    
    @pytest.fixture
    def project_manager(self):
        """Create ProjectManager with mocked components."""
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        return ProjectManager(
            project_path="/test/path",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
    
    def test_execute_pipeline_handles_all_exceptions(self, project_manager):
        """Test that execute_pipeline handles all types of exceptions."""
        exception_types = [
            ValueError("Value error"),
            TypeError("Type error"),
            RuntimeError("Runtime error"),
            Exception("Generic error")
        ]
        
        for exception in exception_types:
            project_manager.planning_engine.generate_plan.side_effect = exception
            
            result = project_manager.execute_pipeline("Test objective")
            
            assert isinstance(result, ProjectResult)
            assert result.success is False
            assert str(exception) in result.message
            assert len(result.errors) == 1
    
    def test_resume_pipeline_handles_all_exceptions(self, project_manager):
        """Test that resume_pipeline handles all types of exceptions."""
        exception_types = [
            ValueError("Value error"),
            TypeError("Type error"),
            RuntimeError("Runtime error"),
            Exception("Generic error")
        ]
        
        for exception in exception_types:
            project_manager.state_manager.get_current_progress.side_effect = exception
            
            result = project_manager.resume_pipeline()
            
            assert isinstance(result, ProjectResult)
            assert result.success is False
            assert str(exception) in result.message
    
    def test_validate_project_state_handles_all_exceptions(self, project_manager):
        """Test that validate_project_state handles all types of exceptions."""
        exception_types = [
            ValueError("Value error"),
            TypeError("Type error"),
            RuntimeError("Runtime error"),
            Exception("Generic error")
        ]
        
        for exception in exception_types:
            project_manager.state_manager.load_project_plan.side_effect = exception
            
            result = project_manager.validate_project_state()
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            assert len(result.issues) == 1
            assert str(exception) in result.issues[0]


class TestProjectManagerIntegration:
    """Integration tests for ProjectManager with real-like scenarios."""
    
    def test_complete_pipeline_simulation(self):
        """Test a complete pipeline execution simulation."""
        # Create mocks that simulate real behavior
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        # Create realistic project plan
        sample_plan = ProjectPlan(
            objective="Build a calculator application",
            modules=[
                Module(
                    name="calculator",
                    description="Main calculator module",
                    file_path="calculator.py",
                    functions=[
                        FunctionSpec(
                            name="add",
                            module="calculator",
                            docstring="Add two numbers"
                        ),
                        FunctionSpec(
                            name="subtract",
                            module="calculator",
                            docstring="Subtract two numbers"
                        )
                    ]
                ),
                Module(
                    name="utils",
                    description="Utility functions",
                    file_path="utils.py",
                    functions=[
                        FunctionSpec(
                            name="validate_input",
                            module="utils",
                            docstring="Validate numeric input"
                        )
                    ]
                )
            ],
            dependency_graph=DependencyGraph(
                nodes=["calculator", "utils"],
                edges=[("calculator", "utils")]
            ),
            estimated_functions=3
        )
        
        mock_planning_engine.generate_plan.return_value = sample_plan

        # Mock other phases to return success
        from a3.core.models import SpecificationSet, ImplementationResult, IntegrationResult
        
        all_functions = []
        for module in sample_plan.modules:
            all_functions.extend(module.functions)
        
        spec_set = SpecificationSet(functions=all_functions)
        mock_spec_generator.generate_specifications.return_value = spec_set
        
        impl_result = ImplementationResult(
            implemented_functions=["add", "subtract", "validate_input"],
            failed_functions=[],
            success_rate=1.0
        )
        mock_code_generator.implement_all.return_value = impl_result
        
        integration_result = IntegrationResult(
            success=True,
            integrated_modules=["calculator", "utils"],
            import_errors=[]
        )
        mock_integration_engine.integrate_modules.return_value = integration_result
        
        # Mock state manager to return the plan when needed
        mock_state_manager.load_project_plan.return_value = sample_plan
        
        # Create project manager
        pm = ProjectManager(
            project_path="/test/calculator",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
        
        # Execute pipeline
        result = pm.execute_pipeline("Build a calculator application")
        
        # Verify comprehensive results
        assert result.success is True
        assert result.data['phase'] == 'completed'
        
        # Verify all state operations were called correctly
        mock_state_manager.save_project_plan.assert_called_once_with(sample_plan)
        # save_progress should be called for each phase (planning, spec, impl, integration, completed)
        assert mock_state_manager.save_progress.call_count >= 4
    
    def test_resumption_workflow_simulation(self):
        """Test a realistic resumption workflow."""
        mock_state_manager = Mock(spec=StateManagerInterface)
        mock_planning_engine = Mock(spec=PlanningEngineInterface)
        mock_spec_generator = Mock(spec=SpecificationGeneratorInterface)
        mock_code_generator = Mock(spec=CodeGeneratorInterface)
        mock_integration_engine = Mock(spec=IntegrationEngineInterface)
        
        # Simulate interrupted project at specification phase
        interrupted_progress = ProjectProgress(
            current_phase=ProjectPhase.SPECIFICATION,
            completed_phases=[ProjectPhase.PLANNING],
            total_functions=5,
            implemented_functions=0,
            failed_functions=[]
        )
        mock_state_manager.get_current_progress.return_value = interrupted_progress

        # Mock project plan
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
            ],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1
        )
        mock_state_manager.load_project_plan.return_value = sample_plan

        # Mock other phases to return success
        from a3.core.models import SpecificationSet, ImplementationResult, IntegrationResult
        
        spec_set = SpecificationSet(functions=sample_plan.modules[0].functions)
        mock_spec_generator.generate_specifications.return_value = spec_set
        
        impl_result = ImplementationResult(
            implemented_functions=["test_func"],
            failed_functions=[],
            success_rate=1.0
        )
        mock_code_generator.implement_all.return_value = impl_result
        
        integration_result = IntegrationResult(
            success=True,
            integrated_modules=["test_module"],
            import_errors=[]
        )
        mock_integration_engine.integrate_modules.return_value = integration_result
        
        pm = ProjectManager(
            project_path="/test/interrupted",
            state_manager=mock_state_manager,
            planning_engine=mock_planning_engine,
            spec_generator=mock_spec_generator,
            code_generator=mock_code_generator,
            integration_engine=mock_integration_engine
        )
        
        # Resume pipeline
        result = pm.resume_pipeline()
        
        # Verify resumption
        assert result.success is True
        assert "Pipeline resumed and completed successfully" in result.message
        assert result.data['phase'] == 'completed'
        
        # Verify state manager was queried (may be called multiple times for validation)
        assert mock_state_manager.get_current_progress.call_count >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])