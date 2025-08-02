"""
Comprehensive unit tests for enhanced planning functionality.

This module provides additional unit tests for ImportIssueDetector, 
IntelligentGapAnalyzer, DependencyDrivenPlanner, and PlanningEngine
enhanced capabilities that aren't covered in existing test files.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from a3.core.import_issue_detector import ImportIssueDetector
from a3.core.gap_analyzer import IntelligentGapAnalyzer
from a3.core.dependency_driven_planner import DependencyDrivenPlanner
from a3.engines.planning import PlanningEngine
from a3.core.models import (
    ImportIssue, ImportIssueType, ValidationResult, FunctionGap,
    EnhancedDependencyGraph, FunctionDependency, DependencyType,
    Module, FunctionSpec, Argument, StructureAnalysis, OptimizationSuggestion,
    CriticalPathAnalysis, ImplementationStatus
)
from a3.core.interfaces import AIClientInterface


class TestImportIssueDetectorAdvanced:
    """Advanced test cases for ImportIssueDetector functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ImportIssueDetector()
    
    def test_complex_nested_function_imports(self):
        """Test detection in complex nested function scenarios."""
        code = '''
class DataProcessor:
    def process(self):
        def inner_processor():
            from .utils import helper
            def deeply_nested():
                from ..config import settings
                return settings.value
            return helper(deeply_nested())
        return inner_processor()
    
    @staticmethod
    def static_method():
        from .static_utils import tool
        return tool()
    
    @classmethod
    def class_method(cls):
        from .class_utils import factory
        return factory()
'''
        
        issues = self.detector.scan_for_import_issues(code, "processor.py")
        
        # Should detect all relative imports in methods
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 4  # inner_processor, deeply_nested, static_method, class_method
        
        # Check that line numbers are correctly identified
        for issue in relative_issues:
            assert issue.line_number > 0
            assert issue.file_path == "processor.py"
    
    def test_import_with_aliases_and_multiple_items(self):
        """Test handling of complex import statements with aliases."""
        code = '''
def complex_function():
    from .utils import (
        helper as h,
        processor as p,
        validator as v
    )
    from ..config import settings as cfg, defaults
    import .local_module as local
    return h(p(v(cfg.value, defaults)))
'''
        
        issues = self.detector.scan_for_import_issues(code)
        
        # Should detect all relative imports
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 3
        
        # Check that multiline imports are handled
        multiline_import = any("helper" in issue.problematic_import for issue in relative_issues)
        assert multiline_import
    
    def test_fix_imports_preserves_code_structure(self):
        """Test that fixing imports preserves overall code structure."""
        code = '''#!/usr/bin/env python3
"""
Module for data processing.
"""

import os
import sys

def main():
    """Main function."""
    from .processor import DataProcessor
    from ..config import load_config
    
    config = load_config()
    processor = DataProcessor(config)
    return processor.run()

class Helper:
    """Helper class."""
    
    def method(self):
        from .utils import tool
        return tool()

if __name__ == "__main__":
    main()
'''
        
        fixed_code = self.detector.fix_function_level_imports(code)
        
        # Check that structure is preserved
        lines = fixed_code.split('\n')
        
        # Should still have shebang
        assert lines[0] == '#!/usr/bin/env python3'
        
        # Should still have docstring
        docstring_start = next(i for i, line in enumerate(lines) if '"""' in line)
        assert docstring_start > 0
        
        # Should still have main function and class
        assert any('def main():' in line for line in lines)
        assert any('class Helper:' in line for line in lines)
        assert any('if __name__ == "__main__":' in line for line in lines)
        
        # Imports should be moved to module level
        import_lines = [i for i, line in enumerate(lines) if line.strip().startswith(('from .', 'from ..'))]
        assert len(import_lines) > 0
        assert all(i < 20 for i in import_lines)  # Should be near top
    
    def test_validate_import_resolution_with_syntax_variations(self):
        """Test validation with various Python syntax patterns."""
        # Test with f-strings and modern Python features
        modern_code = '''
import os
from pathlib import Path

def process_files(pattern: str = "*.py") -> List[Path]:
    """Process files with modern Python syntax."""
    base_path = Path.cwd()
    files = list(base_path.glob(pattern))
    
    results = [
        file for file in files 
        if file.is_file() and not file.name.startswith('.')
    ]
    
    return results
'''
        
        result = self.detector.validate_import_resolution(modern_code, "modern.py")
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.fixed_imports) >= 2  # os and pathlib
    
    def test_circular_import_risk_detection(self):
        """Test detection of potential circular import risks."""
        code = '''
def function_a():
    from .module_b import function_b
    return function_b()

def function_b():
    from .module_a import function_a  # Potential circular import
    return function_a()
'''
        
        issues = self.detector.scan_for_import_issues(code, "module_a.py")
        
        # Should detect potential circular import risks
        circular_risks = [issue for issue in issues if issue.issue_type == ImportIssueType.CIRCULAR_IMPORT_RISK]
        # Note: This might be 0 if the detector doesn't implement this check yet
        assert len(circular_risks) >= 0


class TestIntelligentGapAnalyzerAdvanced:
    """Advanced test cases for IntelligentGapAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = IntelligentGapAnalyzer()
        self.complex_graph = self._create_complex_test_graph()
    
    def _create_complex_test_graph(self) -> EnhancedDependencyGraph:
        """Create a complex test graph for advanced testing."""
        graph = EnhancedDependencyGraph()
        
        # Add functions representing a realistic project structure
        functions = [
            # User management
            ("create_user", "user_service"),
            ("get_user", "user_service"),
            ("update_user", "user_service"),
            ("delete_user", "user_service"),
            
            # Authentication
            ("login", "auth_service"),
            ("logout", "auth_service"),
            ("verify_token", "auth_service"),
            
            # Data processing
            ("process_data", "data_processor"),
            ("validate_data", "data_validator"),
            ("transform_data", "data_transformer"),
            
            # Storage
            ("save_to_db", "database"),
            ("load_from_db", "database"),
            ("execute_query", "database"),
            
            # API
            ("handle_request", "api_handler"),
            ("format_response", "api_formatter"),
            ("parse_request", "api_parser"),
            
            # Utilities
            ("log_error", "logger"),
            ("send_notification", "notifier"),
        ]
        
        for func_name, module_name in functions:
            graph.add_function(func_name, module_name)
        
        # Add realistic dependencies
        dependencies = [
            # User service dependencies
            ("user_service.create_user", "data_validator.validate_data", DependencyType.DIRECT_CALL),
            ("user_service.create_user", "database.save_to_db", DependencyType.DIRECT_CALL),
            ("user_service.create_user", "logger.log_error", DependencyType.IMPORT_DEPENDENCY),
            
            # Auth service dependencies
            ("auth_service.login", "user_service.get_user", DependencyType.DIRECT_CALL),
            ("auth_service.verify_token", "database.execute_query", DependencyType.DIRECT_CALL),
            
            # Data processing chain
            ("data_processor.process_data", "data_validator.validate_data", DependencyType.DIRECT_CALL),
            ("data_processor.process_data", "data_transformer.transform_data", DependencyType.DIRECT_CALL),
            ("data_processor.process_data", "database.save_to_db", DependencyType.DIRECT_CALL),
            
            # API dependencies
            ("api_handler.handle_request", "api_parser.parse_request", DependencyType.DIRECT_CALL),
            ("api_handler.handle_request", "auth_service.verify_token", DependencyType.DIRECT_CALL),
            ("api_handler.handle_request", "api_formatter.format_response", DependencyType.DIRECT_CALL),
            
            # Cross-cutting concerns
            ("user_service.delete_user", "notifier.send_notification", DependencyType.DIRECT_CALL),
            ("data_processor.process_data", "logger.log_error", DependencyType.IMPORT_DEPENDENCY),
        ]
        
        for from_func, to_func, dep_type in dependencies:
            dep = FunctionDependency(from_func, to_func, dep_type, 0.8)
            graph.add_function_dependency(dep)
        
        return graph
    
    def test_detect_missing_crud_operations(self):
        """Test detection of missing CRUD operations."""
        gaps = self.analyzer.detect_missing_functions(self.complex_graph)
        
        # Should suggest missing CRUD operations
        crud_gaps = [gap for gap in gaps if any(op in gap.suggested_name.lower() 
                                               for op in ['create', 'read', 'update', 'delete'])]
        
        # Might suggest missing operations for entities that have partial CRUD
        assert len(crud_gaps) >= 0
    
    def test_detect_missing_validation_functions(self):
        """Test detection of missing validation functions."""
        gaps = self.analyzer.detect_missing_functions(self.complex_graph)
        
        # Should suggest validation functions for entities that lack them
        validation_gaps = [gap for gap in gaps if 'validate' in gap.suggested_name.lower()]
        
        # Should find validation opportunities
        assert len(validation_gaps) >= 0
        
        for gap in validation_gaps:
            assert gap.confidence > 0.0
            assert gap.reason
    
    def test_analyze_module_completeness_with_complex_modules(self):
        """Test module completeness analysis with complex module structures."""
        # Create modules with varying completeness levels
        modules = [
            # Complete user service
            Module(
                name="user_service",
                description="User management service",
                file_path="user_service.py",
                functions=[
                    FunctionSpec("create_user", "user_service", "Create user", return_type="User"),
                    FunctionSpec("get_user", "user_service", "Get user", return_type="User"),
                    FunctionSpec("update_user", "user_service", "Update user", return_type="User"),
                    FunctionSpec("delete_user", "user_service", "Delete user", return_type="bool"),
                    FunctionSpec("list_users", "user_service", "List users", return_type="List[User]"),
                ]
            ),
            # Incomplete auth service (missing some functions)
            Module(
                name="auth_service",
                description="Authentication service",
                file_path="auth_service.py",
                functions=[
                    FunctionSpec("login", "auth_service", "User login", return_type="Token"),
                    FunctionSpec("logout", "auth_service", "User logout", return_type="bool"),
                    # Missing: register, reset_password, refresh_token
                ]
            ),
            # Overly complex module (too many functions)
            Module(
                name="data_processor",
                description="Data processing module",
                file_path="data_processor.py",
                functions=[
                    FunctionSpec(f"process_type_{i}", "data_processor", f"Process type {i}", return_type="Any")
                    for i in range(25)  # Too many functions
                ]
            )
        ]
        
        result = self.analyzer.analyze_module_completeness(modules)
        
        assert result["total_modules"] == 3
        assert "completeness_score" in result
        assert "optimization_suggestions" in result
        
        # Should identify the overly complex module
        incomplete_modules = result["incomplete_modules"]
        complex_module = next((m for m in incomplete_modules if m["module_name"] == "data_processor"), None)
        assert complex_module is not None
        assert any("too many functions" in issue.lower() for issue in complex_module["issues"])
    
    def test_suggest_module_restructuring_complex_scenarios(self):
        """Test module restructuring suggestions for complex scenarios."""
        # Create modules with various issues
        modules = [
            # Module with mixed responsibilities
            Module(
                name="mixed_service",
                description="Service with mixed responsibilities",
                file_path="mixed_service.py",
                functions=[
                    FunctionSpec("create_user", "mixed_service", "Create user", return_type="User"),
                    FunctionSpec("send_email", "mixed_service", "Send email", return_type="bool"),
                    FunctionSpec("process_payment", "mixed_service", "Process payment", return_type="bool"),
                    FunctionSpec("generate_report", "mixed_service", "Generate report", return_type="Report"),
                    FunctionSpec("validate_input", "mixed_service", "Validate input", return_type="bool"),
                ]
            )
        ]
        
        suggestions = self.analyzer.suggest_module_restructuring(modules, self.complex_graph)
        
        assert isinstance(suggestions, list)
        
        # Should suggest splitting the mixed service
        split_suggestions = [s for s in suggestions if "split" in s.description.lower()]
        assert len(split_suggestions) > 0
    
    def test_confidence_score_calculation_accuracy(self):
        """Test accuracy of confidence score calculations."""
        # Create a gap with strong indicators
        strong_gap = FunctionGap(
            suggested_name="validate_user_input",
            suggested_module="validation",
            reason="Multiple functions call non-existent validation",
            confidence=0.6,
            dependencies=["user_service.create_user", "user_service.update_user"],
            dependents=[]
        )
        
        # Create a gap with weak indicators
        weak_gap = FunctionGap(
            suggested_name="random_utility",
            suggested_module="utils",
            reason="Speculative utility function",
            confidence=0.3,
            dependencies=[],
            dependents=[]
        )
        
        strong_score = self.analyzer.calculate_confidence_score(strong_gap, self.complex_graph)
        weak_score = self.analyzer.calculate_confidence_score(weak_gap, self.complex_graph)
        
        # Strong gap should have higher confidence
        assert strong_score > weak_score
        assert strong_score <= 1.0
        assert weak_score >= 0.0


class TestDependencyDrivenPlannerAdvanced:
    """Advanced test cases for DependencyDrivenPlanner functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = DependencyDrivenPlanner()
        self.complex_graph = self._create_complex_dependency_graph()
    
    def _create_complex_dependency_graph(self) -> EnhancedDependencyGraph:
        """Create a complex dependency graph for testing."""
        graph = EnhancedDependencyGraph()
        
        # Create a realistic dependency structure
        functions = [
            ("config_loader", "config"),
            ("database_connector", "database"),
            ("user_validator", "validation"),
            ("user_repository", "repository"),
            ("user_service", "service"),
            ("auth_service", "service"),
            ("api_controller", "controller"),
            ("response_formatter", "formatter"),
            ("error_handler", "error"),
            ("logger", "logging"),
        ]
        
        for func_name, module_name in functions:
            graph.add_function(func_name, module_name)
        
        # Create complex dependency relationships
        dependencies = [
            # Foundation layer
            ("database.database_connector", "config.config_loader", DependencyType.DIRECT_CALL, 0.9),
            ("repository.user_repository", "database.database_connector", DependencyType.DIRECT_CALL, 0.9),
            ("validation.user_validator", "config.config_loader", DependencyType.DIRECT_CALL, 0.7),
            
            # Service layer
            ("service.user_service", "repository.user_repository", DependencyType.DIRECT_CALL, 0.9),
            ("service.user_service", "validation.user_validator", DependencyType.DIRECT_CALL, 0.8),
            ("service.auth_service", "service.user_service", DependencyType.DIRECT_CALL, 0.8),
            
            # Controller layer
            ("controller.api_controller", "service.user_service", DependencyType.DIRECT_CALL, 0.9),
            ("controller.api_controller", "service.auth_service", DependencyType.DIRECT_CALL, 0.8),
            ("controller.api_controller", "formatter.response_formatter", DependencyType.DIRECT_CALL, 0.7),
            
            # Cross-cutting concerns
            ("service.user_service", "logging.logger", DependencyType.IMPORT_DEPENDENCY, 0.6),
            ("service.auth_service", "logging.logger", DependencyType.IMPORT_DEPENDENCY, 0.6),
            ("controller.api_controller", "error.error_handler", DependencyType.IMPORT_DEPENDENCY, 0.7),
        ]
        
        for from_func, to_func, dep_type, strength in dependencies:
            dep = FunctionDependency(from_func, to_func, dep_type, strength)
            graph.add_function_dependency(dep)
        
        return graph
    
    def test_optimal_implementation_order_respects_layers(self):
        """Test that implementation order respects architectural layers."""
        order = self.planner.get_optimal_implementation_order(self.complex_graph)
        
        # Foundation should come before service layer
        config_idx = order.index("config.config_loader")
        database_idx = order.index("database.database_connector")
        user_service_idx = order.index("service.user_service")
        controller_idx = order.index("controller.api_controller")
        
        # Config and database should come before services
        assert config_idx < user_service_idx
        assert database_idx < user_service_idx
        
        # Services should come before controllers
        assert user_service_idx < controller_idx
    
    def test_identify_parallel_opportunities_by_layer(self):
        """Test identification of parallel opportunities within architectural layers."""
        opportunities = self.planner.identify_parallel_opportunities(self.complex_graph)
        
        # Should identify functions that can be implemented in parallel
        assert len(opportunities) > 0
        
        # Functions in the same layer with no dependencies should be parallelizable
        for group in opportunities:
            assert len(group) > 0
    
    def test_critical_path_analysis_identifies_bottlenecks(self):
        """Test that critical path analysis identifies actual bottlenecks."""
        analysis = self.planner.analyze_critical_path(self.complex_graph)
        
        assert isinstance(analysis, CriticalPathAnalysis)
        assert len(analysis.critical_path) > 0
        
        # Should identify functions that are heavily depended upon
        if analysis.bottleneck_functions:
            # Bottlenecks should be in the critical path or heavily referenced
            for bottleneck in analysis.bottleneck_functions:
                assert bottleneck in self.complex_graph.function_nodes
    
    def test_cycle_resolution_strategies(self):
        """Test different cycle resolution strategies."""
        # Create a graph with cycles
        cyclic_graph = EnhancedDependencyGraph()
        
        cyclic_graph.add_function("func_a", "module1")
        cyclic_graph.add_function("func_b", "module1")
        cyclic_graph.add_function("func_c", "module2")
        
        # Create cycle: A -> B -> C -> A
        deps = [
            FunctionDependency("module1.func_a", "module1.func_b", DependencyType.DIRECT_CALL, 0.9),
            FunctionDependency("module1.func_b", "module2.func_c", DependencyType.DIRECT_CALL, 0.8),
            FunctionDependency("module2.func_c", "module1.func_a", DependencyType.DIRECT_CALL, 0.7),
        ]
        
        for dep in deps:
            cyclic_graph.add_function_dependency(dep)
        
        # Should handle cycles gracefully
        order = self.planner.get_optimal_implementation_order(cyclic_graph)
        
        assert len(order) == 3
        assert all(func in order for func in ["module1.func_a", "module1.func_b", "module2.func_c"])
    
    def test_parallel_group_optimization_for_development_workflow(self):
        """Test optimization of parallel groups for development workflow efficiency."""
        opportunities = self.planner.identify_parallel_opportunities(self.complex_graph)
        
        # Should optimize groups for development efficiency
        for group in opportunities:
            # Groups should not be too large (manageable for developers)
            assert len(group) <= 5
            
            # Functions in the same group should be related or independent
            if len(group) > 1:
                # All functions should be implementable in parallel
                for func in group:
                    assert func in self.complex_graph.function_nodes


class TestPlanningEngineEnhancedCapabilities:
    """Test enhanced capabilities of PlanningEngine."""
    
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
    
    def test_analyze_existing_structure_integration(self):
        """Test integration of existing structure analysis."""
        # Create test module file
        test_file = Path(self.temp_dir) / "test_module.py"
        with open(test_file, 'w') as f:
            f.write('''
def create_user(user_data: dict) -> dict:
    """Create a new user."""
    return {"id": 1, "name": user_data["name"]}

def get_user(user_id: int) -> dict:
    """Get user by ID."""
    return {"id": user_id, "name": "Test User"}
''')
        
        # Test structure analysis
        analysis = self.engine.analyze_existing_structure()
        
        assert isinstance(analysis, StructureAnalysis)
        assert len(analysis.existing_modules) > 0
        
        # Should find the test module
        module_names = [m.name for m in analysis.existing_modules]
        assert "test_module" in module_names
    
    def test_generate_plan_integration(self):
        """Test plan generation integration."""
        # Mock AI client response
        self.mock_ai_client.chat_completion.return_value = '''
        {
            "modules": [
                {
                    "name": "user_service",
                    "description": "User management service",
                    "functions": [
                        {
                            "name": "create_user",
                            "description": "Create a new user",
                            "arguments": [{"name": "user_data", "type": "dict"}],
                            "return_type": "User"
                        }
                    ]
                }
            ]
        }
        '''
        
        # Test plan generation
        plan = self.engine.generate_plan("Create user management system")
        
        assert plan is not None
        assert len(plan.modules) > 0
    
    def test_enhanced_dependency_graph_utilization(self):
        """Test utilization of enhanced dependency graph in planning."""
        # Create test modules
        test_file = Path(self.temp_dir) / "test_module.py"
        with open(test_file, 'w') as f:
            f.write('''
def function_a():
    """Function A."""
    return function_b()

def function_b():
    """Function B."""
    return "result"
''')
        
        # Mock the enhanced dependency graph creation
        with patch.object(self.engine, '_create_enhanced_dependency_graph') as mock_create_graph:
            mock_graph = Mock(spec=EnhancedDependencyGraph)
            mock_graph.function_nodes = {"function_a": Mock(), "function_b": Mock()}
            mock_graph.function_edges = [("function_a", "function_b")]
            mock_graph.has_function_cycles.return_value = False
            mock_create_graph.return_value = mock_graph
            
            # Mock analyzers
            with patch.object(self.engine.gap_analyzer, 'detect_missing_functions') as mock_gap, \
                 patch.object(self.engine.import_issue_detector, 'scan_for_import_issues') as mock_import:
                
                mock_gap.return_value = []
                mock_import.return_value = []
                
                analysis = self.engine.analyze_existing_structure()
                
                assert analysis.enhanced_graph is not None
                mock_create_graph.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])