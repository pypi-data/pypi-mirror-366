"""
Debug analyzer engine for comprehensive error analysis and code revision.

This module provides comprehensive debugging capabilities including traceback analysis,
function inspection, docstring parsing, and AI-powered code revision suggestions.
"""

import inspect
import traceback
import sys
import ast
import re
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

try:
    from docstring_parser import parse as parse_docstring
except ImportError:
    # Fallback if docstring_parser is not available
    def parse_docstring(docstring: str):
        return None

from ..core.interfaces import DebugAnalyzerInterface, AIClientInterface, StateManagerInterface
from ..core.models import (
    TracebackAnalysis, FunctionInspection, ParsedDocstring, DebugContext,
    CodeRevision, FunctionSpec, StackFrame, Parameter, ComplexityMetrics,
    ValidationResult, VerificationResult, ExecutionResult
)
from .base import BaseEngine


class DebugAnalyzer(BaseEngine, DebugAnalyzerInterface):
    """
    Comprehensive debug analyzer for error analysis and code revision.
    
    Provides detailed analysis of runtime errors, function inspection,
    docstring parsing, and AI-powered code revision suggestions.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None,
                 project_path: str = "."):
        """
        Initialize the debug analyzer.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
            project_path: Path to the project root directory
        """
        super().__init__(ai_client, state_manager)
        self.project_path = Path(project_path)
    
    def analyze_traceback(self, exception: Exception) -> TracebackAnalysis:
        """
        Analyze a traceback and identify root causes.
        
        Args:
            exception: The exception to analyze
            
        Returns:
            TracebackAnalysis: Comprehensive analysis of the traceback
        """
        self._ensure_initialized()
        
        # Extract basic exception information
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Build exception chain
        exception_chain = []
        current_exception = exception
        while current_exception:
            exception_chain.append(f"{type(current_exception).__name__}: {current_exception}")
            current_exception = current_exception.__cause__ or current_exception.__context__
        
        # Extract stack trace
        stack_trace = []
        tb = exception.__traceback__
        
        while tb is not None:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            line_number = tb.tb_lineno
            function_name = frame.f_code.co_name
            
            # Try to get the actual code line
            code_line = None
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if 0 <= line_number - 1 < len(lines):
                        code_line = lines[line_number - 1].strip()
            except (IOError, IndexError):
                pass
            
            # Extract local variables (limit to avoid overwhelming output)
            local_vars = {}
            for var_name, var_value in frame.f_locals.items():
                if not var_name.startswith('__'):
                    try:
                        # Convert to string representation, truncate if too long
                        var_str = repr(var_value)
                        if len(var_str) > 100:
                            var_str = var_str[:97] + "..."
                        local_vars[var_name] = var_str
                    except Exception:
                        local_vars[var_name] = "<unable to represent>"
                
                # Limit number of variables to avoid overwhelming output
                if len(local_vars) >= 10:
                    break
            
            stack_frame = StackFrame(
                filename=filename,
                line_number=line_number,
                function_name=function_name,
                code_line=code_line,
                local_variables=local_vars
            )
            stack_trace.append(stack_frame)
            tb = tb.tb_next
        
        # Analyze root cause
        root_cause = self._identify_root_cause(exception, stack_trace)
        
        # Generate suggested fixes
        suggested_fixes = self._generate_fix_suggestions(exception, stack_trace)
        
        return TracebackAnalysis(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            root_cause=root_cause,
            suggested_fixes=suggested_fixes,
            exception_chain=exception_chain
        )
    
    def inspect_function(self, function: Any) -> FunctionInspection:
        """
        Inspect a function using Python's inspect module.
        
        Args:
            function: The function to inspect
            
        Returns:
            FunctionInspection: Detailed inspection results
        """
        self._ensure_initialized()
        
        try:
            # Get function signature
            sig = inspect.signature(function)
            signature = str(sig)
            
            # Get source code
            source_code = None
            try:
                source_code = inspect.getsource(function)
            except (OSError, TypeError):
                pass
            
            # Get docstring
            docstring = inspect.getdoc(function)
            
            # Extract parameters
            parameters = []
            for param_name, param in sig.parameters.items():
                # Handle annotation formatting
                annotation = None
                if param.annotation != inspect.Parameter.empty:
                    if hasattr(param.annotation, '__name__'):
                        annotation = param.annotation.__name__
                    else:
                        annotation = str(param.annotation)
                
                param_info = Parameter(
                    name=param_name,
                    annotation=annotation,
                    default_value=str(param.default) if param.default != inspect.Parameter.empty else None,
                    kind=param.kind.name
                )
                parameters.append(param_info)
            
            # Get return annotation
            return_annotation = None
            if sig.return_annotation != inspect.Signature.empty:
                if hasattr(sig.return_annotation, '__name__'):
                    return_annotation = sig.return_annotation.__name__
                else:
                    return_annotation = str(sig.return_annotation)
            
            # Get file path and line number
            file_path = None
            line_number = None
            try:
                file_path = inspect.getfile(function)
                line_number = inspect.getsourcelines(function)[1]
            except (OSError, TypeError):
                pass
            
            # Calculate complexity metrics if source is available
            complexity_metrics = None
            if source_code:
                complexity_metrics = self._calculate_complexity_metrics(source_code)
            
            return FunctionInspection(
                signature=signature,
                source_code=source_code,
                docstring=docstring,
                parameters=parameters,
                return_annotation=return_annotation,
                complexity_metrics=complexity_metrics,
                file_path=file_path,
                line_number=line_number
            )
            
        except Exception as e:
            # Return minimal inspection if full inspection fails
            return FunctionInspection(
                signature=f"<unable to inspect: {e}>",
                source_code=None,
                docstring=None,
                parameters=[],
                return_annotation=None,
                complexity_metrics=None,
                file_path=None,
                line_number=None
            )
    
    def parse_docstring(self, docstring: str) -> ParsedDocstring:
        """
        Parse a docstring using docstring_parser.
        
        Args:
            docstring: The docstring to parse
            
        Returns:
            ParsedDocstring: Parsed docstring information
        """
        self._ensure_initialized()
        
        if not docstring or not docstring.strip():
            return ParsedDocstring()
        
        try:
            # Use docstring_parser if available
            if parse_docstring is not None:
                parsed = parse_docstring(docstring)
                
                # Extract parameters
                parameters = []
                for param in parsed.params:
                    param_info = {
                        'name': param.arg_name,
                        'type': param.type_name or '',
                        'description': param.description or ''
                    }
                    parameters.append(param_info)
                
                # Extract returns information
                returns = None
                if parsed.returns:
                    returns = {
                        'type': parsed.returns.type_name or '',
                        'description': parsed.returns.description or ''
                    }
                
                # Extract raises information
                raises = []
                for exc in parsed.raises:
                    exc_info = {
                        'exception': exc.type_name or '',
                        'description': exc.description or ''
                    }
                    raises.append(exc_info)
                
                # Extract examples (if available in the parser)
                examples = []
                if hasattr(parsed, 'examples') and parsed.examples:
                    examples = [str(example) for example in parsed.examples]
                
                return ParsedDocstring(
                    short_description=parsed.short_description or '',
                    long_description=parsed.long_description or '',
                    parameters=parameters,
                    returns=returns,
                    raises=raises,
                    examples=examples
                )
            else:
                # Fallback parsing if docstring_parser is not available
                return self._fallback_docstring_parse(docstring)
                
        except Exception:
            # Fallback to basic parsing if docstring_parser fails
            return self._fallback_docstring_parse(docstring)
    
    def generate_debug_context(self, error: Exception, function_spec: FunctionSpec) -> DebugContext:
        """
        Generate comprehensive debug context for AI revision.
        
        Args:
            error: The exception that occurred
            function_spec: Specification of the function that failed
            
        Returns:
            DebugContext: Comprehensive debug context
        """
        self._ensure_initialized()
        
        # Analyze the traceback
        traceback_analysis = self.analyze_traceback(error)
        
        # Try to inspect the function if we can find it
        function_inspection = None
        try:
            # Try to find and inspect the actual function
            function_obj = self._find_function_object(function_spec)
            if function_obj:
                function_inspection = self.inspect_function(function_obj)
        except Exception:
            pass
        
        # Parse the docstring from the function spec
        parsed_docstring = None
        if function_spec.docstring:
            parsed_docstring = self.parse_docstring(function_spec.docstring)
        
        # Collect related code (dependencies, imports, etc.)
        related_code = self._collect_related_code(function_spec)
        
        # Gather execution environment information
        execution_environment = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': str(self.project_path),
            'function_module': function_spec.module,
            'function_name': function_spec.name
        }
        
        return DebugContext(
            function_spec=function_spec,
            traceback_analysis=traceback_analysis,
            function_inspection=function_inspection,
            parsed_docstring=parsed_docstring,
            related_code=related_code,
            execution_environment=execution_environment,
            revision_history=[]
        )
    
    def suggest_code_revision(self, debug_context: DebugContext) -> CodeRevision:
        """
        Generate AI-powered code revision suggestions.
        
        Args:
            debug_context: Comprehensive debug context
            
        Returns:
            CodeRevision: AI-generated code revision
        """
        self._ensure_initialized()
        
        if not self.ai_client:
            raise RuntimeError("AI client is required for code revision suggestions")
        
        # Build the prompt for AI revision
        prompt = self._build_revision_prompt(debug_context)
        
        try:
            # Check fallback configuration
            from ..config import A3Config
            config = A3Config.load()
            use_fallbacks = config.use_fallback_models
            
            # Get AI suggestion
            ai_response = self.ai_client.generate_with_retry(prompt, max_retries=3, use_fallbacks=use_fallbacks)
            
            # Parse the AI response to extract revised code
            original_code = ""
            if debug_context.function_inspection and debug_context.function_inspection.source_code:
                original_code = debug_context.function_inspection.source_code
            
            revised_code, revision_reason, confidence = self._parse_ai_revision_response(ai_response)
            
            return CodeRevision(
                original_code=original_code,
                revised_code=revised_code,
                revision_reason=revision_reason,
                confidence_score=confidence,
                applied=False,
                test_results=None
            )
            
        except Exception as e:
            # Return a basic revision if AI fails
            return CodeRevision(
                original_code=debug_context.function_inspection.source_code if debug_context.function_inspection else "",
                revised_code="# AI revision failed, manual intervention required",
                revision_reason=f"AI revision failed: {e}",
                confidence_score=0.0,
                applied=False,
                test_results=None
            )
    
    def apply_revision(self, revision: CodeRevision, module_path: str) -> bool:
        """
        Apply a code revision to the actual source file.
        
        Args:
            revision: The code revision to apply
            module_path: Path to the module file
            
        Returns:
            bool: True if revision was applied successfully
        """
        self._ensure_initialized()
        
        try:
            file_path = Path(module_path)
            if not file_path.exists():
                return False
            
            # Read the current file content
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Replace the original code with revised code
            if revision.original_code and revision.original_code.strip():
                new_content = current_content.replace(revision.original_code, revision.revised_code)
                
                # Write the updated content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                revision.applied = True
                return True
            
            return False
            
        except Exception:
            return False
    
    def verify_revision(self, revision: CodeRevision, function_spec: FunctionSpec) -> VerificationResult:
        """
        Verify that a code revision resolves the original issue.
        
        Args:
            revision: The code revision to verify
            function_spec: The function specification
            
        Returns:
            VerificationResult: Results of the verification
        """
        self._ensure_initialized()
        
        verification_errors = []
        
        # Basic syntax check
        try:
            ast.parse(revision.revised_code)
        except SyntaxError as e:
            verification_errors.append(f"Syntax error in revised code: {e}")
        
        # Try to execute the revised code (if safe)
        execution_result = None
        try:
            # This is a simplified verification - in practice, you'd want more sophisticated testing
            exec(revision.revised_code)
            execution_result = ExecutionResult(success=True, output="Code executed without errors")
        except Exception as e:
            execution_result = ExecutionResult(success=False, error=e)
            verification_errors.append(f"Execution error in revised code: {e}")
        
        is_verified = len(verification_errors) == 0
        
        return VerificationResult(
            function_name=function_spec.name,
            is_verified=is_verified,
            execution_result=execution_result,
            test_result=None,  # Would need test executor integration
            import_validation=None,  # Would need import validator integration
            verification_errors=verification_errors
        )
    
    def debug_and_revise_loop(self, error: Exception, function_spec: FunctionSpec, 
                             module_path: str, max_iterations: int = 3) -> List[CodeRevision]:
        """
        Perform a complete debug and revision loop with multiple attempts.
        
        Args:
            error: The original exception that occurred
            function_spec: Specification of the function that failed
            module_path: Path to the module file
            max_iterations: Maximum number of revision attempts
            
        Returns:
            List[CodeRevision]: List of all revision attempts
        """
        self._ensure_initialized()
        
        if not self.ai_client:
            raise RuntimeError("AI client is required for debug and revision loop")
        
        revisions = []
        current_error = error
        
        for iteration in range(max_iterations):
            # Generate debug context for current error
            debug_context = self.generate_debug_context(current_error, function_spec)
            
            # Add revision history to context
            debug_context.revision_history = [rev.revision_reason for rev in revisions]
            
            # Get AI revision suggestion
            revision = self.suggest_code_revision(debug_context)
            
            # Verify the revision
            verification = self.verify_revision(revision, function_spec)
            
            # Store verification results in revision
            revision.test_results = verification.execution_result
            
            revisions.append(revision)
            
            # If revision is successful, we're done
            if verification.is_verified:
                # Apply the successful revision
                if self.apply_revision(revision, module_path):
                    revision.applied = True  # Mark as applied
                    break
            else:
                # If verification failed, use the verification error for next iteration
                if verification.execution_result and verification.execution_result.error:
                    current_error = verification.execution_result.error
                else:
                    # If no specific error, create a generic one
                    current_error = RuntimeError(f"Revision verification failed: {verification.verification_errors}")
        
        return revisions
    
    def analyze_and_fix_function(self, function_spec: FunctionSpec, module_path: str, 
                                original_error: Optional[Exception] = None) -> Dict[str, Any]:
        """
        Complete analysis and fixing workflow for a function.
        
        Args:
            function_spec: Specification of the function to analyze and fix
            module_path: Path to the module file
            original_error: Original error that occurred (if any)
            
        Returns:
            Dict containing analysis results, revisions, and final status
        """
        self._ensure_initialized()
        
        result = {
            'function_spec': function_spec,
            'original_error': original_error,
            'debug_context': None,
            'revisions': [],
            'final_status': 'unknown',
            'success': False
        }
        
        try:
            if original_error:
                # If we have an error, perform debug and revision loop
                revisions = self.debug_and_revise_loop(original_error, function_spec, module_path)
                result['revisions'] = revisions
                
                # Check if any revision was successful
                successful_revisions = [rev for rev in revisions if rev.applied]
                if successful_revisions:
                    result['final_status'] = 'fixed'
                    result['success'] = True
                else:
                    result['final_status'] = 'failed_to_fix'
            else:
                # If no error, just analyze the function
                try:
                    function_obj = self._find_function_object(function_spec)
                    if function_obj:
                        inspection = self.inspect_function(function_obj)
                        result['debug_context'] = DebugContext(
                            function_spec=function_spec,
                            function_inspection=inspection,
                            parsed_docstring=self.parse_docstring(function_spec.docstring) if function_spec.docstring else None
                        )
                        result['final_status'] = 'analyzed'
                        result['success'] = True
                    else:
                        result['final_status'] = 'function_not_found'
                except Exception as e:
                    result['original_error'] = e
                    result['final_status'] = 'analysis_failed'
                    
        except Exception as e:
            result['final_status'] = 'workflow_error'
            result['original_error'] = e
        
        return result
    
    def _identify_root_cause(self, exception: Exception, stack_trace: List[StackFrame]) -> str:
        """Identify the root cause of an exception."""
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Common error patterns and their root causes
        if error_type == "NameError":
            if "is not defined" in error_message:
                # Extract variable name from error message
                parts = error_message.split("'")
                if len(parts) >= 2:
                    var_name = parts[1]
                    return f"Variable or function '{var_name}' is not defined or not in scope"
        elif error_type == "AttributeError":
            if "has no attribute" in error_message:
                return f"Object does not have the expected attribute or method"
        elif error_type == "TypeError":
            if "takes" in error_message and "positional argument" in error_message:
                return "Function called with incorrect number of arguments"
            elif "unsupported operand type" in error_message:
                return "Operation attempted on incompatible data types"
        elif error_type == "ImportError" or error_type == "ModuleNotFoundError":
            return f"Required module or package is not installed or not found"
        elif error_type == "IndentationError":
            return "Code has incorrect indentation"
        elif error_type == "SyntaxError":
            return "Code has syntax errors that prevent parsing"
        
        # If no specific pattern matches, provide a general analysis
        if stack_trace:
            last_frame = stack_trace[-1]
            return f"{error_type} occurred in {last_frame.function_name} at line {last_frame.line_number}"
        
        return f"{error_type}: {error_message}"
    
    def _generate_fix_suggestions(self, exception: Exception, stack_trace: List[StackFrame]) -> List[str]:
        """Generate suggested fixes based on the exception and stack trace."""
        suggestions = []
        error_type = type(exception).__name__
        error_message = str(exception)
        
        if error_type == "NameError":
            suggestions.append("Check if the variable is defined before use")
            suggestions.append("Verify the variable name is spelled correctly")
            suggestions.append("Ensure the variable is in the correct scope")
        elif error_type == "AttributeError":
            suggestions.append("Check if the object has the expected attribute or method")
            suggestions.append("Verify the object type is correct")
            suggestions.append("Consider using hasattr() to check for attribute existence")
        elif error_type == "TypeError":
            suggestions.append("Check the function signature and argument types")
            suggestions.append("Verify the correct number of arguments are passed")
            suggestions.append("Ensure data types are compatible for the operation")
        elif error_type == "ImportError" or error_type == "ModuleNotFoundError":
            suggestions.append("Install the required package using pip")
            suggestions.append("Check if the module name is spelled correctly")
            suggestions.append("Verify the module is in the Python path")
        elif error_type == "IndentationError":
            suggestions.append("Check indentation consistency (spaces vs tabs)")
            suggestions.append("Ensure proper indentation levels")
        elif error_type == "SyntaxError":
            suggestions.append("Check for missing parentheses, brackets, or quotes")
            suggestions.append("Verify proper syntax for Python constructs")
        
        # Add general suggestions
        suggestions.append("Review the code logic and flow")
        suggestions.append("Add error handling and validation")
        suggestions.append("Consider adding unit tests to catch similar issues")
        
        return suggestions
    
    def _calculate_complexity_metrics(self, source_code: str) -> ComplexityMetrics:
        """Calculate complexity metrics for source code."""
        try:
            tree = ast.parse(source_code)
            
            # Count lines of code (excluding empty lines, comments, and docstrings)
            lines = source_code.split('\n')
            loc = 0
            in_docstring = False
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith('#'):
                    continue
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                        # Single line docstring
                        continue
                    in_docstring = not in_docstring
                    continue
                if in_docstring:
                    continue
                if stripped.startswith('def ') or stripped.startswith('class '):
                    continue
                loc += 1
            
            # Simple cyclomatic complexity calculation
            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            # Simple single-responsibility score (inverse of complexity)
            sr_score = max(0.0, 1.0 - (complexity - 1) * 0.1)
            
            return ComplexityMetrics(
                cyclomatic_complexity=complexity,
                cognitive_complexity=complexity,  # Simplified
                lines_of_code=loc,
                single_responsibility_score=sr_score
            )
            
        except Exception:
            return ComplexityMetrics()
    
    def _fallback_docstring_parse(self, docstring: str) -> ParsedDocstring:
        """Fallback docstring parsing when docstring_parser is not available."""
        lines = docstring.strip().split('\n')
        if not lines:
            return ParsedDocstring()
        
        short_description = lines[0].strip()
        long_description = ""
        
        if len(lines) > 1:
            # Find the first non-empty line after the short description
            for i in range(1, len(lines)):
                if lines[i].strip():
                    long_description = '\n'.join(lines[i:]).strip()
                    break
        
        return ParsedDocstring(
            short_description=short_description,
            long_description=long_description,
            parameters=[],
            returns=None,
            raises=[],
            examples=[]
        )
    
    def _find_function_object(self, function_spec: FunctionSpec) -> Optional[Callable]:
        """Try to find the actual function object for inspection."""
        try:
            # This is a simplified implementation
            # In practice, you'd need more sophisticated module loading
            module_path = self.project_path / f"{function_spec.module}.py"
            if module_path.exists():
                # Dynamic import would go here
                pass
        except Exception:
            pass
        return None
    
    def _collect_related_code(self, function_spec: FunctionSpec) -> List[str]:
        """Collect related code snippets for context."""
        related_code = []
        
        try:
            # Add the function specification as context
            spec_info = f"Function: {function_spec.name}\n"
            spec_info += f"Module: {function_spec.module}\n"
            spec_info += f"Docstring: {function_spec.docstring}\n"
            spec_info += f"Arguments: {[arg.name for arg in function_spec.arguments]}\n"
            spec_info += f"Return type: {function_spec.return_type}"
            related_code.append(spec_info)
            
            # Try to read the module file for additional context
            module_path = self.project_path / f"{function_spec.module}.py"
            if module_path.exists():
                with open(module_path, 'r', encoding='utf-8') as f:
                    module_content = f.read()
                    # Add imports and class definitions as context
                    lines = module_content.split('\n')
                    context_lines = []
                    for line in lines[:20]:  # First 20 lines for imports/setup
                        if line.strip().startswith(('import ', 'from ', 'class ', 'def ')):
                            context_lines.append(line)
                    if context_lines:
                        related_code.append('\n'.join(context_lines))
                        
        except Exception:
            pass
        
        return related_code
    
    def _build_revision_prompt(self, debug_context: DebugContext) -> str:
        """Build a comprehensive prompt for AI code revision."""
        prompt = "You are an expert Python developer tasked with fixing a bug in the following function.\n\n"
        
        # Add function specification
        prompt += "FUNCTION SPECIFICATION:\n"
        prompt += f"Name: {debug_context.function_spec.name}\n"
        prompt += f"Module: {debug_context.function_spec.module}\n"
        prompt += f"Docstring: {debug_context.function_spec.docstring}\n"
        prompt += f"Arguments: {[f'{arg.name}: {arg.type_hint}' for arg in debug_context.function_spec.arguments]}\n"
        prompt += f"Return type: {debug_context.function_spec.return_type}\n\n"
        
        # Add error information
        if debug_context.traceback_analysis:
            prompt += "ERROR ANALYSIS:\n"
            prompt += f"Error Type: {debug_context.traceback_analysis.error_type}\n"
            prompt += f"Error Message: {debug_context.traceback_analysis.error_message}\n"
            prompt += f"Root Cause: {debug_context.traceback_analysis.root_cause}\n"
            if debug_context.traceback_analysis.suggested_fixes:
                prompt += f"Suggested Fixes: {', '.join(debug_context.traceback_analysis.suggested_fixes)}\n"
            prompt += "\n"
        
        # Add current implementation if available
        if debug_context.function_inspection and debug_context.function_inspection.source_code:
            prompt += "CURRENT IMPLEMENTATION:\n"
            prompt += debug_context.function_inspection.source_code
            prompt += "\n\n"
        
        # Add related code context
        if debug_context.related_code:
            prompt += "RELATED CODE CONTEXT:\n"
            for code_snippet in debug_context.related_code:
                prompt += code_snippet + "\n"
            prompt += "\n"
        
        prompt += "Please provide a corrected implementation that:\n"
        prompt += "1. Fixes the identified error\n"
        prompt += "2. Maintains the function signature and docstring\n"
        prompt += "3. Follows Python best practices\n"
        prompt += "4. Includes proper error handling\n\n"
        prompt += "Respond with the complete corrected function implementation."
        
        return prompt
    
    def _parse_ai_revision_response(self, ai_response: str) -> tuple[str, str, float]:
        """Parse the AI response to extract revised code, reason, and confidence."""
        # This is a simplified parser - in practice, you'd want more sophisticated parsing
        revised_code = ai_response.strip()
        revision_reason = "AI-generated code revision based on error analysis"
        confidence = 0.8  # Default confidence
        
        # Try to extract code blocks if present
        code_block_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_block_pattern, ai_response, re.DOTALL)
        if matches:
            revised_code = matches[0].strip()
            confidence = 0.9
        
        return revised_code, revision_reason, confidence