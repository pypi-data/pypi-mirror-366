"""
Tests for ValidationResult class consolidation and backward compatibility.

This module tests the unified ValidationResult class to ensure:
1. Backward compatibility with the 'issues' property
2. Field consistency across all usage patterns
3. Migration scenarios and error handling
4. Proper initialization with different parameter combinations
"""

import pytest
from typing import List

from a3.core.models import ValidationResult


class TestValidationResultConsolidation:
    """Test suite for ValidationResult class consolidation."""
    
    def test_default_initialization(self):
        """Test ValidationResult with default parameters."""
        result = ValidationResult()
        
        assert result.is_valid is False
        assert result.errors == []
        assert result.warnings == []
        assert result.fixed_imports == []
        assert result.issues == []  # Backward compatibility
    
    def test_initialization_with_errors(self):
        """Test ValidationResult initialization with errors parameter."""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(is_valid=True, errors=errors)
        
        assert result.is_valid is True
        assert result.errors == errors
        assert result.issues == errors  # Backward compatibility
        assert result.warnings == []
        assert result.fixed_imports == []
    
    def test_initialization_with_issues_backward_compatibility(self):
        """Test ValidationResult initialization with deprecated 'issues' parameter."""
        issues = ["Issue 1", "Issue 2"]
        result = ValidationResult(is_valid=False, issues=issues)
        
        assert result.is_valid is False
        assert result.errors == issues  # Issues mapped to errors
        assert result.issues == issues  # Backward compatibility
        assert result.warnings == []
        assert result.fixed_imports == []
    
    def test_initialization_with_all_parameters(self):
        """Test ValidationResult initialization with all parameters."""
        errors = ["Error 1"]
        warnings = ["Warning 1"]
        fixed_imports = ["import os"]
        
        result = ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            fixed_imports=fixed_imports
        )
        
        assert result.is_valid is True
        assert result.errors == errors
        assert result.issues == errors  # Backward compatibility
        assert result.warnings == warnings
        assert result.fixed_imports == fixed_imports
    
    def test_issues_errors_conflict_raises_error(self):
        """Test that providing both 'issues' and 'errors' raises ValueError."""
        with pytest.raises(ValueError, match="Cannot specify both 'issues' and 'errors' parameters"):
            ValidationResult(errors=["Error"], issues=["Issue"])
    
    def test_issues_property_getter(self):
        """Test that issues property returns errors list."""
        errors = ["Error 1", "Error 2", "Error 3"]
        result = ValidationResult(errors=errors)
        
        assert result.issues == errors
        assert result.issues is result.errors  # Same object reference
    
    def test_issues_property_setter(self):
        """Test that issues property setter updates errors list."""
        result = ValidationResult()
        new_issues = ["New Issue 1", "New Issue 2"]
        
        result.issues = new_issues
        
        assert result.errors == new_issues
        assert result.issues == new_issues
    
    def test_issues_property_modification(self):
        """Test that modifying issues list affects errors list."""
        result = ValidationResult(errors=["Initial Error"])
        
        # Modify through issues property
        result.issues.append("Added through issues")
        
        assert "Added through issues" in result.errors
        assert "Added through issues" in result.issues
    
    def test_errors_property_modification(self):
        """Test that modifying errors list affects issues property."""
        result = ValidationResult(errors=["Initial Error"])
        
        # Modify through errors property
        result.errors.append("Added through errors")
        
        assert "Added through errors" in result.errors
        assert "Added through errors" in result.issues
    
    def test_field_consistency_across_usage_patterns(self):
        """Test field consistency across different usage patterns."""
        # Pattern 1: Direct errors assignment
        result1 = ValidationResult(errors=["Error 1"])
        
        # Pattern 2: Issues assignment (backward compatibility)
        result2 = ValidationResult(issues=["Error 1"])
        
        # Pattern 3: Property setter
        result3 = ValidationResult()
        result3.issues = ["Error 1"]
        
        # Pattern 4: Property modification
        result4 = ValidationResult()
        result4.errors = ["Error 1"]
        
        # All should have consistent state
        for result in [result1, result2, result3, result4]:
            assert result.errors == ["Error 1"]
            assert result.issues == ["Error 1"]
            assert result.errors is result.issues
    
    def test_none_parameters_handling(self):
        """Test handling of None parameters."""
        result = ValidationResult(
            errors=None,
            warnings=None,
            fixed_imports=None
        )
        
        assert result.errors == []
        assert result.warnings == []
        assert result.fixed_imports == []
        assert result.issues == []
    
    def test_empty_list_parameters(self):
        """Test handling of empty list parameters."""
        result = ValidationResult(
            errors=[],
            warnings=[],
            fixed_imports=[]
        )
        
        assert result.errors == []
        assert result.warnings == []
        assert result.fixed_imports == []
        assert result.issues == []
    
    def test_migration_scenario_issues_to_errors(self):
        """Test migration scenario from issues-based to errors-based code."""
        # Simulate old code using 'issues'
        def old_validation_function():
            return ValidationResult(is_valid=False, issues=["Old style issue"])
        
        # Simulate new code expecting 'errors'
        def new_validation_consumer(validation_result):
            return len(validation_result.errors) > 0
        
        # Test that old and new code work together
        result = old_validation_function()
        has_errors = new_validation_consumer(result)
        
        assert has_errors is True
        assert result.errors == ["Old style issue"]
        assert result.issues == ["Old style issue"]
    
    def test_migration_scenario_mixed_usage(self):
        """Test migration scenario with mixed usage patterns."""
        result = ValidationResult(issues=["Initial issue"])
        
        # Simulate code that adds errors through different properties
        result.errors.append("Added via errors")
        result.issues.append("Added via issues")
        
        expected_errors = ["Initial issue", "Added via errors", "Added via issues"]
        assert result.errors == expected_errors
        assert result.issues == expected_errors
    
    def test_error_handling_invalid_types(self):
        """Test error handling for invalid parameter types."""
        # These should not raise errors during initialization
        # but the properties should handle type conversion gracefully
        result = ValidationResult()
        
        # Test setting invalid types (should be handled by user code)
        with pytest.raises(AttributeError):
            result.errors = "not a list"  # This will fail when trying to append
    
    def test_backward_compatibility_with_existing_tests(self):
        """Test backward compatibility with existing test patterns."""
        # Pattern from existing tests: result.issues access
        result = ValidationResult(is_valid=True, errors=[])
        assert len(result.issues) == 0
        
        result = ValidationResult(is_valid=False, errors=["Error"])
        assert len(result.issues) == 1
        
        # Pattern: result.issues modification
        result = ValidationResult()
        result.issues.append("New issue")
        assert "New issue" in result.errors
    
    def test_validation_result_as_boolean(self):
        """Test ValidationResult boolean evaluation patterns."""
        # Valid result
        valid_result = ValidationResult(is_valid=True)
        assert valid_result.is_valid is True
        
        # Invalid result
        invalid_result = ValidationResult(is_valid=False, errors=["Error"])
        assert invalid_result.is_valid is False
        assert len(invalid_result.issues) > 0
    
    def test_validation_result_serialization_compatibility(self):
        """Test that ValidationResult maintains serialization compatibility."""
        result = ValidationResult(
            is_valid=True,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            fixed_imports=["import os", "import sys"]
        )
        
        # Test that all expected attributes exist
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'fixed_imports')
        assert hasattr(result, 'issues')  # Backward compatibility
        
        # Test attribute access
        attrs = {
            'is_valid': result.is_valid,
            'errors': result.errors,
            'warnings': result.warnings,
            'fixed_imports': result.fixed_imports,
            'issues': result.issues
        }
        
        assert attrs['is_valid'] is True
        assert attrs['errors'] == ["Error 1", "Error 2"]
        assert attrs['warnings'] == ["Warning 1"]
        assert attrs['fixed_imports'] == ["import os", "import sys"]
        assert attrs['issues'] == ["Error 1", "Error 2"]
    
    def test_validation_result_equality_and_comparison(self):
        """Test ValidationResult equality and comparison operations."""
        result1 = ValidationResult(is_valid=True, errors=["Error"])
        result2 = ValidationResult(is_valid=True, errors=["Error"])
        
        # Note: ValidationResult doesn't implement __eq__, so this tests object identity
        assert result1 is not result2
        
        # But the contents should be the same
        assert result1.is_valid == result2.is_valid
        assert result1.errors == result2.errors
        assert result1.issues == result2.issues
    
    def test_validation_result_with_complex_error_messages(self):
        """Test ValidationResult with complex error messages."""
        complex_errors = [
            "Circular dependency detected: module_a -> module_b -> module_a",
            "Function 'calculate_total' has undefined parameter 'tax_rate'",
            "Import error: cannot import 'missing_module' from 'nonexistent.package'"
        ]
        
        result = ValidationResult(is_valid=False, errors=complex_errors)
        
        assert result.errors == complex_errors
        assert result.issues == complex_errors
        assert len(result.errors) == 3
        assert len(result.issues) == 3
        
        # Test that complex messages are preserved
        assert "Circular dependency detected" in result.errors[0]
        assert "Circular dependency detected" in result.issues[0]


class TestValidationResultIntegration:
    """Integration tests for ValidationResult with other components."""
    
    def test_validation_result_with_project_manager_pattern(self):
        """Test ValidationResult usage pattern from project manager tests."""
        # Simulate project manager validation
        def validate_project_state():
            return ValidationResult(is_valid=True, errors=[])
        
        result = validate_project_state()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.issues) == 0  # Backward compatibility check
    
    def test_validation_result_with_planning_engine_pattern(self):
        """Test ValidationResult usage pattern from planning engine tests."""
        # Simulate planning engine dependency analysis
        def analyze_dependencies():
            return ValidationResult(
                is_valid=False,
                errors=["Circular dependency detected: module_a -> module_b -> module_a"],
                warnings=["Module 'utils' has no dependencies"]
            )
        
        result = analyze_dependencies()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.issues) == 1  # Backward compatibility
        assert "Circular dependency detected" in result.issues[0]
        assert len(result.warnings) == 1
    
    def test_validation_result_with_import_detector_pattern(self):
        """Test ValidationResult usage pattern from import issue detector tests."""
        # Simulate import issue detector validation
        def validate_import_resolution():
            return ValidationResult(
                is_valid=True,
                errors=[],
                fixed_imports=["from .utils import helper", "import os"]
            )
        
        result = validate_import_resolution()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.fixed_imports) > 0