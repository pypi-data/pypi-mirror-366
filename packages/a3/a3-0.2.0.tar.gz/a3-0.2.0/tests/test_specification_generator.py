"""
Unit tests for the SpecificationGenerator class.

Tests specification generation, validation, and storage functionality.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from a3.engines.specification import (
    SpecificationGenerator, SpecificationGeneratorError,
    SpecificationGenerationError, SpecificationValidationError
)
from a3.core.models import (
    FunctionSpec, Argument, SpecificationSet, ValidationResult,
    Module, ProjectPhase, ImplementationStatus
)
from a3.core.interfaces import AIClientInterface, StateManagerInterface


class TestSpecificationGenerator:
    """Test cases for SpecificationGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_client = Mock(spec=AIClientInterface)
        self.mock_state_manager = Mock(spec=StateManagerInterface)
        
        # Configure mock AI client
        self.mock_ai_client.validate_api_key.return_value = True
        self.mock_ai_client.generate_with_retry.return_value = '''
        {
            "docstring": "Calculate the sum of two integers.\\n\\nArgs:\\n    a: First integer to add\\n    b: Second integer to add\\n\\nReturns:\\n    int: The sum of a and b\\n\\nRaises:\\n    TypeError: If inputs are not integers",
            "arguments": [
                {
                    "name": "a",
                    "type_hint": "int",
                    "description": "First integer to add",
                    "default_value": null
                },
                {
                    "name": "b", 
                    "type_hint": "int",
                    "description": "Second integer to add",
                    "default_value": null
                }
            ],
            "return_type": "int",
            "required_imports": [],
            "raises": ["TypeError"]
        }
        '''
        
        self.spec_generator = SpecificationGenerator(
            ai_client=self.mock_ai_client,
            state_manager=self.mock_state_manager
        )
        self.spec_generator.initialize()
    
    def create_test_function(self, name="test_func", module="test_module"):
        """Create a test function specification."""
        return FunctionSpec(
            name=name,
            module=module,
            docstring="Test function",
            arguments=[
                Argument(name="param1", type_hint="str", description="Test parameter")
            ],
            return_type="str",
            implementation_status=ImplementationStatus.NOT_STARTED
        )
    
    def test_initialization(self):
        """Test SpecificationGenerator initialization."""
        spec_gen = SpecificationGenerator()
        
        # Should initialize without error
        spec_gen.initialize()
        
        # Should validate prerequisites
        result = spec_gen.validate_prerequisites()
        assert not result.is_valid
        assert "AI client is required but not provided" in result.issues
    
    def test_initialization_with_dependencies(self):
        """Test initialization with proper dependencies."""
        result = self.spec_generator.validate_prerequisites()
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_generate_specifications_empty_list(self):
        """Test generate_specifications with empty function list."""
        with pytest.raises(SpecificationGenerationError, match="Function list cannot be empty"):
            self.spec_generator.generate_specifications([])
    
    def test_generate_specifications_success(self):
        """Test successful specification generation."""
        test_functions = [
            self.create_test_function("func1", "module1"),
            self.create_test_function("func2", "module1"),
            self.create_test_function("func3", "module2")
        ]
        
        result = self.spec_generator.generate_specifications(test_functions)
        
        assert isinstance(result, SpecificationSet)
        assert len(result.functions) == 3
        assert len(result.modules) == 2
        assert isinstance(result.generated_at, datetime)
        
        # Verify AI client was called for each function
        assert self.mock_ai_client.generate_with_retry.call_count == 3
        
        # Verify state manager was called to save
        self.mock_state_manager.save_progress.assert_called_once()
        call_args = self.mock_state_manager.save_progress.call_args
        assert call_args[0][0] == ProjectPhase.SPECIFICATION
    
    def test_generate_specifications_ai_failure(self):
        """Test specification generation with AI failure."""
        self.mock_ai_client.generate_with_retry.side_effect = Exception("AI service error")
        
        test_functions = [self.create_test_function()]
        
        # Should still return result but with original function
        result = self.spec_generator.generate_specifications(test_functions)
        
        assert isinstance(result, SpecificationSet)
        assert len(result.functions) == 1
        # Function should be unchanged due to AI failure
        assert result.functions[0].docstring == "Test function"
    
    def test_validate_specifications_valid(self):
        """Test validation of valid specifications."""
        functions = [
            FunctionSpec(
                name="func1",
                module="module1", 
                docstring="Test function 1",
                arguments=[Argument(name="param", type_hint="str")],
                return_type="str"
            )
        ]
        
        modules = [
            Module(
                name="module1",
                description="Test module",
                file_path="module1.py",
                functions=functions
            )
        ]
        
        spec_set = SpecificationSet(functions=functions, modules=modules)
        
        result = self.spec_generator.validate_specifications(spec_set)
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_validate_specifications_duplicate_function(self):
        """Test validation with duplicate function names."""
        functions = [
            FunctionSpec(name="func1", module="module1", docstring="Test 1", return_type="str"),
            FunctionSpec(name="func1", module="module1", docstring="Test 2", return_type="str")
        ]
        
        modules = [
            Module(
                name="module1",
                description="Test module", 
                file_path="module1.py",
                functions=functions
            )
        ]
        
        spec_set = SpecificationSet(functions=functions, modules=modules)
        
        result = self.spec_generator.validate_specifications(spec_set)
        
        assert not result.is_valid
        assert any("Duplicate function name" in issue for issue in result.issues)
    
    def test_validate_specifications_module_mismatch(self):
        """Test validation with module/function mismatch."""
        functions = [
            FunctionSpec(name="func1", module="module1", docstring="Test", return_type="str")
        ]
        
        modules = [
            Module(
                name="module1",
                description="Test module",
                file_path="module1.py", 
                functions=[
                    FunctionSpec(name="func2", module="module1", docstring="Different", return_type="str")
                ]
            )
        ]
        
        spec_set = SpecificationSet(functions=functions, modules=modules)
        
        result = self.spec_generator.validate_specifications(spec_set)
        
        assert not result.is_valid
        assert any("missing functions" in issue or "extra functions" in issue for issue in result.issues)
    
    def test_validate_specifications_invalid_function(self):
        """Test validation with invalid function specification."""
        functions = [
            FunctionSpec(name="", module="module1", docstring="", return_type="")  # Invalid
        ]
        
        modules = [
            Module(name="module1", description="Test", file_path="module1.py", functions=functions)
        ]
        
        spec_set = SpecificationSet(functions=functions, modules=modules)
        
        result = self.spec_generator.validate_specifications(spec_set)
        
        assert not result.is_valid
        assert len(result.issues) > 0
    
    def test_group_functions_by_module(self):
        """Test grouping functions by module."""
        functions = [
            self.create_test_function("func1", "module1"),
            self.create_test_function("func2", "module1"), 
            self.create_test_function("func3", "module2")
        ]
        
        grouped = self.spec_generator._group_functions_by_module(functions)
        
        assert len(grouped) == 2
        assert len(grouped["module1"]) == 2
        assert len(grouped["module2"]) == 1
        assert grouped["module1"][0].name == "func1"
        assert grouped["module1"][1].name == "func2"
        assert grouped["module2"][0].name == "func3"
    
    def test_create_module_context(self):
        """Test creation of module context for specification generation."""
        functions_by_module = {
            "module1": [self.create_test_function("func1", "module1")],
            "module2": [self.create_test_function("func2", "module2")]
        }
        
        context = self.spec_generator._create_module_context("module1", functions_by_module)
        
        assert context["current_module"] == "module1"
        assert "module1" in context["available_modules"]
        assert "module2" in context["available_modules"]
        assert "module2" in context["module_functions"]
        assert "module1" not in context["module_functions"]  # Excludes current module
    
    def test_create_basic_signature(self):
        """Test creation of basic function signature."""
        func = FunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test",
            arguments=[
                Argument(name="param1", type_hint="str"),
                Argument(name="param2", type_hint="int", default_value="10")
            ],
            return_type="bool"
        )
        
        signature = self.spec_generator._create_basic_signature(func)
        
        expected = "test_func(param1: str, param2: int = 10) -> bool"
        assert signature == expected
    
    def test_parse_specification_response_valid(self):
        """Test parsing valid AI response."""
        response = '''
        {
            "docstring": "Test docstring",
            "arguments": [{"name": "param", "type_hint": "str", "description": "Test param", "default_value": null}],
            "return_type": "str",
            "required_imports": ["typing"],
            "raises": ["ValueError"]
        }
        '''
        
        result = self.spec_generator._parse_specification_response(response)
        
        assert result["docstring"] == "Test docstring"
        assert len(result["arguments"]) == 1
        assert result["return_type"] == "str"
    
    def test_parse_specification_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        response = "This is not JSON"
        
        with pytest.raises(SpecificationGenerationError, match="Failed to parse specification response"):
            self.spec_generator._parse_specification_response(response)
    
    def test_parse_specification_response_missing_fields(self):
        """Test parsing response with missing required fields."""
        response = '{"docstring": "Test"}'  # Missing arguments and return_type
        
        with pytest.raises(SpecificationGenerationError, match="Missing required field"):
            self.spec_generator._parse_specification_response(response)
    
    def test_create_enhanced_function(self):
        """Test creation of enhanced function from AI data."""
        original_func = self.create_test_function()
        
        enhanced_data = {
            "docstring": "Enhanced docstring with details",
            "arguments": [
                {
                    "name": "param1",
                    "type_hint": "str",
                    "description": "Enhanced parameter description",
                    "default_value": None
                }
            ],
            "return_type": "str"
        }
        
        enhanced_func = self.spec_generator._create_enhanced_function(original_func, enhanced_data)
        
        assert enhanced_func.name == original_func.name
        assert enhanced_func.module == original_func.module
        assert enhanced_func.docstring == "Enhanced docstring with details"
        assert len(enhanced_func.arguments) == 1
        assert enhanced_func.arguments[0].description == "Enhanced parameter description"
    
    def test_create_enhanced_function_invalid_data(self):
        """Test creation of enhanced function with invalid data."""
        original_func = self.create_test_function()
        
        # Invalid enhanced data should return original function
        enhanced_data = {"invalid": "data"}
        
        enhanced_func = self.spec_generator._create_enhanced_function(original_func, enhanced_data)
        
        # Should return original function when enhancement fails
        assert enhanced_func == original_func
    
    def test_save_specifications(self):
        """Test saving specifications to state manager."""
        functions = [self.create_test_function()]
        modules = [Module(name="test_module", description="Test", file_path="test.py", functions=functions)]
        spec_set = SpecificationSet(functions=functions, modules=modules)
        
        self.spec_generator._save_specifications(spec_set)
        
        # Verify state manager was called
        self.mock_state_manager.save_progress.assert_called_once()
        call_args = self.mock_state_manager.save_progress.call_args
        assert call_args[0][0] == ProjectPhase.SPECIFICATION
        
        # Verify the saved data structure
        saved_data = call_args[0][1]
        assert "functions" in saved_data
        assert "generated_at" in saved_data
        assert len(saved_data["functions"]) == 1
    
    def test_save_specifications_no_state_manager(self):
        """Test saving specifications without state manager."""
        spec_gen = SpecificationGenerator(ai_client=self.mock_ai_client)
        spec_gen.initialize()
        
        functions = [self.create_test_function()]
        modules = [Module(name="test_module", description="Test", file_path="test.py", functions=functions)]
        spec_set = SpecificationSet(functions=functions, modules=modules)
        
        # Should not raise error even without state manager
        spec_gen._save_specifications(spec_set)
    
    def test_is_valid_type_hint(self):
        """Test type hint validation."""
        # Valid type hints
        assert self.spec_generator._is_valid_type_hint("str")
        assert self.spec_generator._is_valid_type_hint("List[str]")
        assert self.spec_generator._is_valid_type_hint("Dict[str, int]")
        assert self.spec_generator._is_valid_type_hint("Optional[str]")
        assert self.spec_generator._is_valid_type_hint("Union[str, int]")
        assert self.spec_generator._is_valid_type_hint("CustomClass")
        
        # Invalid type hints
        assert not self.spec_generator._is_valid_type_hint("")
        assert not self.spec_generator._is_valid_type_hint("   ")
    
    def test_specification_update_mechanism(self):
        """Test that specifications can be updated and re-validated."""
        # Create initial specifications
        functions = [self.create_test_function("func1", "module1")]
        
        result1 = self.spec_generator.generate_specifications(functions)
        assert len(result1.functions) == 1
        
        # Add more functions and regenerate
        functions.append(self.create_test_function("func2", "module1"))
        
        result2 = self.spec_generator.generate_specifications(functions)
        assert len(result2.functions) == 2
        
        # Validate both results
        validation1 = self.spec_generator.validate_specifications(result1)
        validation2 = self.spec_generator.validate_specifications(result2)
        
        assert validation1.is_valid
        assert validation2.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])