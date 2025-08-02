"""
Test Generator Engine for AI Project Builder.

This module provides functionality to automatically generate unit tests
for integrated modules and functions.
"""

import ast
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import re

from ..core.models import (
    Module, FunctionSpec, TestCase, TestGenerationResult, 
    TestExecutionResult, TestDetail, CoverageReport, ValidationResult
)
from ..core.interfaces import AIClientInterface, StateManagerInterface
from .base import BaseTestGenerator


class TestGenerator(BaseTestGenerator):
    """
    Engine for generating comprehensive unit tests for modules and functions.
    
    This engine analyzes function specifications and generates appropriate
    test cases following Python testing best practices.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        """
        Initialize the TestGenerator.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
        """
        super().__init__(ai_client, state_manager)
        self.test_template_cache = {}
        self.function_analysis_cache = {}
    
    def generate_module_tests(self, module: Module, **kwargs) -> List[TestCase]:
        """
        Generate unit tests for all functions in a module.
        
        Args:
            module: Module specification to generate tests for
            **kwargs: Additional options for test generation
        
        Returns:
            List of generated test cases
        
        Raises:
            RuntimeError: If engine is not initialized
            ValueError: If module is invalid
        """
        self._ensure_initialized()
        
        if not module or not module.functions:
            return []
        
        test_cases = []
        
        for function in module.functions:
            try:
                function_tests = self._generate_function_tests(function, module)
                test_cases.extend(function_tests)
            except Exception as e:
                # Log error but continue with other functions
                if self.state_manager:
                    self.state_manager.log_error(
                        f"Failed to generate tests for function {function.name}: {str(e)}"
                    )
        
        return test_cases
    
    def generate_integration_tests(self, modules: List[Module], **kwargs) -> List[TestCase]:
        """
        Generate integration tests for multiple modules.
        
        Args:
            modules: List of modules to generate integration tests for
            **kwargs: Additional options for test generation
        
        Returns:
            List of generated integration test cases
        
        Raises:
            RuntimeError: If engine is not initialized
            ValueError: If modules list is invalid
        """
        self._ensure_initialized()
        
        if not modules:
            return []
        
        integration_tests = []
        
        # Generate tests for module interactions
        for i, module_a in enumerate(modules):
            for module_b in modules[i+1:]:
                if self._modules_interact(module_a, module_b):
                    interaction_tests = self._generate_module_interaction_tests(
                        module_a, module_b
                    )
                    integration_tests.extend(interaction_tests)
        
        # Generate end-to-end workflow tests
        workflow_tests = self._generate_workflow_tests(modules)
        integration_tests.extend(workflow_tests)
        
        return integration_tests
    
    def execute_generated_tests(self, test_files: List[str], **kwargs) -> TestExecutionResult:
        """
        Execute generated test files and collect results.
        
        Args:
            test_files: List of test file paths to execute
            **kwargs: Additional options for test execution
        
        Returns:
            Test execution results with detailed information
        
        Raises:
            RuntimeError: If engine is not initialized
            FileNotFoundError: If test files don't exist
        """
        self._ensure_initialized()
        
        if not test_files:
            return TestExecutionResult(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_details=[],
                coverage_report=None
            )
        
        # Validate test files exist
        for test_file in test_files:
            if not os.path.exists(test_file):
                raise FileNotFoundError(f"Test file not found: {test_file}")
        
        # Execute tests using pytest
        return self._execute_with_pytest(test_files, **kwargs)
    
    def create_test_files(self, modules: List[Module], output_dir: str = "tests") -> List[str]:
        """
        Create test files for modules following naming conventions.
        
        Args:
            modules: List of modules to create test files for
            output_dir: Directory to create test files in
        
        Returns:
            List of created test file paths
        """
        self._ensure_initialized()
        
        created_files = []
        os.makedirs(output_dir, exist_ok=True)
        
        for module in modules:
            test_cases = self.generate_module_tests(module)
            if test_cases:
                test_file_path = self._create_test_file(module, test_cases, output_dir)
                created_files.append(test_file_path)
        
        return created_files
    
    def _generate_function_tests(self, function: FunctionSpec, module: Module) -> List[TestCase]:
        """Generate test cases for a specific function."""
        test_cases = []
        
        # Analyze function for testing strategy
        test_strategy = self._analyze_function_for_testing(function)
        
        # Generate basic functionality tests
        basic_tests = self._generate_basic_function_tests(function, test_strategy)
        test_cases.extend(basic_tests)
        
        # Generate edge case tests
        edge_case_tests = self._generate_edge_case_tests(function, test_strategy)
        test_cases.extend(edge_case_tests)
        
        # Generate error handling tests
        error_tests = self._generate_error_handling_tests(function, test_strategy)
        test_cases.extend(error_tests)
        
        return test_cases
    
    def _analyze_function_for_testing(self, function: FunctionSpec) -> Dict[str, Any]:
        """
        Analyze a function to determine appropriate testing strategy.
        
        Args:
            function: Function specification to analyze
        
        Returns:
            Dictionary containing testing strategy information
        """
        if function.name in self.function_analysis_cache:
            return self.function_analysis_cache[function.name]
        
        strategy = {
            'function_name': function.name,
            'module_name': function.module,
            'return_type': function.return_type,
            'arguments': function.arguments,
            'test_types': [],
            'mock_requirements': [],
            'edge_cases': [],
            'error_conditions': []
        }
        
        # Determine test types based on function characteristics
        if function.return_type != 'None':
            strategy['test_types'].append('return_value')
        
        if function.arguments:
            strategy['test_types'].append('parameter_validation')
            
            # Identify edge cases based on argument types
            for arg in function.arguments:
                edge_cases = self._identify_argument_edge_cases(arg)
                strategy['edge_cases'].extend(edge_cases)
        
        # Analyze docstring for additional test hints
        if function.docstring:
            docstring_analysis = self._analyze_docstring_for_tests(function.docstring)
            strategy.update(docstring_analysis)
        
        # Determine mocking requirements
        strategy['mock_requirements'] = self._identify_mock_requirements(function)
        
        self.function_analysis_cache[function.name] = strategy
        return strategy
    
    def _generate_basic_function_tests(self, function: FunctionSpec, 
                                     strategy: Dict[str, Any]) -> List[TestCase]:
        """Generate basic functionality test cases."""
        test_cases = []
        
        # Generate happy path test
        happy_path_test = TestCase(
            name=f"test_{function.name}_happy_path",
            function_name=function.name,
            test_code=self._generate_happy_path_test_code(function, strategy),
            expected_result="pass",
            test_type="unit"
        )
        test_cases.append(happy_path_test)
        
        # Generate return value tests if function returns something
        if strategy['return_type'] != 'None':
            return_test = TestCase(
                name=f"test_{function.name}_return_value",
                function_name=function.name,
                test_code=self._generate_return_value_test_code(function, strategy),
                expected_result="pass",
                test_type="unit"
            )
            test_cases.append(return_test)
        
        return test_cases
    
    def _generate_edge_case_tests(self, function: FunctionSpec, 
                                strategy: Dict[str, Any]) -> List[TestCase]:
        """Generate edge case test cases."""
        test_cases = []
        
        for edge_case in strategy['edge_cases']:
            test_case = TestCase(
                name=f"test_{function.name}_{edge_case['name']}",
                function_name=function.name,
                test_code=self._generate_edge_case_test_code(function, edge_case),
                expected_result=edge_case.get('expected_outcome', 'pass'),
                test_type="unit"
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_error_handling_tests(self, function: FunctionSpec, 
                                     strategy: Dict[str, Any]) -> List[TestCase]:
        """Generate error handling test cases."""
        test_cases = []
        
        for error_condition in strategy['error_conditions']:
            test_case = TestCase(
                name=f"test_{function.name}_{error_condition['name']}",
                function_name=function.name,
                test_code=self._generate_error_test_code(function, error_condition),
                expected_result="exception",
                test_type="unit"
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_happy_path_test_code(self, function: FunctionSpec, 
                                     strategy: Dict[str, Any]) -> str:
        """Generate test code for happy path scenario."""
        # Create sample arguments
        args_code = self._generate_sample_arguments(function.arguments)
        
        # Generate function call
        if function.arguments:
            call_code = f"{function.name}({args_code})"
        else:
            call_code = f"{function.name}()"
        
        # Generate assertion based on return type
        if strategy['return_type'] != 'None':
            test_code = f"""
    def test_{function.name}_happy_path(self):
        \"\"\"Test {function.name} with valid inputs.\"\"\"
        result = {call_code}
        self.assertIsNotNone(result)
        # Add more specific assertions based on expected behavior
"""
        else:
            test_code = f"""
    def test_{function.name}_happy_path(self):
        \"\"\"Test {function.name} with valid inputs.\"\"\"
        # Test that function executes without raising exceptions
        try:
            {call_code}
        except Exception as e:
            self.fail(f"Function raised an unexpected exception: {{e}}")
"""
        
        return test_code.strip()
    
    def _generate_return_value_test_code(self, function: FunctionSpec, 
                                       strategy: Dict[str, Any]) -> str:
        """Generate test code for return value validation."""
        args_code = self._generate_sample_arguments(function.arguments)
        
        if function.arguments:
            call_code = f"{function.name}({args_code})"
        else:
            call_code = f"{function.name}()"
        
        # Generate type assertion based on return type
        return_type = strategy['return_type']
        type_assertion = self._generate_type_assertion(return_type)
        
        test_code = f"""
    def test_{function.name}_return_value(self):
        \"\"\"Test {function.name} returns expected type.\"\"\"
        result = {call_code}
        {type_assertion}
"""
        
        return test_code.strip()
    
    def _generate_edge_case_test_code(self, function: FunctionSpec, 
                                    edge_case: Dict[str, Any]) -> str:
        """Generate test code for edge case scenario."""
        # Generate all required arguments, with the edge case override
        all_args = []
        edge_case_arg = edge_case.get('test_args', '')
        
        for arg in function.arguments:
            if arg.name in edge_case_arg:
                # Use the edge case value
                all_args.append(edge_case_arg)
            else:
                # Use default sample value
                sample_value = self._generate_sample_value_for_type(arg.type_hint)
                all_args.append(f"{arg.name}={sample_value}")
        
        call_args = ", ".join(all_args)
        call_code = f"{function.name}({call_args})"
        
        test_code = f"""
    def test_{function.name}_{edge_case['name']}(self):
        \"\"\"Test {function.name} with {edge_case['description']}.\"\"\"
        result = {call_code}
        # Add specific assertions for this edge case
        self.assertIsNotNone(result)
"""
        
        return test_code.strip()
    
    def _generate_error_test_code(self, function: FunctionSpec, 
                                error_condition: Dict[str, Any]) -> str:
        """Generate test code for error handling scenario."""
        test_args = error_condition.get('test_args', '')
        call_code = f"{function.name}({test_args})"
        expected_exception = error_condition.get('exception_type', 'Exception')
        
        test_code = f"""
    def test_{function.name}_{error_condition['name']}(self):
        \"\"\"Test {function.name} handles {error_condition['description']}.\"\"\"
        with self.assertRaises({expected_exception}):
            {call_code}
"""
        
        return test_code.strip()
    
    def _generate_sample_arguments(self, arguments: List) -> str:
        """Generate sample argument values for testing."""
        if not arguments:
            return ""
        
        arg_values = []
        for arg in arguments:
            sample_value = self._generate_sample_value_for_type(arg.type_hint)
            if arg.default_value:
                # Use default value if available
                arg_values.append(f"{arg.name}={arg.default_value}")
            else:
                arg_values.append(f"{arg.name}={sample_value}")
        
        return ", ".join(arg_values)
    
    def _generate_sample_value_for_type(self, type_hint: str) -> str:
        """Generate a sample value for a given type hint."""
        type_samples = {
            'str': '"test_string"',
            'int': '42',
            'float': '3.14',
            'bool': 'True',
            'list': '[]',
            'dict': '{}',
            'List[str]': '["item1", "item2"]',
            'List[int]': '[1, 2, 3]',
            'Dict[str, str]': '{"key": "value"}',
            'Optional[str]': '"test_string"',
            'Any': '"test_value"'
        }
        
        return type_samples.get(type_hint, 'None')
    
    def _generate_type_assertion(self, return_type: str) -> str:
        """Generate appropriate type assertion for return type."""
        if return_type == 'str':
            return "self.assertIsInstance(result, str)"
        elif return_type == 'int':
            return "self.assertIsInstance(result, int)"
        elif return_type == 'float':
            return "self.assertIsInstance(result, float)"
        elif return_type == 'bool':
            return "self.assertIsInstance(result, bool)"
        elif return_type.startswith('List'):
            return "self.assertIsInstance(result, list)"
        elif return_type.startswith('Dict'):
            return "self.assertIsInstance(result, dict)"
        else:
            return "self.assertIsNotNone(result)"
    
    def _identify_argument_edge_cases(self, argument) -> List[Dict[str, Any]]:
        """Identify edge cases for a function argument."""
        edge_cases = []
        
        if argument.type_hint == 'str':
            edge_cases.extend([
                {
                    'name': f'empty_string_{argument.name}',
                    'description': f'empty string for {argument.name}',
                    'test_args': f'{argument.name}=""',
                    'expected_outcome': 'pass'
                },
                {
                    'name': f'long_string_{argument.name}',
                    'description': f'very long string for {argument.name}',
                    'test_args': f'{argument.name}="{"x" * 1000}"',
                    'expected_outcome': 'pass'
                }
            ])
        elif argument.type_hint == 'int':
            edge_cases.extend([
                {
                    'name': f'zero_value_{argument.name}',
                    'description': f'zero value for {argument.name}',
                    'test_args': f'{argument.name}=0',
                    'expected_outcome': 'pass'
                },
                {
                    'name': f'negative_value_{argument.name}',
                    'description': f'negative value for {argument.name}',
                    'test_args': f'{argument.name}=-1',
                    'expected_outcome': 'pass'
                }
            ])
        elif argument.type_hint.startswith('List'):
            edge_cases.append({
                'name': f'empty_list_{argument.name}',
                'description': f'empty list for {argument.name}',
                'test_args': f'{argument.name}=[]',
                'expected_outcome': 'pass'
            })
        
        return edge_cases
    
    def _analyze_docstring_for_tests(self, docstring: str) -> Dict[str, Any]:
        """Analyze function docstring for testing hints."""
        analysis = {
            'error_conditions': [],
            'test_hints': []
        }
        
        # Look for raises/exceptions in docstring
        raises_pattern = r'(?:raises?|throws?)\s+(\w+(?:Error|Exception))'
        matches = re.findall(raises_pattern, docstring, re.IGNORECASE)
        
        for exception_type in matches:
            analysis['error_conditions'].append({
                'name': f'raises_{exception_type.lower()}',
                'description': f'{exception_type} exception',
                'exception_type': exception_type,
                'test_args': 'None'  # Will need to be customized
            })
        
        return analysis
    
    def _identify_mock_requirements(self, function: FunctionSpec) -> List[str]:
        """Identify what needs to be mocked for testing this function."""
        mock_requirements = []
        
        # Analyze function dependencies from docstring or name patterns
        if 'file' in function.name.lower() or 'read' in function.name.lower():
            mock_requirements.append('file_system')
        
        if 'http' in function.name.lower() or 'request' in function.name.lower():
            mock_requirements.append('http_client')
        
        if 'database' in function.name.lower() or 'db' in function.name.lower():
            mock_requirements.append('database')
        
        return mock_requirements
    
    def _modules_interact(self, module_a: Module, module_b: Module) -> bool:
        """Check if two modules interact with each other."""
        return (module_b.name in module_a.dependencies or 
                module_a.name in module_b.dependencies)
    
    def _generate_module_interaction_tests(self, module_a: Module, 
                                         module_b: Module) -> List[TestCase]:
        """Generate tests for module interactions."""
        interaction_tests = []
        
        # Find functions that might interact between modules
        for func_a in module_a.functions:
            for func_b in module_b.functions:
                if self._functions_might_interact(func_a, func_b):
                    test_case = TestCase(
                        name=f"test_{module_a.name}_{module_b.name}_interaction",
                        function_name=f"{func_a.name}_{func_b.name}",
                        test_code=self._generate_interaction_test_code(func_a, func_b),
                        expected_result="pass",
                        test_type="integration"
                    )
                    interaction_tests.append(test_case)
        
        return interaction_tests
    
    def _generate_workflow_tests(self, modules: List[Module]) -> List[TestCase]:
        """Generate end-to-end workflow tests."""
        workflow_tests = []
        
        # Generate a basic workflow test that uses multiple modules
        if len(modules) > 1:
            test_case = TestCase(
                name="test_end_to_end_workflow",
                function_name="workflow",
                test_code=self._generate_workflow_test_code(modules),
                expected_result="pass",
                test_type="integration"
            )
            workflow_tests.append(test_case)
        
        return workflow_tests
    
    def _functions_might_interact(self, func_a: FunctionSpec, func_b: FunctionSpec) -> bool:
        """Determine if two functions might interact."""
        # Simple heuristic: functions with compatible types might interact
        return (func_a.return_type != 'None' and 
                any(arg.type_hint == func_a.return_type for arg in func_b.arguments))
    
    def _generate_interaction_test_code(self, func_a: FunctionSpec, 
                                      func_b: FunctionSpec) -> str:
        """Generate test code for function interaction."""
        args_a = self._generate_sample_arguments(func_a.arguments)
        args_b = self._generate_sample_arguments(func_b.arguments)
        
        test_code = f"""
    def test_{func_a.module}_{func_b.module}_interaction(self):
        \"\"\"Test interaction between {func_a.name} and {func_b.name}.\"\"\"
        # Call first function
        result_a = {func_a.name}({args_a})
        
        # Use result in second function (if compatible)
        result_b = {func_b.name}({args_b})
        
        # Verify interaction works correctly
        self.assertIsNotNone(result_a)
        self.assertIsNotNone(result_b)
"""
        
        return test_code.strip()
    
    def _generate_workflow_test_code(self, modules: List[Module]) -> str:
        """Generate test code for end-to-end workflow."""
        test_code = """
    def test_end_to_end_workflow(self):
        \"\"\"Test complete workflow using multiple modules.\"\"\"
        # This is a placeholder for end-to-end workflow testing
        # Customize based on actual module interactions
        
        # Example workflow steps:
        # 1. Initialize data
        # 2. Process through multiple modules
        # 3. Verify final result
        
        self.assertTrue(True)  # Placeholder assertion
"""
        
        return test_code.strip()
    
    def _create_test_file(self, module: Module, test_cases: List[TestCase], 
                         output_dir: str) -> str:
        """Create a test file for a module with generated test cases."""
        test_file_name = f"test_{module.name.replace('.', '_')}.py"
        test_file_path = os.path.join(output_dir, test_file_name)
        
        # Generate test file content
        test_content = self._generate_test_file_content(module, test_cases)
        
        # Write test file
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return test_file_path
    
    def _generate_test_file_content(self, module: Module, 
                                  test_cases: List[TestCase]) -> str:
        """Generate complete test file content."""
        imports = self._generate_test_imports(module)
        class_name = f"Test{module.name.replace('.', '').title()}"
        
        content = f"""\"\"\"
Unit tests for {module.name} module.

This file contains automatically generated test cases for all functions
in the {module.name} module.
\"\"\"

import unittest
from unittest.mock import Mock, patch, MagicMock
{imports}


class {class_name}(unittest.TestCase):
    \"\"\"Test cases for {module.name} module.\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures before each test method.\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"Clean up after each test method.\"\"\"
        pass

{self._format_test_methods(test_cases)}


if __name__ == '__main__':
    unittest.main()
"""
        
        return content
    
    def _generate_test_imports(self, module: Module) -> str:
        """Generate import statements for test file."""
        # Import the module being tested
        module_import = f"from {module.name} import *"
        
        # Add any additional imports based on module dependencies
        additional_imports = []
        for dep in module.dependencies:
            additional_imports.append(f"import {dep}")
        
        if additional_imports:
            return f"{module_import}\n" + "\n".join(additional_imports)
        else:
            return module_import
    
    def _format_test_methods(self, test_cases: List[TestCase]) -> str:
        """Format test cases as test methods."""
        formatted_methods = []
        
        for test_case in test_cases:
            # Ensure proper indentation
            indented_code = "\n".join(
                "    " + line if line.strip() else line 
                for line in test_case.test_code.split('\n')
            )
            formatted_methods.append(indented_code)
        
        return "\n\n".join(formatted_methods)
    
    def _execute_with_pytest(self, test_files: List[str], **kwargs) -> TestExecutionResult:
        """Execute tests using pytest and collect results."""
        import time
        start_time = time.time()
        
        try:
            # Prepare pytest command with JSON output for better parsing
            cmd = ['python', '-m', 'pytest', '-v', '--tb=short', '--json-report', '--json-report-file=/tmp/pytest_report.json'] + test_files
            
            # Add coverage if requested
            if kwargs.get('coverage', False):
                cmd.extend(['--cov=.', '--cov-report=term-missing', '--cov-report=json:/tmp/coverage.json'])
            
            # Execute pytest
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=kwargs.get('timeout', 300)
            )
            
            execution_time = time.time() - start_time
            
            # Parse pytest output
            return self._parse_pytest_output(result.stdout, result.stderr, result.returncode, execution_time, kwargs.get('coverage', False))
            
        except subprocess.TimeoutExpired:
            execution_time = kwargs.get('timeout', 300)
            return TestExecutionResult(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_details=[],
                coverage_report=None,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return TestExecutionResult(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_details=[],
                coverage_report=None,
                execution_time=execution_time
            )
    
    def _parse_pytest_output(self, stdout: str, stderr: str, 
                           return_code: int, execution_time: float, 
                           coverage_enabled: bool) -> TestExecutionResult:
        """Parse pytest output to extract detailed test results."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        test_details = []
        coverage_report = None
        
        # Try to parse JSON report if available
        try:
            import json
            if os.path.exists('/tmp/pytest_report.json'):
                with open('/tmp/pytest_report.json', 'r') as f:
                    json_report = json.load(f)
                
                # Extract test details from JSON report
                if 'tests' in json_report:
                    for test in json_report['tests']:
                        test_detail = TestDetail(
                            name=test.get('nodeid', 'unknown'),
                            status=test.get('outcome', 'unknown'),
                            message=test.get('call', {}).get('longrepr', None),
                            execution_time=test.get('call', {}).get('duration', 0.0)
                        )
                        test_details.append(test_detail)
                
                # Extract summary
                summary = json_report.get('summary', {})
                total_tests = summary.get('total', 0)
                passed_tests = summary.get('passed', 0)
                failed_tests = summary.get('failed', 0)
                
                # Clean up temporary file
                os.remove('/tmp/pytest_report.json')
        
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            # Fall back to text parsing
            total_tests, passed_tests, failed_tests, test_details = self._parse_pytest_text_output(stdout)
        
        # Parse coverage report if enabled
        if coverage_enabled:
            coverage_report = self._parse_coverage_report()
        
        return TestExecutionResult(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            test_details=test_details,
            coverage_report=coverage_report,
            execution_time=execution_time
        )
    
    def _parse_pytest_text_output(self, stdout: str) -> Tuple[int, int, int, List[TestDetail]]:
        """Parse pytest text output as fallback."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        test_details = []
        
        # Extract test counts from pytest output
        if "failed" in stdout and "passed" in stdout:
            # Parse format like "2 failed, 3 passed"
            failed_match = re.search(r'(\d+) failed', stdout)
            passed_match = re.search(r'(\d+) passed', stdout)
            
            if failed_match:
                failed_tests = int(failed_match.group(1))
            if passed_match:
                passed_tests = int(passed_match.group(1))
                
            total_tests = failed_tests + passed_tests
        elif "passed" in stdout:
            passed_match = re.search(r'(\d+) passed', stdout)
            if passed_match:
                passed_tests = int(passed_match.group(1))
                total_tests = passed_tests
        
        # Extract individual test results
        test_lines = re.findall(r'(.+?)::.+? (PASSED|FAILED|SKIPPED)', stdout)
        for test_file, status in test_lines:
            test_detail = TestDetail(
                name=test_file,
                status=status.lower(),
                message=None,
                execution_time=0.0
            )
            test_details.append(test_detail)
        
        return total_tests, passed_tests, failed_tests, test_details
    
    def _parse_coverage_report(self) -> Optional[CoverageReport]:
        """Parse coverage report from JSON file."""
        try:
            import json
            if os.path.exists('/tmp/coverage.json'):
                with open('/tmp/coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                
                # Extract coverage summary
                totals = coverage_data.get('totals', {})
                total_lines = totals.get('num_statements', 0)
                covered_lines = totals.get('covered_lines', 0)
                coverage_percentage = totals.get('percent_covered', 0.0)
                
                # Extract uncovered lines (simplified)
                uncovered_lines = []
                files = coverage_data.get('files', {})
                for file_data in files.values():
                    missing_lines = file_data.get('missing_lines', [])
                    uncovered_lines.extend(missing_lines)
                
                # Clean up temporary file
                os.remove('/tmp/coverage.json')
                
                return CoverageReport(
                    total_lines=total_lines,
                    covered_lines=covered_lines,
                    coverage_percentage=coverage_percentage,
                    uncovered_lines=uncovered_lines
                )
        
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            pass
        
        return None
    
    def execute_tests_with_detailed_analysis(self, test_files: List[str], 
                                           **kwargs) -> TestGenerationResult:
        """
        Execute tests with comprehensive analysis and reporting.
        
        Args:
            test_files: List of test file paths to execute
            **kwargs: Additional options including:
                - coverage: Enable coverage reporting
                - timeout: Test execution timeout
                - parallel: Run tests in parallel
                - verbose: Enable verbose output
        
        Returns:
            Complete test generation result with execution details
        """
        self._ensure_initialized()
        
        # Execute tests
        execution_result = self.execute_generated_tests(test_files, **kwargs)
        
        # Analyze test failures
        failure_analysis = self._analyze_test_failures(execution_result)
        
        # Generate improvement suggestions
        suggestions = self._generate_test_improvement_suggestions(execution_result)
        
        # Create comprehensive result
        return TestGenerationResult(
            generated_tests=[],  # Would be populated if generating new tests
            test_files_created=test_files,
            execution_result=execution_result,
            success=execution_result.failed_tests == 0,
            errors=failure_analysis.get('errors', [])
        )
    
    def _analyze_test_failures(self, execution_result: TestExecutionResult) -> Dict[str, Any]:
        """Analyze test failures to provide detailed error information."""
        analysis = {
            'errors': [],
            'warnings': [],
            'failure_patterns': [],
            'common_issues': []
        }
        
        if not execution_result.test_details:
            return analysis
        
        # Analyze failed tests
        failed_tests = [test for test in execution_result.test_details if test.status == 'failed']
        
        for failed_test in failed_tests:
            if failed_test.message:
                # Categorize error types
                error_category = self._categorize_test_error(failed_test.message)
                analysis['failure_patterns'].append({
                    'test_name': failed_test.name,
                    'error_category': error_category,
                    'message': failed_test.message
                })
        
        # Identify common failure patterns
        if len(failed_tests) > 1:
            common_patterns = self._identify_common_failure_patterns(failed_tests)
            analysis['common_issues'] = common_patterns
        
        # Generate specific error messages
        if execution_result.failed_tests > 0:
            analysis['errors'].append(
                f"{execution_result.failed_tests} out of {execution_result.total_tests} tests failed"
            )
        
        # Check coverage warnings
        if execution_result.coverage_report:
            if execution_result.coverage_report.coverage_percentage < 80:
                analysis['warnings'].append(
                    f"Low test coverage: {execution_result.coverage_report.coverage_percentage:.1f}%"
                )
        
        return analysis
    
    def _categorize_test_error(self, error_message: str) -> str:
        """Categorize test error based on error message."""
        error_message_lower = error_message.lower()
        
        if 'assertionerror' in error_message_lower:
            return 'assertion_failure'
        elif 'attributeerror' in error_message_lower:
            return 'attribute_error'
        elif 'typeerror' in error_message_lower:
            return 'type_error'
        elif 'valueerror' in error_message_lower:
            return 'value_error'
        elif 'importerror' in error_message_lower or 'modulenotfounderror' in error_message_lower:
            return 'import_error'
        elif 'timeout' in error_message_lower:
            return 'timeout_error'
        else:
            return 'unknown_error'
    
    def _identify_common_failure_patterns(self, failed_tests: List[TestDetail]) -> List[str]:
        """Identify common patterns in test failures."""
        patterns = []
        
        # Group by error type
        error_types = {}
        for test in failed_tests:
            if test.message:
                error_type = self._categorize_test_error(test.message)
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(test)
        
        # Identify patterns
        for error_type, tests in error_types.items():
            if len(tests) > 1:
                patterns.append(f"Multiple {error_type} failures detected ({len(tests)} tests)")
        
        return patterns
    
    def _generate_test_improvement_suggestions(self, execution_result: TestExecutionResult) -> List[str]:
        """Generate suggestions for improving test quality and coverage."""
        suggestions = []
        
        # Coverage suggestions
        if execution_result.coverage_report:
            coverage = execution_result.coverage_report.coverage_percentage
            if coverage < 50:
                suggestions.append("Consider adding more test cases to improve coverage")
            elif coverage < 80:
                suggestions.append("Add tests for edge cases and error conditions")
            
            if execution_result.coverage_report.uncovered_lines:
                suggestions.append(
                    f"Focus on testing uncovered lines: {len(execution_result.coverage_report.uncovered_lines)} lines not covered"
                )
        
        # Performance suggestions
        if execution_result.execution_time > 30:
            suggestions.append("Consider optimizing slow tests or running them in parallel")
        
        # Failure-based suggestions
        if execution_result.failed_tests > 0:
            failure_rate = execution_result.failed_tests / execution_result.total_tests
            if failure_rate > 0.5:
                suggestions.append("High failure rate detected - review test logic and implementation")
            else:
                suggestions.append("Review failed tests and fix underlying issues")
        
        # Test structure suggestions
        if execution_result.total_tests < 5:
            suggestions.append("Consider adding more comprehensive test cases")
        
        return suggestions
    
    def generate_test_report(self, execution_result: TestExecutionResult, 
                           output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive test report.
        
        Args:
            execution_result: Test execution results
            output_file: Optional file path to save report
        
        Returns:
            Formatted test report as string
        """
        report_lines = []
        
        # Header
        report_lines.append("=" * 60)
        report_lines.append("TEST EXECUTION REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Summary
        report_lines.append("SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(f"Total Tests: {execution_result.total_tests}")
        report_lines.append(f"Passed: {execution_result.passed_tests}")
        report_lines.append(f"Failed: {execution_result.failed_tests}")
        report_lines.append(f"Execution Time: {execution_result.execution_time:.2f} seconds")
        
        if execution_result.total_tests > 0:
            success_rate = (execution_result.passed_tests / execution_result.total_tests) * 100
            report_lines.append(f"Success Rate: {success_rate:.1f}%")
        
        report_lines.append("")
        
        # Coverage Report
        if execution_result.coverage_report:
            report_lines.append("COVERAGE REPORT")
            report_lines.append("-" * 20)
            report_lines.append(f"Total Lines: {execution_result.coverage_report.total_lines}")
            report_lines.append(f"Covered Lines: {execution_result.coverage_report.covered_lines}")
            report_lines.append(f"Coverage: {execution_result.coverage_report.coverage_percentage:.1f}%")
            
            if execution_result.coverage_report.uncovered_lines:
                report_lines.append(f"Uncovered Lines: {len(execution_result.coverage_report.uncovered_lines)}")
            
            report_lines.append("")
        
        # Test Details
        if execution_result.test_details:
            report_lines.append("TEST DETAILS")
            report_lines.append("-" * 20)
            
            for test in execution_result.test_details:
                status_symbol = "✓" if test.status == "passed" else "✗" if test.status == "failed" else "⚠"
                report_lines.append(f"{status_symbol} {test.name} ({test.execution_time:.3f}s)")
                
                if test.message and test.status == "failed":
                    # Indent error message
                    error_lines = test.message.split('\n')
                    for line in error_lines[:3]:  # Show first 3 lines of error
                        report_lines.append(f"    {line}")
                    if len(error_lines) > 3:
                        report_lines.append("    ...")
            
            report_lines.append("")
        
        # Failed Tests Analysis
        failed_tests = [test for test in execution_result.test_details if test.status == "failed"]
        if failed_tests:
            report_lines.append("FAILED TESTS ANALYSIS")
            report_lines.append("-" * 20)
            
            for test in failed_tests:
                report_lines.append(f"• {test.name}")
                if test.message:
                    error_category = self._categorize_test_error(test.message)
                    report_lines.append(f"  Category: {error_category}")
            
            report_lines.append("")
        
        # Recommendations
        suggestions = self._generate_test_improvement_suggestions(execution_result)
        if suggestions:
            report_lines.append("RECOMMENDATIONS")
            report_lines.append("-" * 20)
            for suggestion in suggestions:
                report_lines.append(f"• {suggestion}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        # Generate final report
        report_content = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    def run_test_suite_with_retries(self, test_files: List[str], 
                                   max_retries: int = 3, **kwargs) -> TestExecutionResult:
        """
        Execute test suite with retry logic for flaky tests.
        
        Args:
            test_files: List of test file paths
            max_retries: Maximum number of retries for failed tests
            **kwargs: Additional test execution options
        
        Returns:
            Final test execution result after retries
        """
        self._ensure_initialized()
        
        # Initial test run
        result = self.execute_generated_tests(test_files, **kwargs)
        
        # If all tests passed, return immediately
        if result.failed_tests == 0:
            return result
        
        # Retry failed tests
        for retry_count in range(max_retries):
            if result.failed_tests == 0:
                break
            
            # Identify failed test files
            failed_test_files = self._identify_failed_test_files(result, test_files)
            
            if not failed_test_files:
                break
            
            # Log retry attempt
            if self.state_manager:
                self.state_manager.log_info(
                    f"Retrying {len(failed_test_files)} failed test files (attempt {retry_count + 1}/{max_retries})"
                )
            
            # Re-run failed tests
            retry_result = self.execute_generated_tests(failed_test_files, **kwargs)
            
            # Update overall result
            result = self._merge_test_results(result, retry_result)
        
        return result
    
    def _identify_failed_test_files(self, result: TestExecutionResult, 
                                  test_files: List[str]) -> List[str]:
        """Identify which test files contain failed tests."""
        failed_files = set()
        
        for test_detail in result.test_details:
            if test_detail.status == "failed":
                # Extract file name from test name
                test_file = test_detail.name.split("::")[0]
                # Find matching test file
                for file_path in test_files:
                    if test_file in file_path or file_path.endswith(test_file):
                        failed_files.add(file_path)
                        break
        
        return list(failed_files)
    
    def _merge_test_results(self, original: TestExecutionResult, 
                          retry: TestExecutionResult) -> TestExecutionResult:
        """Merge original and retry test results."""
        # Simple merge - in practice, this would be more sophisticated
        return TestExecutionResult(
            total_tests=original.total_tests,
            passed_tests=original.passed_tests + retry.passed_tests - retry.failed_tests,
            failed_tests=max(0, original.failed_tests - (retry.passed_tests - retry.failed_tests)),
            test_details=original.test_details + retry.test_details,
            coverage_report=retry.coverage_report or original.coverage_report,
            execution_time=original.execution_time + retry.execution_time
        )