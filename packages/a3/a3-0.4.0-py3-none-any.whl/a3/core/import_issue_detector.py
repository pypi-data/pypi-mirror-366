"""
Import Issue Detector for the A3 project.

This module provides functionality to detect and fix import issues in Python code,
particularly focusing on relative imports within functions and indentation problems.
"""

import ast
import re
from typing import List, Optional, Tuple
from pathlib import Path

from .models import ImportIssue, ImportIssueType, ValidationResult


class ImportIssueDetector:
    """Detects and analyzes import issues in Python code."""
    
    def __init__(self):
        """Initialize the ImportIssueDetector."""
        pass
    
    def scan_for_import_issues(self, code_content: str, file_path: str = "") -> List[ImportIssue]:
        """
        Scan code content for various import issues.
        
        Args:
            code_content: The Python code to scan
            file_path: Path to the file being scanned (for context)
            
        Returns:
            List of ImportIssue objects found in the code
        """
        issues = []
        
        # Split code into lines for analysis
        lines = code_content.split('\n')
        
        # Scan for different types of import issues
        issues.extend(self._detect_relative_imports_in_functions(lines, file_path))
        issues.extend(self._detect_incorrect_indentation(lines, file_path))
        issues.extend(self._detect_unresolvable_relative_imports(lines, file_path))
        
        return issues
    
    def _detect_relative_imports_in_functions(self, lines: List[str], file_path: str) -> List[ImportIssue]:
        """
        Detect relative imports that are incorrectly placed within function definitions.
        
        Args:
            lines: List of code lines
            file_path: Path to the file being scanned
            
        Returns:
            List of ImportIssue objects for relative imports in functions
        """
        issues = []
        in_function = False
        function_indent_level = 0
        current_function = ""
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Check if we're entering a function definition
            if stripped_line.startswith('def ') and ':' in stripped_line:
                in_function = True
                function_indent_level = len(line) - len(line.lstrip())
                # Extract function name
                func_match = re.match(r'\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                current_function = func_match.group(1) if func_match else "unknown"
                continue
            
            # Check if we're exiting the function (dedent to function level or less)
            if in_function and line.strip() and len(line) - len(line.lstrip()) <= function_indent_level:
                # If this line is not more indented than the function definition, we're out
                if not stripped_line.startswith('def ') and not stripped_line.startswith('class '):
                    in_function = False
                    current_function = ""
            
            # Look for relative imports within functions
            if in_function and stripped_line:
                # Check for relative imports (starting with . or ..)
                relative_import_patterns = [
                    r'^\s*from\s+\.+\w*\s+import\s+',  # from .module import something
                    r'^\s*import\s+\.+\w*',            # import .module
                ]
                
                for pattern in relative_import_patterns:
                    if re.match(pattern, line):
                        # Extract the import statement
                        import_match = re.search(r'(from\s+\.+\w*\s+import\s+[^#\n]+|import\s+\.+\w*)', line)
                        problematic_import = import_match.group(1).strip() if import_match else stripped_line
                        
                        # Suggest moving to module level
                        suggested_fix = f"Move '{problematic_import}' to module level (top of file)"
                        
                        context = f"Found in function '{current_function}' at indentation level {len(line) - len(line.lstrip())}"
                        
                        issue = ImportIssue(
                            file_path=file_path,
                            line_number=line_num,
                            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
                            problematic_import=problematic_import,
                            suggested_fix=suggested_fix,
                            context=context
                        )
                        issues.append(issue)
        
        return issues
    
    def _detect_incorrect_indentation(self, lines: List[str], file_path: str) -> List[ImportIssue]:
        """
        Detect import statements with incorrect indentation patterns.
        
        Args:
            lines: List of code lines
            file_path: Path to the file being scanned
            
        Returns:
            List of ImportIssue objects for incorrectly indented imports
        """
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith('#'):
                continue
            
            # Check for import statements
            if stripped_line.startswith(('import ', 'from ')) and 'import' in stripped_line:
                # Get the indentation level
                indent_level = len(line) - len(line.lstrip())
                
                # Check if import is indented but not in a proper context
                if indent_level > 0:
                    # Look at surrounding context to determine if indentation is appropriate
                    context_lines = self._get_context_lines(lines, line_num - 1, 3)
                    
                    # Check if this is inside a function, class, or control structure
                    is_in_valid_context = self._is_import_in_valid_indented_context(context_lines, line_num - 1)
                    
                    if not is_in_valid_context:
                        # This import appears to be incorrectly indented
                        suggested_fix = f"Move import to module level: {stripped_line}"
                        
                        context = f"Import indented {indent_level} spaces without proper context"
                        
                        issue = ImportIssue(
                            file_path=file_path,
                            line_number=line_num,
                            issue_type=ImportIssueType.INCORRECT_INDENTATION,
                            problematic_import=stripped_line,
                            suggested_fix=suggested_fix,
                            context=context
                        )
                        issues.append(issue)
        
        return issues
    
    def _detect_unresolvable_relative_imports(self, lines: List[str], file_path: str) -> List[ImportIssue]:
        """
        Detect relative imports that may not be resolvable.
        
        Args:
            lines: List of code lines
            file_path: Path to the file being scanned
            
        Returns:
            List of ImportIssue objects for potentially unresolvable relative imports
        """
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Look for relative imports with multiple dots that might be problematic
            relative_import_match = re.match(r'^\s*from\s+(\.{2,})([a-zA-Z_][\w.]*)*\s+import\s+', line)
            if relative_import_match:
                dots = relative_import_match.group(1)
                module_part = relative_import_match.group(2) or ""
                dot_count = len(dots)
                
                # If there are many dots, it might be unresolvable
                if dot_count > 2:  # More than .. might be problematic
                    problematic_import = stripped_line
                    suggested_fix = f"Consider using absolute import or verify package structure"
                    context = f"Relative import with {dot_count} dots may be unresolvable"
                    
                    issue = ImportIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type=ImportIssueType.UNRESOLVABLE_RELATIVE_IMPORT,
                        problematic_import=problematic_import,
                        suggested_fix=suggested_fix,
                        context=context
                    )
                    issues.append(issue)
            
            # Also check for imports that reference non-existent relative modules
            # This is a basic check - more sophisticated analysis would require file system access
            single_dot_match = re.match(r'^\s*from\s+\.(\w+)\s+import\s+', line)
            if single_dot_match:
                module_name = single_dot_match.group(1)
                # Basic heuristic: if module name looks suspicious, flag it
                if len(module_name) == 1 or module_name.isdigit():
                    problematic_import = stripped_line
                    suggested_fix = f"Verify that module '{module_name}' exists"
                    context = f"Suspicious module name in relative import"
                    
                    issue = ImportIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type=ImportIssueType.UNRESOLVABLE_RELATIVE_IMPORT,
                        problematic_import=problematic_import,
                        suggested_fix=suggested_fix,
                        context=context
                    )
                    issues.append(issue)
        
        return issues
    
    def _get_context_lines(self, lines: List[str], center_index: int, radius: int) -> List[str]:
        """
        Get context lines around a specific line index.
        
        Args:
            lines: List of all lines
            center_index: Index of the center line (0-based)
            radius: Number of lines to include before and after
            
        Returns:
            List of context lines
        """
        start = max(0, center_index - radius)
        end = min(len(lines), center_index + radius + 1)
        return lines[start:end]
    
    def _is_import_in_valid_indented_context(self, context_lines: List[str], import_line_index: int) -> bool:
        """
        Check if an indented import is in a valid context (function, class, if block, etc.).
        
        Args:
            context_lines: Lines of context around the import
            import_line_index: Index of the import line within the context
            
        Returns:
            True if the import is in a valid indented context
        """
        # Look for function, class, or control structure definitions before the import
        for i in range(len(context_lines)):
            if i >= import_line_index:
                break
                
            line = context_lines[i].strip()
            
            # Check for function, class, if, try, with, for, while definitions
            if re.match(r'^(def|class|if|try|except|finally|with|for|while|elif|else)\s+.*:', line):
                return True
            
            # Check for conditional imports (common pattern)
            if re.match(r'^if\s+.*:', line):
                return True
        
        # Also check if we're inside a function or class by looking at indentation patterns
        # If there's a function/class definition with less indentation than the import, it's valid
        if context_lines and import_line_index < len(context_lines):
            import_line = context_lines[import_line_index]
            import_indent = len(import_line) - len(import_line.lstrip())
            
            for i in range(import_line_index):
                line = context_lines[i]
                if line.strip():
                    line_indent = len(line) - len(line.lstrip())
                    if line_indent < import_indent and re.match(r'^\s*(def|class)\s+.*:', line):
                        return True
        
        return False
    
    def fix_function_level_imports(self, code_content: str) -> str:
        """
        Fix import issues by moving function-level imports to module level and correcting indentation.
        
        Args:
            code_content: The Python code to fix
            
        Returns:
            Fixed code content
        """
        lines = code_content.split('\n')
        
        # First, collect all imports that need to be moved
        imports_to_move = []
        lines_to_remove = []
        
        # Scan for function-level imports
        issues = self.scan_for_import_issues(code_content)
        
        for issue in issues:
            if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION:
                # Extract the import statement
                line_index = issue.line_number - 1  # Convert to 0-based index
                if 0 <= line_index < len(lines):
                    import_line = lines[line_index]
                    cleaned_import = import_line.strip()
                    
                    # Convert relative to absolute if needed
                    fixed_import = self._convert_relative_to_absolute_if_needed(cleaned_import)
                    
                    imports_to_move.append(fixed_import)
                    lines_to_remove.append(line_index)
            
            elif issue.issue_type == ImportIssueType.INCORRECT_INDENTATION:
                # Fix indentation by moving to module level
                line_index = issue.line_number - 1
                if 0 <= line_index < len(lines):
                    import_line = lines[line_index]
                    cleaned_import = import_line.strip()
                    imports_to_move.append(cleaned_import)
                    lines_to_remove.append(line_index)
        
        # Remove duplicate imports and sort removal indices in reverse order
        imports_to_move = list(dict.fromkeys(imports_to_move))  # Remove duplicates while preserving order
        lines_to_remove = sorted(set(lines_to_remove), reverse=True)
        
        # Remove the problematic import lines
        for line_index in lines_to_remove:
            lines[line_index] = ""  # Mark for removal
        
        # Remove empty lines that were marked for removal
        lines = [line for line in lines if line != "" or line.strip() != ""]
        
        # Find the best position to insert imports (after docstrings, before other code)
        insert_position = self._find_import_insertion_position(lines)
        
        # Insert the moved imports at the appropriate position
        for import_stmt in reversed(imports_to_move):  # Reverse to maintain order
            lines.insert(insert_position, import_stmt)
        
        return '\n'.join(lines)
    
    def fix_import_indentation(self, code_content: str) -> str:
        """
        Fix incorrect indentation in import statements.
        
        Args:
            code_content: The Python code to fix
            
        Returns:
            Code with corrected import indentation
        """
        lines = code_content.split('\n')
        
        # Scan for indentation issues
        issues = self.scan_for_import_issues(code_content)
        
        for issue in issues:
            if issue.issue_type == ImportIssueType.INCORRECT_INDENTATION:
                line_index = issue.line_number - 1
                if 0 <= line_index < len(lines):
                    # Remove indentation from the import line
                    lines[line_index] = lines[line_index].strip()
        
        return '\n'.join(lines)
    
    def convert_relative_to_absolute_imports(self, code_content: str, module_path: str = "") -> str:
        """
        Convert relative imports to absolute imports when needed.
        
        Args:
            code_content: The Python code to process
            module_path: Path to the current module (for context)
            
        Returns:
            Code with relative imports converted to absolute where appropriate
        """
        lines = code_content.split('\n')
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Look for relative imports
            relative_match = re.match(r'^from\s+(\.+)(\w*)\s+import\s+(.+)', stripped_line)
            if relative_match:
                dots = relative_match.group(1)
                module_name = relative_match.group(2)
                imports = relative_match.group(3)
                
                # Convert to absolute import if possible
                absolute_import = self._convert_relative_to_absolute(dots, module_name, imports, module_path)
                if absolute_import:
                    # Preserve original indentation
                    indent = line[:len(line) - len(line.lstrip())]
                    lines[i] = indent + absolute_import
        
        return '\n'.join(lines)
    
    def _convert_relative_to_absolute_if_needed(self, import_statement: str) -> str:
        """
        Convert a relative import to absolute if it's problematic as relative.
        
        Args:
            import_statement: The import statement to potentially convert
            
        Returns:
            The import statement, possibly converted to absolute
        """
        # For now, keep relative imports as-is but clean them up
        # In a real implementation, this would use package structure analysis
        
        # Basic cleanup: ensure proper spacing
        import_statement = re.sub(r'\s+', ' ', import_statement.strip())
        
        # If it's a deeply nested relative import, suggest conversion
        if re.match(r'^from\s+\.{3,}', import_statement):
            # For very deep relative imports, suggest absolute
            # This is a placeholder - real implementation would need package context
            return f"# TODO: Convert to absolute import: {import_statement}"
        
        return import_statement
    
    def _convert_relative_to_absolute(self, dots: str, module_name: str, imports: str, current_module_path: str) -> Optional[str]:
        """
        Convert a relative import to absolute import.
        
        Args:
            dots: The dots from the relative import (., .., etc.)
            module_name: The module name after the dots
            imports: The imported items
            current_module_path: Path to the current module
            
        Returns:
            Absolute import string, or None if conversion not possible
        """
        # This is a simplified implementation
        # A full implementation would need to analyze the package structure
        
        dot_count = len(dots)
        
        if dot_count == 1:  # Single dot - same package
            if module_name:
                # Assume we're in a package and can convert
                return f"from {module_name} import {imports}"
            else:
                # from . import something - harder to convert without context
                return None
        
        elif dot_count == 2:  # Double dot - parent package
            if module_name:
                # This would need package structure analysis
                return f"# TODO: Convert relative import: from ..{module_name} import {imports}"
            else:
                return None
        
        # For more complex cases, return None (can't convert without more context)
        return None
    
    def _find_import_insertion_position(self, lines: List[str]) -> int:
        """
        Find the best position to insert import statements.
        
        Args:
            lines: List of code lines
            
        Returns:
            Index where imports should be inserted
        """
        # Skip shebang line
        start_index = 0
        if lines and lines[0].startswith('#!'):
            start_index = 1
        
        # Skip module docstring
        in_docstring = False
        docstring_quotes = None
        
        for i in range(start_index, len(lines)):
            line = lines[i].strip()
            
            # Skip empty lines and comments at the top
            if not line or line.startswith('#'):
                continue
            
            # Check for module docstring
            if not in_docstring:
                if line.startswith('"""') or line.startswith("'''"):
                    docstring_quotes = line[:3]
                    if line.count(docstring_quotes) >= 2:
                        # Single-line docstring
                        return i + 1
                    else:
                        # Multi-line docstring starts
                        in_docstring = True
                        continue
                elif line.startswith('"') or line.startswith("'"):
                    # Possible single-line docstring with single quotes
                    quote = line[0]
                    if line.count(quote) >= 2:
                        return i + 1
            else:
                # We're in a multi-line docstring
                if docstring_quotes and docstring_quotes in line:
                    # End of docstring
                    return i + 1
            
            # If we hit any other code, insert imports here
            if not in_docstring and not line.startswith('#'):
                return i
        
        # If we didn't find a good spot, insert at the beginning (after shebang)
        return start_index
    
    def validate_import_resolution(self, fixed_code: str, module_path: str = "") -> ValidationResult:
        """
        Validate that fixed imports still resolve correctly.
        
        Args:
            fixed_code: The code after import fixes have been applied
            module_path: Path to the module being validated
            
        Returns:
            ValidationResult indicating success/failure and any issues
        """
        errors = []
        warnings = []
        fixed_imports = []
        
        try:
            # Parse the code to check for syntax errors
            ast.parse(fixed_code)
        except SyntaxError as e:
            errors.append(f"Syntax error after import fixes: {e}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, fixed_imports=fixed_imports)
        
        # Extract all import statements from the fixed code
        lines = fixed_code.split('\n')
        import_statements = []
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            if stripped_line.startswith(('import ', 'from ')) and 'import' in stripped_line:
                import_statements.append((line_num, stripped_line))
                fixed_imports.append(stripped_line)
        
        # Validate each import statement
        for line_num, import_stmt in import_statements:
            validation_issues = self._validate_single_import(import_stmt, module_path)
            
            for issue in validation_issues:
                if issue['severity'] == 'error':
                    errors.append(f"Line {line_num}: {issue['message']}")
                else:
                    warnings.append(f"Line {line_num}: {issue['message']}")
        
        # Check for duplicate imports
        import_counts = {}
        for line_num, import_stmt in import_statements:
            normalized_import = self._normalize_import_statement(import_stmt)
            if normalized_import in import_counts:
                warnings.append(f"Duplicate import detected: {import_stmt}")
            else:
                import_counts[normalized_import] = line_num
        
        # Overall validation result
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            fixed_imports=fixed_imports
        )
    
    def validate_fixes_applied(self, original_code: str, fixed_code: str) -> ValidationResult:
        """
        Validate that import fixes were applied correctly by comparing original and fixed code.
        
        Args:
            original_code: The original code before fixes
            fixed_code: The code after fixes were applied
            
        Returns:
            ValidationResult indicating the success of the fixes
        """
        errors = []
        warnings = []
        fixed_imports = []
        
        # Find issues in original code
        original_issues = self.scan_for_import_issues(original_code)
        
        # Find remaining issues in fixed code
        remaining_issues = self.scan_for_import_issues(fixed_code)
        
        # Check if issues were resolved
        original_issue_count = len(original_issues)
        remaining_issue_count = len(remaining_issues)
        
        if remaining_issue_count > 0:
            for issue in remaining_issues:
                errors.append(f"Unresolved import issue at line {issue.line_number}: {issue.problematic_import}")
        
        if remaining_issue_count >= original_issue_count:
            warnings.append("Import fixes may not have been effective")
        
        # Extract fixed imports from the new code
        lines = fixed_code.split('\n')
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith(('import ', 'from ')) and 'import' in stripped_line:
                fixed_imports.append(stripped_line)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            fixed_imports=fixed_imports
        )
    
    def _validate_single_import(self, import_statement: str, module_path: str) -> List[dict]:
        """
        Validate a single import statement for potential issues.
        
        Args:
            import_statement: The import statement to validate
            module_path: Path context for the import
            
        Returns:
            List of validation issues (each with 'severity' and 'message')
        """
        issues = []
        
        # Check for basic syntax issues
        if not import_statement.strip():
            issues.append({'severity': 'error', 'message': 'Empty import statement'})
            return issues
        
        # Check for malformed import statements
        if not re.match(r'^\s*(import\s+\w+|from\s+[\w.]+\s+import\s+.+)', import_statement):
            issues.append({'severity': 'error', 'message': f'Malformed import statement: {import_statement}'})
        
        # Check for relative imports that might be problematic
        if re.match(r'^\s*from\s+\.{3,}', import_statement):
            issues.append({'severity': 'warning', 'message': 'Deep relative import may be unresolvable'})
        
        # Check for imports with suspicious module names
        module_match = re.search(r'(?:import\s+|from\s+)([\w.]+)', import_statement)
        if module_match:
            module_name = module_match.group(1)
            
            # Check for common problematic patterns
            if module_name.startswith('.') and len(module_name.split('.')) > 3:
                issues.append({'severity': 'warning', 'message': f'Complex relative import: {module_name}'})
            
            # Check for module names that look suspicious
            if any(char.isdigit() for char in module_name.replace('.', '')) and not any(char.isalpha() for char in module_name):
                issues.append({'severity': 'warning', 'message': f'Suspicious module name: {module_name}'})
        
        # Check for circular import risks (basic heuristic)
        if 'import' in import_statement and module_path:
            # Extract the module being imported
            if 'from' in import_statement:
                from_match = re.search(r'from\s+([\w.]+)\s+import', import_statement)
                if from_match:
                    imported_module = from_match.group(1)
                    # Basic check: if importing from a module with similar name, warn about potential circular import
                    current_module_name = Path(module_path).stem if module_path else ""
                    if current_module_name and imported_module and current_module_name in imported_module:
                        issues.append({'severity': 'warning', 'message': f'Potential circular import risk with {imported_module}'})
        
        return issues
    
    def _normalize_import_statement(self, import_statement: str) -> str:
        """
        Normalize an import statement for comparison (remove extra whitespace, etc.).
        
        Args:
            import_statement: The import statement to normalize
            
        Returns:
            Normalized import statement
        """
        # Remove extra whitespace and normalize
        normalized = re.sub(r'\s+', ' ', import_statement.strip())
        
        # Sort imports in 'from X import A, B, C' statements for consistent comparison
        from_match = re.match(r'^from\s+([\w.]+)\s+import\s+(.+)', normalized)
        if from_match:
            module = from_match.group(1)
            imports = from_match.group(2)
            
            # Split and sort the imported items
            import_items = [item.strip() for item in imports.split(',')]
            import_items.sort()
            
            normalized = f"from {module} import {', '.join(import_items)}"
        
        return normalized