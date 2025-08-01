"""
Dependency analyzer implementation for AI Project Builder.

This module provides the DependencyAnalyzer class that analyzes module
dependencies, detects circular dependencies, and determines build order.
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque

from .base import BaseDependencyAnalyzer
from ..core.models import Module, ValidationResult, DependencyGraph


class DependencyAnalysisError(Exception):
    """Base exception for dependency analysis errors."""
    pass


class CircularDependencyError(DependencyAnalysisError):
    """Exception raised when circular dependencies are detected."""
    
    def __init__(self, message: str, cycles: List[List[str]]):
        super().__init__(message)
        self.cycles = cycles


class DependencyAnalyzer(BaseDependencyAnalyzer):
    """
    Analyzer for module dependencies and relationships.
    
    Provides comprehensive dependency analysis including cycle detection,
    build order determination, and dependency validation.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the dependency analyzer.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        self._dependency_cache: Dict[str, Set[str]] = {}
        self._reverse_dependency_cache: Dict[str, Set[str]] = {}
    
    def analyze_dependencies(self, modules: List[Module]) -> ValidationResult:
        """
        Analyze module dependencies for issues.
        
        Args:
            modules: List of modules to analyze
            
        Returns:
            ValidationResult with analysis results
        """
        if not modules:
            return ValidationResult(
                is_valid=True,
                issues=[],
                warnings=["No modules provided for analysis"]
            )
        
        issues = []
        warnings = []
        
        try:
            # Build dependency maps
            self._build_dependency_maps(modules)
            
            # Check for missing dependencies
            missing_deps = self._find_missing_dependencies(modules)
            if missing_deps:
                for module, missing in missing_deps.items():
                    issues.append(f"Module '{module}' has missing dependencies: {missing}")
            
            # Check for circular dependencies
            cycles = self.detect_circular_dependencies(modules)
            if cycles:
                for cycle in cycles:
                    issues.append(f"Circular dependency detected: {' -> '.join(cycle + [cycle[0]])}")
            
            # Check for self-dependencies
            self_deps = self._find_self_dependencies(modules)
            if self_deps:
                for module in self_deps:
                    issues.append(f"Module '{module}' depends on itself")
            
            # Check for redundant dependencies
            redundant_deps = self._find_redundant_dependencies(modules)
            if redundant_deps:
                for module, redundant in redundant_deps.items():
                    warnings.append(f"Module '{module}' has redundant dependencies: {redundant}")
            
            # Check dependency depth
            deep_deps = self._find_deep_dependencies(modules, max_depth=5)
            if deep_deps:
                for module, depth in deep_deps.items():
                    warnings.append(f"Module '{module}' has deep dependency chain (depth: {depth})")
            
            return ValidationResult(
                is_valid=len(issues) == 0,
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[f"Dependency analysis failed: {str(e)}"],
                warnings=[]
            )
    
    def detect_circular_dependencies(self, modules: List[Module]) -> List[List[str]]:
        """
        Detect circular dependency chains using Tarjan's algorithm.
        
        Args:
            modules: List of modules to analyze
            
        Returns:
            List of circular dependency chains (each chain is a list of module names)
        """
        if not modules:
            return []
        
        # Build adjacency list
        graph = self._build_adjacency_list(modules)
        
        # Use Tarjan's algorithm to find strongly connected components
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        cycles = []
        
        def strongconnect(node: str):
            # Set the depth index for this node to the smallest unused index
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True
            
            # Consider successors of node
            for successor in graph.get(node, []):
                if successor not in index:
                    # Successor has not yet been visited; recurse on it
                    strongconnect(successor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[successor])
                elif on_stack.get(successor, False):
                    # Successor is in stack and hence in the current SCC
                    lowlinks[node] = min(lowlinks[node], index[successor])
            
            # If node is a root node, pop the stack and create an SCC
            if lowlinks[node] == index[node]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == node:
                        break
                
                # Only add components with more than one node (actual cycles)
                if len(component) > 1:
                    cycles.append(component)
        
        # Find all strongly connected components
        for node in graph:
            if node not in index:
                strongconnect(node)
        
        return cycles
    
    def get_build_order(self, modules: List[Module]) -> List[str]:
        """
        Get the optimal order for building/processing modules using topological sort.
        
        Args:
            modules: List of modules to order
            
        Returns:
            List of module names in build order (dependencies first)
        """
        if not modules:
            return []
        
        # Check for cycles first
        cycles = self.detect_circular_dependencies(modules)
        if cycles:
            raise CircularDependencyError(
                f"Cannot determine build order due to circular dependencies: {cycles}",
                cycles
            )
        
        # Build reverse adjacency list for build order (dependencies -> dependents)
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        all_nodes = {module.name for module in modules}
        
        # Initialize in-degree for all nodes
        for node in all_nodes:
            in_degree[node] = 0
        
        # Build graph where edges go from dependencies to dependents
        for module in modules:
            for dependency in module.dependencies:
                if dependency in all_nodes:
                    graph[dependency].append(module.name)
                    in_degree[module.name] += 1
        
        # Kahn's algorithm for topological sorting
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Remove edges from this node
            for neighbor in graph.get(node, []):
                if neighbor in all_nodes:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # Verify all nodes were processed
        if len(result) != len(all_nodes):
            remaining = all_nodes - set(result)
            raise DependencyAnalysisError(f"Could not determine build order for modules: {remaining}")
        
        return result  
  
    def get_dependency_map(self, modules: List[Module]) -> Dict[str, Set[str]]:
        """
        Get complete dependency mapping for all modules.
        
        Args:
            modules: List of modules to analyze
            
        Returns:
            Dictionary mapping module names to their dependencies
        """
        self._build_dependency_maps(modules)
        return dict(self._dependency_cache)
    
    def get_reverse_dependency_map(self, modules: List[Module]) -> Dict[str, Set[str]]:
        """
        Get reverse dependency mapping (what depends on each module).
        
        Args:
            modules: List of modules to analyze
            
        Returns:
            Dictionary mapping module names to modules that depend on them
        """
        self._build_dependency_maps(modules)
        return dict(self._reverse_dependency_cache)
    
    def get_transitive_dependencies(self, module_name: str, modules: List[Module]) -> Set[str]:
        """
        Get all transitive dependencies for a module.
        
        Args:
            module_name: Name of the module
            modules: List of all modules
            
        Returns:
            Set of all transitive dependency names
        """
        self._build_dependency_maps(modules)
        
        visited = set()
        to_visit = [module_name]
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            
            visited.add(current)
            dependencies = self._dependency_cache.get(current, set())
            
            for dep in dependencies:
                if dep not in visited:
                    to_visit.append(dep)
        
        # Remove the original module from the result
        visited.discard(module_name)
        return visited
    
    def _build_dependency_maps(self, modules: List[Module]) -> None:
        """Build internal dependency and reverse dependency maps."""
        self._dependency_cache.clear()
        self._reverse_dependency_cache.clear()
        
        # Initialize maps
        for module in modules:
            self._dependency_cache[module.name] = set(module.dependencies)
            self._reverse_dependency_cache[module.name] = set()
        
        # Build reverse dependencies
        for module in modules:
            for dep in module.dependencies:
                if dep in self._reverse_dependency_cache:
                    self._reverse_dependency_cache[dep].add(module.name)
    
    def _build_adjacency_list(self, modules: List[Module]) -> Dict[str, List[str]]:
        """Build adjacency list representation of the dependency graph."""
        graph = defaultdict(list)
        
        for module in modules:
            graph[module.name] = list(module.dependencies)
        
        return dict(graph)
    
    def _find_missing_dependencies(self, modules: List[Module]) -> Dict[str, List[str]]:
        """Find modules with dependencies that don't exist."""
        module_names = {module.name for module in modules}
        
        # Create comprehensive mappings for nested structure support
        file_path_to_name = {}
        dotted_names = set()
        
        for module in modules:
            # Add the module's actual name
            dotted_names.add(module.name)
            
            # Convert file path to potential module name
            # e.g., "src/parsers/html_parser.py" -> "parsers.html_parser"
            if '/' in module.file_path:
                path_parts = module.file_path.replace('.py', '').split('/')
                # Skip common prefixes like 'src'
                if path_parts[0] in ['src', 'lib', 'app']:
                    path_parts = path_parts[1:]
                dotted_name = '.'.join(path_parts)
                file_path_to_name[dotted_name] = module.name
                dotted_names.add(dotted_name)
            
            # Also handle the case where module.name is already dotted
            if '.' in module.name:
                dotted_names.add(module.name)
        
        # Standard library and common third-party modules to allow
        allowed_modules = {
            'os', 'sys', 'json', 're', 'math', 'typing', 'pathlib', 'datetime',
            'collections', 'itertools', 'functools', 'operator', 'copy', 'pickle',
            'urllib', 'http', 'html', 'xml', 'csv', 'sqlite3', 'logging',
            'requests', 'beautifulsoup4', 'bs4', 'lxml', 'pandas', 'numpy'
        }
        
        missing_deps = {}
        
        for module in modules:
            missing = []
            for dep in module.dependencies:
                # Check if dependency exists as module name
                if dep in module_names:
                    continue
                # Check if dependency exists in our dotted names set
                elif dep in dotted_names:
                    continue
                # Check if dependency exists as a file path mapping
                elif dep in file_path_to_name:
                    continue
                # Check if it's an allowed module
                elif dep in allowed_modules:
                    continue
                # Check if it's a submodule of an allowed module (e.g., 'os.path')
                elif any(dep.startswith(allowed + '.') for allowed in allowed_modules):
                    continue
                else:
                    missing.append(dep)
            
            if missing:
                missing_deps[module.name] = missing
        
        return missing_deps
    
    def _find_self_dependencies(self, modules: List[Module]) -> List[str]:
        """Find modules that depend on themselves."""
        self_deps = []
        
        for module in modules:
            if module.name in module.dependencies:
                self_deps.append(module.name)
        
        return self_deps   
 
    def _find_redundant_dependencies(self, modules: List[Module]) -> Dict[str, List[str]]:
        """Find redundant dependencies (transitive dependencies listed as direct)."""
        redundant_deps = {}
        
        for module in modules:
            if not module.dependencies:
                continue
            
            # Get transitive dependencies through other direct dependencies
            transitive_through_others = set()
            
            for dep in module.dependencies:
                transitive_deps = self.get_transitive_dependencies(dep, modules)
                transitive_through_others.update(transitive_deps)
            
            # Find direct dependencies that are also transitive
            redundant = []
            for dep in module.dependencies:
                if dep in transitive_through_others:
                    redundant.append(dep)
            
            if redundant:
                redundant_deps[module.name] = redundant
        
        return redundant_deps
    
    def _find_deep_dependencies(self, modules: List[Module], max_depth: int = 5) -> Dict[str, int]:
        """Find modules with dependency chains deeper than max_depth."""
        deep_deps = {}
        
        def get_max_depth(module_name: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()
            
            if module_name in visited:
                return 0  # Cycle detected, return 0 to avoid infinite recursion
            
            visited.add(module_name)
            dependencies = self._dependency_cache.get(module_name, set())
            
            if not dependencies:
                return 0
            
            max_child_depth = 0
            for dep in dependencies:
                child_depth = get_max_depth(dep, visited.copy())
                max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth + 1
        
        self._build_dependency_maps(modules)
        
        for module in modules:
            depth = get_max_depth(module.name)
            if depth > max_depth:
                deep_deps[module.name] = depth
        
        return deep_deps
    
    def create_dependency_graph(self, modules: List[Module]) -> DependencyGraph:
        """
        Create a DependencyGraph object from modules.
        
        Args:
            modules: List of modules to create graph from
            
        Returns:
            DependencyGraph object
        """
        nodes = [module.name for module in modules]
        edges = []
        
        for module in modules:
            for dep in module.dependencies:
                edges.append((module.name, dep))
        
        return DependencyGraph(nodes=nodes, edges=edges)
    
    def validate_dependency_graph(self, graph: DependencyGraph) -> ValidationResult:
        """
        Validate a dependency graph for consistency.
        
        Args:
            graph: DependencyGraph to validate
            
        Returns:
            ValidationResult with validation status
        """
        try:
            graph.validate()
            return ValidationResult(is_valid=True, issues=[], warnings=[])
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[f"Dependency graph validation failed: {str(e)}"],
                warnings=[]
            )