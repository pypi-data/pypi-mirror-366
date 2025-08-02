"""
Tests for PlanningEngine structure analysis functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from a3.engines.planning import PlanningEngine
from a3.core.models import (
    StructureAnalysis, Module, FunctionSpec, Argument, 
    ImplementationStatus, EnhancedDependencyGraph
)
from a3.core.interfaces import AIClientInterface


class TestPlanningEngineStructureAnalysis:
    """Test cases for PlanningEngine structure analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_client = Mock(spec=AIClientInterface)
        self.temp_dir = tempfile.mkdtemp()
        self.engine = PlanningEngine(
            ai_client=self.mock_ai_client,
            project_path=self.temp_dir
        )
        self.engine.initialize()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_existing_structure_empty_project(self):
        """Test analyzing structure of empty project."""
        analysis = self.engine.analyze_existing_structure()
        
        assert isinstance(analysis, StructureAnalysis)
        assert analysis.existing_modules == []
        assert analysis.enhanced_graph is None
        assert analysis.complexity_metrics == {}
        assert analysis.missing_functions == []
        assert analysis.import_issues == []
    
    def test_analyze_existing_structure_with_modules(self):
        """Test analyzing structure with existing modules."""
        # Create test Python files
        test_module_content = '''
"""Test module for structure analysis."""

def test_function(arg1: str, arg2: int = 5) -> str:
    """Test function with arguments."""
    return f"{arg1}_{arg2}"

def another_function() -> None:
    """Another test function."""
    pass
'''
        
        test_file = Path(self.temp_dir) / "sample_module.py"
        with open(test_file, 'w') as f:
            f.write(test_module_content)
        
        # Mock the gap analyzer and import issue detector
        with patch.object(self.engine.gap_analyzer, 'detect_missing_functions') as mock_gap, \
             patch.object(self.engine.gap_analyzer, 'analyze_module_completeness') as mock_completeness, \
             patch.object(self.engine.import_issue_detector, 'scan_for_import_issues') as mock_import:
            
            mock_gap.return_value = []
            mock_completeness.return_value = []
            mock_import.return_value = []
            
            analysis = self.engine.analyze_existing_structure()
        
        assert isinstance(analysis, StructureAnalysis)
        assert len(analysis.existing_modules) == 1
        
        module = analysis.existing_modules[0]
        assert module.name == "sample_module"
        assert len(module.functions) == 2
        
        # Check first function
        func1 = next(f for f in module.functions if f.name == "test_function")
        assert func1.module == "sample_module"
        assert len(func1.arguments) == 2
        assert func1.arguments[0].name == "arg1"
        assert func1.arguments[0].type_hint == "str"
        assert func1.arguments[1].name == "arg2"
        assert func1.arguments[1].type_hint == "int"
        assert func1.return_type == "str"
        assert func1.implementation_status == ImplementationStatus.COMPLETED
        
        # Check second function
        func2 = next(f for f in module.functions if f.name == "another_function")
        assert func2.module == "sample_module"
        assert len(func2.arguments) == 0
        assert func2.return_type == "None"
    
    def test_analyze_existing_structure_with_nested_modules(self):
        """Test analyzing structure with nested module structure."""
        # Create nested directory structure
        nested_dir = Path(self.temp_dir) / "utils"
        nested_dir.mkdir()
        
        nested_module_content = '''
"""Nested utility module."""

def utility_function(data: dict) -> bool:
    """Utility function in nested module."""
    return bool(data)
'''
        
        nested_file = nested_dir / "helpers.py"
        with open(nested_file, 'w') as f:
            f.write(nested_module_content)
        
        # Mock the analyzers
        with patch.object(self.engine.gap_analyzer, 'detect_missing_functions') as mock_gap, \
             patch.object(self.engine.gap_analyzer, 'analyze_module_completeness') as mock_completeness, \
             patch.object(self.engine.import_issue_detector, 'scan_for_import_issues') as mock_import:
            
            mock_gap.return_value = []
            mock_completeness.return_value = []
            mock_import.return_value = []
            
            analysis = self.engine.analyze_existing_structure()
        
        assert len(analysis.existing_modules) == 1
        
        module = analysis.existing_modules[0]
        assert module.name == "utils.helpers"
        assert len(module.functions) == 1
        
        func = module.functions[0]
        assert func.name == "utility_function"
        assert func.module == "utils.helpers"
        assert len(func.arguments) == 1
        assert func.arguments[0].name == "data"
        assert func.arguments[0].type_hint == "dict"
        assert func.return_type == "bool"
    
    def test_extract_complexity_metrics(self):
        """Test complexity metrics extraction."""
        # Create a mock enhanced dependency graph
        enhanced_graph = Mock(spec=EnhancedDependencyGraph)
        
        # Mock function nodes
        mock_func_node1 = Mock()
        mock_func_node1.module = "module1"
        mock_func_node2 = Mock()
        mock_func_node2.module = "module2"
        
        enhanced_graph.function_nodes = {
            "func1": mock_func_node1,
            "func2": mock_func_node2
        }
        enhanced_graph.function_edges = [("func1", "func2")]
        enhanced_graph.has_function_cycles.return_value = False
        
        metrics = self.engine._extract_complexity_metrics(enhanced_graph)
        
        assert metrics['total_functions'] == 2
        assert metrics['total_modules'] == 2
        assert metrics['total_dependencies'] == 1
        assert 'dependency_density' in metrics
        assert 'function_dependencies' in metrics
        assert 'module_coupling' in metrics
        assert metrics['has_circular_dependencies'] is False
    
    def test_extract_complexity_metrics_empty_graph(self):
        """Test complexity metrics extraction with empty graph."""
        enhanced_graph = Mock(spec=EnhancedDependencyGraph)
        enhanced_graph.function_nodes = {}
        enhanced_graph.function_edges = []
        
        metrics = self.engine._extract_complexity_metrics(enhanced_graph)
        
        assert metrics == {}
    
    def test_discover_existing_modules_skips_test_files(self):
        """Test that module discovery skips test files."""
        # Create test files
        test_file = Path(self.temp_dir) / "test_something.py"
        with open(test_file, 'w') as f:
            f.write("def test_func(): pass")
        
        regular_file = Path(self.temp_dir) / "regular_module.py"
        with open(regular_file, 'w') as f:
            f.write("def regular_func(): pass")
        
        modules = self.engine._discover_existing_modules(self.temp_dir)
        
        # Should only find the regular module, not the test file
        assert len(modules) == 1
        assert modules[0].name == "regular_module"
    
    def test_discover_existing_modules_skips_private_functions(self):
        """Test that module discovery skips private functions."""
        module_content = '''
def public_function():
    """Public function."""
    pass

def _private_function():
    """Private function."""
    pass

def __dunder_function__():
    """Dunder function."""
    pass
'''
        
        test_file = Path(self.temp_dir) / "sample_module.py"
        with open(test_file, 'w') as f:
            f.write(module_content)
        
        modules = self.engine._discover_existing_modules(self.temp_dir)
        
        assert len(modules) == 1
        module = modules[0]
        assert len(module.functions) == 1
        assert module.functions[0].name == "public_function"
    
    def test_analyze_existing_structure_integration_with_analyzers(self):
        """Test integration with gap analyzer and import issue detector."""
        # Create test module
        test_module_content = '''
def existing_function():
    """Existing function."""
    pass
'''
        
        test_file = Path(self.temp_dir) / "sample_module.py"
        with open(test_file, 'w') as f:
            f.write(test_module_content)
        
        # Mock analyzer responses
        from a3.core.models import FunctionGap, ImportIssue, ImportIssueType, OptimizationSuggestion
        
        mock_gap = FunctionGap(
            suggested_name="missing_function",
            suggested_module="sample_module",
            reason="Pattern analysis suggests this function is needed",
            confidence=0.8,
            dependencies=[],
            dependents=["sample_module.existing_function"]
        )
        
        mock_issue = ImportIssue(
            file_path="sample_module.py",
            line_number=5,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from . import something",
            suggested_fix="from sample_module import something",
            context="def function():"
        )
        
        mock_optimization = OptimizationSuggestion(
            suggestion_type="refactor",
            description="Consider breaking down complex function",
            affected_modules=["sample_module"],
            priority="medium",
            estimated_effort="medium"
        )
        
        with patch.object(self.engine.gap_analyzer, 'detect_missing_functions') as mock_gap_detect, \
             patch.object(self.engine.gap_analyzer, 'analyze_module_completeness') as mock_completeness, \
             patch.object(self.engine.import_issue_detector, 'scan_for_import_issues') as mock_import_scan:
            
            mock_gap_detect.return_value = [mock_gap]
            mock_completeness.return_value = [mock_optimization]
            mock_import_scan.return_value = [mock_issue]
            
            analysis = self.engine.analyze_existing_structure()
        
        assert len(analysis.missing_functions) == 1
        assert analysis.missing_functions[0].suggested_name == "missing_function"
        
        assert len(analysis.import_issues) == 1
        assert analysis.import_issues[0].issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION
        
        assert len(analysis.optimization_opportunities) == 1
        assert analysis.optimization_opportunities[0].suggestion_type == "refactor"
    
    def test_analyze_existing_structure_handles_file_errors(self):
        """Test that structure analysis handles file reading errors gracefully."""
        # Create a file with invalid Python syntax
        invalid_file = Path(self.temp_dir) / "invalid.py"
        with open(invalid_file, 'w') as f:
            f.write("def invalid_syntax(:\n    pass")
        
        # Should not raise an exception, just skip the invalid file
        analysis = self.engine.analyze_existing_structure()
        
        assert isinstance(analysis, StructureAnalysis)
        assert analysis.existing_modules == []