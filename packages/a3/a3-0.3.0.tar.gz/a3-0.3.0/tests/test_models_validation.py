"""
Unit tests for data model validation logic.
"""

import pytest
from datetime import datetime
from a3.core.models import (
    Argument, FunctionSpec, Module, DependencyGraph, ProjectPlan, ProjectProgress,
    ValidationError, ProjectPlanValidationError, ModuleValidationError,
    FunctionSpecValidationError, DependencyGraphValidationError,
    ProjectPhase, ImplementationStatus
)


class TestArgumentValidation:
    """Test validation for Argument class."""
    
    def test_valid_argument(self):
        """Test that valid arguments pass validation."""
        arg = Argument(name="param", type_hint="str", description="A parameter")
        arg.validate()  # Should not raise
    
    def test_empty_name_raises_error(self):
        """Test that empty argument name raises ValidationError."""
        arg = Argument(name="", type_hint="str")
        with pytest.raises(ValidationError, match="Argument name cannot be empty"):
            arg.validate()
    
    def test_invalid_name_raises_error(self):
        """Test that invalid argument name raises ValidationError."""
        arg = Argument(name="123invalid", type_hint="str")
        with pytest.raises(ValidationError, match="Invalid argument name"):
            arg.validate()
    
    def test_empty_type_hint_raises_error(self):
        """Test that empty type hint raises ValidationError."""
        arg = Argument(name="param", type_hint="")
        with pytest.raises(ValidationError, match="Argument type hint cannot be empty"):
            arg.validate()
    
    def test_keyword_name_raises_error(self):
        """Test that Python keyword as name raises ValidationError."""
        arg = Argument(name="def", type_hint="str")
        with pytest.raises(ValidationError, match="is a Python keyword"):
            arg.validate()


class TestFunctionSpecValidation:
    """Test validation for FunctionSpec class."""
    
    def test_valid_function_spec(self):
        """Test that valid function spec passes validation."""
        func = FunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            arguments=[Argument("param", "str")],
            return_type="bool"
        )
        func.validate()  # Should not raise
    
    def test_empty_name_raises_error(self):
        """Test that empty function name raises error."""
        func = FunctionSpec(name="", module="test", docstring="Test")
        with pytest.raises(FunctionSpecValidationError, match="Function name cannot be empty"):
            func.validate()
    
    def test_invalid_name_raises_error(self):
        """Test that invalid function name raises error."""
        func = FunctionSpec(name="123invalid", module="test", docstring="Test")
        with pytest.raises(FunctionSpecValidationError, match="Invalid function name"):
            func.validate()
    
    def test_empty_module_raises_error(self):
        """Test that empty module name raises error."""
        func = FunctionSpec(name="test", module="", docstring="Test")
        with pytest.raises(FunctionSpecValidationError, match="Module name cannot be empty"):
            func.validate()
    
    def test_empty_docstring_raises_error(self):
        """Test that empty docstring raises error."""
        func = FunctionSpec(name="test", module="test", docstring="")
        with pytest.raises(FunctionSpecValidationError, match="Function docstring cannot be empty"):
            func.validate()
    
    def test_duplicate_argument_names_raises_error(self):
        """Test that duplicate argument names raise error."""
        func = FunctionSpec(
            name="test",
            module="test",
            docstring="Test",
            arguments=[
                Argument("param", "str"),
                Argument("param", "int")  # Duplicate name
            ]
        )
        with pytest.raises(FunctionSpecValidationError, match="Duplicate argument name"):
            func.validate()


class TestModuleValidation:
    """Test validation for Module class."""
    
    def test_valid_module(self):
        """Test that valid module passes validation."""
        module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=[FunctionSpec("test_func", "test_module", "Test function")]
        )
        module.validate()  # Should not raise
    
    def test_empty_name_raises_error(self):
        """Test that empty module name raises error."""
        module = Module(name="", description="Test", file_path="test.py")
        with pytest.raises(ModuleValidationError, match="Module name cannot be empty"):
            module.validate()
    
    def test_invalid_file_path_raises_error(self):
        """Test that non-Python file path raises error."""
        module = Module(name="test", description="Test", file_path="test.txt")
        with pytest.raises(ModuleValidationError, match="must end with .py"):
            module.validate()
    
    def test_self_dependency_raises_error(self):
        """Test that self-dependency raises error."""
        module = Module(
            name="test",
            description="Test",
            file_path="test.py",
            dependencies=["test"]  # Self-dependency
        )
        with pytest.raises(ModuleValidationError, match="cannot depend on itself"):
            module.validate()
    
    def test_duplicate_function_names_raises_error(self):
        """Test that duplicate function names raise error."""
        module = Module(
            name="test",
            description="Test",
            file_path="test.py",
            functions=[
                FunctionSpec("func", "test", "Test 1"),
                FunctionSpec("func", "test", "Test 2")  # Duplicate name
            ]
        )
        with pytest.raises(ModuleValidationError, match="Duplicate function name"):
            module.validate()


class TestDependencyGraphValidation:
    """Test validation for DependencyGraph class."""
    
    def test_valid_dependency_graph(self):
        """Test that valid dependency graph passes validation."""
        graph = DependencyGraph(
            nodes=["module_a", "module_b"],
            edges=[("module_a", "module_b")]
        )
        graph.validate()  # Should not raise
    
    def test_duplicate_nodes_raises_error(self):
        """Test that duplicate nodes raise error."""
        graph = DependencyGraph(nodes=["module_a", "module_a"])
        with pytest.raises(DependencyGraphValidationError, match="duplicate nodes"):
            graph.validate()
    
    def test_invalid_node_name_raises_error(self):
        """Test that invalid node name raises error."""
        graph = DependencyGraph(nodes=["123invalid"])
        with pytest.raises(DependencyGraphValidationError, match="Invalid node name"):
            graph.validate()
    
    def test_edge_to_nonexistent_node_raises_error(self):
        """Test that edge to non-existent node raises error."""
        graph = DependencyGraph(
            nodes=["module_a"],
            edges=[("module_a", "nonexistent")]
        )
        with pytest.raises(DependencyGraphValidationError, match="non-existent node"):
            graph.validate()
    
    def test_self_dependency_raises_error(self):
        """Test that self-dependency raises error."""
        graph = DependencyGraph(
            nodes=["module_a"],
            edges=[("module_a", "module_a")]
        )
        with pytest.raises(DependencyGraphValidationError, match="Self-dependency detected"):
            graph.validate()
    
    def test_circular_dependency_raises_error(self):
        """Test that circular dependencies raise error."""
        graph = DependencyGraph(
            nodes=["module_a", "module_b"],
            edges=[("module_a", "module_b"), ("module_b", "module_a")]
        )
        with pytest.raises(DependencyGraphValidationError, match="circular dependencies"):
            graph.validate()


class TestProjectPlanValidation:
    """Test validation for ProjectPlan class."""
    
    def test_valid_project_plan(self):
        """Test that valid project plan passes validation."""
        module = Module("test_module", "Test", "test.py")
        graph = DependencyGraph(nodes=["test_module"])
        plan = ProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=graph,
            estimated_functions=0
        )
        plan.validate()  # Should not raise
    
    def test_empty_objective_raises_error(self):
        """Test that empty objective raises error."""
        plan = ProjectPlan(objective="")
        with pytest.raises(ProjectPlanValidationError, match="Project objective cannot be empty"):
            plan.validate()
    
    def test_negative_estimated_functions_raises_error(self):
        """Test that negative estimated functions raises error."""
        plan = ProjectPlan(objective="Test", estimated_functions=-1)
        with pytest.raises(ProjectPlanValidationError, match="cannot be negative"):
            plan.validate()
    
    def test_mismatched_graph_nodes_raises_error(self):
        """Test that mismatched graph nodes and modules raise error."""
        module = Module("test_module", "Test", "test.py")
        graph = DependencyGraph(nodes=["different_module"])
        plan = ProjectPlan(
            objective="Test",
            modules=[module],
            dependency_graph=graph
        )
        with pytest.raises(ProjectPlanValidationError, match="don't match module names"):
            plan.validate()


class TestProjectProgressValidation:
    """Test validation for ProjectProgress class."""
    
    def test_valid_project_progress(self):
        """Test that valid project progress passes validation."""
        progress = ProjectProgress(
            current_phase=ProjectPhase.IMPLEMENTATION,
            completed_phases=[ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION],
            total_functions=10,
            implemented_functions=5
        )
        progress.validate()  # Should not raise
    
    def test_negative_total_functions_raises_error(self):
        """Test that negative total functions raises error."""
        progress = ProjectProgress(total_functions=-1)
        with pytest.raises(ValidationError, match="Total functions count cannot be negative"):
            progress.validate()
    
    def test_implemented_exceeds_total_raises_error(self):
        """Test that implemented > total raises error."""
        progress = ProjectProgress(total_functions=5, implemented_functions=10)
        with pytest.raises(ValidationError, match="cannot exceed total functions"):
            progress.validate()
    
    def test_invalid_phase_progression_raises_error(self):
        """Test that invalid phase progression raises error."""
        progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[ProjectPhase.IMPLEMENTATION]  # Future phase marked complete
        )
        with pytest.raises(ValidationError, match="cannot be ahead of current phase"):
            progress.validate()


class TestDependencyGraphAlgorithms:
    """Test dependency graph cycle detection and topological sort."""
    
    def test_has_cycles_detects_simple_cycle(self):
        """Test that has_cycles detects a simple cycle."""
        graph = DependencyGraph(
            nodes=["a", "b"],
            edges=[("a", "b"), ("b", "a")]
        )
        assert graph.has_cycles() is True
    
    def test_has_cycles_detects_complex_cycle(self):
        """Test that has_cycles detects a complex cycle."""
        graph = DependencyGraph(
            nodes=["a", "b", "c"],
            edges=[("a", "b"), ("b", "c"), ("c", "a")]
        )
        assert graph.has_cycles() is True
    
    def test_has_cycles_returns_false_for_acyclic_graph(self):
        """Test that has_cycles returns False for acyclic graph."""
        graph = DependencyGraph(
            nodes=["a", "b", "c"],
            edges=[("a", "b"), ("a", "c")]
        )
        assert graph.has_cycles() is False
    
    def test_topological_sort_orders_correctly(self):
        """Test that topological sort orders nodes correctly."""
        graph = DependencyGraph(
            nodes=["a", "b", "c"],
            edges=[("a", "b"), ("a", "c"), ("b", "c")]
        )
        result = graph.topological_sort()
        
        # 'a' should come before 'b' and 'c'
        # 'b' should come before 'c'
        assert result.index("a") < result.index("b")
        assert result.index("a") < result.index("c")
        assert result.index("b") < result.index("c")
    
    def test_topological_sort_handles_cycle(self):
        """Test that topological sort handles cycles gracefully."""
        graph = DependencyGraph(
            nodes=["a", "b"],
            edges=[("a", "b"), ("b", "a")]
        )
        result = graph.topological_sort()
        # Should return original order when cycle exists
        assert result == ["a", "b"]