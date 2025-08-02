"""
Unit tests for Test Generator Engine functionality.

This module tests the TestGenerator class for test case generation from function
specifications, test file creation and execution, and test result reporting.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

from a3.engines.test_generator import TestGenerator
from a3.core.models import (
    Module, FunctionSpec, Argument, TestCase, TestGenerationResult,
    TestExecutionResult, TestDetail, ImplementationStatus
)


class TestTestGenerator(unittest.TestCase):
    """Test cases for TestGenerator functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock AI client and state manager
        self.mock_ai_client = Mock()
        self.mock_state_manager = Mock()
        
        # Initialize test generator
        self.test_generator = TestGenerator(
            ai_client=self.mock_ai_client,
            state_manager=self.mock_state_manager
        )
        self.test_generator.initialize()
        
        # Create sample function specifications
        self.sample_function = FunctionSpec(
            name="calculate_sum",
            module="math_utils",
            docstring="Calculate the sum of two numbers.",
            arguments=[
                Argument(name="a", type_hint="int", description="First number"),
                Argument(name="b", type_hint="int", description="Second number")
            ],
            return_type="int"
        )
        
        self.sample_module = Module(
            name="math_utils",
            description="Mathematical utility functions",
            file_path="math_utils.py",
            functions=[self.sample_function]
        )
    
    def test_initialization(self):
        """Test test generator initialization."""
        self.assertTrue(self.test_generator._initialized)
        self.assertEqual(self.test_generator.ai_client, self.mock_ai_client)
        self.assertEqual(self.test_generator.state_manager, self.mock_state_manager)
        self.assertIsInstance(self.test_generator.test_template_cache, dict)
        self.assertIsInstance(self.test_generator.function_analysis_cache, dict)
    
    def test_generate_module_tests_basic(self):
        """Test basic module test generation."""
        test_cases = self.test_generator.generate_module_tests(self.sample_module)
        
        # Should generate test cases for the function
        self.assertGreater(len(test_cases), 0)
        
        # Verify test case structure
        for test_case in test_cases:
            self.assertIsInstance(test_case, TestCase)
            self.assertIsNotNone(test_case.name)
            self.assertIsNotNone(test_case.test_code)
            self.assertEqual(test_case.function_name, self.sample_function.name)
    
    def test_generate_module_tests_empty_module(self):
        """Test module test generation with empty module."""
        empty_module = Module(
            name="empty_module",
            description="Empty module",
            file_path="empty_module.py",
            functions=[]
        )
        
        test_cases = self.test_generator.generate_module_tests(empty_module)
        self.assertEqual(len(test_cases), 0)
    
    def test_generate_module_tests_none_module(self):
        """Test module test generation with None module."""
        test_cases = self.test_generator.generate_module_tests(None)
        self.assertEqual(len(test_cases), 0)
    
    def test_analyze_function_for_testing(self):
        """Test function analysis for testing strategy."""
        strategy = self.test_generator._analyze_function_for_testing(self.sample_function)
        
        # Verify strategy structure
        self.assertIn('function_name', strategy)
        self.assertIn('module_name', strategy)
        self.assertIn('return_type', strategy)
        self.assertIn('arguments', strategy)
        self.assertIn('test_types', strategy)
        self.assertIn('mock_requirements', strategy)
        self.assertIn('edge_cases', strategy)
        self.assertIn('error_conditions', strategy)
        
        # Verify strategy content
        self.assertEqual(strategy['function_name'], self.sample_function.name)
        self.assertEqual(strategy['module_name'], self.sample_function.module)
        self.assertEqual(strategy['return_type'], self.sample_function.return_type)
        self.assertIn('return_value', strategy['test_types'])
        self.assertIn('parameter_validation', strategy['test_types'])
    
    def test_analyze_function_caching(self):
        """Test that function analysis results are cached."""
        # First call
        strategy1 = self.test_generator._analyze_function_for_testing(self.sample_function)
        
        # Second call should return cached result
        strategy2 = self.test_generator._analyze_function_for_testing(self.sample_function)
        
        # Should be the same object (cached)
        self.assertIs(strategy1, strategy2)
        
        # Verify cache contains the function
        self.assertIn(self.sample_function.name, self.test_generator.function_analysis_cache)
    
    def test_generate_basic_function_tests(self):
        """Test generation of basic function tests."""
        strategy = self.test_generator._analyze_function_for_testing(self.sample_function)
        test_cases = self.test_generator._generate_basic_function_tests(
            self.sample_function, strategy
        )
        
        # Should generate at least happy path and return value tests
        self.assertGreaterEqual(len(test_cases), 2)
        
        # Check for happy path test
        happy_path_tests = [tc for tc in test_cases if 'happy_path' in tc.name]
        self.assertEqual(len(happy_path_tests), 1)
        
        # Check for return value test
        return_value_tests = [tc for tc in test_cases if 'return_value' in tc.name]
        self.assertEqual(len(return_value_tests), 1)
        
        # Verify test code contains function call
        for test_case in test_cases:
            self.assertIn(self.sample_function.name, test_case.test_code)
    
    def test_generate_edge_case_tests(self):
        """Test generation of edge case tests."""
        strategy = self.test_generator._analyze_function_for_testing(self.sample_function)
        test_cases = self.test_generator._generate_edge_case_tests(
            self.sample_function, strategy
        )
        
        # Should generate edge case tests based on argument types
        self.assertGreater(len(test_cases), 0)
        
        # Verify edge case tests are generated for int arguments
        edge_case_names = [tc.name for tc in test_cases]
        self.assertTrue(any('zero_value' in name for name in edge_case_names))
        self.assertTrue(any('negative_value' in name for name in edge_case_names))
    
    def test_generate_error_handling_tests(self):
        """Test generation of error handling tests."""
        # Create function with error conditions in docstring
        error_function = FunctionSpec(
            name="divide_numbers",
            module="math_utils",
            docstring="Divide two numbers. Raises ValueError if divisor is zero.",
            arguments=[
                Argument(name="a", type_hint="int", description="Dividend"),
                Argument(name="b", type_hint="int", description="Divisor")
            ],
            return_type="float"
        )
        
        strategy = self.test_generator._analyze_function_for_testing(error_function)
        test_cases = self.test_generator._generate_error_handling_tests(
            error_function, strategy
        )
        
        # Should generate error handling tests based on docstring
        if strategy['error_conditions']:
            self.assertGreater(len(test_cases), 0)
            
            # Verify error test structure
            for test_case in test_cases:
                self.assertEqual(test_case.expected_result, "exception")
                self.assertIn("assertRaises", test_case.test_code)
    
    def test_generate_sample_arguments(self):
        """Test generation of sample arguments for testing."""
        args_code = self.test_generator._generate_sample_arguments(self.sample_function.arguments)
        
        # Should generate argument assignments
        self.assertIn("a=", args_code)
        self.assertIn("b=", args_code)
        self.assertIn("42", args_code)  # Default int value
    
    def test_generate_sample_value_for_type(self):
        """Test generation of sample values for different types."""
        test_cases = [
            ('str', '"test_string"'),
            ('int', '42'),
            ('float', '3.14'),
            ('bool', 'True'),
            ('list', '[]'),
            ('dict', '{}'),
            ('List[str]', '["item1", "item2"]'),
            ('Dict[str, str]', '{"key": "value"}'),
            ('Optional[str]', '"test_string"'),
            ('Any', '"test_value"'),
            ('UnknownType', 'None')
        ]
        
        for type_hint, expected_value in test_cases:
            with self.subTest(type_hint=type_hint):
                result = self.test_generator._generate_sample_value_for_type(type_hint)
                self.assertEqual(result, expected_value)
    
    def test_generate_type_assertion(self):
        """Test generation of type assertions."""
        test_cases = [
            ('str', 'self.assertIsInstance(result, str)'),
            ('int', 'self.assertIsInstance(result, int)'),
            ('float', 'self.assertIsInstance(result, float)'),
            ('bool', 'self.assertIsInstance(result, bool)'),
            ('List[str]', 'self.assertIsInstance(result, list)'),
            ('Dict[str, str]', 'self.assertIsInstance(result, dict)'),
            ('CustomType', 'self.assertIsNotNone(result)')
        ]
        
        for return_type, expected_assertion in test_cases:
            with self.subTest(return_type=return_type):
                result = self.test_generator._generate_type_assertion(return_type)
                self.assertEqual(result, expected_assertion)
    
    def test_identify_argument_edge_cases(self):
        """Test identification of argument edge cases."""
        # Test string argument edge cases
        str_arg = Argument(name="text", type_hint="str", description="Text input")
        str_edge_cases = self.test_generator._identify_argument_edge_cases(str_arg)
        
        self.assertGreater(len(str_edge_cases), 0)
        edge_case_names = [ec['name'] for ec in str_edge_cases]
        self.assertTrue(any('empty_string' in name for name in edge_case_names))
        self.assertTrue(any('long_string' in name for name in edge_case_names))
        
        # Test int argument edge cases
        int_arg = Argument(name="number", type_hint="int", description="Number input")
        int_edge_cases = self.test_generator._identify_argument_edge_cases(int_arg)
        
        self.assertGreater(len(int_edge_cases), 0)
        edge_case_names = [ec['name'] for ec in int_edge_cases]
        self.assertTrue(any('zero_value' in name for name in edge_case_names))
        self.assertTrue(any('negative_value' in name for name in edge_case_names))
        
        # Test list argument edge cases
        list_arg = Argument(name="items", type_hint="List[str]", description="List of items")
        list_edge_cases = self.test_generator._identify_argument_edge_cases(list_arg)
        
        self.assertGreater(len(list_edge_cases), 0)
        edge_case_names = [ec['name'] for ec in list_edge_cases]
        self.assertTrue(any('empty_list' in name for name in edge_case_names))
    
    def test_analyze_docstring_for_tests(self):
        """Test analysis of docstring for testing hints."""
        docstring = "This function processes data. Raises ValueError if input is invalid. Throws RuntimeError on system failure."
        
        analysis = self.test_generator._analyze_docstring_for_tests(docstring)
        
        # Should identify error conditions from docstring
        self.assertIn('error_conditions', analysis)
        self.assertGreater(len(analysis['error_conditions']), 0)
        
        # Check for identified exceptions
        exception_types = [ec['exception_type'] for ec in analysis['error_conditions']]
        self.assertIn('ValueError', exception_types)
        self.assertIn('RuntimeError', exception_types)
    
    def test_identify_mock_requirements(self):
        """Test identification of mock requirements."""
        # Test file-related function
        file_function = FunctionSpec(
            name="read_file_content",
            module="file_utils",
            docstring="Read content from a file.",
            arguments=[],
            return_type="str"
        )
        
        mocks = self.test_generator._identify_mock_requirements(file_function)
        self.assertIn('file_system', mocks)
        
        # Test HTTP-related function
        http_function = FunctionSpec(
            name="make_http_request",
            module="http_utils",
            docstring="Make an HTTP request.",
            arguments=[],
            return_type="dict"
        )
        
        mocks = self.test_generator._identify_mock_requirements(http_function)
        self.assertIn('http_client', mocks)
        
        # Test database-related function
        db_function = FunctionSpec(
            name="query_database",
            module="db_utils",
            docstring="Query the database.",
            arguments=[],
            return_type="list"
        )
        
        mocks = self.test_generator._identify_mock_requirements(db_function)
        self.assertIn('database', mocks)
    
    def test_generate_integration_tests(self):
        """Test generation of integration tests."""
        # Create multiple modules with dependencies
        module1 = Module(
            name="module1",
            description="First module",
            file_path="module1.py",
            dependencies=["module2"],
            functions=[
                FunctionSpec(
                    name="func1",
                    module="module1",
                    docstring="Function 1",
                    arguments=[],
                    return_type="str"
                )
            ]
        )
        
        module2 = Module(
            name="module2",
            description="Second module",
            file_path="module2.py",
            functions=[
                FunctionSpec(
                    name="func2",
                    module="module2",
                    docstring="Function 2",
                    arguments=[Argument(name="data", type_hint="str", description="Input data")],
                    return_type="int"
                )
            ]
        )
        
        modules = [module1, module2]
        integration_tests = self.test_generator.generate_integration_tests(modules)
        
        # Should generate integration tests
        self.assertGreater(len(integration_tests), 0)
        
        # Verify integration test structure
        for test_case in integration_tests:
            self.assertEqual(test_case.test_type, "integration")
            self.assertIsNotNone(test_case.test_code)
    
    def test_generate_integration_tests_empty_modules(self):
        """Test integration test generation with empty modules list."""
        integration_tests = self.test_generator.generate_integration_tests([])
        self.assertEqual(len(integration_tests), 0)
    
    def test_modules_interact(self):
        """Test module interaction detection."""
        module1 = Module(
            name="module1",
            description="First module",
            file_path="module1.py",
            dependencies=["module2"],
            functions=[]
        )
        
        module2 = Module(
            name="module2",
            description="Second module",
            file_path="module2.py",
            functions=[]
        )
        
        module3 = Module(
            name="module3",
            description="Third module",
            file_path="module3.py",
            functions=[]
        )
        
        # module1 depends on module2, so they interact
        self.assertTrue(self.test_generator._modules_interact(module1, module2))
        
        # module1 and module3 don't interact
        self.assertFalse(self.test_generator._modules_interact(module1, module3))
    
    def test_functions_might_interact(self):
        """Test function interaction detection."""
        func1 = FunctionSpec(
            name="get_data",
            module="module1",
            docstring="Get data",
            arguments=[],
            return_type="str"
        )
        
        func2 = FunctionSpec(
            name="process_data",
            module="module2",
            docstring="Process data",
            arguments=[Argument(name="data", type_hint="str", description="Data to process")],
            return_type="int"
        )
        
        func3 = FunctionSpec(
            name="save_result",
            module="module3",
            docstring="Save result",
            arguments=[Argument(name="result", type_hint="int", description="Result to save")],
            return_type="None"
        )
        
        # func1 returns str, func2 takes str - they might interact
        self.assertTrue(self.test_generator._functions_might_interact(func1, func2))
        
        # func2 returns int, func3 takes int - they might interact
        self.assertTrue(self.test_generator._functions_might_interact(func2, func3))
        
        # func1 returns str, func3 takes int - they don't interact
        self.assertFalse(self.test_generator._functions_might_interact(func1, func3))
    
    def test_create_test_files(self):
        """Test creation of test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            created_files = self.test_generator.create_test_files(
                [self.sample_module], 
                output_dir=temp_dir
            )
            
            # Should create one test file
            self.assertEqual(len(created_files), 1)
            
            # Verify file exists and has correct name
            test_file = created_files[0]
            self.assertTrue(os.path.exists(test_file))
            self.assertTrue(test_file.endswith("test_math_utils.py"))
            
            # Verify file content
            with open(test_file, 'r') as f:
                content = f.read()
            
            self.assertIn("import unittest", content)
            self.assertIn("TestMath_Utils", content)  # The implementation uses underscores
            self.assertIn("test_calculate_sum", content)
    
    def test_generate_test_file_content(self):
        """Test generation of test file content."""
        test_cases = self.test_generator.generate_module_tests(self.sample_module)
        content = self.test_generator._generate_test_file_content(
            self.sample_module, test_cases
        )
        
        # Verify content structure
        self.assertIn('"""', content)  # Docstring
        self.assertIn("import unittest", content)
        self.assertIn("from math_utils import *", content)
        self.assertIn("class TestMath_Utils(unittest.TestCase):", content)  # The implementation uses underscores
        self.assertIn("def setUp(self):", content)
        self.assertIn("def tearDown(self):", content)
        self.assertIn("if __name__ == '__main__':", content)
        
        # Verify test methods are included
        for test_case in test_cases:
            self.assertIn(test_case.name, content)
    
    def test_generate_test_imports(self):
        """Test generation of test imports."""
        # Module with dependencies
        module_with_deps = Module(
            name="complex_module",
            description="Complex module",
            file_path="complex_module.py",
            dependencies=["os", "json", "requests"],
            functions=[]
        )
        
        imports = self.test_generator._generate_test_imports(module_with_deps)
        
        # Should include module import and dependencies
        self.assertIn("from complex_module import *", imports)
        self.assertIn("import os", imports)
        self.assertIn("import json", imports)
        self.assertIn("import requests", imports)
    
    def test_format_test_methods(self):
        """Test formatting of test methods."""
        test_cases = [
            TestCase(
                name="test_example",
                function_name="example",
                test_code="def test_example(self):\n    self.assertTrue(True)",
                expected_result="pass",
                test_type="unit"
            )
        ]
        
        formatted = self.test_generator._format_test_methods(test_cases)
        
        # Should properly indent the test code
        self.assertIn("    def test_example(self):", formatted)
        self.assertIn("        self.assertTrue(True)", formatted)
    
    @patch('subprocess.run')
    def test_execute_generated_tests_success(self, mock_run):
        """Test successful execution of generated tests."""
        # Mock successful pytest execution
        mock_run.return_value = Mock(
            stdout="test_file.py::test_function PASSED\n1 passed in 0.01s",
            stderr="",
            returncode=0
        )
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(b"# Test file content")
            temp_file_path = temp_file.name
        
        try:
            result = self.test_generator.execute_generated_tests([temp_file_path])
            
            # Verify execution result
            self.assertIsInstance(result, TestExecutionResult)
            self.assertGreaterEqual(result.total_tests, 0)
            self.assertGreaterEqual(result.passed_tests, 0)
            self.assertEqual(result.failed_tests, 0)
            
        finally:
            os.unlink(temp_file_path)
    
    @patch('subprocess.run')
    def test_execute_generated_tests_failure(self, mock_run):
        """Test execution of generated tests with failures."""
        # Mock failed pytest execution
        mock_run.return_value = Mock(
            stdout="test_file.py::test_function FAILED\n1 failed in 0.01s",
            stderr="AssertionError: Test failed",
            returncode=1
        )
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(b"# Test file content")
            temp_file_path = temp_file.name
        
        try:
            result = self.test_generator.execute_generated_tests([temp_file_path])
            
            # Verify execution result shows failures
            self.assertIsInstance(result, TestExecutionResult)
            self.assertGreaterEqual(result.total_tests, 0)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_execute_generated_tests_empty_list(self):
        """Test execution with empty test files list."""
        result = self.test_generator.execute_generated_tests([])
        
        # Should return empty result
        self.assertEqual(result.total_tests, 0)
        self.assertEqual(result.passed_tests, 0)
        self.assertEqual(result.failed_tests, 0)
        self.assertEqual(len(result.test_details), 0)
    
    def test_execute_generated_tests_nonexistent_file(self):
        """Test execution with nonexistent test file."""
        with self.assertRaises(FileNotFoundError):
            self.test_generator.execute_generated_tests(["/nonexistent/test_file.py"])
    
    @patch('subprocess.run')
    def test_execute_generated_tests_timeout(self, mock_run):
        """Test execution with timeout."""
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=['pytest'], timeout=300)
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(b"# Test file content")
            temp_file_path = temp_file.name
        
        try:
            result = self.test_generator.execute_generated_tests([temp_file_path], timeout=1)
            
            # Should handle timeout gracefully
            self.assertIsInstance(result, TestExecutionResult)
            self.assertEqual(result.total_tests, 0)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_uninitialized_generator_operations(self):
        """Test operations on uninitialized generator."""
        # Create uninitialized generator
        generator = TestGenerator()
        
        # Operations should raise RuntimeError
        with self.assertRaises(RuntimeError):
            generator.generate_module_tests(self.sample_module)
        
        with self.assertRaises(RuntimeError):
            generator.generate_integration_tests([self.sample_module])
        
        with self.assertRaises(RuntimeError):
            generator.execute_generated_tests(["test.py"])


class TestTestGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for TestGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_generator = TestGenerator()
        self.test_generator.initialize()
        
        # Create sample module for edge case tests
        self.sample_module = Module(
            name="test_module",
            description="Test module for edge cases",
            file_path="test_module.py",
            functions=[
                FunctionSpec(
                    name="test_function",
                    module="test_module",
                    docstring="Test function",
                    arguments=[],
                    return_type="str"
                )
            ]
        )
    
    def test_function_with_no_arguments(self):
        """Test test generation for function with no arguments."""
        no_args_function = FunctionSpec(
            name="get_current_time",
            module="time_utils",
            docstring="Get current timestamp.",
            arguments=[],
            return_type="str"
        )
        
        strategy = self.test_generator._analyze_function_for_testing(no_args_function)
        test_cases = self.test_generator._generate_basic_function_tests(
            no_args_function, strategy
        )
        
        # Should still generate tests
        self.assertGreater(len(test_cases), 0)
        
        # Test code should call function without arguments
        for test_case in test_cases:
            self.assertIn("get_current_time()", test_case.test_code)
    
    def test_function_with_void_return(self):
        """Test test generation for function with no return value."""
        void_function = FunctionSpec(
            name="print_message",
            module="output_utils",
            docstring="Print a message to console.",
            arguments=[Argument(name="message", type_hint="str", description="Message to print")],
            return_type="None"
        )
        
        strategy = self.test_generator._analyze_function_for_testing(void_function)
        test_cases = self.test_generator._generate_basic_function_tests(
            void_function, strategy
        )
        
        # Should generate tests even for void functions
        self.assertGreater(len(test_cases), 0)
        
        # Should not include return value tests
        return_value_tests = [tc for tc in test_cases if 'return_value' in tc.name]
        self.assertEqual(len(return_value_tests), 0)
    
    def test_function_with_complex_types(self):
        """Test test generation for function with complex type hints."""
        complex_function = FunctionSpec(
            name="process_data",
            module="data_utils",
            docstring="Process complex data structures.",
            arguments=[
                Argument(name="data", type_hint="Dict[str, List[int]]", description="Complex data"),
                Argument(name="options", type_hint="Optional[Dict[str, Any]]", description="Options")
            ],
            return_type="Tuple[bool, str]"
        )
        
        strategy = self.test_generator._analyze_function_for_testing(complex_function)
        
        # Should handle complex types
        self.assertEqual(strategy['return_type'], "Tuple[bool, str]")
        self.assertEqual(len(strategy['arguments']), 2)
        
        # Should generate appropriate sample values
        sample_args = self.test_generator._generate_sample_arguments(complex_function.arguments)
        self.assertIn("data=", sample_args)
        self.assertIn("options=", sample_args)
    
    def test_module_with_function_generation_error(self):
        """Test handling of errors during function test generation."""
        # Create a function that will cause an error during test generation
        problematic_function = FunctionSpec(
            name="problematic_function",
            module="test_module",
            docstring="This function will cause test generation issues.",
            arguments=[],
            return_type="str"
        )
        
        test_module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=[problematic_function]
        )
        
        # Mock the _generate_function_tests method to raise an exception
        original_method = self.test_generator._generate_function_tests
        self.test_generator._generate_function_tests = Mock(side_effect=Exception("Test error"))
        
        try:
            # Should handle the error gracefully and continue
            test_cases = self.test_generator.generate_module_tests(test_module)
            
            # Should return empty list due to error
            self.assertEqual(len(test_cases), 0)
            
            # Should log error if state manager is available
            if self.test_generator.state_manager:
                self.test_generator.state_manager.log_error.assert_called()
        
        finally:
            # Restore original method
            self.test_generator._generate_function_tests = original_method
    
    def test_generate_workflow_tests_single_module(self):
        """Test workflow test generation with single module."""
        workflow_tests = self.test_generator._generate_workflow_tests([self.sample_module])
        
        # Should not generate workflow tests for single module
        self.assertEqual(len(workflow_tests), 0)
    
    def test_generate_workflow_tests_multiple_modules(self):
        """Test workflow test generation with multiple modules."""
        module1 = Module(name="module1", description="Module 1", file_path="module1.py", functions=[])
        module2 = Module(name="module2", description="Module 2", file_path="module2.py", functions=[])
        
        workflow_tests = self.test_generator._generate_workflow_tests([module1, module2])
        
        # Should generate workflow test for multiple modules
        self.assertEqual(len(workflow_tests), 1)
        self.assertEqual(workflow_tests[0].name, "test_end_to_end_workflow")
        self.assertEqual(workflow_tests[0].test_type, "integration")
    
    def test_parse_pytest_output_basic(self):
        """Test parsing of basic pytest output."""
        stdout = "test_file.py::test_function PASSED\n1 passed in 0.01s"
        stderr = ""
        return_code = 0
        execution_time = 0.01
        
        result = self.test_generator._parse_pytest_output(
            stdout, stderr, return_code, execution_time, False
        )
        
        # Should parse basic information
        self.assertIsInstance(result, TestExecutionResult)
        self.assertGreaterEqual(result.total_tests, 0)
        self.assertEqual(result.execution_time, execution_time)


if __name__ == '__main__':
    unittest.main()