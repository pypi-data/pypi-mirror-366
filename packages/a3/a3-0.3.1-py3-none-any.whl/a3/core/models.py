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


@dataclass
class ValidationResult:
    """Result of project state validation."""
    is_valid: bool = False
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


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