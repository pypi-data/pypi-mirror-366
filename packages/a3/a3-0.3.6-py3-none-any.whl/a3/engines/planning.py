"""
Planning engine implementation for AI Project Builder.

This module provides the PlanningEngine class that generates comprehensive
project plans from high-level objectives using AI assistance.
"""

import ast
import json
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .base import BasePlanningEngine
from ..core.models import (
    ProjectPlan, Module, FunctionSpec, Argument, DependencyGraph,
    ValidationResult, ProjectPlanValidationError, ImplementationStatus,
    ComplexityAnalysis, ComplexityMetrics, EnhancedDependencyGraph,
    StructureAnalysis, FunctionGap, ImportIssue, DependencyType,
    CriticalPathAnalysis
)
from ..core.interfaces import AIClientInterface, StateManagerInterface
from ..managers.dependency import DependencyAnalyzer
from ..core.gap_analyzer import IntelligentGapAnalyzer
from ..core.import_issue_detector import ImportIssueDetector
from ..core.dependency_driven_planner import DependencyDrivenPlanner


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
        self.project_path = project_path
        self.dependency_analyzer = DependencyAnalyzer(project_path)
        self.gap_analyzer = IntelligentGapAnalyzer()
        self.import_issue_detector = ImportIssueDetector()
        self.dependency_driven_planner = DependencyDrivenPlanner()
    
    def initialize(self) -> None:
        """Initialize the planning engine and its dependencies."""
        super().initialize()
        # Initialize the dependency analyzer and its package manager
        self.dependency_analyzer.initialize()
        if hasattr(self.dependency_analyzer, 'package_manager'):
            self.dependency_analyzer.package_manager.initialize()
    
    def generate_plan(self, objective: str) -> ProjectPlan:
        """
        Generate a complete project plan from an objective using enhanced dependency analysis.
        
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
            # Step 1: Analyze existing structure first (enhanced capability)
            existing_analysis = self.analyze_existing_structure()
            
            # Step 2: Generate initial project structure
            project_structure = self._generate_project_structure(objective)
            
            # Step 3: Create modules from structure
            modules = self._create_modules_from_structure(project_structure)
            
            # Step 4: Integrate gap analysis results into planning
            if existing_analysis.missing_functions:
                modules = self._integrate_gap_analysis_results(modules, existing_analysis)
            
            # Step 5: Apply import issue fixes during plan generation
            if existing_analysis.import_issues:
                modules = self._apply_import_issue_fixes(modules, existing_analysis.import_issues)
            
            # Step 6: Merge with existing modules if any
            if existing_analysis.existing_modules:
                modules = self._merge_with_existing_modules(modules, existing_analysis.existing_modules)
            
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
            # Get configured model from state manager
            model = self._get_configured_model()
            response = self.ai_client.generate_with_retry(prompt, max_retries=3, model=model)
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
        Create enhanced dependency graph with function-level dependencies using new analysis methods.
        
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
            
            # Apply new analysis methods for enhanced capabilities
            enhanced_graph = self._apply_enhanced_analysis_methods(enhanced_graph, modules)
            
            # Check for function-level cycles and resolve them
            if enhanced_graph.has_function_cycles():
                enhanced_graph = self._resolve_circular_dependencies_with_enhanced_graph(enhanced_graph, modules)
            
            # Integrate complexity analysis into the graph
            enhanced_graph = self._integrate_complexity_analysis_into_graph(enhanced_graph, modules)
            
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
            
            # Get configured model from state manager
            model = self._get_configured_model()
            response = self.ai_client.generate_with_retry(prompt, max_retries=2, model=model)
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
            # Get configured model from state manager
            model = self._get_configured_model()
            response = self.ai_client.generate_with_retry(prompt, max_retries=2, model=model)
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
            
            # Get configured model from state manager
            model = self._get_configured_model()
            response = self.ai_client.generate_with_retry(prompt, max_retries=2, model=model)
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
    
    def analyze_existing_structure(self, project_path: Optional[str] = None) -> StructureAnalysis:
        """
        Analyze existing project structure for enhanced dependency-aware planning.
        
        Args:
            project_path: Path to the project directory to analyze (defaults to self.project_path)
            
        Returns:
            StructureAnalysis containing comprehensive analysis of existing structure
            
        Raises:
            PlanGenerationError: If structure analysis fails
        """
        self._ensure_initialized()
        
        if project_path is None:
            project_path = self.project_path
        
        try:
            # Initialize structure analysis
            analysis = StructureAnalysis()
            
            # Analyze existing modules using dependency analyzer
            existing_modules = self._discover_existing_modules(project_path)
            analysis.existing_modules = existing_modules
            
            if existing_modules:
                # Create enhanced dependency graph from existing modules
                enhanced_graph = self._create_enhanced_dependency_graph(existing_modules)
                analysis.enhanced_graph = enhanced_graph
                
                # Extract complexity metrics from dependency graph
                complexity_metrics = self._extract_complexity_metrics(enhanced_graph)
                analysis.complexity_metrics = complexity_metrics
                
                # Detect missing functions using gap analyzer
                missing_functions = self.gap_analyzer.detect_missing_functions(enhanced_graph)
                analysis.missing_functions = missing_functions
                
                # Scan for import issues in existing code
                import_issues = self._scan_existing_code_for_import_issues(project_path)
                analysis.import_issues = import_issues
                
                # Generate optimization opportunities
                optimization_opportunities = self.gap_analyzer.analyze_module_completeness(existing_modules)
                analysis.optimization_opportunities = optimization_opportunities
            
            # Validate the analysis
            analysis.validate()
            
            return analysis
            
        except Exception as e:
            if isinstance(e, PlanGenerationError):
                raise
            else:
                raise PlanGenerationError(f"Failed to analyze existing structure: {str(e)}")
    
    def _discover_existing_modules(self, project_path: str) -> List[Module]:
        """
        Discover existing modules in the project directory.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            List of Module objects representing existing modules
        """
        try:
            # Use dependency analyzer to discover existing modules
            # This is a simplified implementation - in practice, you might want
            # to use more sophisticated code analysis tools
            modules = []
            
            project_root = Path(project_path)
            
            # Find all Python files in the project
            python_files = []
            for root, dirs, files in os.walk(project_root):
                # Skip common directories that shouldn't be analyzed
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
                
                for file in files:
                    if file.endswith('.py') and not file.startswith('test_'):
                        python_files.append(Path(root) / file)
            
            # Analyze each Python file to extract module information
            for py_file in python_files:
                try:
                    module = self._analyze_python_file(py_file, project_root)
                    if module and module.functions:  # Only include modules with functions
                        modules.append(module)
                except Exception:
                    # Skip files that can't be analyzed
                    continue
            
            return modules
            
        except Exception as e:
            # Return empty list if discovery fails
            return []
    
    def _analyze_python_file(self, file_path: Path, project_root: Path) -> Optional[Module]:
        """
        Analyze a Python file to extract module information.
        
        Args:
            file_path: Path to the Python file
            project_root: Root path of the project
            
        Returns:
            Module object or None if analysis fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Extract module name from file path
            relative_path = file_path.relative_to(project_root)
            module_name = str(relative_path.with_suffix('')).replace(os.sep, '.')
            
            # Extract functions from the AST
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    function_spec = self._extract_function_from_ast(node, module_name)
                    if function_spec:
                        functions.append(function_spec)
            
            if not functions:
                return None
            
            # Create module object
            description = self._extract_module_docstring(tree)
            if not description:
                description = f"Module {module_name}"
            
            module = Module(
                name=module_name,
                description=description,
                file_path=str(relative_path),
                dependencies=[],  # Will be analyzed later
                functions=functions
            )
            
            return module
            
        except Exception:
            return None
    
    def _extract_function_from_ast(self, func_node: ast.FunctionDef, module_name: str) -> Optional[FunctionSpec]:
        """
        Extract function specification from AST node.
        
        Args:
            func_node: AST FunctionDef node
            module_name: Name of the containing module
            
        Returns:
            FunctionSpec object or None if extraction fails
        """
        try:
            # Extract arguments
            arguments = []
            for arg in func_node.args.args:
                if arg.arg != 'self':  # Skip self parameter
                    argument = Argument(
                        name=arg.arg,
                        type_hint=self._extract_type_hint(arg),
                        description=""
                    )
                    arguments.append(argument)
            
            # Extract docstring
            docstring = ""
            if (func_node.body and 
                isinstance(func_node.body[0], ast.Expr) and 
                isinstance(func_node.body[0].value, ast.Constant) and 
                isinstance(func_node.body[0].value.value, str)):
                docstring = func_node.body[0].value.value
            
            # Extract return type
            return_type = "Any"
            if func_node.returns:
                return_type = self._extract_type_hint_from_node(func_node.returns)
            
            function_spec = FunctionSpec(
                name=func_node.name,
                module=module_name,
                docstring=docstring,
                arguments=arguments,
                return_type=return_type,
                implementation_status=ImplementationStatus.COMPLETED
            )
            
            return function_spec
            
        except Exception:
            return None
    
    def _extract_type_hint(self, arg_node) -> str:
        """Extract type hint from argument node."""
        if hasattr(arg_node, 'annotation') and arg_node.annotation:
            return self._extract_type_hint_from_node(arg_node.annotation)
        return "Any"
    
    def _extract_type_hint_from_node(self, node) -> str:
        """Extract type hint string from AST node."""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            elif isinstance(node, ast.Attribute):
                return f"{self._extract_type_hint_from_node(node.value)}.{node.attr}"
            else:
                return "Any"
        except Exception:
            return "Any"
    
    def _extract_module_docstring(self, tree: ast.AST) -> str:
        """Extract module docstring from AST."""
        try:
            if (tree.body and 
                isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                return tree.body[0].value.value
            return ""
        except Exception:
            return ""
    
    def _extract_complexity_metrics(self, enhanced_graph: EnhancedDependencyGraph) -> Dict[str, Any]:
        """
        Extract complexity metrics from enhanced dependency graph.
        
        Args:
            enhanced_graph: Enhanced dependency graph to analyze
            
        Returns:
            Dictionary containing complexity metrics
        """
        try:
            metrics = {}
            
            if not enhanced_graph or not enhanced_graph.function_nodes:
                return metrics
            
            # Basic graph metrics
            metrics['total_functions'] = len(enhanced_graph.function_nodes)
            metrics['total_modules'] = len(set(node.module for node in enhanced_graph.function_nodes.values()))
            metrics['total_dependencies'] = len(enhanced_graph.function_edges)
            
            # Dependency density
            max_possible_edges = len(enhanced_graph.function_nodes) * (len(enhanced_graph.function_nodes) - 1)
            if max_possible_edges > 0:
                metrics['dependency_density'] = len(enhanced_graph.function_edges) / max_possible_edges
            else:
                metrics['dependency_density'] = 0.0
            
            # Function complexity distribution
            function_dependencies = {}
            for func_name in enhanced_graph.function_nodes:
                in_degree = sum(1 for edge in enhanced_graph.function_edges if edge[1] == func_name)
                out_degree = sum(1 for edge in enhanced_graph.function_edges if edge[0] == func_name)
                function_dependencies[func_name] = {'in_degree': in_degree, 'out_degree': out_degree}
            
            metrics['function_dependencies'] = function_dependencies
            
            # Identify highly connected functions (potential complexity hotspots)
            high_complexity_threshold = 5
            highly_connected = [
                func for func, deps in function_dependencies.items()
                if deps['in_degree'] + deps['out_degree'] > high_complexity_threshold
            ]
            metrics['highly_connected_functions'] = highly_connected
            
            # Module coupling metrics
            module_coupling = {}
            for edge in enhanced_graph.function_edges:
                source_module = enhanced_graph.function_nodes[edge[0]].module
                target_module = enhanced_graph.function_nodes[edge[1]].module
                
                if source_module != target_module:
                    if source_module not in module_coupling:
                        module_coupling[source_module] = set()
                    module_coupling[source_module].add(target_module)
            
            metrics['module_coupling'] = {
                module: len(coupled_modules) 
                for module, coupled_modules in module_coupling.items()
            }
            
            # Circular dependency detection
            has_cycles = enhanced_graph.has_function_cycles()
            metrics['has_circular_dependencies'] = has_cycles
            
            if has_cycles:
                # In a more sophisticated implementation, you might want to
                # identify the specific cycles
                metrics['circular_dependency_count'] = 'detected'
            else:
                metrics['circular_dependency_count'] = 0
            
            return metrics
            
        except Exception:
            return {}
    
    def _scan_existing_code_for_import_issues(self, project_path: str) -> List[ImportIssue]:
        """
        Scan existing code for import issues.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            List of ImportIssue objects found in existing code
        """
        try:
            import_issues = []
            
            project_root = Path(project_path)
            
            # Find all Python files in the project
            for root, dirs, files in os.walk(project_root):
                # Skip common directories that shouldn't be analyzed
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Scan this file for import issues
                            file_issues = self.import_issue_detector.scan_for_import_issues(
                                content, str(file_path.relative_to(project_root))
                            )
                            import_issues.extend(file_issues)
                            
                        except Exception:
                            # Skip files that can't be read
                            continue
            
            return import_issues
            
        except Exception:
            return []
    
    def _scan_existing_code_for_import_issues(self, project_path: str) -> List[ImportIssue]:
        """
        Scan existing code for import issues.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            List of ImportIssue objects found in existing code
        """
        issues = []
        
        try:
            project_root = Path(project_path)
            
            # Find all Python files in the project
            for root, dirs, files in os.walk(project_root):
                # Skip common directories that shouldn't be analyzed
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Scan this file for import issues
                            file_issues = self.import_issue_detector.scan_for_import_issues(content, str(file_path))
                            issues.extend(file_issues)
                            
                        except Exception:
                            # Skip files that can't be read
                            continue
            
            return issues
            
        except Exception:
            return []
    
    def suggest_optimal_additions(self, analysis: StructureAnalysis) -> List[Dict[str, Any]]:
        """
        Suggest optimal module and function additions based on structure analysis.
        
        Args:
            analysis: StructureAnalysis containing existing structure information
            
        Returns:
            List of module/function suggestions with rationale
        """
        self._ensure_initialized()
        
        if not analysis:
            return []
        
        suggestions = []
        
        # Use gap analyzer to identify missing functions
        if analysis.missing_functions:
            for gap in analysis.missing_functions:
                # Ensure the suggestion fits within existing dependency graph
                if self._validate_addition_fits_dependency_graph(gap, analysis.enhanced_graph):
                    suggestion = {
                        "type": "function",
                        "name": gap.suggested_name,
                        "module": gap.suggested_module,
                        "reason": gap.reason,
                        "confidence": gap.confidence,
                        "dependencies": gap.dependencies,
                        "dependents": gap.dependents
                    }
                    suggestions.append(suggestion)
        
        # Use optimization opportunities to suggest module restructuring
        if analysis.optimization_opportunities:
            for opportunity in analysis.optimization_opportunities:
                if opportunity.suggestion_type in ["module_split", "pattern_consolidation"]:
                    suggestion = {
                        "type": "module_restructuring",
                        "description": opportunity.description,
                        "affected_modules": opportunity.affected_modules,
                        "priority": opportunity.priority,
                        "estimated_effort": opportunity.estimated_effort
                    }
                    suggestions.append(suggestion)
        
        # Sort suggestions by confidence/priority
        suggestions.sort(key=lambda s: s.get("confidence", 0.5), reverse=True)
        
        return suggestions
    
    def _validate_addition_fits_dependency_graph(self, gap: FunctionGap, 
                                               enhanced_graph: EnhancedDependencyGraph) -> bool:
        """
        Validate that adding a function gap won't create circular dependencies.
        
        Args:
            gap: Function gap to validate
            enhanced_graph: Current enhanced dependency graph
            
        Returns:
            True if the addition is safe, False otherwise
        """
        if not enhanced_graph:
            return True
        
        # Create a temporary copy of the graph with the new function
        temp_graph = EnhancedDependencyGraph()
        temp_graph.function_nodes = enhanced_graph.function_nodes.copy()
        temp_graph.module_nodes = enhanced_graph.module_nodes.copy()
        temp_graph.function_to_module = enhanced_graph.function_to_module.copy()
        temp_graph.module_to_functions = enhanced_graph.module_to_functions.copy()
        temp_graph.function_dependencies = enhanced_graph.function_dependencies.copy()
        temp_graph.module_edges = enhanced_graph.module_edges.copy()
        
        # Add the new function
        new_function_name = f"{gap.suggested_module}.{gap.suggested_name}"
        temp_graph.add_function(gap.suggested_name, gap.suggested_module)
        
        # Add dependencies for the new function
        for dep_func in gap.dependencies:
            if dep_func in temp_graph.function_nodes:
                from .models import FunctionDependency, DependencyType
                dependency = FunctionDependency(
                    from_function=new_function_name,
                    to_function=dep_func,
                    dependency_type=DependencyType.DIRECT_CALL,
                    confidence=0.8
                )
                temp_graph.add_function_dependency(dependency)
        
        # Add dependents for the new function
        for dependent_func in gap.dependents:
            if dependent_func in temp_graph.function_nodes:
                from .models import FunctionDependency, DependencyType
                dependency = FunctionDependency(
                    from_function=dependent_func,
                    to_function=new_function_name,
                    dependency_type=DependencyType.DIRECT_CALL,
                    confidence=0.8
                )
                temp_graph.add_function_dependency(dependency)
        
        # Check if adding this function creates cycles
        return not temp_graph.has_function_cycles()
    
    def _integrate_gap_analysis_results(self, modules: List[Module], existing_analysis: StructureAnalysis) -> List[Module]:
        """
        Integrate gap analysis results into planning by adding suggested functions.
        
        Args:
            modules: List of modules from initial planning
            existing_analysis: Analysis of existing structure with gap information
            
        Returns:
            Updated list of modules with gap analysis integrated
        """
        if not existing_analysis.missing_functions:
            return modules
        
        # Create a mapping of module names to modules for easy lookup
        module_map = {module.name: module for module in modules}
        
        # Process each function gap
        for gap in existing_analysis.missing_functions:
            # Only add high-confidence gaps
            if gap.confidence >= 0.6:
                target_module_name = gap.suggested_module
                
                # Find or create the target module
                if target_module_name in module_map:
                    target_module = module_map[target_module_name]
                else:
                    # Create new module for the gap
                    target_module = Module(
                        name=target_module_name,
                        description=f"Module for {target_module_name} functionality",
                        file_path=f"{target_module_name.replace('.', '/')}.py",
                        dependencies=[],
                        functions=[]
                    )
                    modules.append(target_module)
                    module_map[target_module_name] = target_module
                
                # Create function spec from gap
                gap_function = FunctionSpec(
                    name=gap.suggested_name,
                    module=target_module_name,
                    docstring=f"Function suggested by gap analysis: {gap.reason}",
                    arguments=[],  # Will be refined later
                    return_type="Any",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
                
                # Add to module if not already present
                existing_names = {func.name for func in target_module.functions}
                if gap.suggested_name not in existing_names:
                    target_module.functions.append(gap_function)
        
        return modules
    
    def _apply_import_issue_fixes(self, modules: List[Module], import_issues: List[ImportIssue]) -> List[Module]:
        """
        Apply import issue fixes during plan generation.
        
        Args:
            modules: List of modules from planning
            import_issues: List of import issues found in existing code
            
        Returns:
            Updated list of modules with import fixes applied
        """
        if not import_issues:
            return modules
        
        # Group issues by file path for efficient processing
        issues_by_file = {}
        for issue in import_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        # Process each file with issues
        for file_path, file_issues in issues_by_file.items():
            try:
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # Apply fixes using the import issue detector
                fixed_content = self.import_issue_detector.fix_function_level_imports(original_content)
                
                # Validate the fixes
                validation_result = self.import_issue_detector.validate_import_resolution(fixed_content, file_path)
                
                if validation_result.is_valid:
                    # Write the fixed content back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                
            except Exception:
                # Skip files that can't be processed
                continue
        
        return modules
    
    def _merge_with_existing_modules(self, new_modules: List[Module], existing_modules: List[Module]) -> List[Module]:
        """
        Merge new modules with existing modules, avoiding duplicates.
        
        Args:
            new_modules: Modules from new planning
            existing_modules: Modules discovered from existing code
            
        Returns:
            Merged list of modules
        """
        if not existing_modules:
            return new_modules
        
        # Create a mapping of existing modules by name
        existing_map = {module.name: module for module in existing_modules}
        merged_modules = []
        
        # Process new modules
        for new_module in new_modules:
            if new_module.name in existing_map:
                # Merge with existing module
                existing_module = existing_map[new_module.name]
                merged_module = self._merge_modules(existing_module, new_module)
                merged_modules.append(merged_module)
                # Remove from existing map to avoid duplicates
                del existing_map[new_module.name]
            else:
                # Add new module as-is
                merged_modules.append(new_module)
        
        # Add remaining existing modules that weren't merged
        merged_modules.extend(existing_map.values())
        
        return merged_modules
    
    def _merge_modules(self, existing_module: Module, new_module: Module) -> Module:
        """
        Merge an existing module with a new module.
        
        Args:
            existing_module: Module from existing code
            new_module: Module from new planning
            
        Returns:
            Merged module
        """
        # Combine functions, avoiding duplicates
        existing_function_names = {func.name for func in existing_module.functions}
        merged_functions = list(existing_module.functions)
        
        for new_func in new_module.functions:
            if new_func.name not in existing_function_names:
                merged_functions.append(new_func)
        
        # Combine dependencies
        merged_dependencies = list(set(existing_module.dependencies + new_module.dependencies))
        
        # Use the more detailed description
        description = new_module.description if len(new_module.description) > len(existing_module.description) else existing_module.description
        
        return Module(
            name=existing_module.name,
            description=description,
            file_path=existing_module.file_path,
            dependencies=merged_dependencies,
            functions=merged_functions
        )    

    def _apply_enhanced_analysis_methods(self, enhanced_graph: EnhancedDependencyGraph, modules: List[Module]) -> EnhancedDependencyGraph:
        """
        Apply enhanced analysis methods to the dependency graph.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            modules: List of modules for context
            
        Returns:
            Enhanced dependency graph with analysis methods applied
        """
        try:
            # Use gap analyzer to identify missing functions and update graph
            missing_functions = self.gap_analyzer.detect_missing_functions(enhanced_graph)
            
            # Add missing functions to the graph as potential nodes
            for gap in missing_functions:
                if gap.confidence >= 0.7:  # Only add high-confidence gaps
                    # Add the suggested function as a node
                    full_function_name = f"{gap.suggested_module}.{gap.suggested_name}"
                    enhanced_graph.add_function(full_function_name, gap.suggested_module)
                    
                    # Add dependencies based on gap analysis
                    for dep_func in gap.dependencies:
                        if dep_func in enhanced_graph.function_nodes:
                            enhanced_graph.add_function_dependency(
                                full_function_name, dep_func, DependencyType.FUNCTIONAL
                            )
                    
                    # Add dependents based on gap analysis
                    for dependent_func in gap.dependents:
                        if dependent_func in enhanced_graph.function_nodes:
                            enhanced_graph.add_function_dependency(
                                dependent_func, full_function_name, DependencyType.FUNCTIONAL
                            )
            
            # Apply module completeness analysis
            completeness_analysis = self.gap_analyzer.analyze_module_completeness(modules)
            
            # Store analysis results in the graph for later use
            if hasattr(enhanced_graph, 'analysis_metadata'):
                enhanced_graph.analysis_metadata['completeness_analysis'] = completeness_analysis
            else:
                enhanced_graph.analysis_metadata = {'completeness_analysis': completeness_analysis}
            
            return enhanced_graph
            
        except Exception as e:
            # Return original graph if enhancement fails
            return enhanced_graph
    
    def _resolve_circular_dependencies_with_enhanced_graph(self, enhanced_graph: EnhancedDependencyGraph, modules: List[Module]) -> EnhancedDependencyGraph:
        """
        Resolve circular dependencies using enhanced graph analysis.
        
        Args:
            enhanced_graph: The enhanced dependency graph with cycles
            modules: List of modules for context
            
        Returns:
            Enhanced dependency graph with circular dependencies resolved
        """
        try:
            # Get function-level cycles
            cycles = enhanced_graph.get_function_cycles()
            
            if not cycles:
                return enhanced_graph
            
            # Create a copy of the graph to modify
            resolved_graph = EnhancedDependencyGraph()
            
            # Copy all nodes
            for func_name in enhanced_graph.function_nodes:
                module_name = enhanced_graph.function_to_module.get(func_name, "unknown")
                resolved_graph.add_function(func_name, module_name)
            
            # Copy module edges
            resolved_graph.module_edges = enhanced_graph.module_edges.copy()
            
            # Process function dependencies, breaking cycles
            for dependency in enhanced_graph.function_dependencies:
                from_func = dependency.from_function
                to_func = dependency.to_function
                
                # Check if this dependency creates a cycle
                if self._would_create_cycle(resolved_graph, from_func, to_func):
                    # Try to resolve the cycle by introducing an interface or adapter
                    resolution_strategy = self._determine_cycle_resolution_strategy(
                        from_func, to_func, cycles, modules
                    )
                    
                    if resolution_strategy == "interface":
                        # Create an interface function to break the cycle
                        interface_name = f"{to_func}_interface"
                        interface_module = enhanced_graph.function_to_module.get(to_func, "interfaces")
                        
                        resolved_graph.add_function(interface_name, interface_module)
                        resolved_graph.add_function_dependency(from_func, interface_name, dependency.dependency_type)
                        resolved_graph.add_function_dependency(interface_name, to_func, DependencyType.INTERFACE)
                    
                    elif resolution_strategy == "refactor":
                        # Skip this dependency and suggest refactoring
                        continue
                    
                    else:
                        # Default: add the dependency but mark it as potentially problematic
                        resolved_graph.add_function_dependency(from_func, to_func, dependency.dependency_type)
                else:
                    # Safe to add this dependency
                    resolved_graph.add_function_dependency(from_func, to_func, dependency.dependency_type)
            
            # Store resolution metadata
            if hasattr(resolved_graph, 'analysis_metadata'):
                resolved_graph.analysis_metadata['cycle_resolution'] = {
                    'original_cycles': len(cycles),
                    'resolution_applied': True
                }
            else:
                resolved_graph.analysis_metadata = {
                    'cycle_resolution': {
                        'original_cycles': len(cycles),
                        'resolution_applied': True
                    }
                }
            
            return resolved_graph
            
        except Exception as e:
            # Return original graph if resolution fails
            return enhanced_graph
    
    def _integrate_complexity_analysis_into_graph(self, enhanced_graph: EnhancedDependencyGraph, modules: List[Module]) -> EnhancedDependencyGraph:
        """
        Integrate complexity analysis into plan validation using the enhanced graph.
        
        Args:
            enhanced_graph: The enhanced dependency graph
            modules: List of modules for analysis
            
        Returns:
            Enhanced dependency graph with complexity analysis integrated
        """
        try:
            # Calculate complexity metrics for each function
            function_complexity = {}
            
            for module in modules:
                for function in module.functions:
                    full_function_name = f"{module.name}.{function.name}"
                    
                    # Calculate complexity using existing method
                    complexity_analysis = self.validate_function_complexity(function)
                    function_complexity[full_function_name] = {
                        'complexity_score': complexity_analysis.complexity_score,
                        'needs_refactoring': complexity_analysis.needs_refactoring,
                        'single_responsibility_score': complexity_analysis.single_responsibility_score
                    }
            
            # Calculate module-level complexity
            module_complexity = {}
            for module in modules:
                module_functions = [f"{module.name}.{func.name}" for func in module.functions]
                module_function_complexities = [
                    function_complexity.get(func_name, {}).get('complexity_score', 0.0)
                    for func_name in module_functions
                ]
                
                if module_function_complexities:
                    avg_complexity = sum(module_function_complexities) / len(module_function_complexities)
                    max_complexity = max(module_function_complexities)
                    
                    module_complexity[module.name] = {
                        'average_complexity': avg_complexity,
                        'max_complexity': max_complexity,
                        'function_count': len(module.functions),
                        'high_complexity_functions': [
                            func_name for func_name in module_functions
                            if function_complexity.get(func_name, {}).get('complexity_score', 0.0) > 0.7
                        ]
                    }
            
            # Calculate graph-level complexity metrics
            graph_complexity = self._calculate_graph_complexity_metrics(enhanced_graph, function_complexity)
            
            # Store complexity analysis in the graph
            if hasattr(enhanced_graph, 'analysis_metadata'):
                enhanced_graph.analysis_metadata.update({
                    'function_complexity': function_complexity,
                    'module_complexity': module_complexity,
                    'graph_complexity': graph_complexity
                })
            else:
                enhanced_graph.analysis_metadata = {
                    'function_complexity': function_complexity,
                    'module_complexity': module_complexity,
                    'graph_complexity': graph_complexity
                }
            
            return enhanced_graph
            
        except Exception as e:
            # Return original graph if complexity analysis fails
            return enhanced_graph
    
    def _would_create_cycle(self, graph: EnhancedDependencyGraph, from_func: str, to_func: str) -> bool:
        """
        Check if adding a dependency would create a cycle in the graph.
        
        Args:
            graph: The enhanced dependency graph
            from_func: Source function
            to_func: Target function
            
        Returns:
            True if adding the dependency would create a cycle
        """
        try:
            # Temporarily add the dependency
            graph.add_function_dependency(from_func, to_func, DependencyType.FUNCTIONAL)
            
            # Check for cycles
            has_cycles = graph.has_function_cycles()
            
            # Remove the temporary dependency
            graph.function_dependencies = [
                dep for dep in graph.function_dependencies
                if not (dep.from_function == from_func and dep.to_function == to_func)
            ]
            
            return has_cycles
            
        except Exception:
            return False
    
    def _determine_cycle_resolution_strategy(self, from_func: str, to_func: str, cycles: List[List[str]], modules: List[Module]) -> str:
        """
        Determine the best strategy for resolving a circular dependency.
        
        Args:
            from_func: Source function in the cycle
            to_func: Target function in the cycle
            cycles: List of all cycles in the graph
            modules: List of modules for context
            
        Returns:
            Resolution strategy: "interface", "refactor", or "accept"
        """
        try:
            # Check if functions are in the same module
            from_module = from_func.split('.')[0] if '.' in from_func else "unknown"
            to_module = to_func.split('.')[0] if '.' in to_func else "unknown"
            
            if from_module == to_module:
                # Same module - suggest refactoring
                return "refactor"
            
            # Check if this is a simple two-function cycle
            for cycle in cycles:
                if len(cycle) == 2 and from_func in cycle and to_func in cycle:
                    # Simple cycle - use interface pattern
                    return "interface"
            
            # For complex cycles, suggest refactoring
            return "refactor"
            
        except Exception:
            return "accept"
    
    def _calculate_graph_complexity_metrics(self, enhanced_graph: EnhancedDependencyGraph, function_complexity: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate complexity metrics for the entire dependency graph.
        
        Args:
            enhanced_graph: The enhanced dependency graph
            function_complexity: Function-level complexity data
            
        Returns:
            Dictionary containing graph-level complexity metrics
        """
        try:
            metrics = {}
            
            # Basic graph metrics
            metrics['total_functions'] = len(enhanced_graph.function_nodes)
            metrics['total_dependencies'] = len(enhanced_graph.function_dependencies)
            
            # Complexity distribution
            complexity_scores = [
                data.get('complexity_score', 0.0)
                for data in function_complexity.values()
            ]
            
            if complexity_scores:
                metrics['average_complexity'] = sum(complexity_scores) / len(complexity_scores)
                metrics['max_complexity'] = max(complexity_scores)
                metrics['min_complexity'] = min(complexity_scores)
                metrics['high_complexity_count'] = len([s for s in complexity_scores if s > 0.7])
            else:
                metrics['average_complexity'] = 0.0
                metrics['max_complexity'] = 0.0
                metrics['min_complexity'] = 0.0
                metrics['high_complexity_count'] = 0
            
            # Dependency metrics
            if enhanced_graph.function_dependencies:
                # Calculate fan-in and fan-out
                fan_in = {}
                fan_out = {}
                
                for dep in enhanced_graph.function_dependencies:
                    # Fan-out: how many functions this function depends on
                    if dep.from_function not in fan_out:
                        fan_out[dep.from_function] = 0
                    fan_out[dep.from_function] += 1
                    
                    # Fan-in: how many functions depend on this function
                    if dep.to_function not in fan_in:
                        fan_in[dep.to_function] = 0
                    fan_in[dep.to_function] += 1
                
                fan_out_values = list(fan_out.values())
                fan_in_values = list(fan_in.values())
                
                metrics['average_fan_out'] = sum(fan_out_values) / len(fan_out_values) if fan_out_values else 0
                metrics['max_fan_out'] = max(fan_out_values) if fan_out_values else 0
                metrics['average_fan_in'] = sum(fan_in_values) / len(fan_in_values) if fan_in_values else 0
                metrics['max_fan_in'] = max(fan_in_values) if fan_in_values else 0
            else:
                metrics['average_fan_out'] = 0
                metrics['max_fan_out'] = 0
                metrics['average_fan_in'] = 0
                metrics['max_fan_in'] = 0
            
            # Cycle metrics
            cycles = enhanced_graph.get_function_cycles() if hasattr(enhanced_graph, 'get_function_cycles') else []
            metrics['cycle_count'] = len(cycles)
            metrics['has_cycles'] = len(cycles) > 0
            
            return metrics
            
        except Exception:
            return {
                'total_functions': 0,
                'total_dependencies': 0,
                'average_complexity': 0.0,
                'cycle_count': 0,
                'has_cycles': False
            }
    
    def get_optimal_implementation_order(self, enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Get optimal implementation order using dependency-driven planner.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            List of function names in optimal implementation order
        """
        return self.dependency_driven_planner.get_optimal_implementation_order(enhanced_graph)
    
    def identify_parallel_implementation_opportunities(self, enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """
        Identify parallel implementation opportunities using dependency-driven planner.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            List of parallel groups (functions that can be implemented simultaneously)
        """
        return self.dependency_driven_planner.identify_parallel_opportunities(enhanced_graph)
    
    def analyze_critical_path_for_planning(self, enhanced_graph: EnhancedDependencyGraph) -> CriticalPathAnalysis:
        """
        Analyze critical path for planning decisions using dependency-driven planner.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            CriticalPathAnalysis with critical path information and optimization suggestions
        """
        return self.dependency_driven_planner.analyze_critical_path(enhanced_graph)
    
    def generate_dependency_aware_plan(self, objective: str, existing_analysis: Optional[StructureAnalysis] = None) -> ProjectPlan:
        """
        Generate a dependency-aware project plan using enhanced analysis.
        
        Args:
            objective: High-level project objective description
            existing_analysis: Optional existing structure analysis
            
        Returns:
            ProjectPlan with dependency-aware optimizations applied
        """
        # If no existing analysis provided, analyze current structure
        if existing_analysis is None:
            existing_analysis = self.analyze_existing_structure()
        
        # Generate base plan
        base_plan = self.generate_plan(objective)
        
        # Apply dependency-driven optimizations
        if base_plan.enhanced_dependency_graph:
            # Get optimal implementation order
            implementation_order = self.get_optimal_implementation_order(base_plan.enhanced_dependency_graph)
            
            # Identify parallel opportunities
            parallel_opportunities = self.identify_parallel_implementation_opportunities(base_plan.enhanced_dependency_graph)
            
            # Analyze critical path
            critical_path_analysis = self.analyze_critical_path_for_planning(base_plan.enhanced_dependency_graph)
            
            # Store optimization information in plan metadata
            if not hasattr(base_plan, 'optimization_metadata'):
                base_plan.optimization_metadata = {}
            
            base_plan.optimization_metadata.update({
                'implementation_order': implementation_order,
                'parallel_opportunities': parallel_opportunities,
                'critical_path_analysis': critical_path_analysis,
                'dependency_driven_optimizations_applied': True
            })
        
        return base_plan