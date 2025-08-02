"""
Unit tests for the PlanningEngine class.

This module tests the planning engine functionality including plan generation,
module breakdown, and dependency analysis integration.
"""

import pytest
from unittest.mock import Mock, MagicMock

from a3.engines.planning import PlanningEngine, PlanGenerationError
from a3.core.models import ProjectPlan, Module, FunctionSpec, ValidationResult
from a3.core.interfaces import AIClientInterface, StateManagerInterface


class TestPlanningEngine:
    """Test cases for PlanningEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_client = Mock(spec=AIClientInterface)
        self.mock_state_manager = Mock(spec=StateManagerInterface)
        self.engine = PlanningEngine(
            ai_client=self.mock_ai_client,
            state_manager=self.mock_state_manager,
            project_path="test_project"
        )
        
        # Mock AI client methods
        self.mock_ai_client.validate_api_key.return_value = True
    
    def test_initialization(self):
        """Test planning engine initialization."""
        assert self.engine.ai_client == self.mock_ai_client
        assert self.engine.state_manager == self.mock_state_manager
        assert self.engine.dependency_analyzer is not None
        assert self.engine.max_modules == 20
        assert self.engine.max_functions_per_module == 15
    
    def test_validate_prerequisites_success(self):
        """Test prerequisite validation with valid setup."""
        self.engine.initialize()
        result = self.engine.validate_prerequisites()
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_validate_prerequisites_no_ai_client(self):
        """Test prerequisite validation without AI client."""
        engine = PlanningEngine(project_path="test_project")
        result = engine.validate_prerequisites()
        
        assert not result.is_valid
        assert "AI client is required" in str(result.issues)
    
    def test_analyze_plan_dependencies_empty_plan(self):
        """Test dependency analysis with empty plan."""
        empty_plan = ProjectPlan(objective="test", modules=[])
        result = self.engine.analyze_plan_dependencies(empty_plan)
        
        assert not result.is_valid
        assert "must contain modules" in str(result.issues)
    
    def test_analyze_plan_dependencies_valid_plan(self):
        """Test dependency analysis with valid plan."""
        modules = [
            Module(
                name="core",
                description="Core module",
                file_path="core.py",
                dependencies=[],
                functions=[FunctionSpec(name="core_func", module="core", docstring="Core function")]
            ),
            Module(
                name="utils",
                description="Utils module", 
                file_path="utils.py",
                dependencies=["core"],
                functions=[FunctionSpec(name="util_func", module="utils", docstring="Util function")]
            )
        ]
        
        plan = ProjectPlan(objective="test project", modules=modules)
        result = self.engine.analyze_plan_dependencies(plan)
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_detect_circular_dependencies_none(self):
        """Test circular dependency detection with no cycles."""
        modules = [
            Module(
                name="core",
                description="Core module",
                file_path="core.py", 
                dependencies=[],
                functions=[]
            ),
            Module(
                name="utils",
                description="Utils module",
                file_path="utils.py",
                dependencies=["core"],
                functions=[]
            )
        ]
        
        plan = ProjectPlan(objective="test", modules=modules)
        cycles = self.engine.detect_circular_dependencies(plan)
        
        assert len(cycles) == 0
    
    def test_get_module_build_order(self):
        """Test module build order generation."""
        modules = [
            Module(
                name="core",
                description="Core module",
                file_path="core.py",
                dependencies=[],
                functions=[]
            ),
            Module(
                name="utils", 
                description="Utils module",
                file_path="utils.py",
                dependencies=["core"],
                functions=[]
            )
        ]
        
        plan = ProjectPlan(objective="test", modules=modules)
        build_order = self.engine.get_module_build_order(plan)
        
        assert len(build_order) == 2
        assert build_order[0] == "core"  # Core should come first
        assert build_order[1] == "utils"  # Utils depends on core
    
    def test_get_dependency_map(self):
        """Test dependency map generation."""
        modules = [
            Module(
                name="core",
                description="Core module", 
                file_path="core.py",
                dependencies=[],
                functions=[]
            ),
            Module(
                name="utils",
                description="Utils module",
                file_path="utils.py", 
                dependencies=["core"],
                functions=[]
            )
        ]
        
        plan = ProjectPlan(objective="test", modules=modules)
        dep_map = self.engine.get_dependency_map(plan)
        
        assert len(dep_map) == 2
        assert dep_map["core"] == []
        assert dep_map["utils"] == ["core"]