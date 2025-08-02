"""
Tests for the CodeGenerator class.

This module contains comprehensive tests for the code generation functionality,
including function implementation, retry logic, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from a3.engines.code_generator import (
    CodeGenerator, CodeGeneratorError, CodeGenerationError, CodeValidationError
)
from a3.core.models import (
    FunctionSpec, Argument, SpecificationSet, ImplementationResult,
    ImplementationStatus, ValidationResult, ProjectPhase
)
from a3.core.interfaces import AIClientInterface, StateManagerInterface


class TestCodeGenerator:
    """Test cases for CodeGenerator class."""
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        client = Mock(spec=AIClientInterface)
        client.validate_api_key.return_value = True
        client.generate_with_retry.return_value = '''
def test_function(x: int, y: str = "default") -> str:
    """Test function implementation."""
    return f"{y}: {x}"
'''
        return client
    
    @pytest.fixture
    def mock_state_manager(self):
        """Create a mock state manager."""
        manager = Mock(spec=StateManagerInterface)
        return manager
    
    @pytest.fixture
    def sample_function_spec(self):
        """Create a sample function specification."""
        return FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function for unit testing.",
            arguments=[
                Argument(name="x", type_hint="int", description="Integer parameter"),
                Argument(name="y", type_hint="str", default_value='"default"', description="String parameter")
            ],
            return_type="str",
            implementation_status=ImplementationStatus.NOT_STARTED
        )
    
    @pytest.fixture
    def sample_specification_set(self, sample_function_spec):
        """Create a sample specification set."""
        func2 = FunctionSpec(
            name="another_function",
            module="test_module",
            docstring="Another test function.",
            arguments=[Argument(name="data", type_hint="Dict[str, Any]", description="Data parameter")],
            return_type="bool",
            implementation_status=ImplementationStatus.NOT_STARTED
        )
        
        return SpecificationSet(
            functions=[sample_function_spec, func2],
            modules=[],
            generated_at=datetime.now()
        )
    
    @pytest.fixture
    def code_generator(self, mock_ai_client, mock_state_manager):
        """Create a CodeGenerator instance."""
        generator = CodeGenerator(mock_ai_client, mock_state_manager)
        generator.initialize()
        return generator
    
    def test_initialization(self, mock_ai_client, mock_state_manager):
        """Test CodeGenerator initialization."""
        generator = CodeGenerator(mock_ai_client, mock_state_manager)
        
        assert generator.ai_client == mock_ai_client
        assert generator.state_manager == mock_state_manager
        assert generator.max_retries == 3
        assert generator.generated_code == {}
        assert generator.failed_functions == []
        assert not generator._initialized
        
        generator.initialize()
        assert generator._initialized
    
    def test_validate_prerequisites(self, mock_ai_client, mock_state_manager):
        """Test prerequisite validation."""
        generator = CodeGenerator(mock_ai_client, mock_state_manager)
        
        # Before initialization
        result = generator.validate_prerequisites()
        assert not result.is_valid
        assert "Engine has not been initialized" in result.issues
        
        # After initialization
        generator.initialize()
        result = generator.validate_prerequisites()
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_validate_prerequisites_no_ai_client(self):
        """Test prerequisite validation without AI client."""
        generator = CodeGenerator(None, None)
        result = generator.validate_prerequisites()
        
        assert not result.is_valid
        assert "AI client is required but not provided" in result.issues
        assert "State manager not provided - state will not be persisted" in result.warnings
    
    def test_implement_function_success(self, code_generator, sample_function_spec):
        """Test successful function implementation."""
        # Test implementation
        code = code_generator.implement_function(sample_function_spec)
        
        # Verify results
        assert code is not None
        assert "def test_function(" in code
        assert sample_function_spec.implementation_status == ImplementationStatus.COMPLETED
        assert "test_module.test_function" in code_generator.generated_code
        
        # Verify AI client was called
        code_generator.ai_client.generate_with_retry.assert_called_once()
    
    def test_implement_function_none_spec(self, code_generator):
        """Test implementation with None specification."""
        with pytest.raises(CodeGenerationError, match="Function specification cannot be None"):
            code_generator.implement_function(None)
    
    def test_implement_function_invalid_spec(self, code_generator):
        """Test implementation with invalid specification."""
        invalid_spec = FunctionSpec(
            name="",  # Invalid empty name
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="str"
        )
        
        with pytest.raises(CodeGenerationError):
            code_generator.implement_function(invalid_spec)
    
    def test_implement_function_ai_failure(self, code_generator, sample_function_spec):
        """Test function implementation when AI fails."""
        # Mock AI client to raise exception
        code_generator.ai_client.generate_with_retry.side_effect = Exception("AI service error")
        
        with pytest.raises(CodeGenerationError):
            code_generator.implement_function(sample_function_spec)
        
        # Verify function is marked as failed
        assert sample_function_spec.implementation_status == ImplementationStatus.FAILED
        assert "test_module.test_function" in code_generator.failed_functions
    
    def test_implement_function_already_completed(self, code_generator, sample_function_spec):
        """Test implementation of already completed function."""
        # Mark as completed and cache code
        sample_function_spec.implementation_status = ImplementationStatus.COMPLETED
        cached_code = "def test_function(): pass"
        code_generator.generated_code["test_module.test_function"] = cached_code
        
        # Test implementation
        code = code_generator.implement_function(sample_function_spec)
        
        # Should return cached code without calling AI
        assert code == cached_code
        code_generator.ai_client.generate_with_retry.assert_not_called()
    
    def test_implement_all_success(self, code_generator, sample_specification_set):
        """Test successful implementation of all functions."""
        # Mock AI responses for different functions
        def mock_generate(prompt, max_retries=3):
            if "test_function" in prompt:
                return 'def test_function(x: int, y: str = "default") -> str:\n    """Test function."""\n    return f"{y}: {x}"'
            else:
                return 'def another_function(data: Dict[str, Any]) -> bool:\n    """Another function."""\n    return bool(data)'
        
        code_generator.ai_client.generate_with_retry.side_effect = mock_generate
        
        # Test implementation
        result = code_generator.implement_all(sample_specification_set)
        
        # Verify results
        assert isinstance(result, ImplementationResult)
        assert len(result.implemented_functions) == 2
        assert len(result.failed_functions) == 0
        assert result.success_rate == 1.0
        assert "test_module.test_function" in result.implemented_functions
        assert "test_module.another_function" in result.implemented_functions
        
        # Verify state manager was called
        code_generator.state_manager.save_progress.assert_called()
    
    def test_implement_all_empty_specs(self, code_generator):
        """Test implementation with empty specification set."""
        empty_specs = SpecificationSet(functions=[], modules=[], generated_at=datetime.now())
        
        with pytest.raises(CodeGenerationError, match="Specification set cannot be empty"):
            code_generator.implement_all(empty_specs)
    
    def test_implement_all_partial_failure(self, code_generator, sample_specification_set):
        """Test implementation with some functions failing."""
        # Mock AI to succeed on first function (another_function) and fail on second (test_function)
        call_count = 0
        def mock_generate(prompt, max_retries=3):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First function (another_function alphabetically)
                return 'def another_function(data: Dict[str, Any]) -> bool:\n    """Another function."""\n    return bool(data)'
            else:
                # Second function fails
                raise Exception("AI failure")
        
        code_generator.ai_client.generate_with_retry.side_effect = mock_generate
        
        # Test implementation
        result = code_generator.implement_all(sample_specification_set)
        
        # Verify results
        assert len(result.implemented_functions) == 1
        assert len(result.failed_functions) == 1
        assert result.success_rate == 0.5
        assert "test_module.another_function" in result.implemented_functions
        assert "test_module.test_function" in result.failed_functions
    
    def test_retry_failed_implementations_empty_list(self, code_generator):
        """Test retry with empty failed functions list."""
        result = code_generator.retry_failed_implementations([])
        
        assert isinstance(result, ImplementationResult)
        assert len(result.implemented_functions) == 0
        assert len(result.failed_functions) == 0
        assert result.success_rate == 1.0
    
    def test_retry_failed_implementations_no_specs(self, code_generator):
        """Test retry when specifications cannot be loaded but minimal specs are created."""
        # The enhanced implementation now creates minimal specs as fallback
        # Mock AI to succeed
        code_generator.ai_client.generate_with_retry.return_value = '''
def test_function() -> str:
    """Test function."""
    return "success"
'''
        
        result = code_generator.retry_failed_implementations(["test_module.test_function"])
        
        # Should succeed with minimal spec fallback
        assert result.success_rate == 1.0
        assert len(result.implemented_functions) == 1
    
    def test_create_code_generation_prompt(self, code_generator, sample_function_spec):
        """Test code generation prompt creation."""
        prompt = code_generator._create_code_generation_prompt(sample_function_spec)
        
        assert "test_function" in prompt
        assert "test_module" in prompt
        assert "x: int" in prompt
        assert 'y: str = "default"' in prompt
        assert "str" in prompt  # return type
        assert "Test function for unit testing" in prompt
        assert "def function_name(" in prompt  # example format
    
    def test_extract_code_from_response_with_markdown(self, code_generator):
        """Test code extraction from markdown response."""
        response = '''
Here's the implementation:

```python
def test_function(x: int) -> str:
    """Test function."""
    return str(x)
```

This should work well.
'''
        
        code = code_generator._extract_code_from_response(response)
        expected = 'def test_function(x: int) -> str:\n    """Test function."""\n    return str(x)'
        assert code == expected
    
    def test_extract_code_from_response_without_markdown(self, code_generator):
        """Test code extraction from plain response."""
        response = '''def test_function(x: int) -> str:
    """Test function."""
    return str(x)'''
        
        code = code_generator._extract_code_from_response(response)
        assert code == response
    
    def test_extract_code_from_response_invalid(self, code_generator):
        """Test code extraction from invalid response."""
        response = "This is not a function definition"
        
        with pytest.raises(CodeValidationError, match="Generated code does not start with function definition"):
            code_generator._extract_code_from_response(response)
    
    def test_validate_generated_code_success(self, code_generator, sample_function_spec):
        """Test successful code validation."""
        valid_code = '''def test_function(x: int, y: str = "default") -> str:
    """Test function implementation."""
    return f"{y}: {x}"'''
        
        # Should not raise exception
        code_generator._validate_generated_code(valid_code, sample_function_spec)
    
    def test_validate_generated_code_syntax_error(self, code_generator, sample_function_spec):
        """Test code validation with syntax error."""
        invalid_code = '''def test_function(x: int, y: str = "default") -> str:
    """Test function implementation."""
    return f"{y}: {x"'''  # Missing closing brace
        
        with pytest.raises(CodeValidationError, match="Generated code has syntax errors"):
            code_generator._validate_generated_code(invalid_code, sample_function_spec)
    
    def test_validate_generated_code_wrong_function_name(self, code_generator, sample_function_spec):
        """Test code validation with wrong function name."""
        wrong_name_code = '''def wrong_function(x: int, y: str = "default") -> str:
    """Test function implementation."""
    return f"{y}: {x}"'''
        
        with pytest.raises(CodeValidationError, match="Function name 'test_function' not found"):
            code_generator._validate_generated_code(wrong_name_code, sample_function_spec)
    
    def test_validate_generated_code_missing_docstring(self, code_generator, sample_function_spec):
        """Test code validation with missing docstring."""
        no_docstring_code = '''def test_function(x: int, y: str = "default") -> str:
    return f"{y}: {x}"'''
        
        with pytest.raises(CodeValidationError, match="Generated code missing docstring"):
            code_generator._validate_generated_code(no_docstring_code, sample_function_spec)
    
    def test_validate_generated_code_missing_return(self, code_generator, sample_function_spec):
        """Test code validation with missing return statement."""
        no_return_code = '''def test_function(x: int, y: str = "default") -> str:
    """Test function implementation."""
    print(f"{y}: {x}")'''
        
        with pytest.raises(CodeValidationError, match="Function with non-None return type missing return statement"):
            code_generator._validate_generated_code(no_return_code, sample_function_spec)
    
    def test_validate_generated_code_none_return_type(self, code_generator):
        """Test code validation with None return type (no return required)."""
        spec = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="None"
        )
        
        no_return_code = '''def test_function() -> None:
    """Test function implementation."""
    print("Hello")'''
        
        # Should not raise exception for None return type
        code_generator._validate_generated_code(no_return_code, spec)
    
    def test_order_functions_by_dependencies(self, code_generator, sample_specification_set):
        """Test function ordering by dependencies."""
        ordered = code_generator._order_functions_by_dependencies(sample_specification_set.functions)
        
        # Should be ordered by module name, then function name
        assert len(ordered) == 2
        assert ordered[0].name == "another_function"  # Alphabetically first
        assert ordered[1].name == "test_function"
    
    def test_save_implementation_progress_no_state_manager(self):
        """Test progress saving without state manager."""
        generator = CodeGenerator(Mock(), None)
        generator.initialize()
        
        # Should not raise exception
        generator._save_implementation_progress("test.func", 1, 2, 0)
    
    def test_save_implementation_progress_with_state_manager(self, code_generator):
        """Test progress saving with state manager."""
        code_generator._save_implementation_progress("test.func", 1, 2, 0)
        
        # Verify state manager was called (check that it was called, not exact args due to timestamp)
        code_generator.state_manager.save_progress.assert_called_once()
        call_args = code_generator.state_manager.save_progress.call_args
        
        assert call_args[0][0] == ProjectPhase.IMPLEMENTATION
        progress_data = call_args[0][1]
        assert progress_data['current_function'] == 'test.func'
        assert progress_data['total_functions'] == 2
        assert progress_data['implemented_functions'] == 1
        assert progress_data['progress_percentage'] == 50.0
    
    def test_save_final_implementation_result(self, code_generator, sample_specification_set):
        """Test saving final implementation results."""
        result = ImplementationResult(
            implemented_functions=["test.func1"],
            failed_functions=["test.func2"],
            success_rate=0.5,
            completed_at=datetime.now()
        )
        
        code_generator._save_final_implementation_result(result, sample_specification_set)
        
        # Verify state manager was called (check that it was called, not exact args due to additional fields)
        code_generator.state_manager.save_progress.assert_called_once()
        call_args = code_generator.state_manager.save_progress.call_args
        
        assert call_args[0][0] == ProjectPhase.IMPLEMENTATION
        implementation_data = call_args[0][1]
        assert implementation_data['implemented_functions'] == result.implemented_functions
        assert implementation_data['failed_functions'] == result.failed_functions
        assert implementation_data['success_rate'] == result.success_rate
        assert implementation_data['total_functions'] == 2
    
    def test_load_failed_function_specs_no_state_manager(self):
        """Test loading failed function specs without state manager."""
        generator = CodeGenerator(Mock(), None)
        generator.initialize()
        
        result = generator._load_failed_function_specs(["test.func"])
        assert result == []
    
    def test_load_failed_function_specs_no_progress(self, code_generator):
        """Test loading failed function specs with no progress."""
        code_generator.state_manager.get_current_progress.return_value = None
        
        result = code_generator._load_failed_function_specs(["test.func"])
        assert result == []


class TestCodeGeneratorRetryAndErrorHandling:
    """Test cases for enhanced retry and error handling functionality."""
    
    @pytest.fixture
    def enhanced_code_generator(self):
        """Create a CodeGenerator with enhanced retry capabilities."""
        ai_client = Mock(spec=AIClientInterface)
        ai_client.validate_api_key.return_value = True
        state_manager = Mock(spec=StateManagerInterface)
        
        generator = CodeGenerator(ai_client, state_manager)
        generator.initialize()
        generator.retry_delay = 0.1  # Speed up tests
        return generator
    
    def test_implement_function_with_retry_success_on_second_attempt(self, enhanced_code_generator):
        """Test function implementation succeeding on retry."""
        # Mock AI to fail first, succeed second
        call_count = 0
        def mock_generate(prompt, max_retries=2):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary AI failure")
            else:
                return 'def test_func() -> str:\n    """Test function."""\n    return "success"'
        
        enhanced_code_generator.ai_client.generate_with_retry.side_effect = mock_generate
        
        spec = FunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="str"
        )
        
        # Should succeed on retry
        code = enhanced_code_generator.implement_function(spec)
        
        assert code is not None
        assert "def test_func(" in code
        assert spec.implementation_status == ImplementationStatus.COMPLETED
        assert "test_module.test_func" not in enhanced_code_generator.failed_functions
    
    def test_implement_function_exhausts_retries(self, enhanced_code_generator):
        """Test function implementation failing after all retries."""
        # Mock AI to always fail
        enhanced_code_generator.ai_client.generate_with_retry.side_effect = Exception("Persistent AI failure")
        
        spec = FunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="str"
        )
        
        with pytest.raises(CodeGenerationError):
            enhanced_code_generator.implement_function(spec)
        
        # Verify failure tracking
        assert spec.implementation_status == ImplementationStatus.FAILED
        assert "test_module.test_func" in enhanced_code_generator.failed_functions
        assert "test_module.test_func" in enhanced_code_generator.failure_details
        assert enhanced_code_generator.failure_details["test_module.test_func"]["retry_count"] == 3
    
    def test_retry_failed_implementations_selective(self, enhanced_code_generator):
        """Test selective retry of specific failed functions."""
        # Set up some failed functions
        enhanced_code_generator.failed_functions = ["module1.func1", "module2.func2", "module3.func3"]
        enhanced_code_generator.failure_details = {
            "module1.func1": {"error": "Error 1", "retry_count": 1},
            "module2.func2": {"error": "Error 2", "retry_count": 2},
            "module3.func3": {"error": "Error 3", "retry_count": 3}
        }
        
        # Mock successful retry for selected functions
        enhanced_code_generator.ai_client.generate_with_retry.return_value = '''
def func1() -> str:
    """Function 1."""
    return "success"
'''
        
        # Mock the spec loading to return a minimal spec
        def mock_create_minimal_specs(failed_funcs):
            return [FunctionSpec(
                name="func1",
                module="module1",
                docstring="Function 1",
                arguments=[],
                return_type="str"
            )]
        
        enhanced_code_generator._create_minimal_specs_for_retry = mock_create_minimal_specs
        
        # Retry only specific functions
        result = enhanced_code_generator.retry_failed_implementations(["module1.func1"])
        
        assert len(result.implemented_functions) == 1
        assert "module1.func1" in result.implemented_functions
        assert result.success_rate == 1.0
    
    def test_get_failure_report(self, enhanced_code_generator):
        """Test comprehensive failure report generation."""
        # Set up failure data
        enhanced_code_generator.failed_functions = ["module1.func1", "module2.func2"]
        enhanced_code_generator.failure_details = {
            "module1.func1": {
                "error": "Syntax error",
                "error_type": "CodeValidationError",
                "retry_count": 2,
                "timestamp": "2023-01-01T12:00:00"
            }
        }
        enhanced_code_generator.generated_code = {"module3.func3": "def func3(): pass"}
        
        report = enhanced_code_generator.get_failure_report()
        
        assert report["failed_functions_count"] == 2
        assert "module1.func1" in report["failed_functions"]
        assert "module2.func2" in report["failed_functions"]
        assert report["total_generated"] == 1
        assert report["success_rate"] == 1/3  # 1 success out of 3 total
        assert "report_timestamp" in report
    
    def test_get_retry_candidates(self, enhanced_code_generator):
        """Test identification of good retry candidates."""
        enhanced_code_generator.failed_functions = ["func1", "func2", "func3", "func4"]
        enhanced_code_generator.failure_details = {
            "func1": {"retry_count": 1, "error_type": "APIError"},  # Good candidate
            "func2": {"retry_count": 3, "error_type": "APIError"},  # Too many retries
            "func3": {"retry_count": 1, "error_type": "CodeValidationError"},  # Bad error type
            # func4 has no details, so it's a good candidate
        }
        
        candidates = enhanced_code_generator.get_retry_candidates()
        
        assert "func1" in candidates
        assert "func2" not in candidates  # Too many retries
        assert "func3" not in candidates  # Bad error type
        assert "func4" in candidates  # No details, good candidate
    
    def test_clear_failure_tracking(self, enhanced_code_generator):
        """Test clearing of failure tracking data."""
        # Set up failure data
        enhanced_code_generator.failed_functions = ["func1", "func2"]
        enhanced_code_generator.failure_details = {"func1": {"error": "test"}}
        enhanced_code_generator.retry_attempts = {"func1": 2}
        
        enhanced_code_generator.clear_failure_tracking()
        
        assert len(enhanced_code_generator.failed_functions) == 0
        assert len(enhanced_code_generator.failure_details) == 0
        assert len(enhanced_code_generator.retry_attempts) == 0
    
    def test_enhanced_prompt_with_retry_context(self, enhanced_code_generator):
        """Test that retry prompts include context from previous failures."""
        spec = FunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="str"
        )
        
        # Set up previous failure
        enhanced_code_generator.failure_details["test_module.test_func"] = {
            "error": "Missing return statement"
        }
        
        prompt = enhanced_code_generator._create_code_generation_prompt(spec, retry_count=1)
        
        assert "RETRY ATTEMPT #2" in prompt
        assert "Missing return statement" in prompt
        assert "addresses the previous failure" in prompt


class TestCodeGeneratorIntegration:
    """Integration tests for CodeGenerator."""
    
    def test_full_implementation_workflow(self):
        """Test complete implementation workflow."""
        # Create real-like mocks
        ai_client = Mock(spec=AIClientInterface)
        ai_client.validate_api_key.return_value = True
        ai_client.generate_with_retry.return_value = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b
'''
        
        state_manager = Mock(spec=StateManagerInterface)
        
        # Create function spec
        func_spec = FunctionSpec(
            name="calculate_sum",
            module="math_utils",
            docstring="Calculate the sum of two integers.",
            arguments=[
                Argument(name="a", type_hint="int", description="First integer"),
                Argument(name="b", type_hint="int", description="Second integer")
            ],
            return_type="int",
            implementation_status=ImplementationStatus.NOT_STARTED
        )
        
        spec_set = SpecificationSet(
            functions=[func_spec],
            modules=[],
            generated_at=datetime.now()
        )
        
        # Test workflow
        generator = CodeGenerator(ai_client, state_manager)
        generator.initialize()
        
        result = generator.implement_all(spec_set)
        
        # Verify results
        assert result.success_rate == 1.0
        assert len(result.implemented_functions) == 1
        assert "math_utils.calculate_sum" in result.implemented_functions
        assert len(result.failed_functions) == 0
        
        # Verify function was marked as completed
        assert func_spec.implementation_status == ImplementationStatus.COMPLETED
        
        # Verify code was cached
        assert "math_utils.calculate_sum" in generator.generated_code
        assert "def calculate_sum(" in generator.generated_code["math_utils.calculate_sum"]
    
    def test_full_workflow_with_failures_and_retries(self):
        """Test complete workflow including failures and retry operations."""
        ai_client = Mock(spec=AIClientInterface)
        ai_client.validate_api_key.return_value = True
        state_manager = Mock(spec=StateManagerInterface)
        
        # Mock AI to fail on first function, succeed on second
        call_count = 0
        def mock_generate(prompt, max_retries=2):
            nonlocal call_count
            call_count += 1
            if "func1" in prompt:
                raise Exception("AI failure for func1")
            else:
                return 'def func2() -> str:\n    """Function 2."""\n    return "success"'
        
        ai_client.generate_with_retry.side_effect = mock_generate
        
        # Create specs
        func1_spec = FunctionSpec(
            name="func1",
            module="test_module",
            docstring="Function 1",
            arguments=[],
            return_type="str"
        )
        
        func2_spec = FunctionSpec(
            name="func2",
            module="test_module",
            docstring="Function 2",
            arguments=[],
            return_type="str"
        )
        
        spec_set = SpecificationSet(
            functions=[func1_spec, func2_spec],
            modules=[],
            generated_at=datetime.now()
        )
        
        # Test initial implementation
        generator = CodeGenerator(ai_client, state_manager)
        generator.initialize()
        generator.retry_delay = 0.01  # Speed up test
        
        result = generator.implement_all(spec_set)
        
        # Verify partial success
        assert result.success_rate == 0.5
        assert len(result.implemented_functions) == 1
        assert len(result.failed_functions) == 1
        assert "test_module.func2" in result.implemented_functions
        assert "test_module.func1" in result.failed_functions
        
        # Test retry of failed function
        ai_client.generate_with_retry.side_effect = None
        ai_client.generate_with_retry.return_value = 'def func1() -> str:\n    """Function 1."""\n    return "retry success"'
        
        # Mock minimal spec creation for retry
        def mock_create_minimal_specs(failed_funcs):
            return [FunctionSpec(
                name="func1",
                module="test_module",
                docstring="Function 1",
                arguments=[],
                return_type="str"
            )]
        
        generator._create_minimal_specs_for_retry = mock_create_minimal_specs
        
        retry_result = generator.retry_failed_implementations()
        
        # Verify retry success
        assert retry_result.success_rate == 1.0
        assert len(retry_result.implemented_functions) == 1
        assert "test_module.func1" in retry_result.implemented_functions
        
        # Verify overall state
        assert len(generator.generated_code) == 2
        assert "test_module.func1" not in generator.failed_functions  # Should be removed after successful retry