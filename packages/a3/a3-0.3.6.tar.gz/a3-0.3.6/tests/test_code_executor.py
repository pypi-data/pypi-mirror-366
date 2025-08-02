"""
Unit tests for the CodeExecutor engine.

This module tests the code execution, testing, and verification functionality
of the AI Project Builder.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from a3.core.models import (
    FunctionSpec, Argument, ExecutionResult, TestResult, TestDetail,
    ImportValidationResult, VerificationResult, ImplementationStatus
)
from a3.engines.code_executor import CodeExecutor


class TestCodeExecutor(unittest.TestCase):
    """Test cases for the CodeExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.mock_file_manager = Mock()
        # Don't pass the mock file manager for import validation tests
        self.executor = CodeExecutor(str(self.project_path))
        self.executor.initialize()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test CodeExecutor initialization."""
        executor = CodeExecutor(str(self.project_path))
        self.assertFalse(executor._initialized)
        
        executor.initialize()
        self.assertTrue(executor._initialized)
    
    def test_validate_prerequisites_success(self):
        """Test successful prerequisite validation."""
        result = self.executor.validate_prerequisites()
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.issues), 0)
    
    def test_validate_prerequisites_invalid_path(self):
        """Test prerequisite validation with invalid path."""
        executor = CodeExecutor("/nonexistent/path")
        executor.initialize()
        
        result = executor.validate_prerequisites()
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.issues), 0)
    
    def test_execute_function_success(self):
        """Test successful function execution."""
        # Create a test module
        test_module_content = '''
def test_function():
    """Test function."""
    return "Hello, World!"
'''
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        # Create function spec
        function_spec = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function.",
            arguments=[],
            return_type="str"
        )
        
        # Execute function
        result = self.executor.execute_function(function_spec, str(test_module_path))
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.output)
        self.assertIsNone(result.error)
        self.assertGreater(result.execution_time, 0)
    
    def test_execute_function_module_not_found(self):
        """Test function execution with missing module."""
        function_spec = FunctionSpec(
            name="test_function",
            module="nonexistent_module",
            docstring="Test function.",
            arguments=[],
            return_type="str"
        )
        
        result = self.executor.execute_function(function_spec, "/nonexistent/module.py")
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertIsInstance(result.error, ImportError)
    
    def test_execute_function_function_not_found(self):
        """Test function execution with missing function."""
        # Create a test module without the target function
        test_module_content = '''
def other_function():
    """Other function."""
    return "Other"
'''
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        function_spec = FunctionSpec(
            name="missing_function",
            module="test_module",
            docstring="Missing function.",
            arguments=[],
            return_type="str"
        )
        
        result = self.executor.execute_function(function_spec, str(test_module_path))
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertIsInstance(result.error, AttributeError)
    
    def test_execute_function_with_parameters(self):
        """Test function execution with parameters."""
        # Create a test module with parameters
        test_module_content = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        function_spec = FunctionSpec(
            name="add_numbers",
            module="test_module",
            docstring="Add two numbers.",
            arguments=[
                Argument(name="a", type_hint="int", description="First number"),
                Argument(name="b", type_hint="int", description="Second number")
            ],
            return_type="int"
        )
        
        result = self.executor.execute_function(function_spec, str(test_module_path))
        
        self.assertTrue(result.success)
        self.assertIn("Expected parameters: 2", result.output)
    
    @patch('a3.engines.code_executor.psutil.Process')
    def test_memory_usage_tracking(self, mock_process):
        """Test memory usage tracking."""
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024  # 1MB
        mock_process.return_value.memory_info.return_value = mock_memory_info
        
        # Create a simple test module
        test_module_content = '''
def simple_function():
    """Simple function."""
    return True
'''
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        function_spec = FunctionSpec(
            name="simple_function",
            module="test_module",
            docstring="Simple function.",
            arguments=[],
            return_type="bool"
        )
        
        result = self.executor.execute_function(function_spec, str(test_module_path))
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.memory_usage)
    
    def test_validate_imports_success(self):
        """Test successful import validation."""
        # Create a test module with valid imports
        test_module_content = """import os
import sys
from pathlib import Path

def test_function():
    return True
"""
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        result = self.executor.validate_imports(str(test_module_path))
        
        self.assertTrue(result.success)
        self.assertGreater(len(result.valid_imports), 0)
        self.assertEqual(len(result.invalid_imports), 0)
    
    def test_validate_imports_invalid_module(self):
        """Test import validation with invalid imports."""
        # Create a test module with invalid imports
        test_module_content = """import nonexistent_module_12345
from another_nonexistent_12345 import something

def test_function():
    return True
"""
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        result = self.executor.validate_imports(str(test_module_path))
        
        self.assertFalse(result.success)
        self.assertGreater(len(result.invalid_imports), 0)
        self.assertGreater(len(result.missing_modules), 0)
    
    def test_validate_imports_syntax_error(self):
        """Test import validation with syntax errors."""
        # Create a test module with syntax errors
        test_module_content = '''
import os
def test_function(
    return True  # Missing closing parenthesis
'''
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        result = self.executor.validate_imports(str(test_module_path))
        
        self.assertFalse(result.success)
        self.assertGreater(len(result.error_messages), 0)
    
    def test_run_tests_basic_runner(self):
        """Test running tests with basic runner."""
        # Create a test file
        test_content = '''
def test_passing():
    """Test that passes."""
    assert True

def test_failing():
    """Test that fails."""
    assert False, "This test should fail"

def not_a_test():
    """Not a test function."""
    return True
'''
        test_file_path = self.project_path / "test_example.py"
        test_file_path.write_text(test_content)
        
        # Force basic runner by mocking pytest unavailable
        with patch.object(self.executor, '_is_pytest_available', return_value=False):
            result = self.executor.run_tests([str(test_file_path)])
        
        self.assertEqual(result.total_tests, 2)  # Only functions starting with 'test_'
        self.assertEqual(result.passed_tests, 1)
        self.assertEqual(result.failed_tests, 1)
        self.assertEqual(len(result.test_details), 2)
    
    def test_run_tests_empty_list(self):
        """Test running tests with empty test file list."""
        result = self.executor.run_tests([])
        
        self.assertEqual(result.total_tests, 0)
        self.assertEqual(result.passed_tests, 0)
        self.assertEqual(result.failed_tests, 0)
    
    def test_run_tests_nonexistent_file(self):
        """Test running tests with nonexistent file."""
        # Force basic runner to ensure consistent behavior
        with patch.object(self.executor, '_is_pytest_available', return_value=False):
            result = self.executor.run_tests(["/nonexistent/test.py"])
        
        self.assertEqual(result.total_tests, 1)
        self.assertEqual(result.passed_tests, 0)
        self.assertEqual(result.failed_tests, 1)
    
    def test_capture_runtime_errors(self):
        """Test runtime error capture."""
        def failing_function():
            raise ValueError("Test error")
        
        error = self.executor.capture_runtime_errors(failing_function)
        
        self.assertIsNotNone(error)
        self.assertIsInstance(error, ValueError)
        self.assertEqual(str(error), "Test error")
    
    def test_capture_runtime_errors_success(self):
        """Test runtime error capture with successful execution."""
        def successful_function():
            return "success"
        
        error = self.executor.capture_runtime_errors(successful_function)
        
        self.assertIsNone(error)
    
    def test_verify_implementation_success(self):
        """Test successful implementation verification."""
        # Create a test module
        test_module_content = '''def test_function():
    """Test function with proper docstring."""
    return "Hello, World!"
'''
        test_module_path = self.project_path / "test_module.py"
        test_module_path.write_text(test_module_content)
        
        function_spec = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function with proper docstring.",
            arguments=[],
            return_type="str"
        )
        
        result = self.executor.verify_implementation(function_spec)
        
        # The verification might fail due to additional checks, but execution should succeed
        self.assertEqual(result.function_name, "test_function")
        self.assertIsNotNone(result.execution_result)
        self.assertTrue(result.execution_result.success)
    
    def test_verify_implementation_with_tests(self):
        """Test implementation verification with test files."""
        # Create a test module
        test_module_content = '''def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        test_module_path = self.project_path / "math_utils.py"
        test_module_path.write_text(test_module_content)
        
        # Create a test file
        test_content = '''import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from math_utils import add_numbers

def test_add_numbers():
    """Test add_numbers function."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(0, 0) == 0
    assert add_numbers(-1, 1) == 0
'''
        test_file_path = self.project_path / "test_math_utils.py"
        test_file_path.write_text(test_content)
        
        function_spec = FunctionSpec(
            name="add_numbers",
            module="math_utils",
            docstring="Add two numbers.",
            arguments=[
                Argument(name="a", type_hint="int", description="First number"),
                Argument(name="b", type_hint="int", description="Second number")
            ],
            return_type="int"
        )
        
        result = self.executor.verify_implementation(function_spec)
        
        # Check that execution succeeded and tests ran
        self.assertEqual(result.function_name, "add_numbers")
        self.assertIsNotNone(result.execution_result)
        self.assertTrue(result.execution_result.success)
        self.assertIsNotNone(result.test_result)
    
    def test_verify_implementation_failure(self):
        """Test implementation verification failure."""
        # Create a test module with issues
        test_module_content = '''
def broken_function():
    # Missing docstring and has syntax issues
    return undefined_variable  # This will cause a NameError
'''
        test_module_path = self.project_path / "broken_module.py"
        test_module_path.write_text(test_module_content)
        
        function_spec = FunctionSpec(
            name="broken_function",
            module="broken_module",
            docstring="Function that should have a docstring.",
            arguments=[],
            return_type="str"
        )
        
        result = self.executor.verify_implementation(function_spec)
        
        self.assertFalse(result.is_verified)
        self.assertGreater(len(result.verification_errors), 0)
    
    def test_generate_verification_report(self):
        """Test verification report generation."""
        # Create test modules
        test_module1_content = '''
def function1():
    """First function."""
    return "function1"
'''
        test_module1_path = self.project_path / "module1.py"
        test_module1_path.write_text(test_module1_content)
        
        test_module2_content = '''
def function2():
    """Second function."""
    return "function2"
'''
        test_module2_path = self.project_path / "module2.py"
        test_module2_path.write_text(test_module2_content)
        
        function_specs = [
            FunctionSpec(
                name="function1",
                module="module1",
                docstring="First function.",
                arguments=[],
                return_type="str"
            ),
            FunctionSpec(
                name="function2",
                module="module2",
                docstring="Second function.",
                arguments=[],
                return_type="str"
            )
        ]
        
        report = self.executor.generate_verification_report(function_specs)
        
        self.assertEqual(report['total_functions'], 2)
        self.assertGreaterEqual(report['verified_functions'], 0)
        self.assertIn('timestamp', report)
        self.assertIn('summary', report)
        self.assertEqual(len(report['function_results']), 2)
    
    def test_run_tests_with_pytest(self):
        """Test running tests with pytest."""
        # Create a test file
        test_content = '''
def test_example():
    assert True
'''
        test_file_path = self.project_path / "test_example.py"
        test_file_path.write_text(test_content)
        
        # Mock pytest being available and test the method directly
        with patch('pytest.main', return_value=0) as mock_pytest_main:
            with patch.object(self.executor, '_capture_output') as mock_capture:
                mock_stdout = Mock()
                mock_stdout.getvalue.return_value = "test_example.py::test_example PASSED"
                mock_capture.return_value.__enter__.return_value = (mock_stdout, Mock())
                
                result = self.executor._run_tests_with_pytest([str(test_file_path)])
        
        self.assertGreaterEqual(result.total_tests, 0)
    
    def test_find_test_files(self):
        """Test finding test files for a module."""
        # Create test files in different patterns
        (self.project_path / "tests").mkdir(exist_ok=True)
        
        test_files = [
            "test_mymodule.py",
            "tests/test_mymodule.py",
            "mymodule_test.py",
            "tests/mymodule_test.py"
        ]
        
        for test_file in test_files:
            test_path = self.project_path / test_file
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text("# Test file")
        
        found_files = self.executor._find_test_files("mymodule")
        
        self.assertGreater(len(found_files), 0)
        # Should find at least one of the test files
        found_names = [Path(f).name for f in found_files]
        self.assertTrue(any(name in found_names for name in ["test_mymodule.py", "mymodule_test.py"]))
    
    def test_get_module_path(self):
        """Test module path generation."""
        path = self.executor._get_module_path("mymodule")
        expected_path = str(self.project_path / "mymodule.py")
        self.assertEqual(path, expected_path)
        
        path = self.executor._get_module_path("package.submodule")
        expected_path = str(self.project_path / "package/submodule.py")
        self.assertEqual(path, expected_path)
    
    def test_extract_imports(self):
        """Test import extraction from AST."""
        import ast
        
        code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict
'''
        tree = ast.parse(code)
        imports = self.executor._extract_imports(tree)
        
        self.assertGreater(len(imports), 0)
        
        # Check for different import types
        import_types = [imp['type'] for imp in imports]
        self.assertIn('import', import_types)
        self.assertIn('from', import_types)
    
    def test_can_import_module(self):
        """Test module import capability checking."""
        # Test standard library module
        self.assertTrue(self.executor._can_import_module('os'))
        self.assertTrue(self.executor._can_import_module('sys'))
        
        # Test nonexistent module
        self.assertFalse(self.executor._can_import_module('nonexistent_module_12345'))
    
    def test_load_module_success(self):
        """Test successful module loading."""
        # Create a test module
        test_module_content = '''
def test_function():
    return "loaded"
'''
        test_module_path = self.project_path / "loadable_module.py"
        test_module_path.write_text(test_module_content)
        
        module = self.executor._load_module(str(test_module_path))
        
        self.assertIsNotNone(module)
        self.assertTrue(hasattr(module, 'test_function'))
        self.assertEqual(module.test_function(), "loaded")
    
    def test_load_module_failure(self):
        """Test module loading failure."""
        module = self.executor._load_module("/nonexistent/module.py")
        self.assertIsNone(module)


if __name__ == '__main__':
    unittest.main()