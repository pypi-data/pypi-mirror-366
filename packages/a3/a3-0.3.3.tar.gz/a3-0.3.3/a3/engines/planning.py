"""
Planning engine implementation for AI Project Builder.

This module provides the PlanningEngine class that generates comprehensive
project plans from high-level objectives using AI assistance.
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BasePlanningEngine
from ..core.models import (
    ProjectPlan, Module, FunctionSpec, Argument, DependencyGraph,
    ValidationResult, ProjectPlanValidationError, ImplementationStatus,
    ComplexityAnalysis, ComplexityMetrics, EnhancedDependencyGraph
)
from ..core.interfaces import AIClientInterface, StateManagerInterface
from ..managers.dependency import DependencyAnalyzer


class PlanningEngineError(Exception):
    """Base exception for planning engine errors."""
    pass


class PlanGenerationError(PlanningEngineError):
    """Exception raised when plan generation fails."""
    pass


class ModuleBreakdownError(PlanningEngineError):
    """Exception raised when module breakdown fails."""
    pass


class FunctionIdentificationError(PlanningEngineError):
    """Exception raised when function identification fails."""
    pass


class PlanningEngine(BasePlanningEngine):
    """
    Engine for generating comprehensive project plans from objectives.
    
    Uses AI assistance to break down high-level objectives into detailed
    project plans with modules, functions, and dependency relationships.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None,
                 project_path: str = "."):
        """
        Initialize the planning engine.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
            project_path: Path to the project directory
        """
        super().__init__(ai_client, state_manager)
        self.max_modules = 20  # Reasonable limit for project complexity
        self.max_functions_per_module = 15  # Reasonable limit per module
        self.dependency_analyzer = DependencyAnalyzer(project_path)
    
    def initialize(self) -> None:
        """Initialize the planning engine and its dependencies."""
        super().initialize()
        # Initialize the dependency analyzer and its package manager
        self.dependency_analyzer.initialize()
        if hasattr(self.dependency_analyzer, 'package_manager'):
            self.dependency_analyzer.package_manager.initialize()
    
    def generate_plan(self, objective: str) -> ProjectPlan:
        """
        Generate a complete project plan from an objective.
        
        Args:
            objective: High-level project objective description
            
        Returns:
            Complete ProjectPlan with modules and dependencies
            
        Raises:
            PlanGenerationError: If plan generation fails
        """
        self._ensure_initialized()
        
        if not objective or not objective.strip():
            raise PlanGenerationError("Project objective cannot be empty")
        
        objective = objective.strip()
        
        try:
            # Generate initial project structure
            project_structure = self._generate_project_structure(objective)
            
            # Create modules from structure
            modules = self._create_modules_from_structure(project_structure)
            
            # Apply single-responsibility principle to all functions
            all_functions = []
            for module in modules:
                all_functions.extend(module.functions)
            
            refined_functions = self.apply_single_responsibility_principle(all_functions)
            
            # Update modules with refined functions
            modules = self._update_modules_with_refined_functions(modules, refined_functions)
            
            # Generate dependency graph
            dependency_graph = self._create_dependency_graph(modules)
            
            # Generate enhanced dependency graph
            enhanced_dependency_graph = self._create_enhanced_dependency_graph(modules)
            
            # Estimate total functions
            estimated_functions = sum(len(module.functions) for module in modules)
            
            # Create and validate project plan
            plan = ProjectPlan(
                objective=objective,
                modules=modules,
                dependency_graph=dependency_graph,
                enhanced_dependency_graph=enhanced_dependency_graph,
                estimated_functions=estimated_functions,
                created_at=datetime.now()
            )
            
            # Validate the generated plan
            plan.validate()
            
            # Save plan if state manager is available
            if self.state_manager:
                try:
                    self.state_manager.save_project_plan(plan)
                except Exception as e:
                    # Log warning but don't fail the operation
                    pass
            
            return plan
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to generate project plan: {str(e)}")
    
    def create_module_breakdown(self, plan: ProjectPlan) -> List[Module]:
        """
        Break down the plan into detailed modules.
        
        Args:
            plan: Existing project plan to enhance
            
        Returns:
            List of detailed Module objects
            
        Raises:
            ModuleBreakdownError: If module breakdown fails
        """
        self._ensure_initialized()
        
        if not plan or not plan.modules:
            raise ModuleBreakdownError("Project plan must contain modules")
        
        try:
            enhanced_modules = []
            
            for module in plan.modules:
                # Enhance each module with more detailed information
                enhanced_module = self._enhance_module_details(module, plan.objective)
                enhanced_modules.append(enhanced_module)
            
            return enhanced_modules
            
        except Exception as e:
            raise ModuleBreakdownError(f"Failed to create module breakdown: {str(e)}")
    
    def identify_functions(self, modules: List[Module]) -> List[FunctionSpec]:
        """
        Identify all functions needed across modules.
        
        Args:
            modules: List of modules to analyze
            
        Returns:
            List of all FunctionSpec objects across modules
            
        Raises:
            FunctionIdentificationError: If function identification fails
        """
        self._ensure_initialized()
        
        if not modules:
            raise FunctionIdentificationError("Module list cannot be empty")
        
        try:
            all_functions = []
            
            for module in modules:
                # Extract functions from each module
                for function in module.functions:
                    # Ensure function module matches
                    if function.module != module.name:
                        function.module = module.name
                    all_functions.append(function)
            
            # Validate function consistency across modules
            self._validate_function_consistency(all_functions, modules)
            
            return all_functions
            
        except Exception as e:
            raise FunctionIdentificationError(f"Failed to identify functions: {str(e)}")
    
    def _generate_project_structure(self, objective: str) -> Dict[str, Any]:
        """
        Generate initial project structure using AI.
        
        Args:
            objective: Project objective description
            
        Returns:
            Dictionary containing project structure information
        """
        prompt = self._create_structure_prompt(objective)
        
        try:
            response = self.ai_client.generate_with_retry(prompt, max_retries=3)
            structure = self._parse_structure_response(response)
            return structure
            
        except Exception as e:
            raise PlanGenerationError(f"Failed to generate project structure: {str(e)}")
    
    def _create_structure_prompt(self, objective: str) -> str:
        """Create prompt for project structure generation."""
        return f"""
You are an expert software architect. Given a project objective, create a detailed project structure.

Project Objective: {objective}

Please provide a JSON response with the following structure:
{{
    "project_name": "descriptive_project_name",
    "description": "Brief project description",
    "modules": [
        {{
            "name": "module_name",
            "description": "Module purpose and functionality",
            "file_path": "path/to/module.py",
            "dependencies": ["other_module_names"],
            "functions": [
                {{
                    "name": "function_name",
                    "description": "Function purpose",
                    "arguments": [
                        {{
                            "name": "arg_name",
                            "type": "str",
                            "description": "Argument purpose",
                            "default": null
                        }}
                    ],
                    "return_type": "return_type_hint"
                }}
            ]
        }}
    ]
}}

Guidelines:
1. Create 3-8 modules maximum for maintainability
2. Each module should have 2-10 functions maximum
3. Use clear, descriptive names following Python conventions
4. Support nested directory structures (e.g., "src/parser/html.py", "utils/validators.py")
5. For nested modules, use dotted names in dependencies (e.g., "parser.html", "utils.validators")
6. Ensure dependencies form a valid DAG (no circular dependencies)
7. Include proper type hints for all arguments and returns
8. Make functions focused and single-purpose
9. Consider common software patterns (MVC, repository, etc.)
10. Create logical package hierarchies when appropriate

Respond with ONLY the JSON structure, no additional text.
"""
    
    def _parse_structure_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into project structure.
        
        Args:
            response: Raw AI response text
            
        Returns:
            Parsed project structure dictionary
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
            structure = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['modules']
            for field in required_fields:
                if field not in structure:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate modules structure
            if not isinstance(structure['modules'], list):
                raise ValueError("Modules must be a list")
            
            if len(structure['modules']) == 0:
                raise ValueError("At least one module is required")
            
            if len(structure['modules']) > self.max_modules:
                raise ValueError(f"Too many modules: {len(structure['modules'])} > {self.max_modules}")
            
            return structure
            
        except json.JSONDecodeError as e:
            raise PlanGenerationError(f"Invalid JSON in AI response: {str(e)}")
        except Exception as e:
            raise PlanGenerationError(f"Failed to parse structure response: {str(e)}")
    
    def _create_modules_from_structure(self, structure: Dict[str, Any]) -> List[Module]:
        """
        Create Module objects from parsed structure.
        
        Args:
            structure: Parsed project structure
            
        Returns:
            List of Module objects
        """
        modules = []
        
        for module_data in structure['modules']:
            try:
                # Handle nested module names and file paths first
                module_name = module_data['name']
                file_path = module_data.get('file_path', f"{module_name}.py")
                
                # If file_path suggests a nested structure, adjust module name accordingly
                if '/' in file_path and not '.' in module_name:
                    # Convert file path to dotted module name
                    # e.g., "src/parsers/html_parser.py" -> "parsers.html_parser"
                    path_parts = file_path.replace('.py', '').split('/')
                    # Skip common prefixes like 'src'
                    if path_parts[0] in ['src', 'lib', 'app']:
                        path_parts = path_parts[1:]
                    if len(path_parts) > 1:
                        module_name = '.'.join(path_parts)
                
                # Create function specifications
                functions = []
                for func_data in module_data.get('functions', []):
                    # Create arguments
                    arguments = []
                    for arg_data in func_data.get('arguments', []):
                        argument = Argument(
                            name=arg_data['name'],
                            type_hint=arg_data['type'],
                            default_value=arg_data.get('default'),
                            description=arg_data.get('description', '')
                        )
                        arguments.append(argument)
                    
                    # Create function spec (use the processed module name)
                    function = FunctionSpec(
                        name=func_data['name'],
                        module=module_name,  # Use the processed module name
                        docstring=func_data.get('description', ''),
                        arguments=arguments,
                        return_type=func_data.get('return_type', 'None'),
                        implementation_status=ImplementationStatus.NOT_STARTED
                    )
                    functions.append(function)
                
                # Validate function count
                if len(functions) > self.max_functions_per_module:
                    raise ValueError(f"Too many functions in module {module_data['name']}: {len(functions)} > {self.max_functions_per_module}")
                
                # Create module
                module = Module(
                    name=module_name,
                    description=module_data.get('description', ''),
                    file_path=file_path,
                    dependencies=module_data.get('dependencies', []),
                    functions=functions
                )
                
                # Validate module
                module.validate()
                modules.append(module)
                
            except Exception as e:
                raise PlanGenerationError(f"Failed to create module {module_data.get('name', 'unknown')}: {str(e)}")
        
        return modules
    
    def _create_dependency_graph(self, modules: List[Module]) -> DependencyGraph:
        """
        Create dependency graph from modules using dependency analyzer.
        
        Args:
            modules: List of modules with dependencies
            
        Returns:
            DependencyGraph object
            
        Raises:
            PlanGenerationError: If dependency analysis fails
        """
        try:
            # Use dependency analyzer to create and validate the graph
            graph = self.dependency_analyzer.create_dependency_graph(modules)
            
            # Perform comprehensive dependency analysis
            analysis_result = self.dependency_analyzer.analyze_dependencies(modules)
            
            if not analysis_result.is_valid:
                error_msg = "Dependency analysis failed:\n" + "\n".join(analysis_result.issues)
                raise PlanGenerationError(error_msg)
            
            # Log warnings if any
            if analysis_result.warnings:
                # In a real implementation, you might want to log these warnings
                pass
            
            return graph
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to create dependency graph: {str(e)}")
    
    def _create_enhanced_dependency_graph(self, modules: List[Module]) -> EnhancedDependencyGraph:
        """
        Create enhanced dependency graph with function-level dependencies.
        
        Args:
            modules: List of modules with dependencies
            
        Returns:
            EnhancedDependencyGraph object
            
        Raises:
            PlanGenerationError: If enhanced dependency analysis fails
        """
        try:
            # Use dependency analyzer to create enhanced graph
            enhanced_graph = self.dependency_analyzer.build_enhanced_dependency_graph(modules)
            
            # Check for function-level cycles
            if enhanced_graph.has_function_cycles():
                # Log warning but create a simplified graph without function dependencies
                # This prevents false positive circular dependency errors during planning
                simplified_graph = EnhancedDependencyGraph()
                
                # Add all functions to the graph
                for module in modules:
                    for function in module.functions:
                        simplified_graph.add_function(function.name, module.name)
                
                # Add only module-level dependencies (which are already validated)
                for module in modules:
                    for dep_module in module.dependencies:
                        if dep_module != module.name:  # Avoid self-dependencies
                            simplified_graph.module_edges.append((module.name, dep_module))
                
                return simplified_graph
            
            return enhanced_graph
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to create enhanced dependency graph: {str(e)}")
    
    def _enhance_module_details(self, module: Module, objective: str) -> Module:
        """
        Enhance module with more detailed information using AI.
        
        Args:
            module: Module to enhance
            objective: Original project objective for context
            
        Returns:
            Enhanced Module object
        """
        try:
            # Create prompt for module enhancement
            prompt = f"""
You are enhancing a module for a project with objective: {objective}

Current module:
- Name: {module.name}
- Description: {module.description}
- Dependencies: {module.dependencies}
- Functions: {[f.name for f in module.functions]}

Please provide enhanced details for this module's functions in JSON format:
{{
    "functions": [
        {{
            "name": "existing_function_name",
            "enhanced_docstring": "Detailed docstring with purpose, parameters, returns, and examples",
            "arguments": [
                {{
                    "name": "arg_name",
                    "type_hint": "precise_type_hint",
                    "description": "detailed_argument_description",
                    "default_value": "default_if_any"
                }}
            ],
            "return_type": "precise_return_type"
        }}
    ]
}}

Guidelines:
1. Provide comprehensive docstrings following Google/NumPy style
2. Use precise type hints (List[str], Dict[str, Any], Optional[int], etc.)
3. Include detailed argument descriptions
4. Ensure return types are accurate
5. Keep existing function names unchanged

Respond with ONLY the JSON structure.
"""
            
            response = self.ai_client.generate_with_retry(prompt, max_retries=2)
            enhanced_data = self._parse_enhancement_response(response)
            
            # Update module functions with enhanced details
            enhanced_functions = []
            for func in module.functions:
                enhanced_func_data = next(
                    (f for f in enhanced_data['functions'] if f['name'] == func.name),
                    None
                )
                
                if enhanced_func_data:
                    # Update with enhanced details
                    enhanced_args = []
                    for arg_data in enhanced_func_data.get('arguments', []):
                        enhanced_arg = Argument(
                            name=arg_data['name'],
                            type_hint=arg_data['type_hint'],
                            default_value=arg_data.get('default_value'),
                            description=arg_data.get('description', '')
                        )
                        enhanced_args.append(enhanced_arg)
                    
                    enhanced_func = FunctionSpec(
                        name=func.name,
                        module=func.module,
                        docstring=enhanced_func_data.get('enhanced_docstring', func.docstring),
                        arguments=enhanced_args,
                        return_type=enhanced_func_data.get('return_type', func.return_type),
                        implementation_status=func.implementation_status
                    )
                    enhanced_functions.append(enhanced_func)
                else:
                    # Keep original if enhancement failed
                    enhanced_functions.append(func)
            
            # Create enhanced module
            enhanced_module = Module(
                name=module.name,
                description=module.description,
                file_path=module.file_path,
                dependencies=module.dependencies,
                functions=enhanced_functions
            )
            
            return enhanced_module
            
        except Exception:
            # Return original module if enhancement fails
            return module
    
    def _parse_enhancement_response(self, response: str) -> Dict[str, Any]:
        """Parse AI enhancement response."""
        try:
            response = response.strip()
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No valid JSON found")
            
            json_str = response[start_idx:end_idx + 1]
            return json.loads(json_str)
            
        except Exception:
            return {'functions': []}
    
    def _validate_function_consistency(self, functions: List[FunctionSpec], modules: List[Module]) -> None:
        """
        Validate function consistency across modules.
        
        Args:
            functions: All functions to validate
            modules: All modules for context
        """
        module_names = {module.name for module in modules}
        function_names = set()
        
        for function in functions:
            # Check for duplicate function names
            full_name = f"{function.module}.{function.name}"
            if full_name in function_names:
                raise FunctionIdentificationError(f"Duplicate function: {full_name}")
            function_names.add(full_name)
            
            # Check module exists
            if function.module not in module_names:
                raise FunctionIdentificationError(f"Function {function.name} references non-existent module {function.module}")
            
            # Validate function spec
            try:
                function.validate()
            except Exception as e:
                raise FunctionIdentificationError(f"Invalid function {full_name}: {str(e)}")    

    def analyze_plan_dependencies(self, plan: ProjectPlan) -> ValidationResult:
        """
        Analyze dependencies in a project plan.
        
        Args:
            plan: ProjectPlan to analyze
            
        Returns:
            ValidationResult with dependency analysis results
        """
        if not plan or not plan.modules:
            return ValidationResult(
                is_valid=False,
                issues=["Project plan must contain modules for dependency analysis"],
                warnings=[]
            )
        
        return self.dependency_analyzer.analyze_dependencies(plan.modules)
    
    def detect_circular_dependencies(self, plan: ProjectPlan) -> List[List[str]]:
        """
        Detect circular dependencies in a project plan.
        
        Args:
            plan: ProjectPlan to analyze
            
        Returns:
            List of circular dependency chains
        """
        if not plan or not plan.modules:
            return []
        
        return self.dependency_analyzer.detect_circular_dependencies(plan.modules)
    
    def get_module_build_order(self, plan: ProjectPlan) -> List[str]:
        """
        Get optimal build order for modules in a project plan.
        
        Args:
            plan: ProjectPlan to analyze
            
        Returns:
            List of module names in build order
            
        Raises:
            PlanGenerationError: If circular dependencies prevent ordering
        """
        if not plan or not plan.modules:
            return []
        
        try:
            return self.dependency_analyzer.get_build_order(plan.modules)
        except Exception as e:
            raise PlanGenerationError(f"Failed to determine build order: {str(e)}")
    
    def get_dependency_map(self, plan: ProjectPlan) -> Dict[str, List[str]]:
        """
        Get dependency mapping for all modules in a project plan.
        
        Args:
            plan: ProjectPlan to analyze
            
        Returns:
            Dictionary mapping module names to their dependencies
        """
        if not plan or not plan.modules:
            return {}
        
        dep_map = self.dependency_analyzer.get_dependency_map(plan.modules)
        return {k: list(v) for k, v in dep_map.items()}
    
    def apply_single_responsibility_principle(self, functions: List[FunctionSpec]) -> List[FunctionSpec]:
        """
        Apply single-responsibility principle to function specifications.
        
        Args:
            functions: List of function specifications to analyze
            
        Returns:
            List of refined function specifications with single-responsibility applied
            
        Raises:
            PlanGenerationError: If analysis fails
        """
        self._ensure_initialized()
        
        if not functions:
            return functions
        
        try:
            refined_functions = []
            
            for function in functions:
                # Analyze function complexity
                complexity_analysis = self.validate_function_complexity(function)
                
                if complexity_analysis.needs_refactoring:
                    # Use breakdown suggestions if available
                    if complexity_analysis.breakdown_suggestions:
                        refined_functions.extend(complexity_analysis.breakdown_suggestions)
                    else:
                        # Keep original function but mark for manual review
                        refined_functions.append(function)
                else:
                    refined_functions.append(function)
            
            return refined_functions
            
        except Exception as e:
            raise PlanGenerationError(f"Failed to apply single-responsibility principle: {str(e)}")
    
    def validate_function_complexity(self, function_spec: FunctionSpec) -> ComplexityAnalysis:
        """
        Validate function complexity and single-responsibility adherence.
        
        Args:
            function_spec: Function specification to analyze
            
        Returns:
            ComplexityAnalysis with detailed analysis results
            
        Raises:
            PlanGenerationError: If complexity analysis fails
        """
        self._ensure_initialized()
        
        if not function_spec:
            raise PlanGenerationError("Function specification is required for complexity analysis")
        
        try:
            # Analyze function description and arguments for complexity indicators
            complexity_metrics = self._analyze_function_complexity(function_spec)
            
            # Check for single-responsibility violations
            violations = self._check_single_responsibility_violations(function_spec)
            
            # Generate refactoring suggestions
            refactoring_suggestions = self._generate_refactoring_suggestions(function_spec, violations)
            
            # Generate breakdown suggestions if needed
            breakdown_suggestions = []
            if len(violations) > 0 or complexity_metrics.single_responsibility_score < 0.7:
                breakdown_suggestions = self._generate_breakdown_suggestions(function_spec, violations)
            
            # Calculate overall complexity score
            complexity_score = self._calculate_complexity_score(complexity_metrics, violations)
            
            # Determine if refactoring is needed
            needs_refactoring = (
                complexity_score > 0.6 or
                len(violations) > 2 or
                complexity_metrics.single_responsibility_score < 0.5
            )
            
            analysis = ComplexityAnalysis(
                function_spec=function_spec,
                complexity_metrics=complexity_metrics,
                single_responsibility_violations=violations,
                refactoring_suggestions=refactoring_suggestions,
                breakdown_suggestions=breakdown_suggestions,
                complexity_score=complexity_score,
                needs_refactoring=needs_refactoring
            )
            
            analysis.validate()
            return analysis
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to validate function complexity: {str(e)}")
    
    def _analyze_function_complexity(self, function_spec: FunctionSpec) -> ComplexityMetrics:
        """
        Analyze function complexity based on specification.
        
        Args:
            function_spec: Function specification to analyze
            
        Returns:
            ComplexityMetrics with calculated metrics
        """
        # Estimate cyclomatic complexity based on function description
        cyclomatic_complexity = self._estimate_cyclomatic_complexity(function_spec)
        
        # Estimate cognitive complexity
        cognitive_complexity = self._estimate_cognitive_complexity(function_spec)
        
        # Estimate lines of code
        lines_of_code = self._estimate_lines_of_code(function_spec)
        
        # Calculate single-responsibility score
        single_responsibility_score = self._calculate_single_responsibility_score(function_spec)
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cognitive_complexity,
            lines_of_code=lines_of_code,
            single_responsibility_score=single_responsibility_score
        )
    
    def _estimate_cyclomatic_complexity(self, function_spec: FunctionSpec) -> int:
        """Estimate cyclomatic complexity from function specification."""
        complexity = 1  # Base complexity
        
        # Analyze docstring for complexity indicators
        docstring = function_spec.docstring.lower()
        
        # Count conditional keywords
        conditional_keywords = ['if', 'elif', 'else', 'while', 'for', 'try', 'except', 'case', 'switch']
        for keyword in conditional_keywords:
            complexity += docstring.count(keyword)
        
        # Count logical operators
        logical_operators = [' and ', ' or ', ' not ']
        for operator in logical_operators:
            complexity += docstring.count(operator)
        
        # Adjust based on number of arguments (more args often mean more complexity)
        if len(function_spec.arguments) > 5:
            complexity += 2
        elif len(function_spec.arguments) > 3:
            complexity += 1
        
        return min(complexity, 20)  # Cap at reasonable maximum
    
    def _estimate_cognitive_complexity(self, function_spec: FunctionSpec) -> int:
        """Estimate cognitive complexity from function specification."""
        complexity = 0
        
        docstring = function_spec.docstring.lower()
        
        # Nested structures add more cognitive load
        nesting_indicators = ['nested', 'loop', 'recursive', 'callback', 'chain']
        for indicator in nesting_indicators:
            if indicator in docstring:
                complexity += 3
        
        # Multiple responsibilities increase cognitive load
        responsibility_indicators = [' and ', ' also ', ' additionally', ' furthermore', ' moreover']
        for indicator in responsibility_indicators:
            complexity += docstring.count(indicator) * 2
        
        # Complex return types suggest cognitive complexity
        if 'dict' in function_spec.return_type.lower() or 'tuple' in function_spec.return_type.lower():
            complexity += 1
        
        return min(complexity, 15)  # Cap at reasonable maximum
    
    def _estimate_lines_of_code(self, function_spec: FunctionSpec) -> int:
        """Estimate lines of code from function specification."""
        base_lines = 3  # Function signature, docstring, basic return
        
        # Add lines based on arguments (validation, processing)
        base_lines += len(function_spec.arguments)
        
        # Add lines based on docstring complexity
        docstring_words = len(function_spec.docstring.split())
        if docstring_words > 50:
            base_lines += 10
        elif docstring_words > 20:
            base_lines += 5
        
        # Add lines based on complexity indicators
        docstring = function_spec.docstring.lower()
        complexity_indicators = ['validate', 'process', 'transform', 'calculate', 'analyze', 'generate']
        for indicator in complexity_indicators:
            if indicator in docstring:
                base_lines += 3
        
        return min(base_lines, 100)  # Cap at reasonable maximum
    
    def _calculate_single_responsibility_score(self, function_spec: FunctionSpec) -> float:
        """Calculate single-responsibility adherence score (0-1, higher is better)."""
        score = 1.0
        
        docstring = function_spec.docstring.lower()
        
        # Penalize multiple action verbs
        action_verbs = ['create', 'update', 'delete', 'validate', 'process', 'transform', 
                       'calculate', 'analyze', 'generate', 'parse', 'format', 'convert']
        verb_count = sum(1 for verb in action_verbs if verb in docstring)
        if verb_count > 1:
            score -= (verb_count - 1) * 0.2
        
        # Penalize conjunction words indicating multiple responsibilities
        conjunctions = [' and ', ' also ', ' additionally', ' furthermore', ' moreover', ' plus']
        conjunction_count = sum(docstring.count(conj) for conj in conjunctions)
        score -= conjunction_count * 0.15
        
        # Penalize long function names (often indicate multiple responsibilities)
        if len(function_spec.name) > 25:
            score -= 0.1
        
        # Penalize too many arguments (often indicate multiple responsibilities)
        if len(function_spec.arguments) > 5:
            score -= (len(function_spec.arguments) - 5) * 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_single_responsibility_violations(self, function_spec: FunctionSpec) -> List[str]:
        """Check for single-responsibility principle violations."""
        violations = []
        
        docstring = function_spec.docstring.lower()
        
        # Check for multiple action verbs
        action_verbs = ['create', 'update', 'delete', 'validate', 'process', 'transform', 
                       'calculate', 'analyze', 'generate', 'parse', 'format', 'convert']
        found_verbs = [verb for verb in action_verbs if verb in docstring]
        if len(found_verbs) > 1:
            violations.append(f"Function performs multiple actions: {', '.join(found_verbs)}")
        
        # Check for conjunction words
        conjunctions = [' and ', ' also ', ' additionally', ' furthermore', ' moreover']
        found_conjunctions = [conj.strip() for conj in conjunctions if conj in docstring]
        if found_conjunctions:
            violations.append(f"Function description contains conjunctions indicating multiple responsibilities: {', '.join(found_conjunctions)}")
        
        # Check function name for multiple concepts
        name_parts = function_spec.name.split('_')
        if len(name_parts) > 4:
            violations.append(f"Function name is complex with {len(name_parts)} parts, suggesting multiple responsibilities")
        
        # Check for too many arguments
        if len(function_spec.arguments) > 6:
            violations.append(f"Function has {len(function_spec.arguments)} arguments, which may indicate multiple responsibilities")
        
        # Check for mixed abstraction levels in arguments
        arg_types = [arg.type_hint.lower() for arg in function_spec.arguments]
        primitive_types = ['str', 'int', 'float', 'bool', 'list', 'dict']
        has_primitives = any(ptype in ' '.join(arg_types) for ptype in primitive_types)
        has_complex_types = any(atype not in primitive_types and atype not in ['str', 'int', 'float', 'bool'] 
                               for atype in arg_types if atype)
        
        if has_primitives and has_complex_types:
            violations.append("Function mixes primitive and complex argument types, suggesting multiple abstraction levels")
        
        return violations
    
    def _generate_refactoring_suggestions(self, function_spec: FunctionSpec, violations: List[str]) -> List[str]:
        """Generate refactoring suggestions based on violations."""
        suggestions = []
        
        if not violations:
            return suggestions
        
        # Suggest breaking down based on violations
        for violation in violations:
            if "multiple actions" in violation:
                suggestions.append("Consider breaking this function into separate functions for each action")
            elif "conjunctions" in violation:
                suggestions.append("Split function responsibilities indicated by 'and', 'also', etc.")
            elif "complex" in violation and "name" in violation:
                suggestions.append("Simplify function name by focusing on a single responsibility")
            elif "arguments" in violation:
                suggestions.append("Reduce number of arguments by grouping related parameters or splitting responsibilities")
            elif "abstraction levels" in violation:
                suggestions.append("Separate high-level orchestration from low-level data manipulation")
        
        # General suggestions based on complexity
        if len(violations) > 2:
            suggestions.append("This function appears to have multiple responsibilities and should be refactored into smaller, focused functions")
        
        return suggestions
    
    def _generate_breakdown_suggestions(self, function_spec: FunctionSpec, violations: List[str]) -> List[FunctionSpec]:
        """Generate breakdown suggestions using AI assistance."""
        if not violations:
            return []
        
        try:
            prompt = self._create_breakdown_prompt(function_spec, violations)
            response = self.ai_client.generate_with_retry(prompt, max_retries=2)
            breakdown_functions = self._parse_breakdown_response(response, function_spec.module)
            return breakdown_functions
        except Exception:
            # Return empty list if AI generation fails
            return []
    
    def _create_breakdown_prompt(self, function_spec: FunctionSpec, violations: List[str]) -> str:
        """Create prompt for AI-powered function breakdown."""
        return f"""
You are a software architect focused on applying the single-responsibility principle. 
Analyze the following function specification and break it down into smaller, focused functions.

Function to analyze:
- Name: {function_spec.name}
- Module: {function_spec.module}
- Description: {function_spec.docstring}
- Arguments: {[f"{arg.name}: {arg.type_hint}" for arg in function_spec.arguments]}
- Return Type: {function_spec.return_type}

Identified violations:
{chr(10).join(f"- {violation}" for violation in violations)}

Please provide a JSON response with breakdown suggestions:
{{
    "breakdown_functions": [
        {{
            "name": "focused_function_name",
            "description": "Single responsibility description",
            "arguments": [
                {{
                    "name": "arg_name",
                    "type": "type_hint",
                    "description": "argument description"
                }}
            ],
            "return_type": "return_type"
        }}
    ],
    "orchestrator_function": {{
        "name": "orchestrator_name",
        "description": "Coordinates the breakdown functions",
        "arguments": [
            {{
                "name": "arg_name", 
                "type": "type_hint",
                "description": "argument description"
            }}
        ],
        "return_type": "return_type"
    }}
}}

Guidelines:
1. Each breakdown function should have a single, clear responsibility
2. Function names should be descriptive and focused
3. Minimize coupling between breakdown functions
4. The orchestrator function should coordinate the breakdown functions
5. Preserve the original function's interface in the orchestrator
6. Use clear, descriptive names following Python conventions

Respond with ONLY the JSON structure.
"""
    
    def _parse_breakdown_response(self, response: str, module_name: str) -> List[FunctionSpec]:
        """Parse AI breakdown response into function specifications."""
        try:
            response = response.strip()
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                return []
            
            json_str = response[start_idx:end_idx + 1]
            breakdown_data = json.loads(json_str)
            
            functions = []
            
            # Parse breakdown functions
            for func_data in breakdown_data.get('breakdown_functions', []):
                arguments = []
                for arg_data in func_data.get('arguments', []):
                    argument = Argument(
                        name=arg_data['name'],
                        type_hint=arg_data['type'],
                        description=arg_data.get('description', '')
                    )
                    arguments.append(argument)
                
                function = FunctionSpec(
                    name=func_data['name'],
                    module=module_name,
                    docstring=func_data['description'],
                    arguments=arguments,
                    return_type=func_data.get('return_type', 'None'),
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
                functions.append(function)
            
            # Parse orchestrator function
            orchestrator_data = breakdown_data.get('orchestrator_function')
            if orchestrator_data:
                arguments = []
                for arg_data in orchestrator_data.get('arguments', []):
                    argument = Argument(
                        name=arg_data['name'],
                        type_hint=arg_data['type'],
                        description=arg_data.get('description', '')
                    )
                    arguments.append(argument)
                
                orchestrator = FunctionSpec(
                    name=orchestrator_data['name'],
                    module=module_name,
                    docstring=orchestrator_data['description'],
                    arguments=arguments,
                    return_type=orchestrator_data.get('return_type', 'None'),
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
                functions.append(orchestrator)
            
            return functions
            
        except Exception:
            return []
    
    def _calculate_complexity_score(self, metrics: ComplexityMetrics, violations: List[str]) -> float:
        """Calculate overall complexity score (0-1, lower is better)."""
        # Normalize individual metrics
        cyclomatic_score = min(metrics.cyclomatic_complexity / 10.0, 1.0)
        cognitive_score = min(metrics.cognitive_complexity / 15.0, 1.0)
        loc_score = min(metrics.lines_of_code / 50.0, 1.0)
        
        # Single responsibility score (invert since higher is better)
        sr_score = 1.0 - metrics.single_responsibility_score
        
        # Violation penalty
        violation_score = min(len(violations) / 5.0, 1.0)
        
        # Weighted average
        complexity_score = (
            cyclomatic_score * 0.25 +
            cognitive_score * 0.25 +
            loc_score * 0.15 +
            sr_score * 0.25 +
            violation_score * 0.10
        )
        
        return min(1.0, complexity_score)
    
    def _update_modules_with_refined_functions(self, modules: List[Module], refined_functions: List[FunctionSpec]) -> List[Module]:
        """
        Update modules with refined functions after single-responsibility analysis.
        
        Args:
            modules: Original modules
            refined_functions: Functions after single-responsibility refinement
            
        Returns:
            Updated modules with refined functions
        """
        # Group refined functions by module
        functions_by_module = {}
        for func in refined_functions:
            if func.module not in functions_by_module:
                functions_by_module[func.module] = []
            functions_by_module[func.module].append(func)
        
        # Update modules with refined functions
        updated_modules = []
        for module in modules:
            updated_functions = functions_by_module.get(module.name, module.functions)
            
            updated_module = Module(
                name=module.name,
                description=module.description,
                file_path=module.file_path,
                dependencies=module.dependencies,
                functions=updated_functions
            )
            updated_modules.append(updated_module)
        
        return updated_modules
    
    def validate_implementation_against_single_responsibility(self, function_spec: FunctionSpec, implementation_code: str) -> ComplexityAnalysis:
        """
        Validate an implementation against single-responsibility principle.
        
        Args:
            function_spec: Original function specification
            implementation_code: The actual implementation code
            
        Returns:
            ComplexityAnalysis with validation results
            
        Raises:
            PlanGenerationError: If validation fails
        """
        self._ensure_initialized()
        
        if not function_spec:
            raise PlanGenerationError("Function specification is required for implementation validation")
        
        if not implementation_code or not implementation_code.strip():
            raise PlanGenerationError("Implementation code is required for validation")
        
        try:
            # Analyze the implementation code for complexity
            implementation_metrics = self._analyze_implementation_complexity(implementation_code)
            
            # Check for single-responsibility violations in implementation
            implementation_violations = self._check_implementation_violations(implementation_code, function_spec)
            
            # Generate refactoring suggestions based on implementation
            refactoring_suggestions = self._generate_implementation_refactoring_suggestions(
                implementation_code, implementation_violations
            )
            
            # Calculate complexity score for implementation
            complexity_score = self._calculate_implementation_complexity_score(
                implementation_metrics, implementation_violations
            )
            
            # Determine if refactoring is needed
            needs_refactoring = (
                complexity_score > 0.7 or
                len(implementation_violations) > 2 or
                implementation_metrics.single_responsibility_score < 0.6
            )
            
            analysis = ComplexityAnalysis(
                function_spec=function_spec,
                complexity_metrics=implementation_metrics,
                single_responsibility_violations=implementation_violations,
                refactoring_suggestions=refactoring_suggestions,
                breakdown_suggestions=[],  # Not applicable for implementation validation
                complexity_score=complexity_score,
                needs_refactoring=needs_refactoring
            )
            
            analysis.validate()
            return analysis
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to validate implementation: {str(e)}")
    
    def create_granular_function_plan(self, objective: str, max_function_complexity: float = 0.5) -> List[FunctionSpec]:
        """
        Create a granular function plan with clear separation of concerns.
        
        Args:
            objective: High-level objective to break down
            max_function_complexity: Maximum allowed complexity score (0-1)
            
        Returns:
            List of granular function specifications
            
        Raises:
            PlanGenerationError: If plan creation fails
        """
        self._ensure_initialized()
        
        if not objective or not objective.strip():
            raise PlanGenerationError("Objective cannot be empty")
        
        if max_function_complexity <= 0 or max_function_complexity > 1:
            raise PlanGenerationError("Max function complexity must be between 0 and 1")
        
        try:
            # Generate initial function breakdown using AI
            initial_functions = self._generate_initial_function_breakdown(objective)
            
            # Iteratively refine functions until they meet complexity requirements
            granular_functions = []
            
            for function in initial_functions:
                refined_functions = self._refine_function_to_granular_level(function, max_function_complexity)
                granular_functions.extend(refined_functions)
            
            # Validate final function set for separation of concerns
            self._validate_separation_of_concerns(granular_functions)
            
            return granular_functions
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to create granular function plan: {str(e)}")
    
    def _analyze_implementation_complexity(self, implementation_code: str) -> ComplexityMetrics:
        """
        Analyze complexity of actual implementation code.
        
        Args:
            implementation_code: The implementation code to analyze
            
        Returns:
            ComplexityMetrics with calculated metrics
        """
        lines = implementation_code.strip().split('\n')
        lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Count cyclomatic complexity indicators
        cyclomatic_complexity = 1  # Base complexity
        complexity_keywords = ['if', 'elif', 'else', 'while', 'for', 'try', 'except', 'with', 'and', 'or']
        
        for line in lines:
            line_lower = line.lower()
            for keyword in complexity_keywords:
                cyclomatic_complexity += line_lower.count(f' {keyword} ')
                cyclomatic_complexity += line_lower.count(f'{keyword} ')
        
        # Count cognitive complexity indicators
        cognitive_complexity = 0
        nesting_level = 0
        
        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped.lower() for keyword in ['if', 'for', 'while', 'try']):
                nesting_level += 1
                cognitive_complexity += nesting_level
            elif stripped.startswith(('else', 'elif', 'except', 'finally')):
                cognitive_complexity += nesting_level
            elif stripped in ['', '}', 'pass'] or stripped.startswith('return'):
                nesting_level = max(0, nesting_level - 1)
        
        # Calculate single-responsibility score based on code structure
        single_responsibility_score = self._calculate_implementation_sr_score(implementation_code)
        
        return ComplexityMetrics(
            cyclomatic_complexity=min(cyclomatic_complexity, 20),
            cognitive_complexity=min(cognitive_complexity, 15),
            lines_of_code=lines_of_code,
            single_responsibility_score=single_responsibility_score
        )
    
    def _calculate_implementation_sr_score(self, implementation_code: str) -> float:
        """Calculate single-responsibility score for implementation code."""
        score = 1.0
        
        lines = implementation_code.lower().split('\n')
        
        # Penalize multiple distinct operations
        operation_keywords = ['create', 'update', 'delete', 'validate', 'process', 'transform', 
                             'calculate', 'analyze', 'generate', 'parse', 'format', 'convert', 'save', 'load']
        
        found_operations = set()
        for line in lines:
            for keyword in operation_keywords:
                if keyword in line:
                    found_operations.add(keyword)
        
        if len(found_operations) > 1:
            score -= (len(found_operations) - 1) * 0.15
        
        # Penalize multiple database/file operations
        io_operations = ['open(', 'read(', 'write(', 'save(', 'load(', 'query(', 'insert(', 'update(', 'delete(']
        io_count = sum(1 for line in lines for op in io_operations if op in line)
        if io_count > 2:
            score -= (io_count - 2) * 0.1
        
        # Penalize high nesting (indicates multiple concerns)
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try', 'with']):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.startswith(('else', 'elif', 'except', 'finally')):
                pass  # Same nesting level
            elif not stripped or stripped in ['pass', 'break', 'continue'] or stripped.startswith('return'):
                current_nesting = max(0, current_nesting - 1)
        
        if max_nesting > 3:
            score -= (max_nesting - 3) * 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_implementation_violations(self, implementation_code: str, function_spec: FunctionSpec) -> List[str]:
        """Check for single-responsibility violations in implementation."""
        violations = []
        
        lines = implementation_code.lower().split('\n')
        
        # Check for multiple distinct operations
        operation_keywords = ['create', 'update', 'delete', 'validate', 'process', 'transform', 
                             'calculate', 'analyze', 'generate', 'parse', 'format', 'convert']
        
        found_operations = []
        for line in lines:
            for keyword in operation_keywords:
                if keyword in line and keyword not in found_operations:
                    found_operations.append(keyword)
        
        if len(found_operations) > 1:
            violations.append(f"Implementation performs multiple operations: {', '.join(found_operations)}")
        
        # Check for mixed abstraction levels
        high_level_indicators = ['service', 'manager', 'controller', 'handler']
        low_level_indicators = ['file', 'database', 'sql', 'json', 'xml', 'http']
        
        has_high_level = any(indicator in implementation_code.lower() for indicator in high_level_indicators)
        has_low_level = any(indicator in implementation_code.lower() for indicator in low_level_indicators)
        
        if has_high_level and has_low_level:
            violations.append("Implementation mixes high-level orchestration with low-level details")
        
        # Check for excessive complexity
        lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        if lines_of_code > 50:
            violations.append(f"Implementation is too long ({lines_of_code} lines), suggesting multiple responsibilities")
        
        # Check for multiple error handling patterns
        error_patterns = ['try:', 'except:', 'raise', 'assert', 'if.*error', 'if.*fail']
        error_count = sum(1 for line in lines for pattern in error_patterns if pattern in line)
        if error_count > 5:
            violations.append("Implementation has complex error handling, suggesting multiple failure modes")
        
        return violations
    
    def _generate_implementation_refactoring_suggestions(self, implementation_code: str, violations: List[str]) -> List[str]:
        """Generate refactoring suggestions for implementation."""
        suggestions = []
        
        if not violations:
            return suggestions
        
        for violation in violations:
            if "multiple operations" in violation:
                suggestions.append("Extract each operation into a separate helper function")
            elif "mixed abstraction" in violation:
                suggestions.append("Separate high-level orchestration from low-level implementation details")
            elif "too long" in violation:
                suggestions.append("Break down the function into smaller, focused helper functions")
            elif "complex error handling" in violation:
                suggestions.append("Extract error handling into dedicated validation and error management functions")
        
        # General suggestions
        if len(violations) > 2:
            suggestions.append("Consider applying the Extract Method refactoring pattern")
            suggestions.append("Review the function's purpose and ensure it has a single, clear responsibility")
        
        return suggestions
    
    def _calculate_implementation_complexity_score(self, metrics: ComplexityMetrics, violations: List[str]) -> float:
        """Calculate complexity score for implementation."""
        # Similar to specification complexity score but adjusted for implementation
        cyclomatic_score = min(metrics.cyclomatic_complexity / 15.0, 1.0)  # Higher threshold for implementation
        cognitive_score = min(metrics.cognitive_complexity / 20.0, 1.0)
        loc_score = min(metrics.lines_of_code / 100.0, 1.0)  # Higher threshold for implementation
        
        sr_score = 1.0 - metrics.single_responsibility_score
        violation_score = min(len(violations) / 4.0, 1.0)
        
        complexity_score = (
            cyclomatic_score * 0.3 +
            cognitive_score * 0.3 +
            loc_score * 0.2 +
            sr_score * 0.15 +
            violation_score * 0.05
        )
        
        return min(1.0, complexity_score)
    
    def _generate_initial_function_breakdown(self, objective: str) -> List[FunctionSpec]:
        """Generate initial function breakdown using AI."""
        try:
            prompt = f"""
You are a software architect focused on creating granular, single-responsibility functions.
Break down the following objective into a set of small, focused functions.

Objective: {objective}

Please provide a JSON response with function specifications:
{{
    "functions": [
        {{
            "name": "function_name",
            "description": "Single, clear responsibility description",
            "arguments": [
                {{
                    "name": "arg_name",
                    "type": "type_hint",
                    "description": "argument description"
                }}
            ],
            "return_type": "return_type"
        }}
    ]
}}

Guidelines:
1. Each function should have exactly one responsibility
2. Functions should be small and focused (ideally 10-20 lines when implemented)
3. Use descriptive names that clearly indicate the single purpose
4. Minimize coupling between functions
5. Follow the principle of doing one thing well
6. Avoid functions that perform multiple operations or handle multiple concerns

Respond with ONLY the JSON structure.
"""
            
            response = self.ai_client.generate_with_retry(prompt, max_retries=2)
            return self._parse_function_breakdown_response(response)
            
        except Exception:
            # Return empty list if AI generation fails
            return []
    
    def _parse_function_breakdown_response(self, response: str) -> List[FunctionSpec]:
        """Parse AI function breakdown response."""
        try:
            response = response.strip()
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                return []
            
            json_str = response[start_idx:end_idx + 1]
            breakdown_data = json.loads(json_str)
            
            functions = []
            for func_data in breakdown_data.get('functions', []):
                arguments = []
                for arg_data in func_data.get('arguments', []):
                    argument = Argument(
                        name=arg_data['name'],
                        type_hint=arg_data['type'],
                        description=arg_data.get('description', '')
                    )
                    arguments.append(argument)
                
                function = FunctionSpec(
                    name=func_data['name'],
                    module="generated_module",  # Will be updated later
                    docstring=func_data['description'],
                    arguments=arguments,
                    return_type=func_data.get('return_type', 'None'),
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
                functions.append(function)
            
            return functions
            
        except Exception:
            return []
    
    def _refine_function_to_granular_level(self, function: FunctionSpec, max_complexity: float) -> List[FunctionSpec]:
        """Refine a function to meet granular complexity requirements."""
        # Analyze current function complexity
        analysis = self.validate_function_complexity(function)
        
        if analysis.complexity_score <= max_complexity and not analysis.needs_refactoring:
            return [function]
        
        # If function is too complex, try to break it down
        if analysis.breakdown_suggestions:
            # Use AI-generated breakdown suggestions
            refined_functions = []
            for breakdown_func in analysis.breakdown_suggestions:
                # Recursively refine each breakdown function
                sub_refined = self._refine_function_to_granular_level(breakdown_func, max_complexity)
                refined_functions.extend(sub_refined)
            return refined_functions
        else:
            # If no breakdown suggestions, return original function
            # In a real implementation, you might want to log this for manual review
            return [function]
    
    def _validate_separation_of_concerns(self, functions: List[FunctionSpec]) -> None:
        """Validate that functions have proper separation of concerns."""
        # Check for overlapping responsibilities
        function_purposes = {}
        
        for function in functions:
            # Extract key purpose words from function name and description
            name_words = set(function.name.lower().split('_'))
            desc_words = set(word.lower() for word in function.docstring.split() 
                           if len(word) > 3 and word.isalpha())
            
            purpose_words = name_words.union(desc_words)
            
            # Check for significant overlap with existing functions
            for existing_func, existing_purposes in function_purposes.items():
                overlap = purpose_words.intersection(existing_purposes)
                if len(overlap) > 2:  # Significant overlap
                    # In a real implementation, you might want to log this warning
                    # or suggest further refinement
                    pass
            
            function_purposes[function.name] = purpose_words
    
    def validate_prerequisites(self) -> ValidationResult:
        """
        Validate that all prerequisites are met for operation.
        
        Returns:
            ValidationResult with validation status and issues
        """
        result = super().validate_prerequisites()
        
        # Additional validation specific to planning engine
        if self.ai_client:
            # Check if AI client has validate_prerequisites method (not in interface but some implementations have it)
            if hasattr(self.ai_client, 'validate_prerequisites'):
                ai_validation = self.ai_client.validate_prerequisites()
                result.issues.extend(ai_validation.issues)
                result.warnings.extend(ai_validation.warnings)
        
        result.is_valid = len(result.issues) == 0
        return result