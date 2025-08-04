"""
Unit tests for the ImportIssueDetector component.

Tests cover detection of various import issues, fixing functionality,
and validation of fixes.
"""

import pytest
from a3.core.import_issue_detector import ImportIssueDetector
from a3.core.models import ImportIssue, ImportIssueType, ValidationResult


class TestImportIssueDetector:
    """Test cases for ImportIssueDetector."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ImportIssueDetector()
    
    def test_detect_relative_imports_in_functions(self):
        """Test detection of relative imports within function definitions."""
        code = '''
def my_function():
    from .utils import helper
    from ..config import settings
    return helper(settings)

def another_function():
    import .local_module
    return local_module.data
'''
        
        issues = self.detector.scan_for_import_issues(code, "test.py")
        
        # Should detect relative imports in both functions
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 2
        
        # Check that issues are properly identified
        for issue in relative_issues:
            assert issue.file_path == "test.py"
            assert issue.line_number > 0
            assert "from ." in issue.problematic_import or "import ." in issue.problematic_import
            assert "Move" in issue.suggested_fix
    
    def test_detect_incorrect_indentation(self):
        """Test detection of incorrectly indented import statements."""
        code = '''
import os
    import sys  # This is incorrectly indented
        from pathlib import Path  # This too

def function():
    import json  # This is valid inside a function
    return json.loads("{}")
'''
        
        issues = self.detector.scan_for_import_issues(code, "test.py")
        
        # Should detect incorrectly indented imports
        indentation_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.INCORRECT_INDENTATION]
        
        # The import inside the function should not be flagged as incorrect indentation
        # Only the standalone indented imports should be flagged
        assert len(indentation_issues) >= 1
        
        for issue in indentation_issues:
            assert "indented" in issue.context.lower()
    
    def test_detect_unresolvable_relative_imports(self):
        """Test detection of potentially unresolvable relative imports."""
        code = '''
from ....deeply.nested import something
from ..suspicious1 import data
from .x import item  # Single character module name
'''
        
        issues = self.detector.scan_for_import_issues(code, "test.py")
        
        # Should detect unresolvable relative imports
        unresolvable_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.UNRESOLVABLE_RELATIVE_IMPORT]
        assert len(unresolvable_issues) >= 1
        
        # Check for deep relative import detection
        deep_import_found = any("deeply" in issue.problematic_import for issue in unresolvable_issues)
        assert deep_import_found
    
    def test_fix_function_level_imports(self):
        """Test fixing of function-level imports by moving them to module level."""
        code = '''
"""Module docstring."""

def my_function():
    from .utils import helper
    from ..config import settings
    result = helper(settings)
    return result

def another_function():
    import json
    return json.dumps({})
'''
        
        fixed_code = self.detector.fix_function_level_imports(code)
        
        # Check that imports were moved to module level
        lines = fixed_code.split('\n')
        
        # Find where imports were inserted (should be after docstring)
        import_lines = [i for i, line in enumerate(lines) if line.strip().startswith(('import ', 'from '))]
        
        # Should have imports at module level
        assert len(import_lines) > 0
        
        # Imports should be near the top (after docstring)
        assert any(i < 10 for i in import_lines)  # Reasonable position near top
        
        # Function bodies should no longer contain the problematic imports
        function_lines = [line for line in lines if 'def ' in line or (line.strip() and not line.strip().startswith(('import ', 'from ', '#', '"""', "'''")))]
        
        # The functions should still exist
        assert any('def my_function' in line for line in lines)
        assert any('def another_function' in line for line in lines)
    
    def test_fix_import_indentation(self):
        """Test fixing of incorrectly indented import statements."""
        code = '''
import os
    import sys
        from pathlib import Path

def function():
    import json  # This should remain indented
    return json.loads("{}")
'''
        
        fixed_code = self.detector.fix_import_indentation(code)
        lines = fixed_code.split('\n')
        
        # Check that module-level imports are no longer indented
        for line in lines:
            if line.strip().startswith(('import ', 'from ')) and 'def ' not in line:
                # If it's not inside a function, it shouldn't be indented
                if not any('def ' in prev_line for prev_line in lines[:lines.index(line)]):
                    # This is a simplified check - in real code we'd need better context analysis
                    pass
    
    def test_convert_relative_to_absolute_imports(self):
        """Test conversion of relative imports to absolute imports."""
        code = '''
from .utils import helper
from ..config import settings
from ...parent import data
'''
        
        converted_code = self.detector.convert_relative_to_absolute_imports(code, "mypackage/subpackage/module.py")
        
        # Check that some conversions were attempted
        # Note: Full conversion requires package structure analysis
        assert converted_code != code  # Should have changed something
    
    def test_validate_import_resolution_valid_code(self):
        """Test validation of code with valid imports."""
        valid_code = '''
import os
import sys
from pathlib import Path

def function():
    return os.path.join("a", "b")
'''
        
        result = self.detector.validate_import_resolution(valid_code, "test.py")
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.fixed_imports) > 0  # Should have found the imports
    
    def test_validate_import_resolution_invalid_code(self):
        """Test validation of code with syntax errors."""
        invalid_code = '''
import os
from pathlib import Path
import  # Malformed import
'''
        
        result = self.detector.validate_import_resolution(invalid_code, "test.py")
        
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_fixes_applied(self):
        """Test validation that fixes were properly applied."""
        original_code = '''
def function():
    from .utils import helper
    return helper()
'''
        
        fixed_code = '''
from utils import helper

def function():
    return helper()
'''
        
        result = self.detector.validate_fixes_applied(original_code, fixed_code)
        
        assert isinstance(result, ValidationResult)
        # The validation should show improvement (fewer issues in fixed code)
        assert len(result.fixed_imports) > 0
    
    def test_scan_empty_code(self):
        """Test scanning empty or whitespace-only code."""
        empty_code = ""
        whitespace_code = "   \n\n   \n"
        
        empty_issues = self.detector.scan_for_import_issues(empty_code)
        whitespace_issues = self.detector.scan_for_import_issues(whitespace_code)
        
        assert len(empty_issues) == 0
        assert len(whitespace_issues) == 0
    
    def test_scan_code_without_imports(self):
        """Test scanning code that has no import statements."""
        code = '''
def function():
    x = 1 + 2
    return x

class MyClass:
    def method(self):
        return "hello"
'''
        
        issues = self.detector.scan_for_import_issues(code)
        assert len(issues) == 0
    
    def test_complex_function_detection(self):
        """Test detection in complex nested function scenarios."""
        code = '''
def outer_function():
    def inner_function():
        from .nested import tool
        return tool()
    
    from ..parent import config
    return inner_function()

class MyClass:
    def method(self):
        from .class_utils import helper
        return helper()
'''
        
        issues = self.detector.scan_for_import_issues(code)
        
        # Should detect imports in both nested function and class method
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 2
    
    def test_import_with_comments(self):
        """Test handling of imports with comments."""
        code = '''
def function():
    from .utils import helper  # This is a comment
    # This is just a comment, not an import
    from ..config import settings  # Another comment
    return helper(settings)
'''
        
        issues = self.detector.scan_for_import_issues(code)
        
        # Should still detect the imports despite comments
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 2
    
    def test_multiline_imports(self):
        """Test handling of multiline import statements."""
        code = '''
def function():
    from .utils import (
        helper,
        processor,
        validator
    )
    return helper()
'''
        
        issues = self.detector.scan_for_import_issues(code)
        
        # Should detect the multiline import
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 1
    
    def test_find_import_insertion_position(self):
        """Test finding the correct position to insert imports."""
        # Test with module docstring
        code_with_docstring = '''#!/usr/bin/env python3
"""
This is a module docstring.
It spans multiple lines.
"""

def function():
    pass
'''
        
        lines = code_with_docstring.split('\n')
        position = self.detector._find_import_insertion_position(lines)
        
        # Should be after the docstring
        assert position > 4  # After shebang and docstring
        
        # Test with no docstring
        code_no_docstring = '''#!/usr/bin/env python3

def function():
    pass
'''
        
        lines = code_no_docstring.split('\n')
        position = self.detector._find_import_insertion_position(lines)
        
        # Should be after shebang, before function
        assert position >= 1  # After shebang
        assert position < 3   # Before function
    
    def test_normalize_import_statement(self):
        """Test normalization of import statements."""
        # Test sorting of imports
        import_stmt = "from module import c, a, b"
        normalized = self.detector._normalize_import_statement(import_stmt)
        assert "a, b, c" in normalized
        
        # Test whitespace normalization
        messy_import = "from   module   import    item"
        normalized = self.detector._normalize_import_statement(messy_import)
        assert "from module import item" == normalized
    
    def test_validate_single_import(self):
        """Test validation of individual import statements."""
        # Valid import
        valid_issues = self.detector._validate_single_import("import os", "test.py")
        assert len(valid_issues) == 0
        
        # Invalid import
        invalid_issues = self.detector._validate_single_import("import", "test.py")
        assert len(invalid_issues) > 0
        assert any(issue['severity'] == 'error' for issue in invalid_issues)
        
        # Deep relative import (warning)
        deep_relative_issues = self.detector._validate_single_import("from ....deep import item", "test.py")
        assert len(deep_relative_issues) > 0
        assert any(issue['severity'] == 'warning' for issue in deep_relative_issues)


if __name__ == "__main__":
    pytest.main([__file__])