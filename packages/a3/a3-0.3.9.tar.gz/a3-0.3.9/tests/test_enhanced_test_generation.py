"""
Tests for enhanced test generation functionality in A3.

This module tests the enhanced test generation capabilities to ensure:
1. AI-powered test case generation works correctly
2. Specific input/output validation functions properly
3. Error handling and fallback mechanisms work as expected
4. Integration with existing test execution framework works
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from a3.core.api import A3, ValidationError, OperationError, ProjectStateError
from a3.core.models import (
    IntelligentTestCase, TestGenerationResult, TestExecutionResult, 
    TestDetail, Module, FunctionSpec, Argument, ProjectPlan
)
from a3.engines.test_generator import TestGenerator


class TestIntelligentTestCase:
    """Test suite for IntelligentTestCase data model."""
    
    def test_intelligent_test_case_creation(self):
        """Test creating an IntelligentTestCase with all fields."""
        test_case = IntelligentTestCase(
            name="test_calculate_total",
            function_name="calculate_total",
            test_code="assert calculate_total(10, 0.1) == 11.0",
            expected_result="pass",
            test_type="unit",
            dependencies=[],
            input_examples=[{"amount": 10, "tax_rate": 0.1}],
            expected_outputs=[11.0],
            test_description="Test calculate_total with basic inputs",
            validation_strategy="exact_match",
            ai_generated=True
        )
        
        assert test_case.name == "test_calculate_total"
        assert test_case.function_name == "calculate_total"
        assert len(test_case.input_examples) == 1
        assert len(test_case.expected_outputs) == 1
        assert test_case.validation_strategy == "exact_match"
        assert test_case.ai_generated is True
    
    def test_intelligent_test_case_validation_success(self):
        """Test that valid IntelligentTestCase passes validation."""
        test_case = IntelligentTestCase(
            name="test_valid_function",
            function_name="valid_function",
            test_code="assert valid_function() == True",
            input_examples=[{}],
            expected_outputs=[True],
            validation_strategy="exact_match"
        )
        
        # Should not raise any exception
        test_case.validate()
    
    def test_intelligent_test_case_validation_empty_name(self):
        """Test that empty name fails validation."""
        test_case = IntelligentTestCase(
            name="",
            function_name="some_function",
            test_code="pass",
            input_examples=[{}],
            expected_outputs=[None]
        )
        
        with pytest.raises(ValidationError, match="Test case name cannot be empty"):
            test_case.validate()
    
    def test_intelligent_test_case_validation_empty_function_name(self):
        """Test that empty function name fails validation."""
        test_case = IntelligentTestCase(
            name="test_something",
            function_name="",
            test_code="pass",
            input_examples=[{}],
            expected_outputs=[None]
        )
        
        with pytest.raises(ValidationError, match="Function name cannot be empty"):
            test_case.validate()
    
    def test_intelligent_test_case_validation_empty_test_code(self):
        """Test that empty test code fails validation."""
        test_case = IntelligentTestCase(
            name="test_something",
            function_name="some_function",
            test_code="",
            input_examples=[{}],
            expected_outputs=[None]
        )
        
        with pytest.raises(ValidationError, match="Test code cannot be empty"):
            test_case.validate()
    
    def test_intelligent_test_case_validation_mismatched_examples(self):
        """Test that mismatched input/output examples fail validation."""
        test_case = IntelligentTestCase(
            name="test_something",
            function_name="some_function",
            test_code="pass",
            input_examples=[{"a": 1}, {"b": 2}],  # 2 inputs
            expected_outputs=[1]  # 1 output
        )
        
        with pytest.raises(ValidationError, match="Number of input examples must match number of expected outputs"):
            test_case.validate()
    
    def test_intelligent_test_case_validation_invalid_strategy(self):
        """Test that invalid validation strategy fails validation."""
        test_case = IntelligentTestCase(
            name="test_something",
            function_name="some_function",
            test_code="pass",
            input_examples=[{}],
            expected_outputs=[None],
            validation_strategy="invalid_strategy"
        )
        
        with pytest.raises(ValidationError, match="Invalid validation strategy"):
            test_case.validate()
    
    def test_intelligent_test_case_validation_non_dict_input(self):
        """Test that non-dictionary input examples fail validation."""
        test_case = IntelligentTestCase(
            name="test_something",
            function_name="some_function",
            test_code="pass",
            input_examples=["not_a_dict"],
            expected_outputs=[None]
        )
        
        with pytest.raises(ValidationError, match="Input example 0 must be a dictionary"):
            test_case.validate()
    
    def test_intelligent_test_case_to_dict(self):
        """Test serialization of IntelligentTestCase to dictionary."""
        test_case = IntelligentTestCase(
            name="test_example",
            function_name="example_function",
            test_code="assert example_function(1) == 2",
            input_examples=[{"x": 1}],
            expected_outputs=[2],
            test_description="Example test",
            validation_strategy="exact_match",
            ai_generated=False
        )
        
        result_dict = test_case.to_dict()
        
        assert result_dict["name"] == "test_example"
        assert result_dict["function_name"] == "example_function"
        assert result_dict["input_examples"] == [{"x": 1}]
        assert result_dict["expected_outputs"] == [2]
        assert result_dict["test_description"] == "Example test"
        assert result_dict["validation_strategy"] == "exact_match"
        assert result_dict["ai_generated"] is False
    
    def test_intelligent_test_case_from_dict(self):
        """Test deserialization of IntelligentTestCase from dictionary."""
        data = {
            "name": "test_from_dict",
            "function_name": "dict_function",
            "test_code": "assert dict_function() == 'success'",
            "input_examples": [{}],
            "expected_outputs": ["success"],
            "test_description": "Test from dict",
            "validation_strategy": "type_check",
            "ai_generated": True
        }
        
        test_case = IntelligentTestCase.from_dict(data)
        
        assert test_case.name == "test_from_dict"
        assert test_case.function_name == "dict_function"
        assert test_case.input_examples == [{}]
        assert test_case.expected_outputs == ["success"]
        assert test_case.test_description == "Test from dict"
        assert test_case.validation_strategy == "type_check"
        assert test_case.ai_generated is True
    
    def test_intelligent_test_case_generate_test_code_exact_match(self):
        """Test generating test code with exact match validation."""
        test_case = IntelligentTestCase(
            name="test_add",
            function_name="add",
            test_code="",
            input_examples=[{"a": 2, "b": 3}, {"a": 5, "b": 7}],
            expected_outputs=[5, 12],
            test_description="Test addition function",
            validation_strategy="exact_match"
        )
        
        generated_code = test_case.generate_test_code()
        
        assert "def test_add():" in generated_code
        assert "add(a=2, b=3)" in generated_code
        assert "add(a=5, b=7)" in generated_code
        assert "assert result_0 == 5" in generated_code
        assert "assert result_1 == 12" in generated_code
    
    def test_intelligent_test_case_generate_test_code_type_check(self):
        """Test generating test code with type check validation."""
        test_case = IntelligentTestCase(
            name="test_get_name",
            function_name="get_name",
            test_code="",
            input_examples=[{"user_id": 1}],
            expected_outputs=["John"],
            test_description="Test get_name function",
            validation_strategy="type_check"
        )
        
        generated_code = test_case.generate_test_code()
        
        assert "def test_get_name():" in generated_code
        assert "get_name(user_id=1)" in generated_code
        assert "assert isinstance(result_0, str)" in generated_code
    
    def test_intelligent_test_case_generate_test_code_custom(self):
        """Test generating test code with custom validation."""
        custom_test_code = "assert len(result_0) > 0"
        test_case = IntelligentTestCase(
            name="test_custom",
            function_name="custom_function",
            test_code=custom_test_code,
            input_examples=[{"param": "test"}],
            expected_outputs=["result"],
            validation_strategy="custom"
        )
        
        generated_code = test_case.generate_test_code()
        
        assert "def test_custom():" in generated_code
        assert "custom_function(param='test')" in generated_code
        assert custom_test_code in generated_code


class TestA3GenerateTestsAPI:
    """Test suite for A3.generate_tests API method."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create temporary directory for test project
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Create A3 instance
        self.a3 = A3(str(self.project_path))
        self.a3.set_api_key("test-api-key")
        
        # Mock the OpenRouter client
        self.mock_client_patcher = patch('a3.clients.openrouter.OpenRouterClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        self.mock_client.validate_api_key.return_value = True
        
        # Create a mock project plan
        self.mock_function = FunctionSpec(
            name="calculate_total",
            module="calculator",
            docstring="Calculate total with tax",
            arguments=[
                Argument(name="amount", type_hint="float"),
                Argument(name="tax_rate", type_hint="float")
            ],
            return_type="float"
        )
        
        self.mock_module = Module(
            name="calculator",
            description="Calculator module",
            file_path="calculator.py",
            functions=[self.mock_function]
        )
        
        self.mock_plan = ProjectPlan(
            objective="Test project",
            modules=[self.mock_module],
            estimated_functions=1
        )
        
        # Mock state manager to return the plan
        self.a3._state_manager.load_project_plan = Mock(return_value=self.mock_plan)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.mock_client_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_tests_valid_input(self):
        """Test generate_tests with valid input."""
        test_cases = [
            {
                "name": "test_basic_calculation",
                "description": "Test basic tax calculation",
                "input_examples": [{"amount": 100.0, "tax_rate": 0.1}],
                "expected_outputs": [110.0],
                "validation_strategy": "exact_match"
            }
        ]
        
        with patch('a3.engines.test_generator.TestGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.initialize.return_value = None
            
            result = self.a3.generate_tests("calculate_total", test_cases)
            
            assert isinstance(result, TestGenerationResult)
            assert result.success is True
            assert len(result.errors) == 0
    
    def test_generate_tests_empty_function_name(self):
        """Test that empty function name raises ValidationError."""
        test_cases = [{"input_examples": [{}], "expected_outputs": [None]}]
        
        with pytest.raises(ValidationError, match="Function name cannot be empty"):
            self.a3.generate_tests("", test_cases)
    
    def test_generate_tests_empty_test_cases(self):
        """Test that empty test cases list raises ValidationError."""
        with pytest.raises(ValidationError, match="Test cases must be a non-empty list"):
            self.a3.generate_tests("some_function", [])
    
    def test_generate_tests_invalid_test_cases_type(self):
        """Test that non-list test cases raises ValidationError."""
        with pytest.raises(ValidationError, match="Test cases must be a non-empty list"):
            self.a3.generate_tests("some_function", "not_a_list")
    
    def test_generate_tests_function_not_found(self):
        """Test that non-existent function raises ValidationError."""
        test_cases = [{"input_examples": [{}], "expected_outputs": [None]}]
        
        with pytest.raises(ValidationError, match="Function 'nonexistent_function' not found"):
            self.a3.generate_tests("nonexistent_function", test_cases)
    
    def test_generate_tests_no_project_plan(self):
        """Test that missing project plan raises ProjectStateError."""
        self.a3._state_manager.load_project_plan = Mock(return_value=None)
        test_cases = [{"input_examples": [{}], "expected_outputs": [None]}]
        
        with pytest.raises(ProjectStateError, match="No project plan found"):
            self.a3.generate_tests("some_function", test_cases)
    
    def test_generate_tests_invalid_test_case_structure(self):
        """Test that invalid test case structure raises ValidationError."""
        test_cases = [
            "not_a_dict"  # Should be a dictionary
        ]
        
        with pytest.raises(ValidationError, match="Test case 0 must be a dictionary"):
            self.a3.generate_tests("calculate_total", test_cases)
    
    def test_generate_tests_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        test_cases = [
            {"description": "Missing input_examples and expected_outputs"}
        ]
        
        with pytest.raises(ValidationError, match="Test case 0 must include 'input_examples'"):
            self.a3.generate_tests("calculate_total", test_cases)
    
    def test_generate_tests_mismatched_input_output_length(self):
        """Test that mismatched input/output lengths raises ValidationError."""
        test_cases = [
            {
                "input_examples": [{"a": 1}, {"b": 2}],  # 2 inputs
                "expected_outputs": [1]  # 1 output
            }
        ]
        
        with pytest.raises(ValidationError, match="number of input examples must match number of expected outputs"):
            self.a3.generate_tests("calculate_total", test_cases)
    
    def test_generate_tests_non_list_inputs_outputs(self):
        """Test that non-list inputs/outputs raises ValidationError."""
        test_cases = [
            {
                "input_examples": "not_a_list",
                "expected_outputs": "also_not_a_list"
            }
        ]
        
        with pytest.raises(ValidationError, match="input_examples and expected_outputs must be lists"):
            self.a3.generate_tests("calculate_total", test_cases)
    
    def test_generate_tests_creates_test_files(self):
        """Test that generate_tests creates test files."""
        test_cases = [
            {
                "input_examples": [{"amount": 100.0, "tax_rate": 0.1}],
                "expected_outputs": [110.0]
            }
        ]
        
        with patch('a3.engines.test_generator.TestGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.initialize.return_value = None
            
            # Mock the test file generation
            with patch.object(self.a3, '_generate_targeted_test_file_content') as mock_content:
                mock_content.return_value = "# Test file content"
                
                result = self.a3.generate_tests("calculate_total", test_cases)
                
                assert len(result.test_files_created) > 0
                assert any("test_calculator_targeted.py" in path for path in result.test_files_created)


class TestTestGeneratorEnhanced:
    """Test suite for enhanced TestGenerator functionality."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.mock_ai_client = Mock()
        self.mock_state_manager = Mock()
        self.test_generator = TestGenerator(self.mock_ai_client, self.mock_state_manager)
        self.test_generator.initialize()
    
    def test_generate_intelligent_test_cases_success(self):
        """Test successful generation of intelligent test cases."""
        # Create mock module and function
        mock_function = FunctionSpec(
            name="add_numbers",
            module="math_utils",
            docstring="Add two numbers",
            arguments=[
                Argument(name="a", type_hint="int"),
                Argument(name="b", type_hint="int")
            ],
            return_type="int"
        )
        
        mock_module = Module(
            name="math_utils",
            description="Math utilities",
            file_path="math_utils.py",
            functions=[mock_function]
        )
        
        # Mock AI client response
        self.mock_ai_client.chat_completion.return_value = Mock(
            content=json.dumps({
                "test_cases": [
                    {
                        "name": "test_add_positive_numbers",
                        "input_examples": [{"a": 2, "b": 3}],
                        "expected_outputs": [5],
                        "description": "Test adding positive numbers"
                    }
                ]
            })
        )
        
        # Mock the AI-powered test case generation method
        with patch.object(self.test_generator, '_generate_ai_powered_test_cases') as mock_generate:
            mock_test_case = IntelligentTestCase(
                name="test_add_positive_numbers",
                function_name="add_numbers",
                test_code="assert add_numbers(2, 3) == 5",
                input_examples=[{"a": 2, "b": 3}],
                expected_outputs=[5],
                test_description="Test adding positive numbers"
            )
            mock_generate.return_value = [mock_test_case]
            
            result = self.test_generator.generate_intelligent_test_cases([mock_module])
            
            assert len(result) == 1
            assert result[0].name == "test_add_positive_numbers"
            assert result[0].function_name == "add_numbers"
    
    def test_generate_intelligent_test_cases_empty_modules(self):
        """Test that empty modules list returns empty result."""
        result = self.test_generator.generate_intelligent_test_cases([])
        assert result == []
    
    def test_generate_intelligent_test_cases_with_failures(self):
        """Test handling of failures during intelligent test generation."""
        mock_function = FunctionSpec(
            name="failing_function",
            module="test_module",
            docstring="A function that fails test generation",
            arguments=[],
            return_type="None"
        )
        
        mock_module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=[mock_function]
        )
        
        # Mock the AI-powered test case generation to fail
        with patch.object(self.test_generator, '_generate_ai_powered_test_cases') as mock_generate:
            mock_generate.side_effect = Exception("AI generation failed")
            
            # Should handle the error gracefully and continue
            result = self.test_generator.generate_intelligent_test_cases([mock_module])
            
            # Should return empty list due to failure
            assert result == []
    
    def test_execute_intelligent_tests_success(self):
        """Test successful execution of intelligent test cases."""
        test_case = IntelligentTestCase(
            name="test_simple",
            function_name="simple_function",
            test_code="def test_simple(): assert True",
            input_examples=[{}],
            expected_outputs=[True]
        )
        
        # Mock pytest execution
        with patch.object(self.test_generator, '_execute_with_pytest_enhanced') as mock_execute:
            mock_result = TestExecutionResult(
                total_tests=1,
                passed_tests=1,
                failed_tests=0,
                test_details=[
                    TestDetail(
                        test_name="test_simple",
                        status="passed",
                        message="Test passed",
                        traceback="",
                        execution_time=0.1
                    )
                ],
                coverage_report=None,
                execution_time=0.1
            )
            mock_execute.return_value = mock_result
            
            result = self.test_generator.execute_intelligent_tests([test_case])
            
            assert result.total_tests == 1
            assert result.passed_tests == 1
            assert result.failed_tests == 0
    
    def test_execute_intelligent_tests_empty_list(self):
        """Test execution with empty test case list."""
        result = self.test_generator.execute_intelligent_tests([])
        
        assert result.total_tests == 0
        assert result.passed_tests == 0
        assert result.failed_tests == 0
        assert result.test_details == []
    
    def test_execute_intelligent_tests_with_failures(self):
        """Test execution of intelligent test cases with failures."""
        test_case = IntelligentTestCase(
            name="test_failing",
            function_name="failing_function",
            test_code="def test_failing(): assert False",
            input_examples=[{}],
            expected_outputs=[True]
        )
        
        # Mock pytest execution with failure
        with patch.object(self.test_generator, '_execute_with_pytest_enhanced') as mock_execute:
            mock_result = TestExecutionResult(
                total_tests=1,
                passed_tests=0,
                failed_tests=1,
                test_details=[
                    TestDetail(
                        test_name="test_failing",
                        status="failed",
                        message="AssertionError: assert False",
                        traceback="Traceback...",
                        execution_time=0.1
                    )
                ],
                coverage_report=None,
                execution_time=0.1
            )
            mock_execute.return_value = mock_result
            
            result = self.test_generator.execute_intelligent_tests([test_case])
            
            assert result.total_tests == 1
            assert result.passed_tests == 0
            assert result.failed_tests == 1
            assert "AssertionError" in result.test_details[0].message


class TestTestGenerationErrorHandling:
    """Test suite for error handling and fallback mechanisms in test generation."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.mock_ai_client = Mock()
        self.mock_state_manager = Mock()
        self.test_generator = TestGenerator(self.mock_ai_client, self.mock_state_manager)
        self.test_generator.initialize()
    
    def test_ai_generation_failure_fallback(self):
        """Test fallback to template-based tests when AI generation fails."""
        mock_function = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="None"
        )
        
        mock_module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=[mock_function]
        )
        
        # Mock AI client to fail
        self.mock_ai_client.chat_completion.side_effect = Exception("AI service unavailable")
        
        # Mock the fallback method
        with patch.object(self.test_generator, '_create_minimal_test_case') as mock_fallback:
            mock_test_case = IntelligentTestCase(
                name="test_function_minimal",
                function_name="test_function",
                test_code="def test_function_minimal(): pass",
                ai_generated=False
            )
            mock_fallback.return_value = [mock_test_case]
            
            result = self.test_generator.generate_module_tests(mock_module)
            
            # Should have fallback test case
            assert len(result) == 1
            assert result[0].ai_generated is False
    
    def test_test_execution_timeout_handling(self):
        """Test handling of test execution timeouts."""
        test_case = IntelligentTestCase(
            name="test_timeout",
            function_name="slow_function",
            test_code="def test_timeout(): import time; time.sleep(10)",
            input_examples=[{}],
            expected_outputs=[None]
        )
        
        # Mock subprocess to raise TimeoutExpired
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("pytest", 5)
            
            result = self.test_generator.execute_intelligent_tests([test_case], timeout=5)
            
            assert result.total_tests == 0
            assert result.failed_tests == 0
            assert len(result.test_details) == 1
            assert "timed out" in result.test_details[0].message
    
    def test_test_file_creation_error_handling(self):
        """Test handling of errors during test file creation."""
        test_case = IntelligentTestCase(
            name="test_file_error",
            function_name="some_function",
            test_code="def test_file_error(): pass",
            input_examples=[{}],
            expected_outputs=[None]
        )
        
        # Mock file operations to fail
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = OSError("Permission denied")
            
            # Should handle the error gracefully
            with patch.object(self.test_generator, '_execute_with_pytest_enhanced') as mock_execute:
                mock_execute.return_value = TestExecutionResult(
                    total_tests=0, passed_tests=0, failed_tests=0,
                    test_details=[], coverage_report=None, execution_time=0.0
                )
                
                result = self.test_generator.execute_intelligent_tests([test_case])
                
                # Should return empty result without crashing
                assert result.total_tests == 0
    
    def test_invalid_test_case_recovery(self):
        """Test recovery from invalid test case specifications."""
        # Create test case with invalid structure
        invalid_test_case = IntelligentTestCase(
            name="",  # Invalid: empty name
            function_name="some_function",
            test_code="invalid code",
            input_examples=[{"a": 1}],
            expected_outputs=[1, 2]  # Invalid: mismatched length
        )
        
        # Validation should fail
        with pytest.raises(ValidationError):
            invalid_test_case.validate()
    
    def test_partial_test_generation_failure_recovery(self):
        """Test recovery when some test cases fail to generate."""
        mock_functions = [
            FunctionSpec(name="good_function", module="test", docstring="Good", arguments=[], return_type="None"),
            FunctionSpec(name="bad_function", module="test", docstring="Bad", arguments=[], return_type="None")
        ]
        
        mock_module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=mock_functions
        )
        
        # Mock one function to succeed, one to fail
        with patch.object(self.test_generator, '_generate_function_tests') as mock_generate:
            def side_effect(func, module):
                if func.name == "good_function":
                    return [IntelligentTestCase(
                        name="test_good_function",
                        function_name="good_function",
                        test_code="def test_good_function(): pass"
                    )]
                else:
                    raise Exception("Generation failed")
            
            mock_generate.side_effect = side_effect
            
            # Mock minimal test case creation for recovery
            with patch.object(self.test_generator, '_create_minimal_test_case') as mock_minimal:
                mock_minimal.return_value = [IntelligentTestCase(
                    name="test_bad_function_minimal",
                    function_name="bad_function",
                    test_code="def test_bad_function_minimal(): pass",
                    ai_generated=False
                )]
                
                result = self.test_generator.generate_module_tests(mock_module)
                
                # Should have both tests: one successful, one recovered
                assert len(result) == 2
                assert any(tc.name == "test_good_function" for tc in result)
                assert any(tc.name == "test_bad_function_minimal" for tc in result)


class TestTestGenerationIntegration:
    """Integration tests for test generation with other A3 components."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.a3 = A3(str(self.project_path))
        self.a3.set_api_key("test-api-key")
        
        # Mock the OpenRouter client
        self.mock_client_patcher = patch('a3.clients.openrouter.OpenRouterClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        self.mock_client.validate_api_key.return_value = True
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.mock_client_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_test_generation_workflow(self):
        """Test complete workflow from function spec to executable tests."""
        # Create mock project structure
        mock_function = FunctionSpec(
            name="multiply",
            module="calculator",
            docstring="Multiply two numbers",
            arguments=[
                Argument(name="x", type_hint="float"),
                Argument(name="y", type_hint="float")
            ],
            return_type="float"
        )
        
        mock_module = Module(
            name="calculator",
            description="Calculator module",
            file_path="calculator.py",
            functions=[mock_function]
        )
        
        mock_plan = ProjectPlan(
            objective="Calculator project",
            modules=[mock_module],
            estimated_functions=1
        )
        
        # Mock state manager
        self.a3._state_manager.load_project_plan = Mock(return_value=mock_plan)
        
        # Define test cases
        test_cases = [
            {
                "name": "test_multiply_positive",
                "description": "Test multiplication of positive numbers",
                "input_examples": [{"x": 3.0, "y": 4.0}],
                "expected_outputs": [12.0],
                "validation_strategy": "exact_match"
            },
            {
                "name": "test_multiply_zero",
                "description": "Test multiplication with zero",
                "input_examples": [{"x": 5.0, "y": 0.0}],
                "expected_outputs": [0.0],
                "validation_strategy": "exact_match"
            }
        ]
        
        # Mock test generator
        with patch('a3.engines.test_generator.TestGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.initialize.return_value = None
            
            # Execute test generation
            result = self.a3.generate_tests("multiply", test_cases)
            
            # Verify result
            assert isinstance(result, TestGenerationResult)
            assert result.success is True
            assert len(result.errors) == 0
    
    def test_test_generation_with_existing_project_state(self):
        """Test test generation works with existing project state."""
        # This would test integration with state management
        # For now, verify that state manager is properly used
        
        mock_plan = ProjectPlan(
            objective="Test project",
            modules=[],
            estimated_functions=0
        )
        
        self.a3._state_manager.load_project_plan = Mock(return_value=mock_plan)
        
        # Should handle empty project gracefully
        test_cases = [{"input_examples": [{}], "expected_outputs": [None]}]
        
        with pytest.raises(ValidationError, match="Function 'nonexistent' not found"):
            self.a3.generate_tests("nonexistent", test_cases)
    
    def test_test_generation_error_logging(self):
        """Test that test generation errors are properly logged."""
        mock_function = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="None"
        )
        
        mock_module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=[mock_function]
        )
        
        mock_plan = ProjectPlan(
            objective="Test project",
            modules=[mock_module],
            estimated_functions=1
        )
        
        self.a3._state_manager.load_project_plan = Mock(return_value=mock_plan)
        
        # Mock test generator to fail
        with patch('a3.engines.test_generator.TestGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.initialize.side_effect = Exception("Initialization failed")
            
            test_cases = [{"input_examples": [{}], "expected_outputs": [None]}]
            
            # Should handle the error and provide meaningful feedback
            with pytest.raises(Exception):  # The specific exception depends on implementation
                self.a3.generate_tests("test_function", test_cases)