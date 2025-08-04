"""
Core data models for the AI Project Builder.

This module defines the fundamental data structures used throughout
the project generation pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import re


# Custom exceptions for validation errors
class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


class ProjectPlanValidationError(ValidationError):
    """Exception raised when project plan validation fails."""
    pass


class ModuleValidationError(ValidationError):
    """Exception raised when module validation fails."""
    pass


class FunctionSpecValidationError(ValidationError):
    """Exception raised when function specification validation fails."""
    pass


class DependencyGraphValidationError(ValidationError):
    """Exception raised when dependency graph validation fails."""
    pass


class ProjectPhase(Enum):
    """Enumeration of project generation phases."""
    PLANNING = "planning"
    SPECIFICATION = "specification"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    INTEGRATION = "integration"
    COMPLETED = "completed"


class DependencyType(Enum):
    """Types of dependencies between functions."""
    DIRECT_CALL = "direct_call"          # Function A calls function B
    DATA_DEPENDENCY = "data_dependency"   # Function A uses output of function B
    TYPE_DEPENDENCY = "type_dependency"   # Function A uses types defined in function B
    IMPORT_DEPENDENCY = "import_dependency"  # Function A imports from module of function B


class ImplementationStatus(Enum):
    """Status of function implementation."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportIssueType(Enum):
    """Types of import issues that can be detected and fixed."""
    RELATIVE_IMPORT_IN_FUNCTION = "relative_import_in_function"
    INCORRECT_INDENTATION = "incorrect_indentation"
    UNRESOLVABLE_RELATIVE_IMPORT = "unresolvable_relative_import"
    CIRCULAR_IMPORT_RISK = "circular_import_risk"


@dataclass
class ModelConfiguration:
    """Configuration for AI model selection and management."""
    current_model: str
    available_models: List[str] = field(default_factory=list)
    fallback_models: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the model configuration."""
        if not self.current_model or not self.current_model.strip():
            raise ValidationError("Current model cannot be empty")
        
        # Validate model name format (allow alphanumeric, hyphens, underscores, colons, slashes, dots)
        if not re.match(r'^[a-zA-Z0-9_:/.,-]+$', self.current_model):
            raise ValidationError(f"Invalid current model name '{self.current_model}': must contain only alphanumeric characters, hyphens, underscores, colons, slashes, dots, and commas")
        
        # Validate available models
        for model in self.available_models:
            if not model or not model.strip():
                raise ValidationError("Available model names cannot be empty")
            if not re.match(r'^[a-zA-Z0-9_:/.,-]+$', model):
                raise ValidationError(f"Invalid available model name '{model}': must contain only alphanumeric characters, hyphens, underscores, colons, slashes, dots, and commas")
        
        # Validate fallback models
        for model in self.fallback_models:
            if not model or not model.strip():
                raise ValidationError("Fallback model names cannot be empty")
            if not re.match(r'^[a-zA-Z0-9_:/.,-]+$', model):
                raise ValidationError(f"Invalid fallback model name '{model}': must contain only alphanumeric characters, hyphens, underscores, colons, slashes, dots, and commas")
        
        # Ensure current model is in available models if available models is not empty
        if self.available_models and self.current_model not in self.available_models:
            raise ValidationError(f"Current model '{self.current_model}' must be in available models list")
        
        # Validate fallback models are in available models if available models is not empty
        if self.available_models:
            for fallback in self.fallback_models:
                if fallback not in self.available_models:
                    raise ValidationError(f"Fallback model '{fallback}' must be in available models list")
        
        # Validate preferences structure
        if not isinstance(self.preferences, dict):
            raise ValidationError("Preferences must be a dictionary")
    
    def set_current_model(self, model_name: str) -> None:
        """Set the current model with validation."""
        if not model_name or not model_name.strip():
            raise ValidationError("Model name cannot be empty")
        
        if not re.match(r'^[a-zA-Z0-9_:/-]+$', model_name):
            raise ValidationError(f"Invalid model name '{model_name}': must contain only alphanumeric characters, hyphens, underscores, colons, and slashes")
        
        if self.available_models and model_name not in self.available_models:
            raise ValidationError(f"Model '{model_name}' is not in available models list")
        
        self.current_model = model_name
        self.last_updated = datetime.now()
    
    def add_available_model(self, model_name: str) -> None:
        """Add a model to the available models list."""
        if not model_name or not model_name.strip():
            raise ValidationError("Model name cannot be empty")
        
        if not re.match(r'^[a-zA-Z0-9_:/-]+$', model_name):
            raise ValidationError(f"Invalid model name '{model_name}': must contain only alphanumeric characters, hyphens, underscores, colons, and slashes")
        
        if model_name not in self.available_models:
            self.available_models.append(model_name)
            self.last_updated = datetime.now()
    
    def add_fallback_model(self, model_name: str) -> None:
        """Add a model to the fallback models list."""
        if not model_name or not model_name.strip():
            raise ValidationError("Model name cannot be empty")
        
        if not re.match(r'^[a-zA-Z0-9_:/-]+$', model_name):
            raise ValidationError(f"Invalid model name '{model_name}': must contain only alphanumeric characters, hyphens, underscores, colons, and slashes")
        
        if self.available_models and model_name not in self.available_models:
            raise ValidationError(f"Fallback model '{model_name}' must be in available models list")
        
        if model_name not in self.fallback_models:
            self.fallback_models.append(model_name)
            self.last_updated = datetime.now()
    
    def get_next_fallback_model(self) -> Optional[str]:
        """Get the next fallback model to try."""
        if not self.fallback_models:
            return None
        
        # Return the first fallback model that's not the current model
        for model in self.fallback_models:
            if model != self.current_model:
                return model
        
        return None
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available."""
        if not self.available_models:
            return True  # If no available models list, assume all models are available
        return model_name in self.available_models


@dataclass
class Argument:
    """Represents a function argument with type information."""
    name: str
    type_hint: str
    default_value: Optional[str] = None
    description: str = ""
    
    def validate(self) -> None:
        """Validate the argument specification."""
        if not self.name or not self.name.strip():
            raise ValidationError("Argument name cannot be empty")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.name):
            raise ValidationError(f"Invalid argument name '{self.name}': must be a valid Python identifier")
        
        if not self.type_hint or not self.type_hint.strip():
            raise ValidationError("Argument type hint cannot be empty")
        
        # Check for reserved keywords
        python_keywords = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class', 'continue',
            'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass',
            'raise', 'return', 'try', 'while', 'with', 'yield'
        }
        if self.name in python_keywords:
            raise ValidationError(f"Argument name '{self.name}' is a Python keyword")


@dataclass
class FunctionSpec:
    """Specification for a function to be implemented."""
    name: str
    module: str
    docstring: str
    arguments: List[Argument] = field(default_factory=list)
    return_type: str = "None"
    implementation_status: ImplementationStatus = ImplementationStatus.NOT_STARTED
    
    def validate(self) -> None:
        """Validate the function specification."""
        if not self.name or not self.name.strip():
            raise FunctionSpecValidationError("Function name cannot be empty")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.name):
            raise FunctionSpecValidationError(f"Invalid function name '{self.name}': must be a valid Python identifier")
        
        if not self.module or not self.module.strip():
            raise FunctionSpecValidationError("Module name cannot be empty")
        
        if not self.docstring or not self.docstring.strip():
            raise FunctionSpecValidationError("Function docstring cannot be empty")
        
        if not self.return_type or not self.return_type.strip():
            raise FunctionSpecValidationError("Return type cannot be empty")
        
        # Validate all arguments
        arg_names = set()
        for arg in self.arguments:
            arg.validate()
            if arg.name in arg_names:
                raise FunctionSpecValidationError(f"Duplicate argument name '{arg.name}' in function '{self.name}'")
            arg_names.add(arg.name)
        
        # Check for reserved function names
        python_builtins = {
            '__init__', '__str__', '__repr__', '__len__', '__getitem__', '__setitem__',
            '__delitem__', '__iter__', '__next__', '__enter__', '__exit__'
        }
        if self.name.startswith('__') and self.name.endswith('__') and self.name not in python_builtins:
            raise FunctionSpecValidationError(f"Invalid dunder method name '{self.name}'")


@dataclass
class Module:
    """Represents a module in the project structure."""
    name: str
    description: str
    file_path: str
    dependencies: List[str] = field(default_factory=list)
    functions: List[FunctionSpec] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate the module specification."""
        if not self.name or not self.name.strip():
            raise ModuleValidationError("Module name cannot be empty")
        
        # Allow dotted module names like 'parsers.html_parser'
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', self.name):
            raise ModuleValidationError(f"Invalid module name '{self.name}': must be a valid Python module identifier")
        
        if not self.description or not self.description.strip():
            raise ModuleValidationError("Module description cannot be empty")
        
        if not self.file_path or not self.file_path.strip():
            raise ModuleValidationError("Module file path cannot be empty")
        
        if not self.file_path.endswith('.py'):
            raise ModuleValidationError(f"Module file path '{self.file_path}' must end with .py")
        
        # Validate dependencies are valid module names
        for dep in self.dependencies:
            if not dep or not dep.strip():
                raise ModuleValidationError("Dependency name cannot be empty")
            # Allow dotted module names like 'parsers.html_parser'
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', dep):
                raise ModuleValidationError(f"Invalid dependency name '{dep}': must be a valid Python module identifier")
        
        # Check for self-dependency
        if self.name in self.dependencies:
            raise ModuleValidationError(f"Module '{self.name}' cannot depend on itself")
        
        # Validate all functions
        function_names = set()
        for func in self.functions:
            func.validate()
            if func.name in function_names:
                raise ModuleValidationError(f"Duplicate function name '{func.name}' in module '{self.name}'")
            function_names.add(func.name)
            
            # Ensure function's module matches this module
            if func.module != self.name:
                raise ModuleValidationError(f"Function '{func.name}' has module '{func.module}' but is in module '{self.name}'")


@dataclass
class DependencyGraph:
    """Represents module dependencies and provides analysis methods."""
    nodes: List[str] = field(default_factory=list)  # Module names
    edges: List[Tuple[str, str]] = field(default_factory=list)  # (from_module, to_module)
    
    def has_cycles(self) -> bool:
        """Check if the dependency graph has circular dependencies using DFS."""
        if not self.nodes or not self.edges:
            return False
            
        # Build adjacency list
        graph = {node: [] for node in self.nodes}
        for from_node, to_node in self.edges:
            if from_node in graph and to_node in self.nodes:
                graph[from_node].append(to_node)
        
        # Track node states: 0=unvisited, 1=visiting, 2=visited
        state = {node: 0 for node in self.nodes}
        
        def dfs(node: str) -> bool:
            if state[node] == 1:  # Currently visiting - cycle detected
                return True
            if state[node] == 2:  # Already visited
                return False
                
            state[node] = 1  # Mark as visiting
            for neighbor in graph[node]:
                if dfs(neighbor):
                    return True
            state[node] = 2  # Mark as visited
            return False
        
        # Check each unvisited node
        for node in self.nodes:
            if state[node] == 0 and dfs(node):
                return True
        return False
    
    def topological_sort(self) -> List[str]:
        """Return modules in topological order using Kahn's algorithm."""
        if not self.nodes:
            return []
            
        # Build adjacency list and in-degree count
        graph = {node: [] for node in self.nodes}
        in_degree = {node: 0 for node in self.nodes}
        
        for from_node, to_node in self.edges:
            if from_node in graph and to_node in self.nodes:
                graph[from_node].append(to_node)
                in_degree[to_node] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node in self.nodes if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Remove edges from this node
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we couldn't process all nodes, there's a cycle
        if len(result) != len(self.nodes):
            # Return original order if cycle exists
            return self.nodes.copy()
            
        return result
    
    def get_dependencies(self, module: str) -> List[str]:
        """Get direct dependencies for a given module."""
        return [to_module for from_module, to_module in self.edges if from_module == module]
    
    def validate(self) -> None:
        """Validate the dependency graph."""
        # Check for duplicate nodes
        if len(self.nodes) != len(set(self.nodes)):
            raise DependencyGraphValidationError("Dependency graph contains duplicate nodes")
        
        # Validate node names
        for node in self.nodes:
            if not node or not node.strip():
                raise DependencyGraphValidationError("Node name cannot be empty")
            # Allow dots in node names for module paths
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', node):
                raise DependencyGraphValidationError(f"Invalid node name '{node}': must be a valid Python module identifier")
        
        # Validate edges reference existing nodes
        for from_node, to_node in self.edges:
            if from_node not in self.nodes:
                raise DependencyGraphValidationError(f"Edge references non-existent node '{from_node}'")
            if to_node not in self.nodes:
                raise DependencyGraphValidationError(f"Edge references non-existent node '{to_node}'")
            if from_node == to_node:
                raise DependencyGraphValidationError(f"Self-dependency detected for node '{from_node}'")
        
        # Check for duplicate edges
        edge_set = set(self.edges)
        if len(self.edges) != len(edge_set):
            raise DependencyGraphValidationError("Dependency graph contains duplicate edges")
        
        # Check for cycles
        if self.has_cycles():
            raise DependencyGraphValidationError("Dependency graph contains circular dependencies")


@dataclass
class FunctionDependency:
    """Represents a dependency between two functions."""
    from_function: str  # Format: "module.function"
    to_function: str    # Format: "module.function"
    dependency_type: DependencyType
    confidence: float = 1.0  # Confidence level (0.0 to 1.0)
    line_number: Optional[int] = None  # Where the dependency occurs
    context: Optional[str] = None  # Additional context about the dependency
    
    def __post_init__(self):
        """Validate the dependency."""
        if not self.from_function or not self.to_function:
            raise ValidationError("Function names cannot be empty")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("Confidence must be between 0.0 and 1.0")
        
        # Validate function name format (module.function)
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_.]*\.[a-zA-Z_][a-zA-Z0-9_]*$'
        if not re.match(pattern, self.from_function):
            raise ValidationError(f"Invalid from_function format: {self.from_function}")
        if not re.match(pattern, self.to_function):
            raise ValidationError(f"Invalid to_function format: {self.to_function}")


@dataclass
class EnhancedDependencyGraph:
    """Enhanced dependency graph with both module and function-level dependencies."""
    
    # Module-level dependencies (existing)
    module_nodes: List[str] = field(default_factory=list)
    module_edges: List[Tuple[str, str]] = field(default_factory=list)
    
    # Function-level dependencies (new)
    function_nodes: List[str] = field(default_factory=list)  # Format: "module.function"
    function_dependencies: List[FunctionDependency] = field(default_factory=list)
    
    # Mapping between functions and modules
    function_to_module: Dict[str, str] = field(default_factory=dict)
    module_to_functions: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_function(self, function_name: str, module_name: str) -> None:
        """Add a function to the graph."""
        full_name = f"{module_name}.{function_name}"
        
        if full_name not in self.function_nodes:
            self.function_nodes.append(full_name)
            self.function_to_module[full_name] = module_name
            
            if module_name not in self.module_to_functions:
                self.module_to_functions[module_name] = []
            self.module_to_functions[module_name].append(full_name)
            
            # Ensure module is in module_nodes
            if module_name not in self.module_nodes:
                self.module_nodes.append(module_name)
    
    def add_function_dependency(self, dependency: FunctionDependency) -> None:
        """Add a function-level dependency."""
        # Ensure both functions exist in the graph
        from_module = dependency.from_function.split('.')[0]
        to_module = dependency.to_function.split('.')[0]
        
        if dependency.from_function not in self.function_nodes:
            self.add_function(dependency.from_function.split('.')[1], from_module)
        
        if dependency.to_function not in self.function_nodes:
            self.add_function(dependency.to_function.split('.')[1], to_module)
        
        # Add the dependency
        self.function_dependencies.append(dependency)
        
        # Update module-level dependencies if cross-module
        if from_module != to_module:
            module_edge = (from_module, to_module)
            if module_edge not in self.module_edges:
                self.module_edges.append(module_edge)
    
    def get_function_dependencies(self, function_name: str) -> List[FunctionDependency]:
        """Get all dependencies for a specific function."""
        return [dep for dep in self.function_dependencies 
                if dep.from_function == function_name]
    
    def get_function_dependents(self, function_name: str) -> List[FunctionDependency]:
        """Get all functions that depend on the specified function."""
        return [dep for dep in self.function_dependencies 
                if dep.to_function == function_name]
    
    def has_function_cycles(self) -> bool:
        """Check if there are circular dependencies at the function level."""
        if not self.function_nodes or not self.function_dependencies:
            return False
        
        # Build adjacency list
        graph = {node: [] for node in self.function_nodes}
        for dep in self.function_dependencies:
            graph[dep.from_function].append(dep.to_function)
        
        # DFS cycle detection
        state = {node: 0 for node in self.function_nodes}  # 0=unvisited, 1=visiting, 2=visited
        
        def dfs(node: str) -> bool:
            if state[node] == 1:  # Currently visiting - cycle detected
                return True
            if state[node] == 2:  # Already visited
                return False
            
            state[node] = 1  # Mark as visiting
            for neighbor in graph[node]:
                if dfs(neighbor):
                    return True
            state[node] = 2  # Mark as visited
            return False
        
        # Check each unvisited node
        for node in self.function_nodes:
            if state[node] == 0 and dfs(node):
                return True
        return False
    
    def get_function_implementation_order(self) -> List[str]:
        """Get optimal order for implementing functions using topological sort."""
        if not self.function_nodes:
            return []
        
        # Build adjacency list and in-degree count
        graph = {node: [] for node in self.function_nodes}
        in_degree = {node: 0 for node in self.function_nodes}
        
        for dep in self.function_dependencies:
            graph[dep.to_function].append(dep.from_function)  # Reverse for implementation order
            in_degree[dep.from_function] += 1
        
        # Kahn's algorithm with priority for functions with no dependencies
        queue = [node for node in self.function_nodes if in_degree[node] == 0]
        result = []
        
        while queue:
            # Sort queue to ensure deterministic order
            queue.sort()
            node = queue.pop(0)
            result.append(node)
            
            # Remove edges from this node
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If not all nodes are included, there are cycles
        if len(result) != len(self.function_nodes):
            # Return partial order with remaining nodes
            remaining = [node for node in self.function_nodes if node not in result]
            result.extend(sorted(remaining))
        
        return result
    
    def get_module_implementation_order(self) -> List[str]:
        """Get optimal order for implementing modules."""
        if not self.module_nodes:
            return []
        
        # Build adjacency list and in-degree count
        graph = {node: [] for node in self.module_nodes}
        in_degree = {node: 0 for node in self.module_nodes}
        
        for from_module, to_module in self.module_edges:
            graph[to_module].append(from_module)  # Reverse for implementation order
            in_degree[from_module] += 1
        
        # Kahn's algorithm
        queue = [node for node in self.module_nodes if in_degree[node] == 0]
        result = []
        
        while queue:
            queue.sort()  # Deterministic order
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def get_critical_path(self) -> List[str]:
        """Find the critical path (longest dependency chain) in the function graph."""
        if not self.function_nodes:
            return []
        
        # Build adjacency list
        graph = {node: [] for node in self.function_nodes}
        for dep in self.function_dependencies:
            graph[dep.from_function].append(dep.to_function)
        
        # Find longest path using DFS
        memo = {}
        
        def longest_path_from(node: str) -> Tuple[int, List[str]]:
            if node in memo:
                return memo[node]
            
            if not graph[node]:  # No outgoing edges
                memo[node] = (1, [node])
                return memo[node]
            
            max_length = 0
            best_path = []
            
            for neighbor in graph[node]:
                length, path = longest_path_from(neighbor)
                if length > max_length:
                    max_length = length
                    best_path = path
            
            result = (max_length + 1, [node] + best_path)
            memo[node] = result
            return result
        
        # Find the overall longest path
        max_length = 0
        critical_path = []
        
        for node in self.function_nodes:
            length, path = longest_path_from(node)
            if length > max_length:
                max_length = length
                critical_path = path
        
        return critical_path
    
    def get_parallel_implementation_groups(self) -> List[List[str]]:
        """Find groups of functions that can be implemented in parallel."""
        parallel_groups = []
        
        # Functions with no dependencies can be implemented first
        no_deps = []
        for func in self.function_nodes:
            deps = self.get_function_dependencies(func)
            if not deps:
                no_deps.append(func)
        
        if no_deps:
            parallel_groups.append(no_deps)
        
        # Find other parallel opportunities by analyzing dependency levels
        implemented = set(no_deps)
        
        while len(implemented) < len(self.function_nodes):
            next_batch = []
            
            for func in self.function_nodes:
                if func in implemented:
                    continue
                
                # Check if all dependencies are implemented
                deps = self.get_function_dependencies(func)
                if all(dep.to_function in implemented for dep in deps):
                    next_batch.append(func)
            
            if next_batch:
                parallel_groups.append(next_batch)
                implemented.update(next_batch)
            else:
                # Handle remaining functions (might have cycles)
                remaining = [f for f in self.function_nodes if f not in implemented]
                if remaining:
                    parallel_groups.append(remaining)
                break
        
        return parallel_groups
    
    def analyze_dependency_complexity(self) -> Dict[str, Any]:
        """Analyze the complexity of the dependency graph."""
        if not self.function_nodes:
            return {}
        
        # Calculate metrics
        total_functions = len(self.function_nodes)
        total_dependencies = len(self.function_dependencies)
        
        # Dependency density (edges / possible edges)
        max_possible_edges = total_functions * (total_functions - 1)
        density = total_dependencies / max_possible_edges if max_possible_edges > 0 else 0
        
        # Average dependencies per function
        avg_dependencies = total_dependencies / total_functions if total_functions > 0 else 0
        
        # Find functions with most dependencies (in and out)
        in_degree = {node: 0 for node in self.function_nodes}
        out_degree = {node: 0 for node in self.function_nodes}
        
        for dep in self.function_dependencies:
            out_degree[dep.from_function] += 1
            in_degree[dep.to_function] += 1
        
        most_dependent = max(out_degree.items(), key=lambda x: x[1]) if out_degree else ("", 0)
        most_depended_on = max(in_degree.items(), key=lambda x: x[1]) if in_degree else ("", 0)
        
        # Critical path length
        critical_path = self.get_critical_path()
        critical_path_length = len(critical_path)
        
        return {
            "total_functions": total_functions,
            "total_dependencies": total_dependencies,
            "dependency_density": density,
            "average_dependencies_per_function": avg_dependencies,
            "most_dependent_function": most_dependent[0],
            "max_outgoing_dependencies": most_dependent[1],
            "most_depended_on_function": most_depended_on[0],
            "max_incoming_dependencies": most_depended_on[1],
            "critical_path_length": critical_path_length,
            "critical_path": critical_path,
            "has_cycles": self.has_function_cycles()
        }
    
    def to_legacy_dependency_graph(self) -> 'DependencyGraph':
        """Convert to legacy DependencyGraph for backward compatibility."""
        return DependencyGraph(
            nodes=self.module_nodes.copy(),
            edges=self.module_edges.copy()
        )


@dataclass
class ProjectPlan:
    """Complete project plan with modules and dependencies."""
    objective: str
    modules: List[Module] = field(default_factory=list)
    dependency_graph: DependencyGraph = field(default_factory=DependencyGraph)
    enhanced_dependency_graph: Optional[EnhancedDependencyGraph] = field(default_factory=lambda: None)
    estimated_functions: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the project plan."""
        if not self.objective or not self.objective.strip():
            raise ProjectPlanValidationError("Project objective cannot be empty")
        
        if self.estimated_functions < 0:
            raise ProjectPlanValidationError("Estimated functions count cannot be negative")
        
        # Validate dependency graph
        self.dependency_graph.validate()
        
        # Validate all modules
        module_names = set()
        total_functions = 0
        
        for module in self.modules:
            module.validate()
            if module.name in module_names:
                raise ProjectPlanValidationError(f"Duplicate module name '{module.name}' in project plan")
            module_names.add(module.name)
            total_functions += len(module.functions)
        
        # Ensure dependency graph nodes match module names
        graph_nodes = set(self.dependency_graph.nodes)
        if graph_nodes != module_names:
            missing_in_graph = module_names - graph_nodes
            extra_in_graph = graph_nodes - module_names
            error_msg = "Dependency graph nodes don't match module names"
            if missing_in_graph:
                error_msg += f". Missing in graph: {missing_in_graph}"
            if extra_in_graph:
                error_msg += f". Extra in graph: {extra_in_graph}"
            raise ProjectPlanValidationError(error_msg)
        
        # Validate module dependencies exist
        for module in self.modules:
            for dep in module.dependencies:
                if dep not in module_names:
                    raise ProjectPlanValidationError(f"Module '{module.name}' depends on non-existent module '{dep}'")
        
        # Validate estimated functions count is reasonable
        if self.estimated_functions > 0 and abs(self.estimated_functions - total_functions) > total_functions * 0.5:
            raise ProjectPlanValidationError(f"Estimated functions ({self.estimated_functions}) differs significantly from actual count ({total_functions})")


@dataclass
class ProjectProgress:
    """Tracks progress through project generation phases."""
    current_phase: ProjectPhase = ProjectPhase.PLANNING
    completed_phases: List[ProjectPhase] = field(default_factory=list)
    total_functions: int = 0
    implemented_functions: int = 0
    failed_functions: List[str] = field(default_factory=list)
    completed_functions: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the project progress."""
        if self.total_functions < 0:
            raise ValidationError("Total functions count cannot be negative")
        
        if self.implemented_functions < 0:
            raise ValidationError("Implemented functions count cannot be negative")
        
        if self.implemented_functions > self.total_functions:
            raise ValidationError("Implemented functions cannot exceed total functions")
        
        # Validate phase progression
        phase_order = [ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION, 
                      ProjectPhase.IMPLEMENTATION, ProjectPhase.INTEGRATION, ProjectPhase.COMPLETED]
        
        current_index = phase_order.index(self.current_phase)
        
        for completed_phase in self.completed_phases:
            completed_index = phase_order.index(completed_phase)
            if completed_index >= current_index and self.current_phase != ProjectPhase.COMPLETED:
                raise ValidationError(f"Completed phase '{completed_phase.value}' cannot be ahead of current phase '{self.current_phase.value}'")
        
        # Validate failed functions are strings
        for func_name in self.failed_functions:
            if not isinstance(func_name, str) or not func_name.strip():
                raise ValidationError("Failed function names must be non-empty strings")


@dataclass
class ProjectStatus:
    """Current status of a project."""
    is_active: bool = False
    progress: Optional[ProjectProgress] = None
    errors: List[str] = field(default_factory=list)
    can_resume: bool = False
    next_action: Optional[str] = None


# Result types for operations
@dataclass
class ProjectResult:
    """Result of a project operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class SpecificationSet:
    """Collection of function specifications."""
    functions: List[FunctionSpec] = field(default_factory=list)
    modules: List[Module] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ImplementationResult:
    """Result of code implementation phase."""
    implemented_functions: List[str] = field(default_factory=list)
    failed_functions: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Return True if implementation was successful (no failed functions)."""
        return len(self.failed_functions) == 0


@dataclass
class IntegrationResult:
    """Result of module integration phase."""
    integrated_modules: List[str] = field(default_factory=list)
    import_errors: List[str] = field(default_factory=list)
    success: bool = False
    completed_at: datetime = field(default_factory=datetime.now)
    test_result: Optional['TestGenerationResult'] = None
    package_updates: Optional[List[str]] = None


class ValidationResult:
    """Unified result of validation operations."""
    
    def __init__(self, is_valid: bool = False, errors: Optional[List[str]] = None, 
                 warnings: Optional[List[str]] = None, fixed_imports: Optional[List[str]] = None,
                 issues: Optional[List[str]] = None):
        """Initialize ValidationResult with backward compatibility for 'issues' parameter."""
        self.is_valid = is_valid
        self.warnings = warnings or []
        self.fixed_imports = fixed_imports or []
        
        # Handle backward compatibility: if 'issues' is provided, use it as 'errors'
        if issues is not None and errors is not None:
            raise ValueError("Cannot specify both 'issues' and 'errors' parameters")
        elif issues is not None:
            self.errors = issues
        else:
            self.errors = errors or []
    
    # Backward compatibility properties
    @property
    def issues(self) -> List[str]:
        """Alias for errors to maintain backward compatibility."""
        return self.errors
    
    @issues.setter
    def issues(self, value: List[str]) -> None:
        """Setter for issues alias."""
        self.errors = value


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    memory_usage: Optional[int] = None


@dataclass
class TestDetail:
    """Details of a single test execution."""
    name: str
    status: str  # 'passed', 'failed', 'skipped'
    message: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class CoverageReport:
    """Code coverage report."""
    total_lines: int
    covered_lines: int
    coverage_percentage: float
    uncovered_lines: List[int] = field(default_factory=list)


@dataclass
class TestResult:
    """Result of test execution."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_details: List[TestDetail] = field(default_factory=list)
    coverage_report: Optional[CoverageReport] = None


@dataclass
class ImportValidationResult:
    """Result of import validation."""
    success: bool
    valid_imports: List[str] = field(default_factory=list)
    invalid_imports: List[str] = field(default_factory=list)
    missing_modules: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    """Result of function implementation verification."""
    function_name: str
    is_verified: bool
    execution_result: Optional[ExecutionResult] = None
    test_result: Optional[TestResult] = None
    import_validation: Optional[ImportValidationResult] = None
    verification_errors: List[str] = field(default_factory=list)


@dataclass
class StackFrame:
    """Represents a single frame in a stack trace."""
    filename: str
    line_number: int
    function_name: str
    code_line: Optional[str] = None
    local_variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class TracebackAnalysis:
    """Comprehensive analysis of a traceback/exception."""
    error_type: str
    error_message: str
    stack_trace: List[StackFrame] = field(default_factory=list)
    root_cause: str = ""
    suggested_fixes: List[str] = field(default_factory=list)
    exception_chain: List[str] = field(default_factory=list)


@dataclass
class Parameter:
    """Represents a function parameter with detailed information."""
    name: str
    annotation: Optional[str] = None
    default_value: Optional[str] = None
    kind: str = "POSITIONAL_OR_KEYWORD"  # inspect.Parameter.kind values


@dataclass
class ComplexityMetrics:
    """Code complexity metrics for a function."""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    single_responsibility_score: float = 0.0


@dataclass
class ComplexityAnalysis:
    """Analysis of function complexity and single-responsibility adherence."""
    function_spec: FunctionSpec
    complexity_metrics: ComplexityMetrics
    single_responsibility_violations: List[str] = field(default_factory=list)
    refactoring_suggestions: List[str] = field(default_factory=list)
    breakdown_suggestions: List[FunctionSpec] = field(default_factory=list)
    complexity_score: float = 0.0  # Overall complexity score (0-1, lower is better)
    needs_refactoring: bool = False
    
    def validate(self) -> None:
        """Validate the complexity analysis."""
        if not self.function_spec:
            raise ValidationError("Function spec is required for complexity analysis")
        
        if not self.complexity_metrics:
            raise ValidationError("Complexity metrics are required")
        
        if self.complexity_score < 0.0 or self.complexity_score > 1.0:
            raise ValidationError("Complexity score must be between 0.0 and 1.0")
        
        # Validate breakdown suggestions
        for suggestion in self.breakdown_suggestions:
            suggestion.validate()


@dataclass
class FunctionInspection:
    """Detailed inspection of a function using Python's inspect module."""
    signature: str
    source_code: Optional[str] = None
    docstring: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)
    return_annotation: Optional[str] = None
    complexity_metrics: Optional[ComplexityMetrics] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ParsedDocstring:
    """Parsed docstring information using docstring_parser."""
    short_description: str = ""
    long_description: str = ""
    parameters: List[Dict[str, str]] = field(default_factory=list)
    returns: Optional[Dict[str, str]] = None
    raises: List[Dict[str, str]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class DebugContext:
    """Comprehensive debug context for AI-powered code revision."""
    function_spec: FunctionSpec
    traceback_analysis: Optional[TracebackAnalysis] = None
    function_inspection: Optional[FunctionInspection] = None
    parsed_docstring: Optional[ParsedDocstring] = None
    related_code: List[str] = field(default_factory=list)
    execution_environment: Dict[str, Any] = field(default_factory=dict)
    revision_history: List[str] = field(default_factory=list)


@dataclass
class CodeRevision:
    """Represents a code revision suggestion from AI analysis."""
    original_code: str
    revised_code: str
    revision_reason: str
    confidence_score: float = 0.0
    applied: bool = False
    test_results: Optional[TestResult] = None


# Project Analysis Models

@dataclass
class SourceFile:
    """Represents a source code file in the project."""
    path: str
    content: str
    language: str = "python"
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    lines_of_code: int = 0
    complexity_score: float = 0.0


@dataclass
class TestFile:
    """Represents a test file in the project."""
    path: str
    content: str
    test_functions: List[str] = field(default_factory=list)
    tested_modules: List[str] = field(default_factory=list)
    test_framework: str = "pytest"


@dataclass
class ConfigFile:
    """Represents a configuration file in the project."""
    path: str
    content: str
    config_type: str  # 'pyproject.toml', 'setup.py', 'requirements.txt', etc.
    parsed_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentationFile:
    """Represents a documentation file in the project."""
    path: str
    content: str
    doc_type: str  # 'README', 'API', 'CHANGELOG', etc.
    sections: List[str] = field(default_factory=list)


@dataclass
class CodingConventions:
    """Represents coding conventions found in the project."""
    naming_style: str = "snake_case"
    docstring_style: str = "google"
    line_length: int = 88
    import_style: str = "absolute"
    type_hints_usage: float = 0.0  # Percentage of functions with type hints
    test_coverage: float = 0.0


@dataclass
class CodePatterns:
    """Represents code patterns identified in the project."""
    architectural_patterns: List[str] = field(default_factory=list)
    design_patterns: List[str] = field(default_factory=list)
    coding_conventions: CodingConventions = field(default_factory=CodingConventions)
    common_utilities: List[str] = field(default_factory=list)
    test_patterns: List[str] = field(default_factory=list)


@dataclass
class ProjectStructure:
    """Represents the complete structure of an analyzed project."""
    root_path: str
    source_files: List[SourceFile] = field(default_factory=list)
    test_files: List[TestFile] = field(default_factory=list)
    config_files: List[ConfigFile] = field(default_factory=list)
    documentation_files: List[DocumentationFile] = field(default_factory=list)
    dependency_graph: DependencyGraph = field(default_factory=DependencyGraph)
    data_source_analysis: Optional['DataSourceAnalysis'] = None
    database_analysis: Optional['DatabaseSchema'] = None
    
    def validate(self) -> None:
        """Validate the project structure."""
        if not self.root_path or not self.root_path.strip():
            raise ValidationError("Project root path cannot be empty")
        
        # Validate dependency graph
        self.dependency_graph.validate()
        
        # Validate file paths are relative to root
        all_files = (self.source_files + self.test_files + 
                    self.config_files + self.documentation_files)
        
        for file_obj in all_files:
            if not hasattr(file_obj, 'path'):
                continue
            # Check if path is absolute (starts with / or drive letter on Windows)
            if file_obj.path.startswith('/') or (len(file_obj.path) > 1 and file_obj.path[1] == ':'):
                raise ValidationError(f"File path should be relative to root: {file_obj.path}")


@dataclass
class ProjectDocumentation:
    """Generated documentation for a project."""
    overview: str = ""
    architecture_description: str = ""
    module_descriptions: Dict[str, str] = field(default_factory=dict)
    function_descriptions: Dict[str, str] = field(default_factory=dict)
    dependency_analysis: str = ""
    usage_examples: List[str] = field(default_factory=list)
    database_documentation: str = ""
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModificationPlan:
    """Plan for modifying an existing project."""
    user_prompt: str
    target_files: List[str] = field(default_factory=list)
    planned_changes: List[Dict[str, str]] = field(default_factory=list)
    estimated_impact: str = "low"  # low, medium, high
    backup_required: bool = True
    dependencies_affected: List[str] = field(default_factory=list)


@dataclass
class ModificationResult:
    """Result of applying modifications to a project."""
    success: bool
    modified_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    backup_location: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)


# Enhanced A3 Integration Models

@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    function_name: str
    test_code: str
    expected_result: Optional[str] = None
    test_type: str = "unit"  # unit, integration, functional
    dependencies: List[str] = field(default_factory=list)


@dataclass
class IntelligentTestCase(TestCase):
    """Enhanced test case with specific input/output validation and AI-generated examples."""
    input_examples: List[Dict[str, Any]] = field(default_factory=list)
    expected_outputs: List[Any] = field(default_factory=list)
    test_description: str = ""
    validation_strategy: str = "exact_match"  # exact_match, type_check, custom
    ai_generated: bool = True
    
    def validate(self) -> None:
        """Validate the intelligent test case."""
        # Validate base TestCase fields
        if not self.name or not self.name.strip():
            raise ValidationError("Test case name cannot be empty")
        
        if not self.function_name or not self.function_name.strip():
            raise ValidationError("Function name cannot be empty")
        
        if not self.test_code or not self.test_code.strip():
            raise ValidationError("Test code cannot be empty")
        
        # Validate IntelligentTestCase specific fields
        if len(self.input_examples) != len(self.expected_outputs):
            raise ValidationError("Number of input examples must match number of expected outputs")
        
        # Validate validation strategy
        valid_strategies = {"exact_match", "type_check", "custom"}
        if self.validation_strategy not in valid_strategies:
            raise ValidationError(f"Invalid validation strategy '{self.validation_strategy}'. Must be one of: {valid_strategies}")
        
        # Validate input examples structure
        for i, example in enumerate(self.input_examples):
            if not isinstance(example, dict):
                raise ValidationError(f"Input example {i} must be a dictionary")
            
            # Check that all required keys are present
            if not example:
                raise ValidationError(f"Input example {i} cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the test case to a dictionary for persistence."""
        return {
            'name': self.name,
            'function_name': self.function_name,
            'test_code': self.test_code,
            'expected_result': self.expected_result,
            'test_type': self.test_type,
            'dependencies': self.dependencies,
            'input_examples': self.input_examples,
            'expected_outputs': self.expected_outputs,
            'test_description': self.test_description,
            'validation_strategy': self.validation_strategy,
            'ai_generated': self.ai_generated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntelligentTestCase':
        """Deserialize a test case from a dictionary."""
        return cls(
            name=data.get('name', ''),
            function_name=data.get('function_name', ''),
            test_code=data.get('test_code', ''),
            expected_result=data.get('expected_result'),
            test_type=data.get('test_type', 'unit'),
            dependencies=data.get('dependencies', []),
            input_examples=data.get('input_examples', []),
            expected_outputs=data.get('expected_outputs', []),
            test_description=data.get('test_description', ''),
            validation_strategy=data.get('validation_strategy', 'exact_match'),
            ai_generated=data.get('ai_generated', True)
        )
    
    def generate_test_code(self) -> str:
        """Generate executable test code from input examples and expected outputs."""
        if not self.input_examples or not self.expected_outputs:
            return self.test_code
        
        test_lines = []
        test_lines.append(f"def {self.name}():")
        test_lines.append(f'    """Test {self.function_name} with specific input/output examples."""')
        
        for i, (inputs, expected) in enumerate(zip(self.input_examples, self.expected_outputs)):
            test_lines.append(f"    # Test case {i + 1}: {self.test_description}")
            
            # Generate function call with inputs
            if isinstance(inputs, dict):
                args_str = ", ".join([f"{k}={repr(v)}" for k, v in inputs.items()])
            else:
                args_str = repr(inputs)
            
            test_lines.append(f"    result_{i} = {self.function_name}({args_str})")
            
            # Generate assertion based on validation strategy
            if self.validation_strategy == "exact_match":
                test_lines.append(f"    assert result_{i} == {repr(expected)}, f'Expected {repr(expected)}, got {{result_{i}}}'")
            elif self.validation_strategy == "type_check":
                expected_type = type(expected).__name__
                test_lines.append(f"    assert isinstance(result_{i}, {expected_type}), f'Expected {expected_type}, got {{type(result_{i}).__name__}}'")
            elif self.validation_strategy == "custom":
                # Use the provided test_code for custom validation
                test_lines.append(f"    # Custom validation")
                test_lines.append(f"    {self.test_code}")
            
            test_lines.append("")  # Empty line between test cases
        
        return "\n".join(test_lines)


@dataclass
class TestGenerationResult:
    """Result of test generation process."""
    generated_tests: List[TestCase]
    test_files_created: List[str]
    execution_result: Optional['TestExecutionResult'] = None
    success: bool = True
    errors: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate the test generation result."""
        if not isinstance(self.success, bool):
            raise ValidationError("Success must be a boolean value")
        
        if not self.success and not self.errors:
            raise ValidationError("Failed test generation must include error messages")
        
        for test_case in self.generated_tests:
            if not test_case.name or not test_case.function_name:
                raise ValidationError("Test cases must have valid names and function names")


@dataclass
class TestExecutionResult:
    """Result of test execution."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_details: List[TestDetail] = field(default_factory=list)
    coverage_report: Optional[CoverageReport] = None
    execution_time: float = 0.0
    
    def validate(self) -> None:
        """Validate the test execution result."""
        if self.total_tests < 0:
            raise ValidationError("Total tests cannot be negative")
        
        if self.passed_tests < 0 or self.failed_tests < 0:
            raise ValidationError("Test counts cannot be negative")
        
        if self.passed_tests + self.failed_tests != self.total_tests:
            raise ValidationError("Passed and failed tests must sum to total tests")
        
        if self.execution_time < 0:
            raise ValidationError("Execution time cannot be negative")


@dataclass
class CSVMetadata:
    """Metadata for CSV file analysis."""
    file_path: str
    columns: List[str]
    data_types: Dict[str, str]
    row_count: int
    sample_data: List[Dict[str, Any]] = field(default_factory=list)
    has_header: bool = True
    delimiter: str = ","
    encoding: str = "utf-8"
    
    def validate(self) -> None:
        """Validate CSV metadata."""
        if not self.file_path:
            raise ValidationError("CSV file path cannot be empty")
        
        if self.row_count < 0:
            raise ValidationError("Row count cannot be negative")
        
        if not self.columns:
            raise ValidationError("CSV must have at least one column")


@dataclass
class JSONMetadata:
    """Metadata for JSON file analysis."""
    file_path: str
    schema: Dict[str, Any]
    structure_type: str  # "object", "array", "primitive"
    sample_data: Optional[Dict[str, Any]] = None
    nested_levels: int = 0
    array_lengths: Dict[str, int] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate JSON metadata."""
        if not self.file_path:
            raise ValidationError("JSON file path cannot be empty")
        
        if self.nested_levels < 0:
            raise ValidationError("Nested levels cannot be negative")
        
        valid_types = ["object", "array", "primitive"]
        if self.structure_type not in valid_types:
            raise ValidationError(f"Structure type must be one of: {valid_types}")


@dataclass
class XMLMetadata:
    """Metadata for XML file analysis."""
    file_path: str
    root_element: str
    elements: List[str]
    attributes: Dict[str, List[str]]
    namespaces: Dict[str, str] = field(default_factory=dict)
    structure_depth: int = 0
    element_counts: Dict[str, int] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate XML metadata."""
        if not self.file_path:
            raise ValidationError("XML file path cannot be empty")
        
        if not self.root_element:
            raise ValidationError("XML must have a root element")
        
        if self.structure_depth < 0:
            raise ValidationError("Structure depth cannot be negative")


@dataclass
class ExcelMetadata:
    """Metadata for Excel file analysis."""
    file_path: str
    sheets: Dict[str, Dict[str, Any]]  # sheet_name -> {columns, data_types, row_count}
    workbook_info: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate Excel metadata."""
        if not self.file_path:
            raise ValidationError("Excel file path cannot be empty")
        
        if not self.sheets:
            raise ValidationError("Excel file must have at least one sheet")
        
        for sheet_name, sheet_data in self.sheets.items():
            if not sheet_name:
                raise ValidationError("Sheet names cannot be empty")
            
            if 'columns' not in sheet_data or 'row_count' not in sheet_data:
                raise ValidationError(f"Sheet {sheet_name} missing required metadata")


@dataclass
class DataSourceMetadata:
    """Unified metadata for analyzed data sources."""
    file_path: str
    file_type: str  # "csv", "json", "xml", "excel"
    schema: Dict[str, Any]
    sample_data: Optional[Dict[str, Any]] = None
    statistics: Dict[str, Any] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate data source metadata."""
        if not self.file_path:
            raise ValidationError("Data source file path cannot be empty")
        
        valid_types = ["csv", "json", "xml", "excel", "yaml"]
        if self.file_type not in valid_types:
            raise ValidationError(f"File type must be one of: {valid_types}")
        
        if not self.schema:
            raise ValidationError("Data source must have schema information")


@dataclass
class DataSourceAnalysis:
    """Complete analysis of data sources in a project."""
    csv_files: List[CSVMetadata] = field(default_factory=list)
    json_files: List[JSONMetadata] = field(default_factory=list)
    xml_files: List[XMLMetadata] = field(default_factory=list)
    excel_files: List[ExcelMetadata] = field(default_factory=list)
    unified_metadata: List[DataSourceMetadata] = field(default_factory=list)
    analysis_summary: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate data source analysis."""
        # Validate all individual metadata objects
        for csv_meta in self.csv_files:
            csv_meta.validate()
        
        for json_meta in self.json_files:
            json_meta.validate()
        
        for xml_meta in self.xml_files:
            xml_meta.validate()
        
        for excel_meta in self.excel_files:
            excel_meta.validate()
        
        for unified_meta in self.unified_metadata:
            unified_meta.validate()


@dataclass
class TableMetadata:
    """Metadata for a database table."""
    table_name: str
    schema_name: str
    columns: List[Dict[str, Any]]  # column_name, data_type, nullable, default, etc.
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]  # column -> referenced_table.column
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    row_count: Optional[int] = None
    
    def validate(self) -> None:
        """Validate table metadata."""
        if not self.table_name:
            raise ValidationError("Table name cannot be empty")
        
        if not self.schema_name:
            raise ValidationError("Schema name cannot be empty")
        
        if not self.columns:
            raise ValidationError("Table must have at least one column")
        
        # Validate column definitions
        column_names = set()
        for column in self.columns:
            if 'column_name' not in column or 'data_type' not in column:
                raise ValidationError("Column must have name and data type")
            
            col_name = column['column_name']
            if col_name in column_names:
                raise ValidationError(f"Duplicate column name: {col_name}")
            column_names.add(col_name)
        
        # Validate primary keys reference existing columns
        for pk in self.primary_keys:
            if pk not in column_names:
                raise ValidationError(f"Primary key {pk} not found in columns")


@dataclass
class Relationship:
    """Represents a relationship between database tables."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str  # "one_to_one", "one_to_many", "many_to_many"
    constraint_name: Optional[str] = None
    
    def validate(self) -> None:
        """Validate relationship."""
        if not all([self.from_table, self.from_column, self.to_table, self.to_column]):
            raise ValidationError("All relationship fields must be specified")
        
        valid_types = ["one_to_one", "one_to_many", "many_to_many"]
        if self.relationship_type not in valid_types:
            raise ValidationError(f"Relationship type must be one of: {valid_types}")


@dataclass
class IndexMetadata:
    """Metadata for a database index."""
    index_name: str
    table_name: str
    columns: List[str]
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = "btree"
    
    def validate(self) -> None:
        """Validate index metadata."""
        if not self.index_name or not self.table_name:
            raise ValidationError("Index and table names cannot be empty")
        
        if not self.columns:
            raise ValidationError("Index must have at least one column")


@dataclass
class ConstraintMetadata:
    """Metadata for a database constraint."""
    constraint_name: str
    table_name: str
    constraint_type: str  # "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK"
    columns: List[str]
    referenced_table: Optional[str] = None
    referenced_columns: Optional[List[str]] = None
    check_condition: Optional[str] = None
    
    def validate(self) -> None:
        """Validate constraint metadata."""
        if not self.constraint_name or not self.table_name:
            raise ValidationError("Constraint and table names cannot be empty")
        
        valid_types = ["PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "NOT NULL"]
        if self.constraint_type not in valid_types:
            raise ValidationError(f"Constraint type must be one of: {valid_types}")
        
        if not self.columns:
            raise ValidationError("Constraint must have at least one column")


@dataclass
class DatabaseSchema:
    """Complete PostgreSQL database schema information."""
    database_name: str
    tables: List[TableMetadata]
    relationships: List[Relationship]
    indexes: List[IndexMetadata]
    constraints: List[ConstraintMetadata]
    schemas: List[str] = field(default_factory=list)
    connection_info: Dict[str, Any] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate database schema."""
        if not self.database_name:
            raise ValidationError("Database name cannot be empty")
        
        if not self.tables:
            raise ValidationError("Database must have at least one table")
        
        # Validate all components
        table_names = set()
        for table in self.tables:
            table.validate()
            full_name = f"{table.schema_name}.{table.table_name}"
            if full_name in table_names:
                raise ValidationError(f"Duplicate table: {full_name}")
            table_names.add(full_name)
        
        for relationship in self.relationships:
            relationship.validate()
        
        for index in self.indexes:
            index.validate()
        
        for constraint in self.constraints:
            constraint.validate()


@dataclass
class DatabaseModel:
    """Generated database model class."""
    class_name: str
    table_name: str
    schema_name: str
    attributes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    methods: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate database model."""
        if not self.class_name or not self.table_name:
            raise ValidationError("Class name and table name cannot be empty")
        
        if not self.attributes:
            raise ValidationError("Database model must have at least one attribute")


@dataclass
class PackageInfo:
    """Information about a package and its usage."""
    name: str
    standard_alias: Optional[str] = None
    import_statement: str = ""
    version: Optional[str] = None
    usage_count: int = 0
    modules_using: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate package info."""
        if not self.name:
            raise ValidationError("Package name cannot be empty")
        
        if self.usage_count < 0:
            raise ValidationError("Usage count cannot be negative")


@dataclass
class PackageRegistry:
    """Registry of package usage and aliases."""
    packages: Dict[str, PackageInfo] = field(default_factory=dict)
    standard_aliases: Dict[str, str] = field(default_factory=dict)
    module_imports: Dict[str, List[str]] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize with standard aliases."""
        if not self.standard_aliases:
            self.standard_aliases = {
                "pandas": "pd",
                "numpy": "np",
                "matplotlib.pyplot": "plt",
                "seaborn": "sns",
                "tensorflow": "tf",
                "torch": "torch",
                "requests": "requests",
                "json": "json",
                "os": "os",
                "sys": "sys",
                "pathlib": "Path",
                "datetime": "datetime",
                "typing": "typing",
                "dataclasses": "dataclass",
                "abc": "ABC",
                "collections": "collections",
                "itertools": "itertools",
                "functools": "functools",
                "operator": "operator",
                "re": "re",
                "math": "math",
                "random": "random",
                "sqlite3": "sqlite3",
                "psycopg2": "psycopg2",
                "sqlalchemy": "sqlalchemy"
            }
    
    def validate(self) -> None:
        """Validate package registry."""
        for package_name, package_info in self.packages.items():
            if package_name != package_info.name:
                raise ValidationError(f"Package key {package_name} doesn't match package name {package_info.name}")
            package_info.validate()


# Enhanced Integration Result
@dataclass
class IntegrationResult:
    """Enhanced integration result with test information."""
    integrated_modules: List[str]
    import_errors: List[str]
    success: bool
    test_result: Optional[TestGenerationResult] = None
    package_updates: Optional[List[str]] = None
    integration_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate integration result."""
        if not isinstance(self.success, bool):
            raise ValidationError("Success must be a boolean value")
        
        if self.integration_time < 0:
            raise ValidationError("Integration time cannot be negative")
        
        if self.test_result:
            self.test_result.validate()


# Enhanced A3 Exception Classes
class A3Error(Exception):
    """Base exception for A3 system errors."""
    pass


class TestGenerationError(A3Error):
    """Exception for test generation failures."""
    pass


class DatabaseConnectionError(A3Error):
    """Exception for database connection issues."""
    pass


class DataSourceAnalysisError(A3Error):
    """Exception for data source analysis failures."""
    pass


class PackageManagementError(A3Error):
    """Exception for package management issues."""
    pass


class DatabaseAnalysisError(A3Error):
    """Exception for database analysis failures."""
    pass


class ImportConsistencyError(A3Error):
    """Exception for import consistency validation failures."""
    pass


@dataclass
class PackageInfo:
    """Information about a package and its usage."""
    name: str
    standard_alias: str
    version: Optional[str] = None
    modules_using: List[str] = field(default_factory=list)
    import_count: int = 0
    last_used: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the package information."""
        if not self.name or not self.name.strip():
            raise ValidationError("Package name cannot be empty")
        
        if not self.standard_alias or not self.standard_alias.strip():
            raise ValidationError("Package standard alias cannot be empty")
        
        if self.import_count < 0:
            raise ValidationError("Import count cannot be negative")
        
        # Validate package name format (allow dots and hyphens)
        if not re.match(r'^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$', self.name):
            raise ValidationError(f"Invalid package name '{self.name}': must be a valid package identifier")


@dataclass
class PackageRegistry:
    """Registry of package usage and aliases."""
    packages: Dict[str, PackageInfo] = field(default_factory=dict)
    standard_aliases: Dict[str, str] = field(default_factory=dict)
    module_imports: Dict[str, List[str]] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    project_path: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the package registry."""
        # Validate all package info
        for package_name, package_info in self.packages.items():
            package_info.validate()
            if package_name != package_info.name:
                raise ValidationError(f"Package key '{package_name}' doesn't match package name '{package_info.name}'")
        
        # Validate standard aliases
        for package_name, alias in self.standard_aliases.items():
            if not package_name or not package_name.strip():
                raise ValidationError("Package name in standard aliases cannot be empty")
            if not alias or not alias.strip():
                raise ValidationError("Alias in standard aliases cannot be empty")
        
        # Validate module imports
        for module_name, imports in self.module_imports.items():
            if not module_name or not module_name.strip():
                raise ValidationError("Module name in module imports cannot be empty")
            for import_stmt in imports:
                if not import_stmt or not import_stmt.strip():
                    raise ValidationError("Import statement cannot be empty")
        
        # Validate requirements format
        for req in self.requirements:
            if not req or not req.strip():
                raise ValidationError("Requirement cannot be empty")
    
    def add_package(self, package_info: PackageInfo) -> None:
        """Add a package to the registry."""
        package_info.validate()
        self.packages[package_info.name] = package_info
        self.standard_aliases[package_info.name] = package_info.standard_alias
        self.last_updated = datetime.now()
    
    def get_package(self, package_name: str) -> Optional[PackageInfo]:
        """Get package information by name."""
        return self.packages.get(package_name)
    
    def get_standard_alias(self, package_name: str) -> Optional[str]:
        """Get the standard alias for a package."""
        return self.standard_aliases.get(package_name)
    
    def register_usage(self, package_name: str, module_name: str) -> None:
        """Register package usage in a module."""
        if package_name in self.packages:
            package_info = self.packages[package_name]
            if module_name not in package_info.modules_using:
                package_info.modules_using.append(module_name)
            package_info.import_count += 1
            package_info.last_used = datetime.now()
            self.last_updated = datetime.now()
    
    def get_modules_using_package(self, package_name: str) -> List[str]:
        """Get list of modules using a specific package."""
        package_info = self.packages.get(package_name)
        return package_info.modules_using if package_info else []
    
    def get_packages_for_module(self, module_name: str) -> List[str]:
        """Get list of packages used by a specific module."""
        packages = []
        for package_name, package_info in self.packages.items():
            if module_name in package_info.modules_using:
                packages.append(package_name)
        return packages

# Database-related models for PostgreSQL integration

@dataclass
class ColumnMetadata:
    """Metadata for a database column."""
    name: str
    data_type: str
    is_nullable: bool = True
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    description: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the column metadata."""
        if not self.name or not self.name.strip():
            raise ValidationError("Column name cannot be empty")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.name):
            raise ValidationError(f"Invalid column name '{self.name}': must be a valid identifier")
        
        if not self.data_type or not self.data_type.strip():
            raise ValidationError("Column data type cannot be empty")
        
        if self.max_length is not None and self.max_length <= 0:
            raise ValidationError("Column max_length must be positive")
        
        if self.precision is not None and self.precision <= 0:
            raise ValidationError("Column precision must be positive")
        
        if self.scale is not None and self.scale < 0:
            raise ValidationError("Column scale cannot be negative")
        
        if self.is_foreign_key:
            if not self.foreign_key_table:
                raise ValidationError("Foreign key column must specify foreign_key_table")
            if not self.foreign_key_column:
                raise ValidationError("Foreign key column must specify foreign_key_column")


@dataclass
class IndexMetadata:
    """Metadata for a database index."""
    name: str
    table_name: str
    columns: List[str] = field(default_factory=list)
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = "btree"
    description: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the index metadata."""
        if not self.name or not self.name.strip():
            raise ValidationError("Index name cannot be empty")
        
        if not self.table_name or not self.table_name.strip():
            raise ValidationError("Index table name cannot be empty")
        
        if not self.columns:
            raise ValidationError("Index must have at least one column")
        
        for column in self.columns:
            if not column or not column.strip():
                raise ValidationError("Index column name cannot be empty")


@dataclass
class ConstraintMetadata:
    """Metadata for a database constraint."""
    name: str
    table_name: str
    constraint_type: str  # PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
    columns: List[str] = field(default_factory=list)
    referenced_table: Optional[str] = None
    referenced_columns: Optional[List[str]] = None
    check_clause: Optional[str] = None
    description: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the constraint metadata."""
        if not self.name or not self.name.strip():
            raise ValidationError("Constraint name cannot be empty")
        
        if not self.table_name or not self.table_name.strip():
            raise ValidationError("Constraint table name cannot be empty")
        
        valid_types = ["PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "NOT NULL"]
        if self.constraint_type not in valid_types:
            raise ValidationError(f"Invalid constraint type '{self.constraint_type}'. Must be one of: {valid_types}")
        
        if not self.columns:
            raise ValidationError("Constraint must have at least one column")
        
        if self.constraint_type == "FOREIGN KEY":
            if not self.referenced_table:
                raise ValidationError("Foreign key constraint must specify referenced_table")
            if not self.referenced_columns:
                raise ValidationError("Foreign key constraint must specify referenced_columns")


@dataclass
class TableMetadata:
    """Metadata for a database table."""
    name: str
    schema: str = "public"
    columns: List[ColumnMetadata] = field(default_factory=list)
    indexes: List[IndexMetadata] = field(default_factory=list)
    constraints: List[ConstraintMetadata] = field(default_factory=list)
    row_count: Optional[int] = None
    table_size: Optional[str] = None
    description: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the table metadata."""
        if not self.name or not self.name.strip():
            raise ValidationError("Table name cannot be empty")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.name):
            raise ValidationError(f"Invalid table name '{self.name}': must be a valid identifier")
        
        if not self.schema or not self.schema.strip():
            raise ValidationError("Table schema cannot be empty")
        
        if not self.columns:
            raise ValidationError("Table must have at least one column")
        
        # Validate all columns
        column_names = set()
        for column in self.columns:
            column.validate()
            if column.name in column_names:
                raise ValidationError(f"Duplicate column name '{column.name}' in table '{self.name}'")
            column_names.add(column.name)
        
        # Validate all indexes
        for index in self.indexes:
            index.validate()
            # Ensure index columns exist in table
            for col_name in index.columns:
                if col_name not in column_names:
                    raise ValidationError(f"Index '{index.name}' references non-existent column '{col_name}'")
        
        # Validate all constraints
        for constraint in self.constraints:
            constraint.validate()
            # Ensure constraint columns exist in table
            for col_name in constraint.columns:
                if col_name not in column_names:
                    raise ValidationError(f"Constraint '{constraint.name}' references non-existent column '{col_name}'")
        
        if self.row_count is not None and self.row_count < 0:
            raise ValidationError("Table row count cannot be negative")
    
    def get_primary_key_columns(self) -> List[str]:
        """Get the primary key columns for this table."""
        pk_columns = []
        for column in self.columns:
            if column.is_primary_key:
                pk_columns.append(column.name)
        return pk_columns
    
    def get_foreign_key_columns(self) -> List[ColumnMetadata]:
        """Get all foreign key columns for this table."""
        return [col for col in self.columns if col.is_foreign_key]
    
    def get_column(self, column_name: str) -> Optional[ColumnMetadata]:
        """Get a specific column by name."""
        for column in self.columns:
            if column.name == column_name:
                return column
        return None


@dataclass
class Relationship:
    """Represents a relationship between database tables."""
    from_table: str
    to_table: str
    from_columns: List[str] = field(default_factory=list)
    to_columns: List[str] = field(default_factory=list)
    relationship_type: str = "FOREIGN_KEY"  # FOREIGN_KEY, ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY
    constraint_name: Optional[str] = None
    description: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the relationship."""
        if not self.from_table or not self.from_table.strip():
            raise ValidationError("Relationship from_table cannot be empty")
        
        if not self.to_table or not self.to_table.strip():
            raise ValidationError("Relationship to_table cannot be empty")
        
        if not self.from_columns:
            raise ValidationError("Relationship must have at least one from_column")
        
        if not self.to_columns:
            raise ValidationError("Relationship must have at least one to_column")
        
        if len(self.from_columns) != len(self.to_columns):
            raise ValidationError("Relationship must have equal number of from_columns and to_columns")
        
        valid_types = ["FOREIGN_KEY", "ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_MANY"]
        if self.relationship_type not in valid_types:
            raise ValidationError(f"Invalid relationship type '{self.relationship_type}'. Must be one of: {valid_types}")


@dataclass
class DatabaseSchema:
    """Complete database schema information."""
    database_name: str
    host: str = "localhost"
    port: int = 5432
    username: Optional[str] = None
    tables: List[TableMetadata] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    schemas: List[str] = field(default_factory=lambda: ["public"])
    version: Optional[str] = None
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the database schema."""
        if not self.database_name or not self.database_name.strip():
            raise ValidationError("Database name cannot be empty")
        
        if not self.host or not self.host.strip():
            raise ValidationError("Database host cannot be empty")
        
        if not (1 <= self.port <= 65535):
            raise ValidationError("Database port must be between 1 and 65535")
        
        if not self.schemas:
            raise ValidationError("Database must have at least one schema")
        
        # Validate all tables
        table_names = set()
        for table in self.tables:
            table.validate()
            full_name = f"{table.schema}.{table.name}"
            if full_name in table_names:
                raise ValidationError(f"Duplicate table '{full_name}' in database schema")
            table_names.add(full_name)
        
        # Validate all relationships
        for relationship in self.relationships:
            relationship.validate()
            # Ensure referenced tables exist
            from_table_exists = any(t.name == relationship.from_table for t in self.tables)
            to_table_exists = any(t.name == relationship.to_table for t in self.tables)
            
            if not from_table_exists:
                raise ValidationError(f"Relationship references non-existent from_table '{relationship.from_table}'")
            if not to_table_exists:
                raise ValidationError(f"Relationship references non-existent to_table '{relationship.to_table}'")
    
    def get_table(self, table_name: str, schema: str = "public") -> Optional[TableMetadata]:
        """Get a specific table by name and schema."""
        for table in self.tables:
            if table.name == table_name and table.schema == schema:
                return table
        return None
    
    def get_tables_in_schema(self, schema: str) -> List[TableMetadata]:
        """Get all tables in a specific schema."""
        return [table for table in self.tables if table.schema == schema]
    
    def get_relationships_for_table(self, table_name: str) -> List[Relationship]:
        """Get all relationships involving a specific table."""
        return [rel for rel in self.relationships 
                if rel.from_table == table_name or rel.to_table == table_name]


@dataclass
class DatabaseConnection:
    """Represents a database connection with metadata."""
    connection_string: str
    host: str
    port: int
    database: str
    username: str
    password: str = field(repr=False)  # Don't include in repr for security
    schema: str = "public"
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    is_connected: bool = False
    connection_pool_size: int = 5
    max_overflow: int = 10
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    
    def validate(self) -> None:
        """Validate the database connection parameters."""
        if not self.connection_string or not self.connection_string.strip():
            raise ValidationError("Connection string cannot be empty")
        
        if not self.host or not self.host.strip():
            raise ValidationError("Database host cannot be empty")
        
        if not (1 <= self.port <= 65535):
            raise ValidationError("Database port must be between 1 and 65535")
        
        if not self.database or not self.database.strip():
            raise ValidationError("Database name cannot be empty")
        
        if not self.username or not self.username.strip():
            raise ValidationError("Database username cannot be empty")
        
        if not self.password:
            raise ValidationError("Database password cannot be empty")
        
        if self.connection_timeout <= 0:
            raise ValidationError("Connection timeout must be positive")
        
        if self.connection_pool_size <= 0:
            raise ValidationError("Connection pool size must be positive")
        
        if self.max_overflow < 0:
            raise ValidationError("Max overflow cannot be negative")
        
        valid_ssl_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if self.ssl_mode not in valid_ssl_modes:
            raise ValidationError(f"Invalid SSL mode '{self.ssl_mode}'. Must be one of: {valid_ssl_modes}")
    
    def get_safe_connection_string(self) -> str:
        """Get connection string with password masked for logging."""
        return self.connection_string.replace(self.password, "***")


@dataclass
class DatabaseModel:
    """Generated database model class information."""
    table_name: str
    class_name: str
    module_name: str
    file_path: str
    fields: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    generated_code: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the database model."""
        if not self.table_name or not self.table_name.strip():
            raise ValidationError("Database model table_name cannot be empty")
        
        if not self.class_name or not self.class_name.strip():
            raise ValidationError("Database model class_name cannot be empty")
        
        if not re.match(r'^[A-Z][a-zA-Z0-9_]*$', self.class_name):
            raise ValidationError(f"Invalid class name '{self.class_name}': must be a valid Python class name")
        
        if not self.module_name or not self.module_name.strip():
            raise ValidationError("Database model module_name cannot be empty")
        
        if not self.file_path or not self.file_path.strip():
            raise ValidationError("Database model file_path cannot be empty")
        
        if not self.file_path.endswith('.py'):
            raise ValidationError("Database model file_path must end with .py")


@dataclass
class DatabaseAnalysisResult:
    """Result of database analysis operation."""
    success: bool
    schema: Optional[DatabaseSchema] = None
    models: List[DatabaseModel] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    analysis_duration: float = 0.0
    tables_analyzed: int = 0
    relationships_found: int = 0
    generated_files: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate the database analysis result."""
        if self.success and self.schema is None:
            raise ValidationError("Successful analysis must include schema")
        
        if self.schema:
            self.schema.validate()
        
        for model in self.models:
            model.validate()
        
        if self.analysis_duration < 0:
            raise ValidationError("Analysis duration cannot be negative")
        
        if self.tables_analyzed < 0:
            raise ValidationError("Tables analyzed count cannot be negative")
        
        if self.relationships_found < 0:
            raise ValidationError("Relationships found count cannot be negative")


@dataclass
class DatabaseConnectionError(Exception):
    """Exception for database connection issues."""
    message: str
    connection_string: Optional[str] = None
    error_code: Optional[str] = None
    troubleshooting_tips: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return self.message


@dataclass
class ImportIssue:
    """Represents an import issue detected in code."""
    file_path: str
    line_number: int
    issue_type: ImportIssueType
    problematic_import: str
    suggested_fix: str
    context: str = ""
    
    def validate(self) -> None:
        """Validate the import issue specification."""
        if not self.file_path or not self.file_path.strip():
            raise ValidationError("Import issue file path cannot be empty")
        
        if self.line_number < 1:
            raise ValidationError("Line number must be positive")
        
        if not self.problematic_import or not self.problematic_import.strip():
            raise ValidationError("Problematic import cannot be empty")
        
        if not self.suggested_fix or not self.suggested_fix.strip():
            raise ValidationError("Suggested fix cannot be empty")





@dataclass
class FunctionGap:
    """Represents a missing function identified through dependency analysis."""
    suggested_name: str
    suggested_module: str
    reason: str
    confidence: float
    dependencies: List[str] = field(default_factory=list)  # Functions that would depend on this
    dependents: List[str] = field(default_factory=list)    # Functions this would depend on
    
    def validate(self) -> None:
        """Validate the function gap specification."""
        if not self.suggested_name or not self.suggested_name.strip():
            raise ValidationError("Function gap suggested name cannot be empty")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.suggested_name):
            raise ValidationError(f"Invalid function name '{self.suggested_name}': must be a valid Python identifier")
        
        if not self.suggested_module or not self.suggested_module.strip():
            raise ValidationError("Function gap suggested module cannot be empty")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', self.suggested_module):
            raise ValidationError(f"Invalid module name '{self.suggested_module}': must be a valid Python module identifier")
        
        if not self.reason or not self.reason.strip():
            raise ValidationError("Function gap reason cannot be empty")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("Function gap confidence must be between 0.0 and 1.0")
        
        # Validate dependency function names
        for dep in self.dependencies + self.dependents:
            if not dep or not dep.strip():
                raise ValidationError("Dependency function name cannot be empty")
            # Allow module.function format
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*\.[a-zA-Z_][a-zA-Z0-9_]*$', dep):
                raise ValidationError(f"Invalid dependency function format '{dep}': must be 'module.function'")


@dataclass
class OptimizationSuggestion:
    """Represents a suggestion for optimizing project structure."""
    suggestion_type: str
    description: str
    affected_modules: List[str] = field(default_factory=list)
    affected_functions: List[str] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high
    estimated_effort: str = "unknown"  # small, medium, large, unknown
    
    def validate(self) -> None:
        """Validate the optimization suggestion."""
        if not self.suggestion_type or not self.suggestion_type.strip():
            raise ValidationError("Optimization suggestion type cannot be empty")
        
        if not self.description or not self.description.strip():
            raise ValidationError("Optimization suggestion description cannot be empty")
        
        valid_priorities = {"low", "medium", "high"}
        if self.priority not in valid_priorities:
            raise ValidationError(f"Priority must be one of {valid_priorities}")
        
        valid_efforts = {"small", "medium", "large", "unknown"}
        if self.estimated_effort not in valid_efforts:
            raise ValidationError(f"Estimated effort must be one of {valid_efforts}")


@dataclass
class StructureAnalysis:
    """Comprehensive analysis of existing project structure for enhanced planning."""
    existing_modules: List[Module] = field(default_factory=list)
    enhanced_graph: Optional[EnhancedDependencyGraph] = None
    complexity_metrics: Dict[str, Any] = field(default_factory=dict)
    missing_functions: List[FunctionGap] = field(default_factory=list)
    import_issues: List[ImportIssue] = field(default_factory=list)
    optimization_opportunities: List[OptimizationSuggestion] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the structure analysis."""
        # Validate all existing modules
        module_names = set()
        for module in self.existing_modules:
            module.validate()
            if module.name in module_names:
                raise ValidationError(f"Duplicate module name '{module.name}' in structure analysis")
            module_names.add(module.name)
        
        # Validate enhanced graph if present
        if self.enhanced_graph is not None:
            # Basic validation - the enhanced graph has its own validation methods
            if not isinstance(self.enhanced_graph, EnhancedDependencyGraph):
                raise ValidationError("Enhanced graph must be an EnhancedDependencyGraph instance")
        
        # Validate missing functions
        function_names = set()
        for gap in self.missing_functions:
            gap.validate()
            gap_key = f"{gap.suggested_module}.{gap.suggested_name}"
            if gap_key in function_names:
                raise ValidationError(f"Duplicate function gap '{gap_key}' in structure analysis")
            function_names.add(gap_key)
        
        # Validate import issues
        for issue in self.import_issues:
            issue.validate()
        
        # Validate optimization opportunities
        for suggestion in self.optimization_opportunities:
            suggestion.validate()
        
        # Validate complexity metrics structure
        if not isinstance(self.complexity_metrics, dict):
            raise ValidationError("Complexity metrics must be a dictionary")
    
    def get_total_functions(self) -> int:
        """Get total number of functions across all modules."""
        return sum(len(module.functions) for module in self.existing_modules)
    
    def get_modules_with_issues(self) -> List[str]:
        """Get list of module names that have import issues."""
        modules_with_issues = set()
        for issue in self.import_issues:
            # Extract module name from file path
            if '/' in issue.file_path:
                module_name = issue.file_path.split('/')[-1].replace('.py', '')
            else:
                module_name = issue.file_path.replace('.py', '')
            modules_with_issues.add(module_name)
        return list(modules_with_issues)
    
    def get_high_priority_gaps(self, min_confidence: float = 0.7) -> List[FunctionGap]:
        """Get function gaps with high confidence scores."""
        return [gap for gap in self.missing_functions if gap.confidence >= min_confidence]
    
    def get_critical_optimization_suggestions(self) -> List[OptimizationSuggestion]:
        """Get optimization suggestions marked as high priority."""
        return [suggestion for suggestion in self.optimization_opportunities 
                if suggestion.priority == "high"]


@dataclass
class CriticalPathAnalysis:
    """Analysis of the critical path in the dependency graph."""
    critical_path: List[str] = field(default_factory=list)
    path_length: int = 0
    bottleneck_functions: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    parallel_opportunities: List[List[str]] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> None:
        """Validate the critical path analysis."""
        if self.path_length < 0:
            raise ValidationError("Path length cannot be negative")
        
        if self.path_length != len(self.critical_path):
            raise ValidationError("Path length must match critical path length")
        
        # Validate that all functions in critical path are valid identifiers
        for func_name in self.critical_path:
            if not func_name or not isinstance(func_name, str):
                raise ValidationError("Critical path function names must be non-empty strings")
            
            # Check for valid module.function format
            if '.' not in func_name:
                raise ValidationError(f"Function name '{func_name}' must be in module.function format")
        
        # Validate bottleneck functions
        for func_name in self.bottleneck_functions:
            if not func_name or not isinstance(func_name, str):
                raise ValidationError("Bottleneck function names must be non-empty strings")
        
        # Validate parallel opportunities structure
        for opportunity in self.parallel_opportunities:
            if not isinstance(opportunity, list):
                raise ValidationError("Each parallel opportunity must be a list of function names")
            
            for func_name in opportunity:
                if not func_name or not isinstance(func_name, str):
                    raise ValidationError("Function names in parallel opportunities must be non-empty strings")
    
    def get_critical_bottlenecks(self) -> List[str]:
        """Get bottleneck functions that are on the critical path."""
        return [func for func in self.bottleneck_functions if func in self.critical_path]
    
    def has_parallel_opportunities(self) -> bool:
        """Check if there are any parallel implementation opportunities."""
        return len(self.parallel_opportunities) > 0
    
    def get_optimization_priority(self) -> str:
        """Get the priority level for optimizing this critical path."""
        if self.path_length > 10:
            return "high"
        elif self.path_length > 5:
            return "medium"
        else:
            return "low"