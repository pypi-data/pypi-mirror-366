"""
Intelligent Gap Analyzer for enhanced dependency planning.

This module provides functionality to analyze existing code structures
and identify missing functions based on dependency patterns.
"""

from typing import List, Dict, Set, Tuple, Any, Optional
import re
from dataclasses import dataclass
from collections import defaultdict, Counter

from .models import (
    EnhancedDependencyGraph, FunctionGap, Module, FunctionSpec,
    OptimizationSuggestion, DependencyType, FunctionDependency
)


class IntelligentGapAnalyzer:
    """Analyzes dependency patterns to identify missing functionality and optimization opportunities."""
    
    def __init__(self):
        """Initialize the gap analyzer."""
        self.confidence_threshold = 0.5
        self.min_pattern_frequency = 2
    
    def detect_missing_functions(self, enhanced_graph: EnhancedDependencyGraph) -> List[FunctionGap]:
        """
        Analyze dependency patterns to identify missing functions.
        
        Args:
            enhanced_graph: The enhanced dependency graph to analyze
            
        Returns:
            List of identified function gaps with confidence scores
        """
        if not enhanced_graph or not enhanced_graph.function_nodes:
            return []
        
        gaps = []
        
        # Analyze common dependency patterns
        pattern_gaps = self._analyze_dependency_patterns(enhanced_graph)
        gaps.extend(pattern_gaps)
        
        # Analyze incomplete function chains
        chain_gaps = self._analyze_incomplete_chains(enhanced_graph)
        gaps.extend(chain_gaps)
        
        # Analyze utility function opportunities
        utility_gaps = self._analyze_utility_opportunities(enhanced_graph)
        gaps.extend(utility_gaps)
        
        # Remove duplicates and sort by confidence
        unique_gaps = self._deduplicate_gaps(gaps)
        return sorted(unique_gaps, key=lambda g: g.confidence, reverse=True)
    
    def _analyze_dependency_patterns(self, enhanced_graph: EnhancedDependencyGraph) -> List[FunctionGap]:
        """Analyze common dependency patterns to identify missing functions."""
        gaps = []
        
        # Group functions by module to analyze patterns
        module_functions = defaultdict(list)
        for func_name in enhanced_graph.function_nodes:
            module_name = enhanced_graph.function_to_module[func_name]
            module_functions[module_name].append(func_name)
        
        # Analyze cross-module dependency patterns
        for module_name, functions in module_functions.items():
            # Look for functions that depend on multiple external modules
            # This might indicate a need for adapter/bridge functions
            for func_name in functions:
                deps = enhanced_graph.get_function_dependencies(func_name)
                external_modules = set()
                
                for dep in deps:
                    dep_module = enhanced_graph.function_to_module.get(dep.to_function)
                    if dep_module and dep_module != module_name:
                        external_modules.add(dep_module)
                
                # If function depends on 3+ external modules, suggest adapter
                if len(external_modules) >= 3:
                    adapter_name = f"{func_name.split('.')[-1]}_adapter"
                    gap = FunctionGap(
                        suggested_name=adapter_name,
                        suggested_module=module_name,
                        reason=f"Adapter function to simplify dependencies from {len(external_modules)} external modules",
                        confidence=0.6,
                        dependencies=[func_name],
                        dependents=[dep.to_function for dep in deps if enhanced_graph.function_to_module.get(dep.to_function) != module_name]
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _analyze_incomplete_chains(self, enhanced_graph: EnhancedDependencyGraph) -> List[FunctionGap]:
        """Analyze dependency chains to identify missing intermediate functions."""
        gaps = []
        
        # Find functions with high fan-out (many dependents)
        dependents_count = defaultdict(int)
        for dep in enhanced_graph.function_dependencies:
            dependents_count[dep.to_function] += 1
        
        # Look for functions that are heavily depended upon
        high_usage_functions = [func for func, count in dependents_count.items() if count >= 3]
        
        for func_name in high_usage_functions:
            dependents = enhanced_graph.get_function_dependents(func_name)
            
            # Group dependents by module
            module_usage = defaultdict(list)
            for dep in dependents:
                dep_module = enhanced_graph.function_to_module.get(dep.from_function)
                if dep_module:
                    module_usage[dep_module].append(dep.from_function)
            
            # If multiple modules use this function, suggest module-specific wrappers
            if len(module_usage) >= 2:
                func_module = enhanced_graph.function_to_module.get(func_name)
                base_func_name = func_name.split('.')[-1]
                
                for using_module, using_functions in module_usage.items():
                    if using_module != func_module and len(using_functions) >= 2:
                        wrapper_name = f"{base_func_name}_wrapper"
                        gap = FunctionGap(
                            suggested_name=wrapper_name,
                            suggested_module=using_module,
                            reason=f"Module-specific wrapper for heavily used function {base_func_name}",
                            confidence=0.7,
                            dependencies=using_functions,
                            dependents=[func_name]
                        )
                        gaps.append(gap)
        
        return gaps
    
    def _analyze_utility_opportunities(self, enhanced_graph: EnhancedDependencyGraph) -> List[FunctionGap]:
        """Analyze opportunities for utility functions based on common patterns."""
        gaps = []
        
        # Analyze function names for common patterns that suggest missing utilities
        function_names = [func.split('.')[-1] for func in enhanced_graph.function_nodes]
        
        # Look for validation patterns
        validation_functions = [name for name in function_names if 'validate' in name.lower()]
        if len(validation_functions) >= 2:
            # Suggest a common validation utility
            gap = FunctionGap(
                suggested_name="validation_utils",
                suggested_module="utils",
                reason=f"Common validation utilities based on {len(validation_functions)} validation functions",
                confidence=0.8,
                dependencies=[],
                dependents=[f"utils.{name}" for name in validation_functions]
            )
            gaps.append(gap)
        
        # Look for data transformation patterns
        transform_functions = [name for name in function_names 
                             if any(keyword in name.lower() for keyword in ['convert', 'transform', 'parse', 'format'])]
        if len(transform_functions) >= 3:
            gap = FunctionGap(
                suggested_name="data_transformers",
                suggested_module="utils",
                reason=f"Common data transformation utilities based on {len(transform_functions)} transform functions",
                confidence=0.75,
                dependencies=[],
                dependents=[f"utils.{name}" for name in transform_functions]
            )
            gaps.append(gap)
        
        # Look for error handling patterns
        error_functions = [name for name in function_names 
                          if any(keyword in name.lower() for keyword in ['error', 'exception', 'handle'])]
        if len(error_functions) >= 2:
            gap = FunctionGap(
                suggested_name="error_handlers",
                suggested_module="utils",
                reason=f"Common error handling utilities based on {len(error_functions)} error functions",
                confidence=0.7,
                dependencies=[],
                dependents=[f"utils.{name}" for name in error_functions]
            )
            gaps.append(gap)
        
        return gaps
    
    def _deduplicate_gaps(self, gaps: List[FunctionGap]) -> List[FunctionGap]:
        """Remove duplicate function gaps based on name and module."""
        seen = set()
        unique_gaps = []
        
        for gap in gaps:
            gap_key = f"{gap.suggested_module}.{gap.suggested_name}"
            if gap_key not in seen:
                seen.add(gap_key)
                unique_gaps.append(gap)
        
        return unique_gaps
    
    def determine_optimal_module_placement(self, function_name: str, 
                                         enhanced_graph: EnhancedDependencyGraph,
                                         existing_modules: List[Module]) -> str:
        """
        Determine the optimal module for placing a new function.
        
        Args:
            function_name: Name of the function to place
            enhanced_graph: The enhanced dependency graph
            existing_modules: List of existing modules
            
        Returns:
            Suggested module name for the function
        """
        if not enhanced_graph or not existing_modules:
            return "utils"  # Default fallback
        
        # Analyze where similar functions are placed
        similar_functions = self._find_similar_functions(function_name, enhanced_graph)
        
        if similar_functions:
            # Count module preferences based on similar functions
            module_scores = defaultdict(int)
            for similar_func in similar_functions:
                module = enhanced_graph.function_to_module.get(similar_func)
                if module:
                    module_scores[module] += 1
            
            # Return the module with highest score
            if module_scores:
                return max(module_scores.items(), key=lambda x: x[1])[0]
        
        # Analyze function name patterns to suggest module
        name_lower = function_name.lower()
        
        # Common module patterns
        if any(keyword in name_lower for keyword in ['validate', 'check', 'verify']):
            return "validation"
        elif any(keyword in name_lower for keyword in ['parse', 'convert', 'transform', 'format']):
            return "parsers"
        elif any(keyword in name_lower for keyword in ['handle', 'error', 'exception']):
            return "handlers"
        elif any(keyword in name_lower for keyword in ['util', 'helper', 'common']):
            return "utils"
        elif any(keyword in name_lower for keyword in ['data', 'model', 'entity']):
            return "models"
        elif any(keyword in name_lower for keyword in ['api', 'client', 'service']):
            return "services"
        
        # If no pattern matches, suggest utils as default
        return "utils"
    
    def _find_similar_functions(self, function_name: str, 
                               enhanced_graph: EnhancedDependencyGraph) -> List[str]:
        """Find functions with similar names or patterns."""
        similar_functions = []
        name_lower = function_name.lower()
        
        # Extract keywords from function name
        keywords = re.findall(r'[a-z]+', name_lower)
        
        for func_name in enhanced_graph.function_nodes:
            func_base_name = func_name.split('.')[-1].lower()
            func_keywords = re.findall(r'[a-z]+', func_base_name)
            
            # Calculate similarity based on common keywords
            common_keywords = set(keywords) & set(func_keywords)
            if len(common_keywords) >= 1 and len(common_keywords) / max(len(keywords), len(func_keywords)) >= 0.3:
                similar_functions.append(func_name)
        
        return similar_functions
    
    def calculate_confidence_score(self, gap: FunctionGap, 
                                 enhanced_graph: EnhancedDependencyGraph) -> float:
        """
        Calculate confidence score for a function gap.
        
        Args:
            gap: The function gap to score
            enhanced_graph: The enhanced dependency graph
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = gap.confidence
        
        # Boost confidence based on number of dependencies/dependents
        dependency_boost = min(0.2, len(gap.dependencies) * 0.05)
        dependent_boost = min(0.2, len(gap.dependents) * 0.05)
        
        # Boost confidence if similar functions exist
        similar_functions = self._find_similar_functions(gap.suggested_name, enhanced_graph)
        similarity_boost = min(0.15, len(similar_functions) * 0.03)
        
        # Calculate final confidence
        final_confidence = base_confidence + dependency_boost + dependent_boost + similarity_boost
        
        return min(1.0, final_confidence)
    
    def analyze_module_completeness(self, modules: List[Module]) -> Dict[str, Any]:
        """
        Analyze existing module structure for completeness and optimization opportunities.
        
        Args:
            modules: List of existing modules to analyze
            
        Returns:
            Dictionary containing completeness analysis results
        """
        if not modules:
            return {
                "total_modules": 0,
                "incomplete_modules": [],
                "optimization_suggestions": [],
                "completeness_score": 1.0
            }
        
        incomplete_modules = []
        optimization_suggestions = []
        
        # Analyze each module for completeness patterns
        for module in modules:
            module_analysis = self._analyze_single_module_completeness(module)
            
            if not module_analysis["is_complete"]:
                incomplete_modules.append({
                    "module_name": module.name,
                    "issues": module_analysis["issues"],
                    "suggestions": module_analysis["suggestions"]
                })
            
            optimization_suggestions.extend(module_analysis["optimizations"])
        
        # Calculate overall completeness score
        total_modules = len(modules)
        complete_modules = total_modules - len(incomplete_modules)
        completeness_score = complete_modules / total_modules if total_modules > 0 else 1.0
        
        # Analyze cross-module patterns
        cross_module_suggestions = self._analyze_cross_module_patterns(modules)
        optimization_suggestions.extend(cross_module_suggestions)
        
        return {
            "total_modules": total_modules,
            "complete_modules": complete_modules,
            "incomplete_modules": incomplete_modules,
            "optimization_suggestions": optimization_suggestions,
            "completeness_score": completeness_score,
            "analysis_summary": self._generate_completeness_summary(incomplete_modules, optimization_suggestions)
        }
    
    def _analyze_single_module_completeness(self, module: Module) -> Dict[str, Any]:
        """Analyze a single module for completeness patterns."""
        issues = []
        suggestions = []
        optimizations = []
        
        # Check for common completeness patterns
        function_names = [func.name for func in module.functions]
        
        # Check for CRUD pattern completeness
        crud_analysis = self._analyze_crud_completeness(function_names, module.name)
        if crud_analysis["missing_operations"]:
            issues.append(f"Incomplete CRUD operations: missing {', '.join(crud_analysis['missing_operations'])}")
            for op in crud_analysis["missing_operations"]:
                suggestions.append(f"Add {op} operation for {module.name}")
        
        # Check for validation pattern completeness
        validation_analysis = self._analyze_validation_completeness(function_names, module.name)
        if validation_analysis["needs_validation"]:
            issues.append("Missing validation functions")
            suggestions.extend(validation_analysis["suggestions"])
        
        # Check for error handling completeness
        error_analysis = self._analyze_error_handling_completeness(function_names, module.name)
        if error_analysis["needs_error_handling"]:
            issues.append("Insufficient error handling")
            suggestions.extend(error_analysis["suggestions"])
        
        # Check for utility function opportunities
        utility_analysis = self._analyze_utility_completeness(function_names, module.name)
        optimizations.extend(utility_analysis["optimizations"])
        
        # Check module size and complexity
        complexity_analysis = self._analyze_module_complexity(module)
        if complexity_analysis["needs_splitting"]:
            optimizations.append(OptimizationSuggestion(
                suggestion_type="module_split",
                description=f"Module {module.name} is complex and should be split",
                affected_modules=[module.name],
                priority="medium",
                estimated_effort="large"
            ))
        
        is_complete = len(issues) == 0
        
        return {
            "is_complete": is_complete,
            "issues": issues,
            "suggestions": suggestions,
            "optimizations": optimizations
        }
    
    def _analyze_crud_completeness(self, function_names: List[str], module_name: str) -> Dict[str, Any]:
        """Analyze if module has complete CRUD operations."""
        crud_patterns = {
            "create": ["create", "add", "insert", "new"],
            "read": ["get", "find", "read", "fetch", "retrieve", "list"],
            "update": ["update", "modify", "edit", "change"],
            "delete": ["delete", "remove", "destroy"]
        }
        
        found_operations = set()
        
        for func_name in function_names:
            func_lower = func_name.lower()
            for operation, patterns in crud_patterns.items():
                if any(pattern in func_lower for pattern in patterns):
                    found_operations.add(operation)
        
        # Only suggest missing CRUD if we found at least one CRUD operation
        if found_operations:
            missing_operations = set(crud_patterns.keys()) - found_operations
            return {
                "has_crud": True,
                "found_operations": list(found_operations),
                "missing_operations": list(missing_operations)
            }
        
        return {
            "has_crud": False,
            "found_operations": [],
            "missing_operations": []
        }
    
    def _analyze_validation_completeness(self, function_names: List[str], module_name: str) -> Dict[str, Any]:
        """Analyze if module needs validation functions."""
        has_validation = any("validate" in name.lower() or "check" in name.lower() 
                           for name in function_names)
        
        # Check if module likely needs validation (has data operations)
        data_operations = any(keyword in name.lower() 
                            for name in function_names 
                            for keyword in ["create", "update", "add", "modify", "set"])
        
        needs_validation = data_operations and not has_validation
        suggestions = []
        
        if needs_validation:
            suggestions.append(f"Add validation function for {module_name} data")
            suggestions.append(f"Add input sanitization for {module_name} operations")
        
        return {
            "has_validation": has_validation,
            "needs_validation": needs_validation,
            "suggestions": suggestions
        }
    
    def _analyze_error_handling_completeness(self, function_names: List[str], module_name: str) -> Dict[str, Any]:
        """Analyze if module has adequate error handling."""
        has_error_handling = any(keyword in name.lower() 
                               for name in function_names 
                               for keyword in ["error", "exception", "handle", "catch"])
        
        # Check if module likely needs error handling (has complex operations)
        complex_operations = any(keyword in name.lower() 
                               for name in function_names 
                               for keyword in ["process", "execute", "run", "perform", "analyze"])
        
        needs_error_handling = complex_operations and not has_error_handling
        suggestions = []
        
        if needs_error_handling:
            suggestions.append(f"Add error handling utilities for {module_name}")
            suggestions.append(f"Add exception classes specific to {module_name}")
        
        return {
            "has_error_handling": has_error_handling,
            "needs_error_handling": needs_error_handling,
            "suggestions": suggestions
        }
    
    def _analyze_utility_completeness(self, function_names: List[str], module_name: str) -> Dict[str, Any]:
        """Analyze opportunities for utility functions within the module."""
        optimizations = []
        
        # Look for repeated patterns that could be utilities
        name_patterns = defaultdict(list)
        for name in function_names:
            # Extract common patterns
            if "_" in name:
                parts = name.split("_")
                for i in range(len(parts) - 1):
                    pattern = "_".join(parts[i:i+2])
                    name_patterns[pattern].append(name)
        
        # Suggest utility functions for common patterns
        for pattern, functions in name_patterns.items():
            if len(functions) >= 3:  # Pattern appears in 3+ functions
                optimizations.append(OptimizationSuggestion(
                    suggestion_type="utility_extraction",
                    description=f"Extract common '{pattern}' pattern into utility function",
                    affected_modules=[module_name],
                    affected_functions=functions,
                    priority="low",
                    estimated_effort="small"
                ))
        
        return {"optimizations": optimizations}
    
    def _analyze_module_complexity(self, module: Module) -> Dict[str, Any]:
        """Analyze if module is too complex and needs splitting."""
        function_count = len(module.functions)
        
        # Simple heuristics for complexity
        needs_splitting = False
        reasons = []
        
        if function_count > 15:
            needs_splitting = True
            reasons.append(f"Too many functions ({function_count})")
        
        # Check for diverse functionality (different naming patterns)
        function_prefixes = set()
        for func in module.functions:
            if "_" in func.name:
                prefix = func.name.split("_")[0]
                function_prefixes.add(prefix)
        
        if len(function_prefixes) > 5:
            needs_splitting = True
            reasons.append(f"Diverse functionality patterns ({len(function_prefixes)} different prefixes)")
        
        return {
            "needs_splitting": needs_splitting,
            "reasons": reasons,
            "function_count": function_count,
            "complexity_score": min(1.0, function_count / 10.0)
        }
    
    def _analyze_cross_module_patterns(self, modules: List[Module]) -> List[OptimizationSuggestion]:
        """Analyze patterns across modules for optimization opportunities."""
        suggestions = []
        
        # Find duplicate function patterns across modules
        function_patterns = defaultdict(list)
        
        for module in modules:
            for func in module.functions:
                # Extract function pattern (simplified)
                pattern = self._extract_function_pattern(func.name)
                if pattern:
                    function_patterns[pattern].append((module.name, func.name))
        
        # Suggest consolidation for common patterns
        for pattern, occurrences in function_patterns.items():
            if len(occurrences) >= 3:  # Pattern appears in 3+ modules
                affected_modules = list(set(occ[0] for occ in occurrences))
                affected_functions = [f"{occ[0]}.{occ[1]}" for occ in occurrences]
                
                suggestions.append(OptimizationSuggestion(
                    suggestion_type="pattern_consolidation",
                    description=f"Consolidate common '{pattern}' pattern across modules",
                    affected_modules=affected_modules,
                    affected_functions=affected_functions,
                    priority="medium",
                    estimated_effort="medium"
                ))
        
        return suggestions
    
    def _extract_function_pattern(self, function_name: str) -> Optional[str]:
        """Extract a pattern from function name for cross-module analysis."""
        name_lower = function_name.lower()
        
        # Common patterns to look for
        patterns = [
            "validate", "check", "verify",
            "parse", "convert", "transform",
            "create", "update", "delete", "get",
            "handle", "process", "execute"
        ]
        
        for pattern in patterns:
            if pattern in name_lower:
                return pattern
        
        return None
    
    def _generate_completeness_summary(self, incomplete_modules: List[Dict], 
                                     optimization_suggestions: List[OptimizationSuggestion]) -> str:
        """Generate a human-readable summary of the completeness analysis."""
        if not incomplete_modules and not optimization_suggestions:
            return "All modules appear complete with no optimization opportunities identified."
        
        summary_parts = []
        
        if incomplete_modules:
            summary_parts.append(f"Found {len(incomplete_modules)} modules with completeness issues")
        
        if optimization_suggestions:
            high_priority = len([s for s in optimization_suggestions if s.priority == "high"])
            medium_priority = len([s for s in optimization_suggestions if s.priority == "medium"])
            low_priority = len([s for s in optimization_suggestions if s.priority == "low"])
            
            priority_summary = []
            if high_priority:
                priority_summary.append(f"{high_priority} high priority")
            if medium_priority:
                priority_summary.append(f"{medium_priority} medium priority")
            if low_priority:
                priority_summary.append(f"{low_priority} low priority")
            
            summary_parts.append(f"Identified {len(optimization_suggestions)} optimization opportunities: {', '.join(priority_summary)}")
        
        return ". ".join(summary_parts) + "."
    
    def suggest_module_restructuring(self, modules: List[Module], 
                                   enhanced_graph: Optional[EnhancedDependencyGraph] = None) -> List[OptimizationSuggestion]:
        """
        Suggest module restructuring based on analysis.
        
        Args:
            modules: List of existing modules
            enhanced_graph: Optional enhanced dependency graph for dependency analysis
            
        Returns:
            List of restructuring suggestions
        """
        suggestions = []
        
        if not modules:
            return suggestions
        
        # Analyze each module for restructuring opportunities
        for module in modules:
            module_suggestions = self._analyze_module_restructuring(module, enhanced_graph)
            suggestions.extend(module_suggestions)
        
        # Analyze cross-module restructuring opportunities
        if enhanced_graph:
            cross_module_suggestions = self._analyze_cross_module_restructuring(modules, enhanced_graph)
            suggestions.extend(cross_module_suggestions)
        
        return suggestions
    
    def _analyze_module_restructuring(self, module: Module, 
                                    enhanced_graph: Optional[EnhancedDependencyGraph]) -> List[OptimizationSuggestion]:
        """Analyze a single module for restructuring opportunities."""
        suggestions = []
        
        # Check if module should be split
        if len(module.functions) > 12:
            # Analyze function groupings
            function_groups = self._group_functions_by_similarity(module.functions)
            
            if len(function_groups) >= 2:
                for i, group in enumerate(function_groups):
                    if len(group) >= 3:  # Only suggest split if group is substantial
                        new_module_name = f"{module.name}_{self._suggest_group_name(group)}"
                        suggestions.append(OptimizationSuggestion(
                            suggestion_type="module_split",
                            description=f"Split {len(group)} functions into new module '{new_module_name}'",
                            affected_modules=[module.name],
                            affected_functions=[f"{module.name}.{func.name}" for func in group],
                            priority="medium",
                            estimated_effort="large"
                        ))
        
        # Check for functions that might belong in other modules
        if enhanced_graph:
            misplaced_functions = self._find_misplaced_functions(module, enhanced_graph)
            for func, suggested_module in misplaced_functions:
                suggestions.append(OptimizationSuggestion(
                    suggestion_type="function_relocation",
                    description=f"Move function '{func.name}' to module '{suggested_module}'",
                    affected_modules=[module.name, suggested_module],
                    affected_functions=[f"{module.name}.{func.name}"],
                    priority="low",
                    estimated_effort="small"
                ))
        
        return suggestions
    
    def _group_functions_by_similarity(self, functions: List[FunctionSpec]) -> List[List[FunctionSpec]]:
        """Group functions by naming similarity and functionality."""
        groups = []
        ungrouped = functions.copy()
        
        while ungrouped:
            current_func = ungrouped.pop(0)
            current_group = [current_func]
            
            # Find similar functions
            to_remove = []
            for func in ungrouped:
                if self._functions_are_similar(current_func, func):
                    current_group.append(func)
                    to_remove.append(func)
            
            # Remove grouped functions from ungrouped
            for func in to_remove:
                ungrouped.remove(func)
            
            groups.append(current_group)
        
        return groups
    
    def _functions_are_similar(self, func1: FunctionSpec, func2: FunctionSpec) -> bool:
        """Check if two functions are similar based on naming patterns."""
        name1_parts = set(re.findall(r'[a-z]+', func1.name.lower()))
        name2_parts = set(re.findall(r'[a-z]+', func2.name.lower()))
        
        # Calculate similarity based on common words
        common_parts = name1_parts & name2_parts
        total_parts = name1_parts | name2_parts
        
        if not total_parts:
            return False
        
        similarity = len(common_parts) / len(total_parts)
        return similarity >= 0.4  # 40% similarity threshold
    
    def _suggest_group_name(self, functions: List[FunctionSpec]) -> str:
        """Suggest a name for a group of functions."""
        # Extract common words from function names
        all_words = []
        for func in functions:
            words = re.findall(r'[a-z]+', func.name.lower())
            all_words.extend(words)
        
        # Find most common words
        word_counts = Counter(all_words)
        if word_counts:
            most_common_word = word_counts.most_common(1)[0][0]
            return most_common_word
        
        return "utils"
    
    def _find_misplaced_functions(self, module: Module, 
                                enhanced_graph: EnhancedDependencyGraph) -> List[Tuple[FunctionSpec, str]]:
        """Find functions that might be better placed in other modules."""
        misplaced = []
        
        for func in module.functions:
            func_full_name = f"{module.name}.{func.name}"
            
            # Analyze dependencies to suggest better placement
            deps = enhanced_graph.get_function_dependencies(func_full_name)
            
            if deps:
                # Count dependencies by module
                module_deps = defaultdict(int)
                for dep in deps:
                    dep_module = enhanced_graph.function_to_module.get(dep.to_function)
                    if dep_module and dep_module != module.name:
                        module_deps[dep_module] += 1
                
                # If function depends heavily on another module, suggest moving it
                if module_deps:
                    best_module, dep_count = max(module_deps.items(), key=lambda x: x[1])
                    if dep_count >= 2:  # At least 2 dependencies in another module
                        misplaced.append((func, best_module))
        
        return misplaced
    
    def _analyze_cross_module_restructuring(self, modules: List[Module], 
                                          enhanced_graph: EnhancedDependencyGraph) -> List[OptimizationSuggestion]:
        """Analyze cross-module restructuring opportunities."""
        suggestions = []
        
        # Look for tightly coupled modules that could be merged
        module_coupling = self._calculate_module_coupling(modules, enhanced_graph)
        
        for (module1, module2), coupling_score in module_coupling.items():
            if coupling_score >= 0.7:  # High coupling threshold
                suggestions.append(OptimizationSuggestion(
                    suggestion_type="module_merge",
                    description=f"Consider merging highly coupled modules '{module1}' and '{module2}'",
                    affected_modules=[module1, module2],
                    priority="low",
                    estimated_effort="large"
                ))
        
        return suggestions
    
    def _calculate_module_coupling(self, modules: List[Module], 
                                 enhanced_graph: EnhancedDependencyGraph) -> Dict[Tuple[str, str], float]:
        """Calculate coupling scores between modules."""
        coupling_scores = {}
        module_names = [m.name for m in modules]
        
        for i, module1 in enumerate(module_names):
            for module2 in module_names[i+1:]:
                # Count cross-dependencies between modules
                cross_deps = 0
                total_deps = 0
                
                for dep in enhanced_graph.function_dependencies:
                    from_module = enhanced_graph.function_to_module.get(dep.from_function)
                    to_module = enhanced_graph.function_to_module.get(dep.to_function)
                    
                    if from_module in [module1, module2] or to_module in [module1, module2]:
                        total_deps += 1
                        if (from_module == module1 and to_module == module2) or \
                           (from_module == module2 and to_module == module1):
                            cross_deps += 1
                
                if total_deps > 0:
                    coupling_score = cross_deps / total_deps
                    coupling_scores[(module1, module2)] = coupling_score
        
        return coupling_scores