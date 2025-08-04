"""
Code generator implementation for AI Project Builder.

This module provides the CodeGenerator class that generates function implementations
using OpenRouter AI service with retry logic and progress tracking.
"""

import json
import re
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime

from .base import BaseCodeGenerator
from ..core.models import (
    FunctionSpec, SpecificationSet, ImplementationResult, ValidationResult,
    ImplementationStatus, ProjectPhase
)
from ..core.interfaces import AIClientInterface, StateManagerInterface


class CodeGeneratorError(Exception):
    """Base exception for code generator errors."""
    pass


class CodeGenerationError(CodeGeneratorError):
    """Exception raised when code generation fails."""
    pass


class CodeValidationError(CodeGeneratorError):
    """Exception raised when generated code validation fails."""
    pass


class CodeGenerator(BaseCodeGenerator):
    """
    Engine for generating function implementations using AI.
    
    Generates working Python code for functions based on their specifications,
    with retry logic, progress tracking, and error handling.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None,
                 project_path: Optional[str] = None):
        """
        Initialize the code generator.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
            project_path: Path to the project directory
        """
        super().__init__(ai_client, state_manager)
        self.project_path = project_path
        self.max_retries = 3
        self.retry_delay = 1.0  # Base delay between retries in seconds
        self.generated_code = {}  # Cache for generated code
        self.failed_functions = []  # Track failed implementations
        self.failure_details = {}  # Detailed failure information for debugging
        self.retry_attempts = {}  # Track retry attempts per function
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def set_project_path(self, project_path: str) -> None:
        """
        Set the project path for file operations.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        
    def implement_function(self, spec: FunctionSpec, retry_count: int = 0) -> str:
        """
        Generate implementation code for a single function with retry logic.
        
        Args:
            spec: Function specification to implement
            retry_count: Current retry attempt (for internal use)
            
        Returns:
            Generated Python code for the function
            
        Raises:
            CodeGenerationError: If code generation fails after all retries
        """
        self._ensure_initialized()
        
        if not spec:
            raise CodeGenerationError("Function specification cannot be None")
        
        function_key = f"{spec.module}.{spec.name}"
        
        try:
            # Validate the specification
            spec.validate()
            
            # Check if already implemented
            if spec.implementation_status == ImplementationStatus.COMPLETED:
                if function_key in self.generated_code:
                    self.logger.info(f"Function {function_key} already implemented, returning cached code")
                    return self.generated_code[function_key]
            
            # Log attempt
            if retry_count == 0:
                self.logger.info(f"Implementing function {function_key}")
            else:
                self.logger.info(f"Retrying implementation of function {function_key} (attempt {retry_count + 1}/{self.max_retries + 1})")
            
            # Generate the implementation with retry logic
            code = self._generate_function_code_with_retry(spec, retry_count)
            
            # Validate the generated code
            self._validate_generated_code(code, spec)
            
            # Cache the generated code
            self.generated_code[function_key] = code
            
            # Update implementation status and clear any previous failures
            spec.implementation_status = ImplementationStatus.COMPLETED
            if function_key in self.failed_functions:
                self.failed_functions.remove(function_key)
            if function_key in self.failure_details:
                del self.failure_details[function_key]
            if function_key in self.retry_attempts:
                del self.retry_attempts[function_key]
            
            self.logger.info(f"Successfully implemented function {function_key}")
            return code
            
        except Exception as e:
            # Track retry attempts
            if function_key not in self.retry_attempts:
                self.retry_attempts[function_key] = 0
            self.retry_attempts[function_key] = retry_count + 1
            
            # Log the error
            error_msg = str(e)
            self.logger.error(f"Failed to implement function {function_key} (attempt {retry_count + 1}): {error_msg}")
            
            # Store detailed failure information
            self.failure_details[function_key] = {
                'error': error_msg,
                'error_type': type(e).__name__,
                'retry_count': retry_count,
                'timestamp': datetime.now().isoformat(),
                'spec_summary': {
                    'name': spec.name,
                    'module': spec.module,
                    'args_count': len(spec.arguments),
                    'return_type': spec.return_type
                }
            }
            
            # Retry if we haven't exceeded max retries
            if retry_count < self.max_retries:
                # Exponential backoff with jitter
                delay = self.retry_delay * (2 ** retry_count) + (retry_count * 0.1)
                self.logger.info(f"Waiting {delay:.1f} seconds before retry...")
                time.sleep(delay)
                
                # Recursive retry
                return self.implement_function(spec, retry_count + 1)
            
            # Mark as failed after all retries exhausted
            spec.implementation_status = ImplementationStatus.FAILED
            if function_key not in self.failed_functions:
                self.failed_functions.append(function_key)
            
            # Log final failure
            self.logger.error(f"Function {function_key} failed after {self.max_retries + 1} attempts")
            
            # Save failure details to state if available
            self._save_failure_details()
            
            if isinstance(e, CodeGeneratorError):
                raise
            else:
                raise CodeGenerationError(f"Failed to implement function {function_key} after {self.max_retries + 1} attempts: {error_msg}")
    
    def implement_all(self, specs: SpecificationSet) -> ImplementationResult:
        """
        Generate implementations for all functions in the specification set.
        
        Args:
            specs: SpecificationSet containing all function specifications
            
        Returns:
            ImplementationResult with success/failure information
            
        Raises:
            CodeGenerationError: If the operation fails completely
        """
        self._ensure_initialized()
        
        if not specs or not specs.functions:
            raise CodeGenerationError("Specification set cannot be empty")
        
        implemented_functions = []
        failed_functions = []
        total_functions = len(specs.functions)
        
        try:
            # Sort functions by dependency order if possible
            ordered_functions = self._order_functions_by_dependencies(specs.functions)
            
            # Generate implementations for each function
            for i, func_spec in enumerate(ordered_functions):
                try:
                    # Update progress
                    if self.state_manager:
                        self._save_implementation_progress(
                            current_function=f"{func_spec.module}.{func_spec.name}",
                            completed=i,
                            total=total_functions,
                            failed=len(failed_functions)
                        )
                    
                    # Generate implementation
                    code = self.implement_function(func_spec)
                    
                    # Write the generated code to file
                    try:
                        self._write_function_to_file(func_spec, code, specs)
                        implemented_functions.append(f"{func_spec.module}.{func_spec.name}")
                    except Exception as write_error:
                        self.logger.error(f"Failed to write function {func_spec.module}.{func_spec.name} to file: {write_error}")
                        failed_functions.append(f"{func_spec.module}.{func_spec.name}")
                        continue
                    
                except CodeGeneratorError as e:
                    failed_functions.append(f"{func_spec.module}.{func_spec.name}")
                    # Continue with other functions
                    continue
            
            # Calculate success rate
            success_rate = len(implemented_functions) / total_functions if total_functions > 0 else 0.0
            
            # Create result
            result = ImplementationResult(
                implemented_functions=implemented_functions,
                failed_functions=failed_functions,
                success_rate=success_rate,
                completed_at=datetime.now()
            )
            
            # Save final progress
            if self.state_manager:
                self._save_final_implementation_result(result, specs)
            
            return result
            
        except Exception as e:
            if isinstance(e, CodeGeneratorError):
                raise
            else:
                raise CodeGenerationError(f"Failed to implement functions: {str(e)}")
    
    def retry_failed_implementations(self, failed_functions: List[str] = None) -> ImplementationResult:
        """
        Retry implementation for previously failed functions with enhanced selective re-generation.
        
        Args:
            failed_functions: List of function names to retry. If None, retries all failed functions.
            
        Returns:
            ImplementationResult with retry results
            
        Raises:
            CodeGenerationError: If retry operation fails
        """
        self._ensure_initialized()
        
        # Use all failed functions if none specified
        if failed_functions is None:
            failed_functions = self.failed_functions.copy()
        
        if not failed_functions:
            self.logger.info("No failed functions to retry")
            return ImplementationResult(
                implemented_functions=[],
                failed_functions=[],
                success_rate=1.0,
                completed_at=datetime.now()
            )
        
        self.logger.info(f"Retrying implementation for {len(failed_functions)} failed functions: {failed_functions}")
        
        try:
            # Load function specifications for failed functions
            specs_to_retry = self._load_failed_function_specs(failed_functions)
            
            if not specs_to_retry:
                # Try to get specs from current state or create minimal specs
                specs_to_retry = self._create_minimal_specs_for_retry(failed_functions)
                
                if not specs_to_retry:
                    raise CodeGenerationError("Could not load or create specifications for failed functions")
            
            # Reset retry counters for selected functions
            for func_name in failed_functions:
                if func_name in self.retry_attempts:
                    self.retry_attempts[func_name] = 0
            
            # Implement each function individually for better control
            implemented_functions = []
            still_failed_functions = []
            
            for spec in specs_to_retry:
                function_key = f"{spec.module}.{spec.name}"
                
                if function_key not in failed_functions:
                    continue  # Skip if not in the retry list
                
                try:
                    # Reset status for retry
                    spec.implementation_status = ImplementationStatus.NOT_STARTED
                    
                    # Attempt implementation
                    code = self.implement_function(spec)
                    implemented_functions.append(function_key)
                    
                    self.logger.info(f"Successfully retried function {function_key}")
                    
                except CodeGenerationError as e:
                    still_failed_functions.append(function_key)
                    self.logger.error(f"Retry failed for function {function_key}: {str(e)}")
                    continue
            
            # Calculate success rate
            total_retried = len(failed_functions)
            success_rate = len(implemented_functions) / total_retried if total_retried > 0 else 0.0
            
            # Create result
            result = ImplementationResult(
                implemented_functions=implemented_functions,
                failed_functions=still_failed_functions,
                success_rate=success_rate,
                completed_at=datetime.now()
            )
            
            # Save retry results
            if self.state_manager:
                self._save_retry_results(result, failed_functions)
            
            self.logger.info(f"Retry completed: {len(implemented_functions)} succeeded, {len(still_failed_functions)} still failed")
            
            return result
            
        except Exception as e:
            if isinstance(e, CodeGeneratorError):
                raise
            else:
                raise CodeGenerationError(f"Failed to retry implementations: {str(e)}")
    
    def _generate_function_code_with_retry(self, spec: FunctionSpec, retry_count: int) -> str:
        """
        Generate code for a single function using AI with enhanced retry logic.
        
        Args:
            spec: Function specification
            retry_count: Current retry attempt
            
        Returns:
            Generated Python code
        """
        function_key = f"{spec.module}.{spec.name}"
        
        try:
            # Create prompt for code generation (enhanced for retries)
            prompt = self._create_code_generation_prompt(spec, retry_count)
            
            # Get configured model from state manager
            model = self._get_configured_model()
            
            # Check fallback configuration
            from ..config import A3Config
            config = A3Config.load()
            use_fallbacks = config.use_fallback_models
            
            # Generate code with AI client's built-in retry logic
            response = self.ai_client.generate_with_retry(prompt, max_retries=2, model=model, use_fallbacks=use_fallbacks)  # Reduced to avoid double retry
            
            # Extract and clean the code
            code = self._extract_code_from_response(response)
            
            return code
            
        except Exception as e:
            # Enhanced error context for retries
            error_context = f"retry {retry_count + 1}/{self.max_retries + 1}"
            if retry_count > 0:
                error_context += f", previous errors: {self.failure_details.get(function_key, {}).get('error', 'unknown')}"
            
            raise CodeGenerationError(f"Failed to generate code for {spec.module}.{spec.name} ({error_context}): {str(e)}")
    
    def _generate_function_code(self, spec: FunctionSpec) -> str:
        """
        Generate code for a single function using AI (legacy method for compatibility).
        
        Args:
            spec: Function specification
            
        Returns:
            Generated Python code
        """
        return self._generate_function_code_with_retry(spec, 0)
    
    def _create_code_generation_prompt(self, spec: FunctionSpec, retry_count: int = 0) -> str:
        """
        Create prompt for AI code generation with retry context.
        
        Args:
            spec: Function specification
            retry_count: Current retry attempt (0 for first attempt)
            
        Returns:
            Formatted prompt string
        """
        # Build argument list
        args_list = []
        for arg in spec.arguments:
            arg_str = f"{arg.name}: {arg.type_hint}"
            if arg.default_value:
                arg_str += f" = {arg.default_value}"
            args_list.append(arg_str)
        
        args_string = ", ".join(args_list)
        
        # Create context about the module
        module_context = f"This function belongs to the '{spec.module}' module."
        
        # Add retry context if this is a retry attempt
        retry_context = ""
        function_key = f"{spec.module}.{spec.name}"
        if retry_count > 0 and function_key in self.failure_details:
            previous_error = self.failure_details[function_key].get('error', 'unknown error')
            retry_context = f"""
RETRY ATTEMPT #{retry_count + 1}:
Previous attempt failed with: {previous_error}
Please ensure the implementation addresses the previous failure and follows all requirements strictly.
"""
        
        # Build the prompt
        prompt = f"""
You are a Python expert implementing a function based on its specification.

{module_context}
{retry_context}

Function Specification:
- Name: {spec.name}
- Arguments: {args_string}
- Return Type: {spec.return_type}
- Documentation: {spec.docstring}

Requirements:
1. Implement the function exactly as specified
2. Follow the docstring requirements precisely
3. Use proper error handling with appropriate exceptions
4. Include type hints as specified
5. Write clean, readable, and efficient code
6. Handle edge cases appropriately
7. Follow Python best practices and PEP 8 style guidelines
8. Ensure the function name matches exactly: {spec.name}
9. Include a proper docstring with triple quotes

Please provide ONLY the function implementation code, starting with 'def' and properly indented.
Do not include any explanations, comments outside the function, or example usage.
The code should be ready to use as-is.

Example format:
def function_name(arg1: type1, arg2: type2 = default) -> return_type:
    \"\"\"Function docstring here.\"\"\"
    # Implementation here
    return result
"""
        
        return prompt
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        Extract Python code from AI response.
        
        Args:
            response: Raw AI response
            
        Returns:
            Cleaned Python code
        """
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            
            # Look for code blocks
            if "```python" in response:
                start = response.find("```python") + 9
                end = response.find("```", start)
                if end != -1:
                    code = response[start:end].strip()
                else:
                    code = response[start:].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    code = response[start:end].strip()
                else:
                    code = response[start:].strip()
            else:
                # No code blocks, assume entire response is code
                code = response.strip()
            
            # Clean up the code
            lines = code.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip empty lines at the beginning
                if not cleaned_lines and not line.strip():
                    continue
                cleaned_lines.append(line)
            
            # Remove trailing empty lines
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()
            
            code = '\n'.join(cleaned_lines)
            
            # Validate that it starts with 'def'
            if not code.strip().startswith('def '):
                raise CodeValidationError("Generated code does not start with function definition")
            
            return code
            
        except CodeValidationError:
            raise
        except Exception as e:
            raise CodeGenerationError(f"Failed to extract code from response: {str(e)}")
    
    def _validate_generated_code(self, code: str, spec: FunctionSpec) -> None:
        """
        Validate that generated code meets basic requirements.
        
        Args:
            code: Generated Python code
            spec: Original function specification
            
        Raises:
            CodeValidationError: If validation fails
        """
        try:
            # Basic syntax validation
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                raise CodeValidationError(f"Generated code has syntax errors: {str(e)}")
            
            # Check function name
            if f"def {spec.name}(" not in code:
                raise CodeValidationError(f"Function name '{spec.name}' not found in generated code")
            
            # Check that it's a function definition
            if not code.strip().startswith('def '):
                raise CodeValidationError("Generated code is not a function definition")
            
            # Check for docstring presence
            if '"""' not in code and "'''" not in code:
                raise CodeValidationError("Generated code missing docstring")
            
            # Check for return statement (unless return type is None)
            if spec.return_type != "None" and "return " not in code:
                raise CodeValidationError("Function with non-None return type missing return statement")
            
        except CodeValidationError:
            raise
        except Exception as e:
            raise CodeValidationError(f"Code validation failed: {str(e)}")
    
    def _get_configured_model(self) -> Optional[str]:
        """
        Get the currently configured model from state manager.
        
        Returns:
            Currently configured model name, or None to use client default
        """
        try:
            if self.state_manager:
                model_config = self.state_manager.load_model_configuration()
                if model_config:
                    return model_config.current_model
            return None
        except Exception as e:
            # Log warning but don't fail - fall back to client default
            # In a real implementation, you might want to log this warning
            return None
    
    def _order_functions_by_dependencies(self, functions: List[FunctionSpec]) -> List[FunctionSpec]:
        """
        Order functions to minimize dependency issues during implementation.
        
        Args:
            functions: List of function specifications
            
        Returns:
            Ordered list of functions based on enhanced dependency analysis
        """
        try:
            # Try to get enhanced dependency graph from state manager
            if self.state_manager:
                plan = self.state_manager.load_project_plan()
                if plan and plan.enhanced_dependency_graph:
                    # Use enhanced dependency graph for optimal ordering
                    enhanced_graph = plan.enhanced_dependency_graph
                    optimal_order = enhanced_graph.get_function_implementation_order()
                    
                    # Create a mapping from function names to FunctionSpec objects
                    func_map = {}
                    for func in functions:
                        full_name = f"{func.module}.{func.name}"
                        func_map[full_name] = func
                    
                    # Order functions according to optimal implementation order
                    ordered_functions = []
                    for func_name in optimal_order:
                        if func_name in func_map:
                            ordered_functions.append(func_map[func_name])
                    
                    # Add any remaining functions that weren't in the optimal order
                    for func in functions:
                        full_name = f"{func.module}.{func.name}"
                        if full_name not in [f"{f.module}.{f.name}" for f in ordered_functions]:
                            ordered_functions.append(func)
                    
                    self.logger.info(f"Using enhanced dependency ordering for {len(ordered_functions)} functions")
                    return ordered_functions
            
            # Fallback to simple ordering if enhanced graph is not available
            self.logger.info("Enhanced dependency graph not available, using simple ordering")
            return sorted(functions, key=lambda f: (f.module, f.name))
            
        except Exception as e:
            # If anything goes wrong, fall back to simple ordering
            self.logger.warning(f"Failed to use enhanced dependency ordering: {e}")
            return sorted(functions, key=lambda f: (f.module, f.name))
    
    def get_parallel_implementation_groups(self, functions: List[FunctionSpec]) -> List[List[FunctionSpec]]:
        """
        Get groups of functions that can be implemented in parallel.
        
        Args:
            functions: List of function specifications
            
        Returns:
            List of groups, where each group contains functions that can be implemented in parallel
        """
        try:
            # Try to get enhanced dependency graph from state manager
            if self.state_manager:
                plan = self.state_manager.load_project_plan()
                if plan and plan.enhanced_dependency_graph:
                    enhanced_graph = plan.enhanced_dependency_graph
                    parallel_groups = enhanced_graph.get_parallel_implementation_groups()
                    
                    # Create a mapping from function names to FunctionSpec objects
                    func_map = {}
                    for func in functions:
                        full_name = f"{func.module}.{func.name}"
                        func_map[full_name] = func
                    
                    # Convert parallel groups to FunctionSpec groups
                    spec_groups = []
                    for group in parallel_groups:
                        spec_group = []
                        for func_name in group:
                            if func_name in func_map:
                                spec_group.append(func_map[func_name])
                        if spec_group:
                            spec_groups.append(spec_group)
                    
                    self.logger.info(f"Found {len(spec_groups)} parallel implementation groups")
                    return spec_groups
            
            # Fallback: return all functions as a single group
            return [functions]
            
        except Exception as e:
            self.logger.warning(f"Failed to get parallel implementation groups: {e}")
            return [functions]
    
    def _save_implementation_progress(self, current_function: str, completed: int, 
                                    total: int, failed: int) -> None:
        """Save current implementation progress to state manager with enhanced tracking."""
        if not self.state_manager:
            return
        
        try:
            progress_data = {
                'current_function': current_function,
                'total_functions': total,
                'implemented_functions': completed,
                'failed_functions': self.failed_functions.copy(),
                'progress_percentage': (completed / total * 100) if total > 0 else 0,
                'generated_code_count': len(self.generated_code),
                'failure_details': self.failure_details.copy(),
                'retry_attempts': self.retry_attempts.copy(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.state_manager.save_progress(ProjectPhase.IMPLEMENTATION, progress_data)
            
            # Log progress
            self.logger.info(f"Progress: {completed}/{total} functions implemented ({progress_data['progress_percentage']:.1f}%), {failed} failed")
            
        except Exception as e:
            self.logger.warning(f"Failed to save implementation progress: {str(e)}")
            # Don't fail the operation if progress saving fails
    
    def _save_final_implementation_result(self, result: ImplementationResult, 
                                        specs: SpecificationSet) -> None:
        """Save final implementation results to state manager with comprehensive data."""
        if not self.state_manager:
            return
        
        try:
            # Save comprehensive implementation data
            implementation_data = {
                'implemented_functions': result.implemented_functions,
                'failed_functions': result.failed_functions,
                'success_rate': result.success_rate,
                'completed_at': result.completed_at.isoformat(),
                'total_functions': len(specs.functions),
                'generated_code': self.generated_code.copy(),
                'failure_details': self.failure_details.copy(),
                'retry_attempts': self.retry_attempts.copy(),
                'failure_report': self.get_failure_report(),
                'retry_candidates': self.get_retry_candidates()
            }
            
            self.state_manager.save_progress(ProjectPhase.IMPLEMENTATION, implementation_data)
            
            # Log final summary
            self.logger.info(f"Implementation completed: {len(result.implemented_functions)} succeeded, "
                           f"{len(result.failed_functions)} failed, {result.success_rate:.1%} success rate")
            
            if result.failed_functions:
                self.logger.warning(f"Failed functions: {result.failed_functions}")
                retry_candidates = self.get_retry_candidates()
                if retry_candidates:
                    self.logger.info(f"Retry candidates: {retry_candidates}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save final implementation result: {str(e)}")
            # Don't fail the operation if saving fails
    
    def _save_failure_details(self) -> None:
        """Save detailed failure information to state manager."""
        if not self.state_manager or not self.failure_details:
            return
        
        try:
            failure_data = {
                'failed_functions': self.failed_functions.copy(),
                'failure_details': self.failure_details.copy(),
                'retry_attempts': self.retry_attempts.copy(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.state_manager.save_progress(ProjectPhase.IMPLEMENTATION, {
                'failure_tracking': failure_data
            })
            
            self.logger.debug(f"Saved failure details for {len(self.failed_functions)} functions")
            
        except Exception as e:
            self.logger.warning(f"Failed to save failure details: {str(e)}")
    
    def _standardize_import_aliases(self, imports: List[str]) -> List[str]:
        """
        Standardize import aliases to avoid naming inconsistencies.
        
        Args:
            imports: List of import statements
            
        Returns:
            List of standardized import statements
        """
        # Standard alias mappings
        standard_aliases = {
            'pandas': 'pd',
            'numpy': 'np',
            'matplotlib.pyplot': 'plt',
            'seaborn': 'sns',
            'tensorflow': 'tf',
            'torch': 'torch',
            'sklearn': 'sklearn',
            'requests': 'requests',
            'json': 'json',
            'os': 'os',
            'sys': 'sys',
            'pathlib': 'pathlib',
            'datetime': 'datetime',
            'typing': 'typing',
            're': 're'
        }
        
        standardized = []
        for import_stmt in imports:
            # Check if this is an import that should be standardized
            for module, alias in standard_aliases.items():
                if f'import {module}' in import_stmt and ' as ' not in import_stmt:
                    # Replace with standardized alias
                    import_stmt = import_stmt.replace(f'import {module}', f'import {module} as {alias}')
                    break
            
            standardized.append(import_stmt)
        
        return standardized
    
    def _extract_required_imports(self, code: str, func_spec: FunctionSpec, 
                                module_info: Optional[Any], specs: Any) -> List[str]:
        """
        Extract required imports from generated code.
        
        Args:
            code: Generated function code
            func_spec: Function specification
            module_info: Module information
            specs: Complete specification set
            
        Returns:
            List of required import statements
        """
        imports = []
        
        # Common patterns to detect imports needed
        import_patterns = [
            (r'\bpd\.', 'import pandas as pd'),
            (r'pd\.DataFrame', 'import pandas as pd'),
            (r'\bnp\.', 'import numpy as np'),
            (r'np\.array', 'import numpy as np'),
            (r'\bplt\.', 'import matplotlib.pyplot as plt'),
            (r'plt\.plot', 'import matplotlib.pyplot as plt'),
            (r'\bsns\.', 'import seaborn as sns'),
            (r'\btf\.', 'import tensorflow as tf'),
            (r'\btorch\.', 'import torch'),
            (r'\brequests\.', 'import requests'),
            (r'\bjson\.', 'import json'),
            (r'json\.dumps', 'import json'),
            (r'json\.loads', 'import json'),
            (r'\bos\.', 'import os'),
            (r'\bsys\.', 'import sys'),
            (r'\bPath\(', 'from pathlib import Path'),
            (r'Path\(', 'from pathlib import Path'),
            (r'\bdatetime\.', 'import datetime'),
            (r'\bList\[', 'from typing import List'),
            (r'\bDict\[', 'from typing import Dict'),
            (r'\bOptional\[', 'from typing import Optional'),
            (r'\bUnion\[', 'from typing import Union'),
            (r'\bTuple\[', 'from typing import Tuple'),
            (r'\bAny\b', 'from typing import Any'),
            (r'\bre\.', 'import re')
        ]
        
        for pattern, import_stmt in import_patterns:
            match = re.search(pattern, code)
            if match:
                if import_stmt not in imports:
                    imports.append(import_stmt)
                    # Debug print removed
        
        return imports
    
    def _parse_file_content(self, content: str) -> Tuple[str, str]:
        """
        Parse file content into imports and functions sections.
        
        Args:
            content: File content to parse
            
        Returns:
            Tuple of (imports_section, functions_section)
        """
        if not content.strip():
            return "", ""
        
        lines = content.split('\n')
        imports_end = 0
        
        # Find where imports end
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not (stripped.startswith('import ') or 
                               stripped.startswith('from ') or 
                               stripped.startswith('#') or
                               stripped.startswith('"""') or
                               stripped.startswith("'''") or
                               stripped == ''):
                imports_end = i
                break
        else:
            imports_end = len(lines)
        
        imports_section = '\n'.join(lines[:imports_end])
        functions_section = '\n'.join(lines[imports_end:])
        
        return imports_section, functions_section
    
    def _merge_imports(self, existing_imports: str, new_imports: List[str]) -> str:
        """
        Merge existing imports with new required imports.
        
        Args:
            existing_imports: Existing imports section
            new_imports: New imports to add
            
        Returns:
            Merged imports section
        """
        if not new_imports:
            return existing_imports
        
        # Parse existing imports
        existing_lines = existing_imports.split('\n') if existing_imports else []
        existing_import_set = set(line.strip() for line in existing_lines if line.strip())
        
        # Add new imports that don't already exist
        for new_import in new_imports:
            if new_import.strip() not in existing_import_set:
                existing_lines.append(new_import)
                existing_import_set.add(new_import.strip())
        
        # Sort imports for consistency
        import_lines = [line for line in existing_lines if line.strip()]
        import_lines.sort()
        
        return '\n'.join(import_lines)
    
    def _update_function_in_content(self, functions_content: str, function_name: str, new_code: str) -> str:
        """
        Update or add a function in the functions section.
        
        Args:
            functions_content: Existing functions content
            function_name: Name of function to update
            new_code: New function code
            
        Returns:
            Updated functions content
        """
        if not functions_content.strip():
            return new_code + '\n'
        
        # Try to find and replace existing function
        lines = functions_content.split('\n')
        function_start = None
        function_end = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith(f'def {function_name}('):
                function_start = i
                # Find end of function
                indent_level = len(line) - len(line.lstrip())
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) <= indent_level:
                        function_end = j
                        break
                else:
                    function_end = len(lines)
                break
        
        if function_start is not None:
            # Replace existing function
            new_lines = lines[:function_start] + [new_code] + lines[function_end:]
            return '\n'.join(new_lines)
        else:
            # Add new function
            return functions_content + '\n\n' + new_code + '\n'
    
    def _combine_file_content(self, imports: str, functions: str) -> str:
        """
        Combine imports and functions into final file content.
        
        Args:
            imports: Imports section
            functions: Functions section
            
        Returns:
            Combined file content
        """
        content_parts = []
        
        if imports.strip():
            content_parts.append(imports.strip())
        
        if functions.strip():
            content_parts.append(functions.strip())
        
        return '\n\n'.join(content_parts) + '\n'
    
    def _save_retry_results(self, result: ImplementationResult, retried_functions: List[str]) -> None:
        """Save retry operation results to state manager."""
        if not self.state_manager:
            return
        
        try:
            retry_data = {
                'retried_functions': retried_functions,
                'retry_results': {
                    'implemented_functions': result.implemented_functions,
                    'failed_functions': result.failed_functions,
                    'success_rate': result.success_rate,
                    'completed_at': result.completed_at.isoformat()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.state_manager.save_progress(ProjectPhase.IMPLEMENTATION, {
                'retry_operation': retry_data
            })
            
            self.logger.debug(f"Saved retry results for {len(retried_functions)} functions")
            
        except Exception as e:
            self.logger.warning(f"Failed to save retry results: {str(e)}")
    
    def _load_failed_function_specs(self, failed_functions: List[str]) -> List[FunctionSpec]:
        """
        Load function specifications for failed functions from state.
        
        Args:
            failed_functions: List of failed function names (module.function format)
            
        Returns:
            List of FunctionSpec objects for retry
        """
        if not self.state_manager:
            return []
        
        try:
            # This would load from saved specification data
            # For now, return empty list as the full state loading is complex
            # In a complete implementation, this would reconstruct FunctionSpec objects
            # from saved state data
            return []
            
        except Exception as e:
            self.logger.warning(f"Failed to load function specs from state: {str(e)}")
            return []
    
    def _create_minimal_specs_for_retry(self, failed_functions: List[str]) -> List[FunctionSpec]:
        """
        Create minimal function specifications for retry when specs can't be loaded.
        
        Args:
            failed_functions: List of failed function names (module.function format)
            
        Returns:
            List of minimal FunctionSpec objects
        """
        specs = []
        
        for func_key in failed_functions:
            try:
                if '.' not in func_key:
                    continue
                
                module_name, func_name = func_key.rsplit('.', 1)
                
                # Create minimal spec (this is a fallback - ideally specs would be loaded from state)
                spec = FunctionSpec(
                    name=func_name,
                    module=module_name,
                    docstring=f"Function {func_name} in module {module_name}.",
                    arguments=[],  # Would need to be loaded from state
                    return_type="Any",  # Would need to be loaded from state
                    implementation_status=ImplementationStatus.FAILED
                )
                
                specs.append(spec)
                
            except Exception as e:
                self.logger.warning(f"Failed to create minimal spec for {func_key}: {str(e)}")
                continue
        
        return specs
    
    def get_failure_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive failure report for user review.
        
        Returns:
            Dictionary containing detailed failure information
        """
        return {
            'failed_functions_count': len(self.failed_functions),
            'failed_functions': self.failed_functions.copy(),
            'failure_details': self.failure_details.copy(),
            'retry_attempts': self.retry_attempts.copy(),
            'total_generated': len(self.generated_code),
            'success_rate': len(self.generated_code) / (len(self.generated_code) + len(self.failed_functions)) if (len(self.generated_code) + len(self.failed_functions)) > 0 else 0.0,
            'report_timestamp': datetime.now().isoformat()
        }
    
    def clear_failure_tracking(self) -> None:
        """Clear all failure tracking data (useful for fresh starts)."""
        self.failed_functions.clear()
        self.failure_details.clear()
        self.retry_attempts.clear()
        self.logger.info("Cleared all failure tracking data")
    
    def get_retry_candidates(self) -> List[str]:
        """
        Get list of functions that are good candidates for retry.
        
        Returns:
            List of function names that might succeed on retry
        """
        candidates = []
        
        for func_key in self.failed_functions:
            if func_key not in self.failure_details:
                candidates.append(func_key)
                continue
            
            failure_info = self.failure_details[func_key]
            retry_count = failure_info.get('retry_count', 0)
            error_type = failure_info.get('error_type', '')
            
            # Consider functions with fewer retries and certain error types as good candidates
            if retry_count < self.max_retries and error_type not in ['CodeValidationError', 'FunctionSpecValidationError']:
                candidates.append(func_key)
        
        return candidates
    
    def _write_function_to_file(self, func_spec: FunctionSpec, code: str, specs: SpecificationSet) -> None:
        """
        Write generated function code to the appropriate module file with proper imports and structure.
        
        Args:
            func_spec: Function specification
            code: Generated code for the function
            specs: Complete specification set for context
        """
        import os
        import re
        from pathlib import Path
        
        # Find the module info
        module_info = None
        if specs.modules:
            for module in specs.modules:
                if module.name == func_spec.module:
                    module_info = module
                    break
        
        # Determine file path
        if module_info and module_info.file_path:
            module_file_path = module_info.file_path
        else:
            # Fallback: create path based on module name (support nested structure)
            if '.' in func_spec.module:
                # Convert dotted module name to path: 'parsers.html_parser' -> 'parsers/html_parser.py'
                module_file_path = func_spec.module.replace('.', '/') + '.py'
            else:
                module_file_path = f"{func_spec.module}.py"
            self.logger.warning(f"Could not find file path for module {func_spec.module}, using fallback: {module_file_path}")
        
        # Get project path - prioritize state manager, then try to infer from context
        project_path = Path.cwd()  # Default fallback
        if hasattr(self, 'state_manager') and self.state_manager and hasattr(self.state_manager, 'project_path'):
            project_path = Path(self.state_manager.project_path)
        elif hasattr(self, 'project_path') and self.project_path:
            project_path = Path(self.project_path)
        else:
            # Try to find project root by looking for .A3 directory
            current = Path.cwd()
            while current != current.parent:
                if (current / '.A3').exists():
                    project_path = current
                    break
                current = current.parent
        
        file_path = Path(module_file_path)
        if not file_path.is_absolute():
            file_path = project_path / file_path
        
        # Create directory structure
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for package structure
        self._create_init_files(file_path.parent, project_path)
        
        # Analyze code to extract required imports
        required_imports = self._extract_required_imports(code, func_spec, module_info, specs)
        
        # Standardize import aliases
        required_imports = self._standardize_import_aliases(required_imports)
        
        # Read existing file content
        existing_content = ""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except Exception:
                existing_content = ""
        
        # Parse existing content
        imports_section, functions_section = self._parse_file_content(existing_content)
        
        # Merge imports
        merged_imports = self._merge_imports(imports_section, required_imports)
        
        # Update or add function
        updated_functions = self._update_function_in_content(functions_section, func_spec.name, code)
        
        # Combine everything
        final_content = self._combine_file_content(merged_imports, updated_functions)
        
        # Write the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            self.logger.info(f"Successfully wrote function {func_spec.name} to {file_path}")
        except Exception as e:
            raise CodeGenerationError(f"Failed to write function {func_spec.name} to file {file_path}: {e}")
    
    def _create_init_files(self, directory: Path, project_root: Path) -> None:
        """Create __init__.py files for proper package structure."""
        current_dir = directory
        while current_dir != project_root and current_dir.parent != current_dir:
            init_file = current_dir / "__init__.py"
            if not init_file.exists():
                try:
                    init_file.touch()
                    self.logger.debug(f"Created __init__.py in {current_dir}")
                except Exception:
                    pass  # Don't fail if we can't create __init__.py
            current_dir = current_dir.parent
    

    
    def _parse_file_content(self, content: str) -> tuple:
        """Parse file content into imports and functions sections."""
        lines = content.split('\n')
        imports_section = []
        functions_section = []
        
        in_imports = True
        for line in lines:
            stripped = line.strip()
            if in_imports and (stripped.startswith('import ') or stripped.startswith('from ') or stripped == '' or stripped.startswith('#')):
                imports_section.append(line)
            else:
                in_imports = False
                functions_section.append(line)
        
        return '\n'.join(imports_section), '\n'.join(functions_section)
    
    def _merge_imports(self, existing_imports: str, new_imports: List[str]) -> str:
        """Merge existing imports with new required imports."""
        existing_lines = [line.strip() for line in existing_imports.split('\n') if line.strip()]
        
        # Add new imports that don't already exist
        for new_import in new_imports:
            if new_import not in existing_lines:
                existing_lines.append(new_import)
        
        # Sort imports (standard library first, then third-party, then local)
        stdlib_imports = []
        thirdparty_imports = []
        local_imports = []
        
        for imp in existing_lines:
            if imp.startswith('from typing') or imp.startswith('import math') or imp.startswith('import os') or imp.startswith('import sys') or imp.startswith('import re') or imp.startswith('import json'):
                stdlib_imports.append(imp)
            elif imp.startswith('import requests') or imp.startswith('from bs4') or imp.startswith('import pandas') or imp.startswith('import numpy'):
                thirdparty_imports.append(imp)
            else:
                local_imports.append(imp)
        
        # Combine with proper spacing
        result = []
        if stdlib_imports:
            result.extend(sorted(stdlib_imports))
            result.append('')
        if thirdparty_imports:
            result.extend(sorted(thirdparty_imports))
            result.append('')
        if local_imports:
            result.extend(sorted(local_imports))
            result.append('')
        
        return '\n'.join(result)
    
    def _update_function_in_content(self, functions_content: str, func_name: str, new_code: str) -> str:
        """Update or add a function in the functions section."""
        import re
        
        function_pattern = rf"^def {func_name}\s*\("
        if re.search(function_pattern, functions_content, re.MULTILINE):
            # Replace existing function
            lines = functions_content.split('\n')
            new_lines = []
            in_function = False
            function_indent = 0
            
            for line in lines:
                if re.match(function_pattern, line.strip()):
                    in_function = True
                    function_indent = len(line) - len(line.lstrip())
                    new_lines.append(new_code)
                    continue
                elif in_function:
                    if line.strip() == "":
                        continue
                    elif len(line) - len(line.lstrip()) <= function_indent and line.strip():
                        in_function = False
                        new_lines.append(line)
                    continue
                else:
                    new_lines.append(line)
            
            return '\n'.join(new_lines)
        else:
            # Add new function
            if functions_content and not functions_content.endswith('\n'):
                functions_content += '\n'
            return functions_content + '\n' + new_code + '\n'
    
    def _combine_file_content(self, imports: str, functions: str) -> str:
        """Combine imports and functions into final file content."""
        result = []
        
        if imports.strip():
            result.append(imports.rstrip())
            result.append('')
        
        if functions.strip():
            result.append(functions.rstrip())
        
        return '\n'.join(result) + '\n'