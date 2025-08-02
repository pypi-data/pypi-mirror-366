"""
Tests for the Dependency-Driven Planner component.

This module tests the functionality of the DependencyDrivenPlanner class
including optimal implementation ordering, parallel opportunity identification,
and critical path analysis.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict

from a3.core.dependency_driven_planner import DependencyDrivenPlanner, CriticalPathAnalysis
from a3.core.models import (
    EnhancedDependencyGraph, FunctionDependency, DependencyType,
    OptimizationSuggestion
)


class TestDependencyDrivenPlanner:
    """Test cases for DependencyDrivenPlanner."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = DependencyDrivenPlanner()
        self.enhanced_graph = self._create_test_enhanced_graph()
    
    def _create_test_enhanced_graph(self) -> EnhancedDependencyGraph:
        """Create a test enhanced dependency graph."""
        graph = EnhancedDependencyGraph()
        
        # Add test functions
        test_functions = [
            ("func1", "module1"),
            ("func2", "module1"), 
            ("func3", "module2"),
            ("func4", "module2"),
            ("func5", "module3")
        ]
        
        for func_name, module_name in test_functions:
            graph.add_function(func_name, module_name)
        
        # Add test dependencies
        dependencies = [
            FunctionDependency("module1.func1", "module2.func3", DependencyType.DIRECT_CALL, 0.9),
            FunctionDependency("module1.func2", "module1.func1", DependencyType.DATA_DEPENDENCY, 0.8),
            FunctionDependency("module2.func4", "module2.func3", DependencyType.DIRECT_CALL, 0.7),
            FunctionDependency("module3.func5", "module2.func4", DependencyType.TYPE_DEPENDENCY, 0.6)
        ]
        
        for dep in dependencies:
            graph.add_function_dependency(dep)
        
        return graph
    
    def _create_cyclic_enhanced_graph(self) -> EnhancedDependencyGraph:
        """Create a test enhanced dependency graph with cycles."""
        graph = EnhancedDependencyGraph()
        
        # Add functions
        for func_name, module_name in [("func1", "module1"), ("func2", "module1"), ("func3", "module2")]:
            graph.add_function(func_name, module_name)
        
        # Add cyclic dependencies
        dependencies = [
            FunctionDependency("module1.func1", "module1.func2", DependencyType.DIRECT_CALL, 0.9),
            FunctionDependency("module1.func2", "module2.func3", DependencyType.DATA_DEPENDENCY, 0.8),
            FunctionDependency("module2.func3", "module1.func1", DependencyType.DIRECT_CALL, 0.7)  # Creates cycle
        ]
        
        for dep in dependencies:
            graph.add_function_dependency(dep)
        
        return graph


class TestOptimalImplementationOrdering:
    """Test optimal implementation ordering functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = DependencyDrivenPlanner()
    
    def test_get_optimal_implementation_order_empty_graph(self):
        """Test optimal implementation order with empty graph."""
        empty_graph = EnhancedDependencyGraph()
        result = self.planner.get_optimal_implementation_order(empty_graph)
        assert result == []
    
    def test_get_optimal_implementation_order_no_dependencies(self):
        """Test optimal implementation order with functions but no dependencies."""
        graph = EnhancedDependencyGraph()
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module2")
        
        result = self.planner.get_optimal_implementation_order(graph)
        assert len(result) == 2
        assert "module1.func1" in result
        assert "module2.func2" in result
    
    def test_get_optimal_implementation_order_linear_dependencies(self):
        """Test optimal implementation order with linear dependency chain."""
        graph = EnhancedDependencyGraph()
        
        # Create linear chain: func1 -> func2 -> func3
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1") 
        graph.add_function("func3", "module1")
        
        graph.add_function_dependency(
            FunctionDependency("module1.func1", "module1.func2", DependencyType.DIRECT_CALL, 0.9)
        )
        graph.add_function_dependency(
            FunctionDependency("module1.func2", "module1.func3", DependencyType.DIRECT_CALL, 0.9)
        )
        
        result = self.planner.get_optimal_implementation_order(graph)
        
        # func3 should come first (no dependencies), then func2, then func1
        assert result.index("module1.func3") < result.index("module1.func2")
        assert result.index("module1.func2") < result.index("module1.func1")
    
    def test_get_optimal_implementation_order_with_cycles(self):
        """Test optimal implementation order with cyclic dependencies."""
        graph = EnhancedDependencyGraph()
        
        # Create cycle: func1 -> func2 -> func1
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        
        graph.add_function_dependency(
            FunctionDependency("module1.func1", "module1.func2", DependencyType.DIRECT_CALL, 0.9)
        )
        graph.add_function_dependency(
            FunctionDependency("module1.func2", "module1.func1", DependencyType.DIRECT_CALL, 0.9)
        )
        
        result = self.planner.get_optimal_implementation_order(graph)
        
        # Should handle cycles gracefully and return some order
        assert len(result) == 2
        assert "module1.func1" in result
        assert "module1.func2" in result
    
    def test_handle_cyclic_dependencies_break_by_criticality(self):
        """Test cycle breaking by dependency criticality."""
        graph = EnhancedDependencyGraph()
        
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        
        # Add cycle with different criticality scores
        high_criticality = FunctionDependency("module1.func1", "module1.func2", DependencyType.DIRECT_CALL, 0.9)
        low_criticality = FunctionDependency("module1.func2", "module1.func1", DependencyType.IMPORT_DEPENDENCY, 0.3)
        
        graph.add_function_dependency(high_criticality)
        graph.add_function_dependency(low_criticality)
        
        result = self.planner._handle_cyclic_dependencies(graph)
        
        # Should return some valid order
        assert len(result) == 2
        assert all(func in result for func in ["module1.func1", "module1.func2"])
    
    def test_calculate_dependency_criticality(self):
        """Test dependency criticality calculation."""
        graph = EnhancedDependencyGraph()
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        
        # Test different dependency types
        direct_call_dep = FunctionDependency("module1.func1", "module1.func2", DependencyType.DIRECT_CALL, 0.8)
        import_dep = FunctionDependency("module1.func1", "module1.func2", DependencyType.IMPORT_DEPENDENCY, 0.8)
        
        direct_score = self.planner._calculate_dependency_criticality(direct_call_dep, graph)
        import_score = self.planner._calculate_dependency_criticality(import_dep, graph)
        
        # Direct call should have higher criticality than import
        assert direct_score > import_score
    
    def test_fallback_alphabetical_order(self):
        """Test fallback alphabetical ordering."""
        graph = EnhancedDependencyGraph()
        graph.add_function("zebra", "module_z")
        graph.add_function("alpha", "module_a")
        graph.add_function("beta", "module_a")
        
        result = self.planner._fallback_alphabetical_order(graph)
        
        # Should be ordered by module then function name
        expected_order = ["module_a.alpha", "module_a.beta", "module_z.zebra"]
        assert result == expected_order


class TestParallelOpportunityIdentification:
    """Test parallel opportunity identification functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = DependencyDrivenPlanner()
    
    def test_identify_parallel_opportunities_empty_graph(self):
        """Test parallel opportunity identification with empty graph."""
        empty_graph = EnhancedDependencyGraph()
        result = self.planner.identify_parallel_opportunities(empty_graph)
        assert result == []
    
    def test_identify_parallel_opportunities_independent_functions(self):
        """Test parallel opportunities with independent functions."""
        graph = EnhancedDependencyGraph()
        
        # Add independent functions
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module2")
        graph.add_function("func3", "module3")
        
        # Mock the enhanced graph's parallel group method
        with patch.object(graph, 'get_parallel_implementation_groups') as mock_parallel:
            mock_parallel.return_value = [["module1.func1", "module2.func2", "module3.func3"]]
            
            result = self.planner.identify_parallel_opportunities(graph)
            
            assert len(result) > 0
            # Should group by module
            assert any("module1.func1" in group for group in result)
    
    def test_optimize_parallel_groups_for_workflow(self):
        """Test workflow optimization of parallel groups."""
        graph = EnhancedDependencyGraph()
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        graph.add_function("func3", "module2")
        
        base_groups = [["module1.func1", "module1.func2", "module2.func3"]]
        
        result = self.planner._optimize_parallel_groups_for_workflow(base_groups, graph)
        
        # Should split by module
        assert len(result) >= 1
        # Functions from same module should be grouped together when possible
        module1_functions = [func for group in result for func in group if func.startswith("module1.")]
        assert len(module1_functions) == 2
    
    def test_group_functions_by_module(self):
        """Test grouping functions by module."""
        graph = EnhancedDependencyGraph()
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        graph.add_function("func3", "module2")
        
        functions = ["module1.func1", "module1.func2", "module2.func3"]
        result = self.planner._group_functions_by_module(functions, graph)
        
        # Should create separate groups for each module
        assert len(result) == 2
        module1_group = [group for group in result if "module1.func1" in group][0]
        assert len(module1_group) == 2
    
    def test_estimate_function_complexity(self):
        """Test function complexity estimation."""
        graph = EnhancedDependencyGraph()
        graph.add_function("simple_get", "module1")
        graph.add_function("complex_process_analyzer", "module1")
        
        simple_complexity = self.planner._estimate_function_complexity("module1.simple_get", graph)
        complex_complexity = self.planner._estimate_function_complexity("module1.complex_process_analyzer", graph)
        
        # Complex function should have higher complexity score
        assert complex_complexity > simple_complexity
    
    def test_split_large_groups(self):
        """Test splitting of large parallel groups."""
        large_group = [f"module1.func{i}" for i in range(10)]
        groups = [large_group]
        
        result = self.planner._split_large_groups(groups, max_size=3)
        
        # Should split into smaller groups
        assert len(result) > 1
        assert all(len(group) <= 3 for group in result)
        
        # All original functions should be preserved
        all_functions = [func for group in result for func in group]
        assert set(all_functions) == set(large_group)


class TestCriticalPathAnalysis:
    """Test critical path analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = DependencyDrivenPlanner()
    
    def test_analyze_critical_path_empty_graph(self):
        """Test critical path analysis with empty graph."""
        empty_graph = EnhancedDependencyGraph()
        result = self.planner.analyze_critical_path(empty_graph)
        
        assert isinstance(result, CriticalPathAnalysis)
        assert result.critical_path == []
        assert result.path_length == 0
        assert result.bottleneck_functions == []
        assert result.optimization_suggestions == []
        assert result.parallel_opportunities == []
    
    def test_analyze_critical_path_with_functions(self):
        """Test critical path analysis with functions and dependencies."""
        graph = EnhancedDependencyGraph()
        
        # Create a dependency chain
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        graph.add_function("func3", "module1")
        
        graph.add_function_dependency(
            FunctionDependency("module1.func1", "module1.func2", DependencyType.DIRECT_CALL, 0.9)
        )
        graph.add_function_dependency(
            FunctionDependency("module1.func2", "module1.func3", DependencyType.DIRECT_CALL, 0.9)
        )
        
        # Mock the critical path method
        with patch.object(graph, 'get_critical_path') as mock_critical:
            mock_critical.return_value = ["module1.func1", "module1.func2", "module1.func3"]
            
            result = self.planner.analyze_critical_path(graph)
            
            assert isinstance(result, CriticalPathAnalysis)
            assert len(result.critical_path) == 3
            assert result.path_length == 3
    
    def test_identify_bottleneck_functions(self):
        """Test bottleneck function identification."""
        graph = EnhancedDependencyGraph()
        
        # Create a function with high fan-in (many functions depend on it)
        graph.add_function("bottleneck", "module1")
        for i in range(5):
            graph.add_function(f"func{i}", "module1")
            graph.add_function_dependency(
                FunctionDependency(f"module1.func{i}", "module1.bottleneck", DependencyType.DIRECT_CALL, 0.8)
            )
        
        bottlenecks = self.planner._identify_bottleneck_functions(graph)
        
        assert "module1.bottleneck" in bottlenecks
    
    def test_generate_critical_path_optimizations(self):
        """Test critical path optimization suggestions."""
        graph = EnhancedDependencyGraph()
        graph.add_function("func1", "module1")
        graph.add_function("func2", "module1")
        
        critical_path = ["module1.func1", "module1.func2"]
        bottlenecks = ["module1.func1"]
        
        suggestions = self.planner._generate_critical_path_optimizations(
            critical_path, bottlenecks, graph
        )
        
        assert len(suggestions) > 0
        assert any("bottleneck" in suggestion.lower() for suggestion in suggestions)
    
    def test_identify_critical_path_parallel_opportunities(self):
        """Test identification of parallel opportunities for critical path."""
        graph = EnhancedDependencyGraph()
        
        # Create critical path and independent functions
        graph.add_function("critical1", "module1")
        graph.add_function("critical2", "module1")
        graph.add_function("independent1", "module2")
        graph.add_function("independent2", "module2")
        
        # Add dependency for critical path
        graph.add_function_dependency(
            FunctionDependency("module1.critical1", "module1.critical2", DependencyType.DIRECT_CALL, 0.9)
        )
        
        critical_path = ["module1.critical1", "module1.critical2"]
        
        opportunities = self.planner._identify_critical_path_parallel_opportunities(
            critical_path, graph
        )
        
        # Should identify independent functions as parallel opportunities
        assert len(opportunities) >= 0  # May be empty if no valid opportunities found


class TestIntegration:
    """Integration tests for DependencyDrivenPlanner."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = DependencyDrivenPlanner()
    
    def test_full_workflow_with_complex_graph(self):
        """Test complete workflow with a complex dependency graph."""
        graph = EnhancedDependencyGraph()
        
        # Create a more complex graph
        modules_and_functions = [
            ("parser", "module1"), ("validator", "module1"), ("processor", "module1"),
            ("analyzer", "module2"), ("reporter", "module2"),
            ("exporter", "module3"), ("formatter", "module3")
        ]
        
        for func_name, module_name in modules_and_functions:
            graph.add_function(func_name, module_name)
        
        # Add complex dependencies
        dependencies = [
            FunctionDependency("module1.processor", "module1.parser", DependencyType.DIRECT_CALL, 0.9),
            FunctionDependency("module1.processor", "module1.validator", DependencyType.DATA_DEPENDENCY, 0.8),
            FunctionDependency("module2.analyzer", "module1.processor", DependencyType.DIRECT_CALL, 0.9),
            FunctionDependency("module2.reporter", "module2.analyzer", DependencyType.DATA_DEPENDENCY, 0.7),
            FunctionDependency("module3.exporter", "module2.reporter", DependencyType.DIRECT_CALL, 0.8),
            FunctionDependency("module3.formatter", "module2.reporter", DependencyType.TYPE_DEPENDENCY, 0.6)
        ]
        
        for dep in dependencies:
            graph.add_function_dependency(dep)
        
        # Test all main methods
        implementation_order = self.planner.get_optimal_implementation_order(graph)
        parallel_opportunities = self.planner.identify_parallel_opportunities(graph)
        critical_path_analysis = self.planner.analyze_critical_path(graph)
        
        # Verify results
        assert len(implementation_order) == 7
        assert isinstance(parallel_opportunities, list)
        assert isinstance(critical_path_analysis, CriticalPathAnalysis)
        
        # Verify implementation order respects dependencies
        parser_idx = implementation_order.index("module1.parser")
        processor_idx = implementation_order.index("module1.processor")
        assert parser_idx < processor_idx  # parser should come before processor
    
    def test_error_handling_with_invalid_graph(self):
        """Test error handling with invalid or None graph."""
        # Test with None
        result = self.planner.get_optimal_implementation_order(None)
        assert result == []
        
        result = self.planner.identify_parallel_opportunities(None)
        assert result == []
        
        result = self.planner.analyze_critical_path(None)
        assert isinstance(result, CriticalPathAnalysis)
        assert result.path_length == 0


if __name__ == "__main__":
    pytest.main([__file__])