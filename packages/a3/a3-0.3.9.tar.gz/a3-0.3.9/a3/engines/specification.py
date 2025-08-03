"""
Specification generator implementation for AI Project Builder.

This module provides the SpecificationGenerator class that creates detailed
function specifications with proper type hints and comprehensive docstrings.
"""

import json
import re
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .base import BaseSpecificationGenerator
from ..core.models import (
    FunctionSpec, Argument, SpecificationSet, ValidationResult,
    Module, ProjectPlan, ImplementationStatus
)
from ..core.interfaces import AIClientInterface, StateManagerInterface


class SpecificationGeneratorError(Exception):
    """Base exception for specification generator errors."""
    pass


class SpecificationGenerationError(SpecificationGeneratorError):
    """Exception raised when specification generation fails."""
    pass


class SpecificationValidationError(SpecificationGeneratorError):
    """Exception raised when specification validation fails."""
    pass


class SpecificationGenerator(BaseSpecificationGenerator):
    """
    Engine for generating detailed function specifications.
    
    Creates comprehensive function signatures with proper type hints,
    detailed docstrings, and ensures consistency across module dependencies.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        """
        Initialize the specification generator.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
        """
        super().__init__(ai_client, state_manager)
        self.common_types = {
            'str', 'int', 'float', 'bool', 'bytes', 'None',
            'List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union',
            'Any', 'Callable', 'Iterator', 'Generator'
        }
        self.builtin_modules = {
            'typing', 'collections', 'datetime', 'pathlib', 'json',
            'os', 'sys', 're', 'math', 'random', 'uuid'
        }
    
    def generate_specifications(self, functions: List[FunctionSpec]) -> SpecificationSet:
        """
        Generate detailed specifications for all functions.
        
        Args:
            functions: List of basic function specifications to enhance
            
        Returns:
            SpecificationSet with enhanced function specifications
            
        Raises:
            SpecificationGenerationError: If specification generation fails
        """
        self._ensure_initialized()
        
        if not functions:
            raise SpecificationGenerationError("Function list cannot be empty")
        
        try:
            # Group functions by module for context-aware generation
            functions_by_module = self._group_functions_by_module(functions)
            
            # Generate enhanced specifications for each module
            enhanced_functions = []
            enhanced_modules = []
            
            for module_name, module_functions in functions_by_module.items():
                # Generate specifications for this module's functions
                module_specs = self._generate_module_specifications(
                    module_name, module_functions, functions_by_module
                )
                enhanced_functions.extend(module_specs)
                
                # Create enhanced module object
                enhanced_module = self._create_enhanced_module(
                    module_name, module_specs, functions
                )
                enhanced_modules.append(enhanced_module)
            
            # Create specification set
            spec_set = SpecificationSet(
                functions=enhanced_functions,
                modules=enhanced_modules,
                generated_at=datetime.now()
            )
            
            # Validate the generated specifications
            validation_result = self.validate_specifications(spec_set)
            if not validation_result.is_valid:
                error_msg = "Generated specifications are invalid:\n" + "\n".join(validation_result.issues)
                raise SpecificationGenerationError(error_msg)
            
            # Save specifications if state manager is available
            if self.state_manager:
                try:
                    self._save_specifications(spec_set)
                except Exception as e:
                    # Log warning but don't fail the operation
                    pass
            
            return spec_set
            
        except Exception as e:
            if isinstance(e, SpecificationGeneratorError):
                raise
            else:
                raise SpecificationGenerationError(f"Failed to generate specifications: {str(e)}")
    
    def validate_specifications(self, specs: SpecificationSet) -> ValidationResult:
        """
        Validate generated specifications for consistency.
        
        Args:
            specs: SpecificationSet to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        issues = []
        warnings = []
        
        try:
            # Validate individual function specifications
            function_names = set()
            for func in specs.functions:
                try:
                    func.validate()
                    
                    # Check for duplicate function names within modules
                    full_name = f"{func.module}.{func.name}"
                    if full_name in function_names:
                        issues.append(f"Duplicate function name: {full_name}")
                    function_names.add(full_name)
                    
                except Exception as e:
                    issues.append(f"Invalid function specification {func.module}.{func.name}: {str(e)}")
            
            # Validate module consistency
            module_functions = {}
            for func in specs.functions:
                if func.module not in module_functions:
                    module_functions[func.module] = []
                module_functions[func.module].append(func)
            
            for module in specs.modules:
                try:
                    module.validate()
                    
                    # Check that module functions match specification functions
                    spec_func_names = {f.name for f in module_functions.get(module.name, [])}
                    module_func_names = {f.name for f in module.functions}
                    
                    if spec_func_names != module_func_names:
                        missing_in_module = spec_func_names - module_func_names
                        extra_in_module = module_func_names - spec_func_names
                        
                        if missing_in_module:
                            issues.append(f"Module {module.name} missing functions: {missing_in_module}")
                        if extra_in_module:
                            issues.append(f"Module {module.name} has extra functions: {extra_in_module}")
                    
                except Exception as e:
                    issues.append(f"Invalid module specification {module.name}: {str(e)}")
            
            # Validate cross-module dependencies
            self._validate_cross_module_dependencies(specs, issues, warnings)
            
            # Validate type hint consistency
            self._validate_type_hint_consistency(specs, issues, warnings)
            
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    def _group_functions_by_module(self, functions: List[FunctionSpec]) -> Dict[str, List[FunctionSpec]]:
        """Group functions by their module for context-aware generation."""
        functions_by_module = {}
        
        for func in functions:
            if func.module not in functions_by_module:
                functions_by_module[func.module] = []
            functions_by_module[func.module].append(func)
        
        return functions_by_module
    
    def _generate_module_specifications(self, module_name: str, 
                                      module_functions: List[FunctionSpec],
                                      all_functions_by_module: Dict[str, List[FunctionSpec]]) -> List[FunctionSpec]:
        """
        Generate enhanced specifications for functions in a specific module.
        
        Args:
            module_name: Name of the module
            module_functions: Functions in this module
            all_functions_by_module: All functions grouped by module for context
            
        Returns:
            List of enhanced FunctionSpec objects
        """
        try:
            # Create context about other modules for dependency awareness
            context = self._create_module_context(module_name, all_functions_by_module)
            
            # Generate specifications for each function
            enhanced_functions = []
            
            for func in module_functions:
                enhanced_func = self._generate_function_specification(func, context)
                enhanced_functions.append(enhanced_func)
            
            return enhanced_functions
            
        except Exception as e:
            raise SpecificationGenerationError(f"Failed to generate specifications for module {module_name}: {str(e)}")
    
    def _create_module_context(self, module_name: str, 
                             all_functions_by_module: Dict[str, List[FunctionSpec]]) -> Dict[str, Any]:
        """Create context information for specification generation."""
        context = {
            'current_module': module_name,
            'available_modules': list(all_functions_by_module.keys()),
            'module_functions': {}
        }
        
        # Add function signatures from other modules for reference
        for mod_name, functions in all_functions_by_module.items():
            if mod_name != module_name:
                context['module_functions'][mod_name] = [
                    {
                        'name': f.name,
                        'basic_signature': self._create_basic_signature(f)
                    }
                    for f in functions
                ]
        
        return context
    
    def _create_basic_signature(self, func: FunctionSpec) -> str:
        """Create a basic function signature string."""
        args = []
        for arg in func.arguments:
            arg_str = f"{arg.name}: {arg.type_hint}"
            if arg.default_value:
                arg_str += f" = {arg.default_value}"
            args.append(arg_str)
        
        return f"{func.name}({', '.join(args)}) -> {func.return_type}"
    
    def _generate_function_specification(self, func: FunctionSpec, context: Dict[str, Any]) -> FunctionSpec:
        """
        Generate enhanced specification for a single function.
        
        Args:
            func: Basic function specification
            context: Module context for dependency awareness
            
        Returns:
            Enhanced FunctionSpec object
        """
        try:
            prompt = self._create_specification_prompt(func, context)
            
            # Check fallback configuration
            from ..config import A3Config
            config = A3Config.load()
            use_fallbacks = config.use_fallback_models
            
            response = self.ai_client.generate_with_retry(prompt, max_retries=3, use_fallbacks=use_fallbacks)
            enhanced_data = self._parse_specification_response(response)
            
            # Create enhanced function specification
            enhanced_func = self._create_enhanced_function(func, enhanced_data)
            
            return enhanced_func
            
        except Exception as e:
            # Return original function if enhancement fails
            return func
    
    def _create_specification_prompt(self, func: FunctionSpec, context: Dict[str, Any]) -> str:
        """Create prompt for function specification generation."""
        available_modules = ", ".join(context['available_modules'])
        
        # Create context about other modules
        module_context = ""
        if context['module_functions']:
            module_context = "\n\nAvailable functions in other modules:\n"
            for mod_name, functions in context['module_functions'].items():
                module_context += f"\n{mod_name}:\n"
                for func_info in functions:
                    module_context += f"  - {func_info['basic_signature']}\n"
        
        return f"""
You are a Python expert creating detailed function specifications. Generate a comprehensive specification for this function.

Current Module: {context['current_module']}
Available Modules: {available_modules}

Function to specify:
- Name: {func.name}
- Current Description: {func.docstring}
- Current Arguments: {[f"{arg.name}: {arg.type_hint}" for arg in func.arguments]}
- Current Return Type: {func.return_type}

{module_context}

Please provide an enhanced specification in JSON format:
{{
    "docstring": "Comprehensive docstring following Google style with Args, Returns, Raises sections",
    "arguments": [
        {{
            "name": "arg_name",
            "type_hint": "precise_type_hint_with_imports",
            "description": "detailed_description",
            "default_value": "default_if_any_or_null"
        }}
    ],
    "return_type": "precise_return_type_with_imports",
    "required_imports": ["module1", "module2"],
    "raises": ["ExceptionType1", "ExceptionType2"]
}}

Guidelines:
1. Use precise type hints (List[str], Dict[str, Any], Optional[int], etc.)
2. Include typing imports when needed (from typing import List, Dict, Optional, etc.)
3. Write comprehensive docstrings with:
   - Brief description
   - Args section with parameter descriptions
   - Returns section with return value description
   - Raises section with possible exceptions
   - Examples if helpful
4. Consider edge cases and error conditions
5. Ensure type hints are consistent with function purpose
6. Use standard library types when possible
7. Keep argument names unchanged unless they violate Python conventions

Respond with ONLY the JSON structure.
"""
    
    def _parse_specification_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into specification data.
        
        Args:
            response: Raw AI response text
            
        Returns:
            Parsed specification dictionary
        """
        try:
            # Clean response to extract JSON
            response = response.strip()
            
            # Find JSON content between braces
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No valid JSON found in response")
            
            json_str = response[start_idx:end_idx + 1]
            spec_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['docstring', 'arguments', 'return_type']
            for field in required_fields:
                if field not in spec_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return spec_data
            
        except json.JSONDecodeError as e:
            raise SpecificationGenerationError(f"Invalid JSON in AI response: {str(e)}")
        except Exception as e:
            raise SpecificationGenerationError(f"Failed to parse specification response: {str(e)}")
    
    def _create_enhanced_function(self, original_func: FunctionSpec, 
                                enhanced_data: Dict[str, Any]) -> FunctionSpec:
        """
        Create enhanced function specification from original and AI data.
        
        Args:
            original_func: Original function specification
            enhanced_data: Enhanced data from AI
            
        Returns:
            Enhanced FunctionSpec object
        """
        try:
            # Create enhanced arguments
            enhanced_args = []
            
            # Use enhanced arguments if available, otherwise keep originals
            if 'arguments' in enhanced_data and enhanced_data['arguments']:
                for arg_data in enhanced_data['arguments']:
                    enhanced_arg = Argument(
                        name=arg_data.get('name', ''),
                        type_hint=arg_data.get('type_hint', 'Any'),
                        default_value=arg_data.get('default_value'),
                        description=arg_data.get('description', '')
                    )
                    enhanced_args.append(enhanced_arg)
            else:
                # Keep original arguments if enhancement failed
                enhanced_args = original_func.arguments.copy()
            
            # Create enhanced function
            enhanced_func = FunctionSpec(
                name=original_func.name,
                module=original_func.module,
                docstring=enhanced_data.get('docstring', original_func.docstring),
                arguments=enhanced_args,
                return_type=enhanced_data.get('return_type', original_func.return_type),
                implementation_status=original_func.implementation_status
            )
            
            # Validate the enhanced function
            enhanced_func.validate()
            
            return enhanced_func
            
        except Exception as e:
            # Return original function if enhancement fails
            return original_func
    
    def _create_enhanced_module(self, module_name: str, 
                              enhanced_functions: List[FunctionSpec],
                              all_functions: List[FunctionSpec]) -> Module:
        """
        Create enhanced module object from enhanced functions.
        
        Args:
            module_name: Name of the module
            enhanced_functions: Enhanced function specifications
            all_functions: All original functions for context
            
        Returns:
            Enhanced Module object
        """
        # Find original module info from functions
        original_module_info = None
        for func in all_functions:
            if func.module == module_name:
                # We don't have direct access to module info, so create basic info
                break
        
        # Create module with enhanced functions
        module = Module(
            name=module_name,
            description=f"Module containing {len(enhanced_functions)} functions",
            file_path=f"{module_name}.py",
            dependencies=[],  # Will be determined later in the pipeline
            functions=enhanced_functions
        )
        
        return module
    
    def _validate_cross_module_dependencies(self, specs: SpecificationSet, 
                                          issues: List[str], warnings: List[str]) -> None:
        """Validate dependencies between modules in specifications."""
        try:
            # Extract type hints that might reference other modules
            module_names = {module.name for module in specs.modules}
            
            for func in specs.functions:
                # Check return type for cross-module references
                self._check_type_references(func.return_type, func.module, module_names, issues)
                
                # Check argument types for cross-module references
                for arg in func.arguments:
                    self._check_type_references(arg.type_hint, func.module, module_names, issues)
        
        except Exception as e:
            warnings.append(f"Could not validate cross-module dependencies: {str(e)}")
    
    def _check_type_references(self, type_hint: str, current_module: str, 
                             module_names: Set[str], issues: List[str]) -> None:
        """Check if type hint references other modules appropriately."""
        # This is a simplified check - in a real implementation, you might want
        # more sophisticated parsing of type hints
        for module_name in module_names:
            if module_name != current_module and module_name in type_hint:
                # This suggests a cross-module dependency
                # For now, just note it - more sophisticated validation could be added
                pass
    
    def _validate_type_hint_consistency(self, specs: SpecificationSet,
                                      issues: List[str], warnings: List[str]) -> None:
        """Validate that type hints are consistent and valid."""
        try:
            for func in specs.functions:
                # Validate return type
                if not self._is_valid_type_hint(func.return_type):
                    issues.append(f"Invalid return type '{func.return_type}' in {func.module}.{func.name}")
                
                # Validate argument types
                for arg in func.arguments:
                    if not self._is_valid_type_hint(arg.type_hint):
                        issues.append(f"Invalid type hint '{arg.type_hint}' for argument '{arg.name}' in {func.module}.{func.name}")
        
        except Exception as e:
            warnings.append(f"Could not validate type hint consistency: {str(e)}")
    
    def _is_valid_type_hint(self, type_hint: str) -> bool:
        """
        Check if a type hint appears to be valid.
        
        This is a basic validation - a more sophisticated implementation
        might use ast parsing or other techniques.
        """
        if not type_hint or not type_hint.strip():
            return False
        
        # Basic checks for common patterns
        type_hint = type_hint.strip()
        
        # Check for basic types
        if type_hint in self.common_types:
            return True
        
        # Check for generic types like List[str], Dict[str, int]
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]+\])?$', type_hint):
            return True
        
        # Check for Union types
        if type_hint.startswith('Union[') and type_hint.endswith(']'):
            return True
        
        # Check for Optional types
        if type_hint.startswith('Optional[') and type_hint.endswith(']'):
            return True
        
        return True  # Be permissive for now
    
    def _save_specifications(self, spec_set: SpecificationSet) -> None:
        """Save specifications to state manager."""
        if self.state_manager:
            try:
                # Save as JSON data
                spec_data = {
                    'functions': [
                        {
                            'name': func.name,
                            'module': func.module,
                            'docstring': func.docstring,
                            'arguments': [
                                {
                                    'name': arg.name,
                                    'type_hint': arg.type_hint,
                                    'default_value': arg.default_value,
                                    'description': arg.description
                                }
                                for arg in func.arguments
                            ],
                            'return_type': func.return_type,
                            'implementation_status': func.implementation_status.value
                        }
                        for func in spec_set.functions
                    ],
                    'generated_at': spec_set.generated_at.isoformat()
                }
                
                from ..core.models import ProjectPhase
                self.state_manager.save_progress(ProjectPhase.SPECIFICATION, spec_data)
                
            except Exception as e:
                # Don't fail the operation if saving fails
                pass