"""
Dependency-Driven Planner for enhanced dependency planning.

This module provides functionality to create optimal implementation plans
based on enhanced dependency graph analysis.
"""

from typing import List, Dict, Set, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque

from .models import (
    EnhancedDependencyGraph, FunctionDependency, DependencyType,
    OptimizationSuggestion, CriticalPathAnalysis
)


class DependencyDrivenPlanner:
    """
    Uses enhanced dependency graph analysis for optimal planning decisions.
    
    This component provides methods to determine optimal implementation ordering,
    identify parallel opportunities, and analyze critical paths in the dependency graph.
    """
    
    def __init__(self):
        """Initialize the dependency-driven planner."""
        self.cycle_resolution_strategies = [
            "function_refactoring",
            "interface_extraction", 
            "dependency_inversion"
        ]
    
    def get_optimal_implementation_order(self, enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Get optimal order for implementing functions using enhanced graph analysis.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            List of function names in optimal implementation order
        """
        if not enhanced_graph or not enhanced_graph.function_nodes:
            return []
        
        # Check for cycles first
        if enhanced_graph.has_function_cycles():
            return self._handle_cyclic_dependencies(enhanced_graph)
        
        # Use the enhanced graph's built-in topological sort
        base_order = enhanced_graph.get_function_implementation_order()
        
        # Apply additional optimization based on dependency analysis
        optimized_order = self._optimize_implementation_order(base_order, enhanced_graph)
        
        return optimized_order
    
    def _handle_cyclic_dependencies(self, enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Handle cyclic dependencies using fallback strategies.
        
        Args:
            enhanced_graph: The enhanced dependency graph with cycles
            
        Returns:
            List of functions in implementation order with cycle resolution
        """
        # Strategy 1: Break cycles by identifying the least critical dependencies
        cycle_breaking_order = self._break_cycles_by_criticality(enhanced_graph)
        if cycle_breaking_order:
            return cycle_breaking_order
        
        # Strategy 2: Group cyclic functions and implement them together
        cycle_groups = self._identify_cycle_groups(enhanced_graph)
        if cycle_groups:
            return self._create_order_with_cycle_groups(cycle_groups, enhanced_graph)
        
        # Strategy 3: Fallback to simple ordering by module then function name
        return self._fallback_alphabetical_order(enhanced_graph)
    
    def _break_cycles_by_criticality(self, enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Break cycles by temporarily removing least critical dependencies.
        
        Args:
            enhanced_graph: The enhanced dependency graph with cycles
            
        Returns:
            List of functions in order after breaking cycles
        """
        # Create a copy of dependencies to modify
        temp_dependencies = enhanced_graph.function_dependencies.copy()
        
        # Calculate criticality scores for each dependency
        dependency_scores = []
        for i, dep in enumerate(temp_dependencies):
            # Score based on dependency type and confidence
            score = self._calculate_dependency_criticality(dep, enhanced_graph)
            dependency_scores.append((score, i, dep))
        
        # Sort dependencies by criticality (lowest first)
        sorted_deps = [dep for score, i, dep in sorted(dependency_scores, key=lambda x: x[0])]
        
        # Try removing dependencies one by one until cycles are broken
        for dep_to_remove in sorted_deps:
            temp_deps = [d for d in temp_dependencies if d != dep_to_remove]
            
            # Create temporary graph without this dependency
            temp_graph = self._create_temp_graph_without_dependency(enhanced_graph, dep_to_remove)
            
            if not temp_graph.has_function_cycles():
                # Cycles broken! Get the order from this graph
                return temp_graph.get_function_implementation_order()
        
        return []  # Could not break cycles
    
    def _calculate_dependency_criticality(self, dependency: FunctionDependency, 
                                        enhanced_graph: EnhancedDependencyGraph) -> float:
        """
        Calculate criticality score for a dependency (lower = less critical).
        
        Args:
            dependency: The dependency to score
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            Criticality score (lower means less critical, easier to remove)
        """
        base_score = dependency.confidence
        
        # Adjust based on dependency type
        type_weights = {
            DependencyType.DIRECT_CALL: 1.0,
            DependencyType.DATA_DEPENDENCY: 0.8,
            DependencyType.TYPE_DEPENDENCY: 0.6,
            DependencyType.IMPORT_DEPENDENCY: 0.4
        }
        
        type_weight = type_weights.get(dependency.dependency_type, 0.5)
        base_score *= type_weight
        
        # Consider how many other functions depend on the target function
        dependents = enhanced_graph.get_function_dependents(dependency.to_function)
        dependent_boost = len(dependents) * 0.1
        
        return base_score + dependent_boost
    
    def _create_temp_graph_without_dependency(self, enhanced_graph: EnhancedDependencyGraph, 
                                            dep_to_remove: FunctionDependency) -> EnhancedDependencyGraph:
        """
        Create a temporary graph without a specific dependency.
        
        Args:
            enhanced_graph: Original enhanced dependency graph
            dep_to_remove: Dependency to exclude
            
        Returns:
            New EnhancedDependencyGraph without the specified dependency
        """
        temp_graph = EnhancedDependencyGraph()
        
        # Copy all nodes
        temp_graph.function_nodes = enhanced_graph.function_nodes.copy()
        temp_graph.module_nodes = enhanced_graph.module_nodes.copy()
        temp_graph.function_to_module = enhanced_graph.function_to_module.copy()
        temp_graph.module_to_functions = enhanced_graph.module_to_functions.copy()
        temp_graph.module_edges = enhanced_graph.module_edges.copy()
        
        # Copy all dependencies except the one to remove
        temp_graph.function_dependencies = [
            dep for dep in enhanced_graph.function_dependencies 
            if not (dep.from_function == dep_to_remove.from_function and 
                   dep.to_function == dep_to_remove.to_function and
                   dep.dependency_type == dep_to_remove.dependency_type)
        ]
        
        return temp_graph
    
    def _identify_cycle_groups(self, enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """
        Identify groups of functions that form cycles.
        
        Args:
            enhanced_graph: The enhanced dependency graph with cycles
            
        Returns:
            List of cycle groups (each group is a list of function names)
        """
        # Use Tarjan's algorithm to find strongly connected components
        return self._find_strongly_connected_components(enhanced_graph)
    
    def _find_strongly_connected_components(self, enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """
        Find strongly connected components using Tarjan's algorithm.
        
        Args:
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            List of strongly connected components
        """
        # Build adjacency list
        graph = defaultdict(list)
        for dep in enhanced_graph.function_dependencies:
            graph[dep.from_function].append(dep.to_function)
        
        # Tarjan's algorithm implementation
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        components = []
        
        def strongconnect(node):
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True
            
            for successor in graph[node]:
                if successor not in index:
                    strongconnect(successor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[successor])
                elif on_stack.get(successor, False):
                    lowlinks[node] = min(lowlinks[node], index[successor])
            
            if lowlinks[node] == index[node]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == node:
                        break
                if len(component) > 1:  # Only include actual cycles
                    components.append(component)
        
        for node in enhanced_graph.function_nodes:
            if node not in index:
                strongconnect(node)
        
        return components
    
    def _create_order_with_cycle_groups(self, cycle_groups: List[List[str]], 
                                      enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Create implementation order treating cycle groups as single units.
        
        Args:
            cycle_groups: List of cycle groups
            cycle_groups: Enhanced dependency graph
            
        Returns:
            Implementation order with cycle groups handled
        """
        # Create a mapping of functions to their cycle group
        func_to_group = {}
        group_representatives = {}
        
        for i, group in enumerate(cycle_groups):
            group_id = f"cycle_group_{i}"
            group_representatives[group_id] = group[0]  # Use first function as representative
            for func in group:
                func_to_group[func] = group_id
        
        # Build a graph of groups and individual functions
        group_graph = defaultdict(set)
        all_nodes = set()
        
        # Add individual functions that are not in cycles
        for func in enhanced_graph.function_nodes:
            if func not in func_to_group:
                all_nodes.add(func)
        
        # Add group representatives
        for group_id in group_representatives:
            all_nodes.add(group_id)
        
        # Build dependencies between groups/functions
        for dep in enhanced_graph.function_dependencies:
            from_node = func_to_group.get(dep.from_function, dep.from_function)
            to_node = func_to_group.get(dep.to_function, dep.to_function)
            
            if from_node != to_node:  # Skip internal group dependencies
                group_graph[from_node].add(to_node)
        
        # Topological sort of the group graph
        in_degree = {node: 0 for node in all_nodes}
        for node in group_graph:
            for neighbor in group_graph[node]:
                in_degree[neighbor] += 1
        
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            
            # If this is a group representative, add all functions in the group
            if node.startswith("cycle_group_"):
                group_index = int(node.split("_")[-1])
                result.extend(cycle_groups[group_index])
            else:
                result.append(node)
            
            # Update in-degrees
            for neighbor in group_graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _fallback_alphabetical_order(self, enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Fallback to alphabetical ordering when other strategies fail.
        
        Args:
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            Functions ordered alphabetically by module then function name
        """
        # Group functions by module
        module_functions = defaultdict(list)
        for func in enhanced_graph.function_nodes:
            module = enhanced_graph.function_to_module.get(func, "unknown")
            module_functions[module].append(func)
        
        # Sort modules alphabetically, then functions within each module
        result = []
        for module in sorted(module_functions.keys()):
            functions = sorted(module_functions[module])
            result.extend(functions)
        
        return result
    
    def _optimize_implementation_order(self, base_order: List[str], 
                                     enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Apply additional optimizations to the base implementation order.
        
        Args:
            base_order: Base topological order
            enhanced_graph: Enhanced dependency graph
            
        Returns:
            Optimized implementation order
        """
        if not base_order:
            return base_order
        
        # Strategy 1: Prioritize functions with no dependencies (can be implemented first)
        no_deps_functions = []
        has_deps_functions = []
        
        for func in base_order:
            deps = enhanced_graph.get_function_dependencies(func)
            if not deps:
                no_deps_functions.append(func)
            else:
                has_deps_functions.append(func)
        
        # Strategy 2: Within functions with dependencies, prioritize by dependency count
        has_deps_functions.sort(key=lambda f: len(enhanced_graph.get_function_dependencies(f)))
        
        # Strategy 3: Consider module locality - group functions from same module when possible
        optimized_order = self._apply_module_locality_optimization(
            no_deps_functions + has_deps_functions, enhanced_graph
        )
        
        return optimized_order
    
    def _apply_module_locality_optimization(self, order: List[str], 
                                          enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Optimize order to group functions from the same module when dependencies allow.
        
        Args:
            order: Current implementation order
            enhanced_graph: Enhanced dependency graph
            
        Returns:
            Order optimized for module locality
        """
        # This is a simplified optimization - in practice, this would be more sophisticated
        # For now, we'll maintain the dependency order but note module grouping opportunities
        
        # Group consecutive functions from the same module
        optimized = []
        current_module = None
        module_batch = []
        
        for func in order:
            func_module = enhanced_graph.function_to_module.get(func)
            
            if func_module == current_module:
                module_batch.append(func)
            else:
                # Finish current batch
                if module_batch:
                    optimized.extend(module_batch)
                
                # Start new batch
                current_module = func_module
                module_batch = [func]
        
        # Add final batch
        if module_batch:
            optimized.extend(module_batch)
        
        return optimized
    
    def identify_parallel_opportunities(self, enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """
        Identify groups of functions that can be implemented in parallel.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            List of parallel groups (each group contains functions that can be implemented simultaneously)
        """
        if not enhanced_graph or not enhanced_graph.function_nodes:
            return []
        
        # Use the enhanced graph's built-in parallel group identification
        base_groups = enhanced_graph.get_parallel_implementation_groups()
        
        # Apply additional optimizations for development workflow efficiency
        optimized_groups = self._optimize_parallel_groups_for_workflow(base_groups, enhanced_graph)
        
        return optimized_groups
    
    def _optimize_parallel_groups_for_workflow(self, base_groups: List[List[str]], 
                                             enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """
        Optimize parallel groups for development workflow efficiency.
        
        Args:
            base_groups: Base parallel groups from dependency analysis
            enhanced_graph: Enhanced dependency graph
            
        Returns:
            Optimized parallel groups considering workflow efficiency
        """
        optimized_groups = []
        
        for group in base_groups:
            if len(group) <= 1:
                # Single function groups don't need optimization
                optimized_groups.append(group)
                continue
            
            # Strategy 1: Group by module for better developer focus
            module_subgroups = self._group_functions_by_module(group, enhanced_graph)
            
            # Strategy 2: Consider function complexity and size
            balanced_subgroups = self._balance_groups_by_complexity(module_subgroups, enhanced_graph)
            
            # Strategy 3: Ensure groups are not too large (max 5 functions per group for manageability)
            final_subgroups = self._split_large_groups(balanced_subgroups, max_size=5)
            
            optimized_groups.extend(final_subgroups)
        
        return optimized_groups
    
    def _group_functions_by_module(self, functions: List[str], 
                                 enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """Group functions by their module for better developer focus."""
        module_groups = defaultdict(list)
        
        for func in functions:
            module = enhanced_graph.function_to_module.get(func, "unknown")
            module_groups[module].append(func)
        
        return [group for group in module_groups.values() if group]
    
    def _balance_groups_by_complexity(self, groups: List[List[str]], 
                                    enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """Balance groups by estimated function complexity."""
        balanced_groups = []
        
        for group in groups:
            if len(group) <= 2:
                # Small groups don't need balancing
                balanced_groups.append(group)
                continue
            
            # Estimate complexity based on dependency count and function name patterns
            function_complexities = []
            for func in group:
                complexity = self._estimate_function_complexity(func, enhanced_graph)
                function_complexities.append((func, complexity))
            
            # Sort by complexity
            function_complexities.sort(key=lambda x: x[1])
            
            # Split into balanced subgroups
            if len(function_complexities) > 3:
                # Split complex groups
                mid = len(function_complexities) // 2
                group1 = [fc[0] for fc in function_complexities[:mid]]
                group2 = [fc[0] for fc in function_complexities[mid:]]
                balanced_groups.extend([group1, group2])
            else:
                balanced_groups.append([fc[0] for fc in function_complexities])
        
        return balanced_groups
    
    def _estimate_function_complexity(self, function_name: str, 
                                    enhanced_graph: EnhancedDependencyGraph) -> float:
        """Estimate function complexity based on available information."""
        base_complexity = 1.0
        
        # Factor 1: Number of dependencies
        deps = enhanced_graph.get_function_dependencies(function_name)
        dependency_complexity = len(deps) * 0.2
        
        # Factor 2: Number of dependents (functions that depend on this one)
        dependents = enhanced_graph.get_function_dependents(function_name)
        dependent_complexity = len(dependents) * 0.1
        
        # Factor 3: Function name patterns (heuristic)
        name_complexity = self._estimate_complexity_from_name(function_name)
        
        return base_complexity + dependency_complexity + dependent_complexity + name_complexity
    
    def _estimate_complexity_from_name(self, function_name: str) -> float:
        """Estimate complexity based on function name patterns."""
        base_name = function_name.split('.')[-1].lower()
        
        # Complex operation indicators
        complex_patterns = ['process', 'analyze', 'generate', 'transform', 'execute', 'compute']
        simple_patterns = ['get', 'set', 'is', 'has', 'create', 'delete']
        
        if any(pattern in base_name for pattern in complex_patterns):
            return 0.5
        elif any(pattern in base_name for pattern in simple_patterns):
            return -0.2
        
        # Length-based complexity (longer names often indicate more complex functions)
        if len(base_name) > 20:
            return 0.3
        elif len(base_name) < 8:
            return -0.1
        
        return 0.0
    
    def _split_large_groups(self, groups: List[List[str]], max_size: int = 5) -> List[List[str]]:
        """Split groups that are too large for effective parallel development."""
        result = []
        
        for group in groups:
            if len(group) <= max_size:
                result.append(group)
            else:
                # Split large group into smaller chunks
                for i in range(0, len(group), max_size):
                    chunk = group[i:i + max_size]
                    result.append(chunk)
        
        return result
    
    def analyze_critical_path(self, enhanced_graph: EnhancedDependencyGraph) -> CriticalPathAnalysis:
        """
        Analyze the critical path in the dependency graph.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            CriticalPathAnalysis with critical path information and optimization suggestions
        """
        if not enhanced_graph or not enhanced_graph.function_nodes:
            return CriticalPathAnalysis(
                critical_path=[],
                path_length=0,
                bottleneck_functions=[],
                optimization_suggestions=[],
                parallel_opportunities=[]
            )
        
        # Get the critical path from the enhanced graph
        critical_path = enhanced_graph.get_critical_path()
        
        # Identify bottleneck functions (functions with high fan-in/fan-out)
        bottleneck_functions = self._identify_bottleneck_functions(enhanced_graph)
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_critical_path_optimizations(
            critical_path, bottleneck_functions, enhanced_graph
        )
        
        # Identify parallel opportunities that could reduce critical path
        parallel_opportunities = self._identify_critical_path_parallel_opportunities(
            critical_path, enhanced_graph
        )
        
        return CriticalPathAnalysis(
            critical_path=critical_path,
            path_length=len(critical_path),
            bottleneck_functions=bottleneck_functions,
            optimization_suggestions=optimization_suggestions,
            parallel_opportunities=parallel_opportunities
        )
    
    def _identify_bottleneck_functions(self, enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Identify functions that are bottlenecks in the dependency chain.
        
        Args:
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            List of function names that are bottlenecks
        """
        bottlenecks = []
        
        # Calculate in-degree and out-degree for each function
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        for dep in enhanced_graph.function_dependencies:
            out_degree[dep.from_function] += 1
            in_degree[dep.to_function] += 1
        
        # Identify functions with high fan-in (many functions depend on them)
        high_fan_in_threshold = max(2, len(enhanced_graph.function_nodes) // 10)
        for func in enhanced_graph.function_nodes:
            if in_degree[func] >= high_fan_in_threshold:
                bottlenecks.append(func)
        
        # Identify functions with high fan-out (depend on many functions)
        high_fan_out_threshold = max(3, len(enhanced_graph.function_nodes) // 8)
        for func in enhanced_graph.function_nodes:
            if out_degree[func] >= high_fan_out_threshold and func not in bottlenecks:
                bottlenecks.append(func)
        
        # Identify functions that appear in multiple dependency chains
        chain_appearances = defaultdict(int)
        
        # Simple heuristic: functions that have both high in-degree and out-degree
        for func in enhanced_graph.function_nodes:
            if in_degree[func] >= 2 and out_degree[func] >= 2:
                chain_appearances[func] = in_degree[func] + out_degree[func]
        
        # Add functions with high chain appearances
        for func, appearances in chain_appearances.items():
            if appearances >= 5 and func not in bottlenecks:
                bottlenecks.append(func)
        
        return bottlenecks
    
    def _generate_critical_path_optimizations(self, critical_path: List[str], 
                                            bottleneck_functions: List[str],
                                            enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """
        Generate optimization suggestions for the critical path.
        
        Args:
            critical_path: The critical path functions
            bottleneck_functions: Identified bottleneck functions
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        if not critical_path:
            return suggestions
        
        # Suggestion 1: Optimize bottlenecks on the critical path
        critical_bottlenecks = [func for func in critical_path if func in bottleneck_functions]
        if critical_bottlenecks:
            suggestions.append(
                f"Focus on optimizing bottleneck functions on critical path: {', '.join(critical_bottlenecks)}"
            )
        
        # Suggestion 2: Break down complex functions on critical path
        complex_functions = []
        for func in critical_path:
            complexity = self._estimate_function_complexity(func, enhanced_graph)
            if complexity > 2.0:  # High complexity threshold
                complex_functions.append(func)
        
        if complex_functions:
            suggestions.append(
                f"Consider breaking down complex functions on critical path: {', '.join(complex_functions)}"
            )
        
        # Suggestion 3: Parallelize independent sections
        if len(critical_path) > 3:
            suggestions.append(
                "Look for opportunities to parallelize independent sections of the critical path"
            )
        
        # Suggestion 4: Optimize dependencies for critical path functions
        critical_deps = set()
        for func in critical_path:
            deps = enhanced_graph.get_function_dependencies(func)
            for dep in deps:
                if dep.to_function not in critical_path:
                    critical_deps.add(dep.to_function)
        
        if critical_deps:
            suggestions.append(
                f"Optimize dependencies of critical path functions: {', '.join(list(critical_deps)[:3])}"
            )
        
        # Suggestion 5: Consider caching for frequently used functions
        frequent_functions = []
        for func in critical_path:
            dependents = enhanced_graph.get_function_dependents(func)
            if len(dependents) >= 3:
                frequent_functions.append(func)
        
        if frequent_functions:
            suggestions.append(
                f"Consider caching results for frequently used functions: {', '.join(frequent_functions)}"
            )
        
        return suggestions
    
    def _identify_critical_path_parallel_opportunities(self, critical_path: List[str],
                                                     enhanced_graph: EnhancedDependencyGraph) -> List[List[str]]:
        """
        Identify parallel opportunities that could reduce the critical path length.
        
        Args:
            critical_path: The critical path functions
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            List of parallel opportunity groups
        """
        if len(critical_path) < 2:
            return []
        
        parallel_opportunities = []
        
        # Look for functions that could be implemented in parallel with critical path functions
        for i, critical_func in enumerate(critical_path):
            # Find functions that don't depend on this critical function
            # and that this critical function doesn't depend on
            parallel_candidates = []
            
            critical_deps = set(dep.to_function for dep in enhanced_graph.get_function_dependencies(critical_func))
            critical_dependents = set(dep.from_function for dep in enhanced_graph.get_function_dependents(critical_func))
            
            for func in enhanced_graph.function_nodes:
                if func == critical_func or func in critical_path:
                    continue
                
                # Check if this function is independent of the critical function
                func_deps = set(dep.to_function for dep in enhanced_graph.get_function_dependencies(func))
                func_dependents = set(dep.from_function for dep in enhanced_graph.get_function_dependents(func))
                
                # Function is parallel if:
                # 1. It doesn't depend on the critical function
                # 2. The critical function doesn't depend on it
                # 3. They don't share dependencies that would create ordering constraints
                if (critical_func not in func_deps and 
                    func not in critical_deps and
                    not (func_deps & critical_dependents) and
                    not (critical_deps & func_dependents)):
                    parallel_candidates.append(func)
            
            if parallel_candidates:
                # Group parallel candidates with the critical function
                opportunity_group = [critical_func] + parallel_candidates[:3]  # Limit to 3 for manageability
                parallel_opportunities.append(opportunity_group)
        
        # Remove duplicate opportunities and merge similar ones
        unique_opportunities = []
        seen_functions = set()
        
        for opportunity in parallel_opportunities:
            # Check if this opportunity overlaps significantly with existing ones
            overlap = len(set(opportunity) & seen_functions)
            if overlap < len(opportunity) // 2:  # Less than 50% overlap
                unique_opportunities.append(opportunity)
                seen_functions.update(opportunity)
        
        return unique_opportunities