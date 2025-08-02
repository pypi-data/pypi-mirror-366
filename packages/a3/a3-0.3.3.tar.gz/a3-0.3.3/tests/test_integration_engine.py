"""
Tests for the IntegrationEngine class.

This module contains unit tests for the integration engine functionality
including import generation, module integration, and verification.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import os

from a3.engines.integration import IntegrationEngine, IntegrationError, ImportGenerationError
from a3.core.models import (
    Module, FunctionSpec, IntegrationResult, ValidationResult, 
    DependencyGraph, Argument
)
from a3.core.interfaces import DependencyAnalyzerInterface, FileSystemManagerInterface


class TestIntegrationEngine:
    """Test cases for IntegrationEngine class."""
    
    @pytest.fixture
    def mock_dependency_analyzer(self):
        """Create a mock dependency analyzer."""
        analyzer = Mock(spec=DependencyAnalyzerInterface)
        analyzer.get_build_order.return_value = ["module_a", "module_b", "module_c"]
        analyzer.detect_circular_dependencies.return_value = []
        # Add the missing method
        analyzer.create_dependency_graph.return_value = Mock()
        analyzer.validate_dependency_graph.return_value = ValidationResult(
            is_valid=True, issues=[], warnings=[]
        )
        return analyzer
    
    @pytest.fixture
    def mock_filesystem_manager(self):
        """Create a mock filesystem manager."""
        manager = Mock(spec=FileSystemManagerInterface)
        manager.file_exists.return_value = True
        manager.read_file.return_value = '"""\nModule docstring\n"""\n\n'
        manager.write_file.return_value = True
        return manager
    
    @pytest.fixture
    def sample_modules(self):
        """Create sample modules for testing."""
        module_a = Module(
            name="module_a",
            description="Module A",
            file_path="src/module_a.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="func_a",
                    module="module_a",
                    docstring="Function A",
                    arguments=[],
                    return_type="str"
                )
            ]
        )
        
        module_b = Module(
            name="module_b", 
            description="Module B",
            file_path="src/module_b.py",
            dependencies=["module_a"],
            functions=[
                FunctionSpec(
                    name="func_b",
                    module="module_b",
                    docstring="Function B",
                    arguments=[
                        Argument(name="param1", type_hint="str", description="Parameter 1")
                    ],
                    return_type="int"
                )
            ]
        )
        
        module_c = Module(
            name="module_c",
            description="Module C", 
            file_path="src/module_c.py",
            dependencies=["module_a", "module_b"],
            functions=[
                FunctionSpec(
                    name="func_c",
                    module="module_c",
                    docstring="Function C",
                    arguments=[],
                    return_type="None"
                )
            ]
        )
        
        return [module_a, module_b, module_c]
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        from a3.core.interfaces import AIClientInterface
        client = Mock(spec=AIClientInterface)
        client.validate_api_key.return_value = True
        return client
    
    @pytest.fixture
    def integration_engine(self, mock_dependency_analyzer, mock_filesystem_manager, mock_ai_client):
        """Create an IntegrationEngine instance with mocked dependencies."""
        engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager,
            ai_client=mock_ai_client
        )
        engine.initialize()
        return engine
    
    def test_initialization(self, mock_dependency_analyzer, mock_filesystem_manager):
        """Test IntegrationEngine initialization."""
        engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        
        assert engine.dependency_analyzer is mock_dependency_analyzer
        assert engine.filesystem_manager is mock_filesystem_manager
        assert not engine._initialized
        
        engine.initialize()
        assert engine._initialized
    
    def test_validate_prerequisites_success(self, integration_engine):
        """Test successful prerequisite validation."""
        result = integration_engine.validate_prerequisites()
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_validate_prerequisites_missing_dependencies(self):
        """Test prerequisite validation with missing dependencies."""
        engine = IntegrationEngine()
        engine.initialize()
        
        result = engine.validate_prerequisites()
        
        assert not result.is_valid
        assert "Dependency analyzer is required" in str(result.issues)
        assert "File system manager is required" in str(result.issues)
    
    def test_generate_imports_empty_modules(self, integration_engine):
        """Test import generation with empty module list."""
        result = integration_engine.generate_imports([])
        
        assert result == {}
    
    def test_generate_imports_no_dependencies(self, integration_engine):
        """Test import generation for modules with no dependencies."""
        modules = [
            Module(
                name="standalone",
                description="Standalone module",
                file_path="standalone.py",
                dependencies=[],
                functions=[]
            )
        ]
        
        result = integration_engine.generate_imports(modules)
        
        assert result == {"standalone": []}
    
    def test_generate_imports_with_dependencies(self, integration_engine, sample_modules):
        """Test import generation for modules with dependencies."""
        result = integration_engine.generate_imports(sample_modules)
        
        # Check that imports were generated
        assert "module_a" in result
        assert "module_b" in result  
        assert "module_c" in result
        
        # Module A has no dependencies
        assert result["module_a"] == []
        
        # Module B depends on Module A
        assert len(result["module_b"]) > 0
        assert any("module_a" in imp for imp in result["module_b"])
        
        # Module C depends on both A and B
        assert len(result["module_c"]) > 0
        assert any("module_a" in imp for imp in result["module_c"])
        assert any("module_b" in imp for imp in result["module_c"])
    
    def test_generate_import_statement(self, integration_engine):
        """Test generation of individual import statements."""
        from_module = Module(
            name="from_mod",
            description="From module",
            file_path="src/from_mod.py",
            dependencies=["to_mod"]
        )
        
        to_module = Module(
            name="to_mod",
            description="To module", 
            file_path="src/to_mod.py",
            dependencies=[]
        )
        
        # Test the private method
        import_stmt = integration_engine._generate_import_statement(from_module, to_module)
        
        assert import_stmt is not None
        assert "to_mod" in import_stmt
        assert import_stmt.startswith("from")
    
    def test_integrate_modules_empty_list(self, integration_engine):
        """Test module integration with empty module list."""
        result = integration_engine.integrate_modules([])
        
        assert result.success
        assert result.integrated_modules == []
        assert result.import_errors == []
    
    def test_integrate_modules_success(self, integration_engine, sample_modules):
        """Test successful module integration."""
        # Mock file content with expected functions
        def mock_read_file(path):
            if "module_a" in path:
                return '''
"""Module A"""

def func_a():
    pass
'''
            elif "module_b" in path:
                return '''
"""Module B"""

def func_b(param1: str) -> int:
    pass
'''
            elif "module_c" in path:
                return '''
"""Module C"""

def func_c() -> None:
    pass
'''
            return '"""Default module"""'
        
        integration_engine.filesystem_manager.read_file.side_effect = mock_read_file
        
        result = integration_engine.integrate_modules(sample_modules)
        
        assert result.success
        assert len(result.integrated_modules) == 3
        assert "module_a" in result.integrated_modules
        assert "module_b" in result.integrated_modules
        assert "module_c" in result.integrated_modules
        assert len(result.import_errors) == 0
    
    def test_integrate_modules_with_filesystem_error(self, integration_engine, sample_modules):
        """Test module integration with filesystem errors."""
        # Make filesystem operations fail
        integration_engine.filesystem_manager.write_file.return_value = False
        
        result = integration_engine.integrate_modules(sample_modules)
        
        assert not result.success
        assert len(result.import_errors) > 0
    
    def test_verify_integration_empty_modules(self, integration_engine):
        """Test integration verification with empty module list."""
        result = integration_engine.verify_integration([])
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_verify_integration_missing_files(self, integration_engine, sample_modules):
        """Test integration verification with missing module files."""
        # Make file existence check fail
        integration_engine.filesystem_manager.file_exists.return_value = False
        
        result = integration_engine.verify_integration(sample_modules)
        
        assert not result.is_valid
        assert len(result.issues) > 0
        assert any("does not exist" in issue for issue in result.issues)
    
    def test_verify_integration_success(self, integration_engine, sample_modules):
        """Test successful integration verification."""
        # Mock file content with valid Python that includes the expected functions
        def mock_read_file(path):
            if "module_a" in path:
                return '''
"""Module A"""

def func_a():
    pass
'''
            elif "module_b" in path:
                return '''
"""Module B"""

def func_b(param1: str) -> int:
    pass
'''
            elif "module_c" in path:
                return '''
"""Module C"""

def func_c() -> None:
    pass
'''
            return '"""Default module"""'
        
        integration_engine.filesystem_manager.read_file.side_effect = mock_read_file
        
        result = integration_engine.verify_integration(sample_modules)
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_insert_imports_into_content(self, integration_engine):
        """Test insertion of imports into module content."""
        content = '''"""
Module docstring
"""

def existing_function():
    pass
'''
        
        imports = ["from .other_module import *", "from .another_module import func"]
        
        result = integration_engine._insert_imports_into_content(content, imports)
        
        assert "from .other_module import *" in result
        assert "from .another_module import func" in result
        assert "def existing_function():" in result
        
        # Check that imports are placed after docstring
        lines = result.split('\n')
        docstring_end = None
        import_start = None
        
        for i, line in enumerate(lines):
            if '"""' in line and docstring_end is None:
                # Find the end of docstring
                if line.count('"""') == 2:
                    docstring_end = i
                else:
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j]:
                            docstring_end = j
                            break
            if line.strip().startswith('from .'):
                import_start = i
                break
        
        if docstring_end is not None and import_start is not None:
            assert import_start > docstring_end
    
    def test_find_import_insertion_position(self, integration_engine):
        """Test finding the correct position to insert imports."""
        lines = [
            '"""',
            'Module docstring',
            '"""',
            '',
            'import os',
            'from typing import List',
            '',
            'def function():',
            '    pass'
        ]
        
        position = integration_engine._find_import_insertion_position(lines)
        
        # Should insert after existing imports
        assert position == 6  # After the blank line following imports
    
    def test_extract_imports_from_ast(self, integration_engine):
        """Test extraction of imports from AST."""
        import ast
        
        code = '''
import os
import sys as system
from typing import List, Dict
from .relative_module import func
'''
        
        tree = ast.parse(code)
        imports = integration_engine._extract_imports_from_ast(tree)
        
        assert len(imports) >= 4
        
        # Check for different import types
        import_statements = [imp['statement'] for imp in imports]
        assert any('import os' in stmt for stmt in import_statements)
        assert any('import sys as system' in stmt for stmt in import_statements)
        assert any('from typing import' in stmt for stmt in import_statements)
        assert any('from .relative_module import func' in stmt for stmt in import_statements)
    
    def test_circular_dependency_detection(self, integration_engine):
        """Test detection of circular import dependencies."""
        # Create modules with circular dependencies
        module_x = Module(
            name="module_x",
            description="Module X",
            file_path="module_x.py",
            dependencies=["module_y"]
        )
        
        module_y = Module(
            name="module_y", 
            description="Module Y",
            file_path="module_y.py",
            dependencies=["module_x"]
        )
        
        modules = [module_x, module_y]
        
        # Mock dependency analyzer to return circular dependency
        integration_engine.dependency_analyzer.detect_circular_dependencies.return_value = [
            ["module_x", "module_y"]
        ]
        
        result = integration_engine.verify_integration(modules)
        
        # Should detect the circular dependency
        assert not result.is_valid or len(result.warnings) > 0
    
    def test_error_handling_in_import_generation(self, integration_engine):
        """Test error handling during import generation."""
        # Create a module with invalid file path
        invalid_module = Module(
            name="invalid",
            description="Invalid module",
            file_path="",  # Invalid path
            dependencies=["other"]
        )
        
        modules = [invalid_module]
        
        # Should handle the error gracefully
        try:
            result = integration_engine.generate_imports(modules)
            # Should return empty imports for invalid module
            assert "invalid" in result
        except ImportGenerationError:
            # Or raise appropriate error
            pass
    
    def test_module_validation_for_integration(self, integration_engine):
        """Test module validation before integration."""
        # Create modules with various issues
        duplicate_module1 = Module(
            name="duplicate",
            description="First duplicate",
            file_path="dup1.py",
            dependencies=[]
        )
        
        duplicate_module2 = Module(
            name="duplicate", 
            description="Second duplicate",
            file_path="dup2.py",
            dependencies=[]
        )
        
        missing_dep_module = Module(
            name="missing_dep",
            description="Module with missing dependency",
            file_path="missing.py",
            dependencies=["nonexistent"]
        )
        
        modules = [duplicate_module1, duplicate_module2, missing_dep_module]
        
        # Test validation
        errors = integration_engine._validate_modules_for_integration(modules)
        
        assert len(errors) > 0
        assert any("Duplicate module names" in error for error in errors)
        assert any("depends on missing module" in error for error in errors)
    
    def test_comprehensive_module_verification(self, integration_engine):
        """Test comprehensive verification of individual modules."""
        # Mock file content with syntax error
        integration_engine.filesystem_manager.read_file.return_value = '''
"""Module with syntax error"""

def broken_function(
    # Missing closing parenthesis and colon
    pass
'''
        
        module = Module(
            name="broken",
            description="Broken module",
            file_path="broken.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="broken_function",
                    module="broken",
                    docstring="Broken function",
                    arguments=[],
                    return_type="None"
                )
            ]
        )
        
        issues, warnings = integration_engine._comprehensive_module_verification(module, [module])
        
        assert len(issues) > 0
        assert any("Syntax error" in issue for issue in issues)
    
    def test_module_connection_with_dependencies(self, integration_engine, sample_modules):
        """Test connecting modules with their dependencies."""
        # Test connecting module B which depends on module A
        module_b = sample_modules[1]  # module_b depends on module_a
        imports = ["from .module_a import *"]
        
        result = integration_engine._connect_module(module_b, sample_modules, imports)
        
        assert result.success
        assert len(result.errors) == 0
    
    def test_dependency_graph_consistency_verification(self, integration_engine, sample_modules):
        """Test verification of dependency graph consistency."""
        # Mock dependency analyzer to return validation result
        integration_engine.dependency_analyzer.create_dependency_graph.return_value = Mock()
        integration_engine.dependency_analyzer.validate_dependency_graph.return_value = ValidationResult(
            is_valid=True, issues=[], warnings=[]
        )
        
        issues = integration_engine._verify_dependency_graph_consistency(sample_modules)
        
        assert len(issues) == 0
    
    def test_module_function_verification(self, integration_engine):
        """Test verification that expected functions are present."""
        content = '''
"""Test module"""

def existing_function():
    pass

def another_function():
    pass
'''
        
        module = Module(
            name="test_mod",
            description="Test module",
            file_path="test.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="existing_function",
                    module="test_mod",
                    docstring="Existing function",
                    arguments=[],
                    return_type="None"
                ),
                FunctionSpec(
                    name="missing_function",
                    module="test_mod", 
                    docstring="Missing function",
                    arguments=[],
                    return_type="None"
                )
            ]
        )
        
        issues = integration_engine._verify_module_functions(module, content)
        
        assert len(issues) == 1
        assert "missing_function" in issues[0]
        assert "not found" in issues[0]
    
    def test_relative_import_resolution(self, integration_engine):
        """Test resolution of relative imports."""
        current_module = Module(
            name="current",
            description="Current module",
            file_path="src/subdir/current.py",
            dependencies=[]
        )
        
        target_module = Module(
            name="target",
            description="Target module", 
            file_path="src/target.py",
            dependencies=[]
        )
        
        all_modules = [current_module, target_module]
        
        # Test relative import resolution
        resolved = integration_engine._resolve_relative_import("target", 1, current_module, all_modules)
        
        # Should be able to resolve or return None gracefully
        assert resolved is None or resolved == target_module


class TestIntegrationEngineIntegration:
    """Integration tests for IntegrationEngine with real file operations."""
    
    def test_real_file_operations(self):
        """Test integration engine with real file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create real filesystem manager
            from a3.managers.filesystem import FileSystemManager
            fs_manager = FileSystemManager(temp_dir)
            fs_manager.initialize()
            
            # Create real dependency analyzer
            from a3.managers.dependency import DependencyAnalyzer
            dep_analyzer = DependencyAnalyzer(temp_dir)
            
            # Create integration engine
            engine = IntegrationEngine(
                dependency_analyzer=dep_analyzer,
                filesystem_manager=fs_manager
            )
            engine.initialize()
            
            # Create test modules
            modules = [
                Module(
                    name="base",
                    description="Base module",
                    file_path="base.py",
                    dependencies=[],
                    functions=[]
                ),
                Module(
                    name="derived",
                    description="Derived module",
                    file_path="derived.py", 
                    dependencies=["base"],
                    functions=[]
                )
            ]
            
            # Create module files
            fs_manager.write_file("base.py", '"""Base module"""\n\ndef base_func():\n    pass\n')
            fs_manager.write_file("derived.py", '"""Derived module"""\n\ndef derived_func():\n    pass\n')
            
            # Test import generation
            imports = engine.generate_imports(modules)
            assert "base" in imports
            assert "derived" in imports
            assert len(imports["derived"]) > 0  # Should have imports for base
            
            # Test integration
            result = engine.integrate_modules(modules)
            assert result.success
            
            # Test verification
            verification = engine.verify_integration(modules)
            assert verification.is_valid


if __name__ == "__main__":
    pytest.main([__file__])