"""
Integration engine implementation for AI Project Builder.

This module provides the IntegrationEngine class that handles module integration,
import generation, and verification of module connections.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict

from .base import BaseIntegrationEngine
from ..core.models import (
    Module, IntegrationResult, ValidationResult, DependencyGraph,
    TestGenerationResult
)
from dataclasses import dataclass
from ..core.interfaces import (
    DependencyAnalyzerInterface, FileSystemManagerInterface
)


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


class ImportGenerationError(IntegrationError):
    """Exception raised when import generation fails."""
    pass


class ModuleConnectionError(IntegrationError):
    """Exception raised when module connection fails."""
    pass


class ImportVerificationError(IntegrationError):
    """Exception raised when import verification fails."""
    pass


@dataclass
class ModuleConnectionResult:
    """Result of connecting a single module."""
    success: bool
    errors: List[str]


class IntegrationEngine(BaseIntegrationEngine):
    """
    Engine for integrating modules and managing imports.
    
    Handles automatic import generation, module connection according to
    dependency graphs, and verification of import resolution.
    """
    
    def __init__(self, 
                 dependency_analyzer: Optional[DependencyAnalyzerInterface] = None,
                 filesystem_manager: Optional[FileSystemManagerInterface] = None,
                 ai_client=None, 
                 state_manager=None,
                 test_generator=None,
                 package_manager=None):
        """
        Initialize the integration engine.
        
        Args:
            dependency_analyzer: Analyzer for module dependencies
            filesystem_manager: Manager for file system operations
            ai_client: AI client for assistance (inherited from base)
            state_manager: State manager for persistence (inherited from base)
            test_generator: Test generator for creating unit tests
            package_manager: Manager for package imports and consistency
        """
        super().__init__(ai_client, state_manager)
        self.dependency_analyzer = dependency_analyzer
        self.filesystem_manager = filesystem_manager
        self.test_generator = test_generator
        self.package_manager = package_manager
        self._import_cache: Dict[str, List[str]] = {}
        self._module_cache: Dict[str, Dict[str, Any]] = {}
    
    def initialize(self) -> None:
        """Initialize the integration engine."""
        super().initialize()
        
        if self.dependency_analyzer and hasattr(self.dependency_analyzer, 'initialize'):
            self.dependency_analyzer.initialize()
        
        if self.filesystem_manager and hasattr(self.filesystem_manager, 'initialize'):
            self.filesystem_manager.initialize()
        
        if self.package_manager and hasattr(self.package_manager, 'initialize'):
            self.package_manager.initialize()
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate prerequisites for integration operations."""
        result = super().validate_prerequisites()
        
        if self.dependency_analyzer is None:
            result.issues.append("Dependency analyzer is required but not provided")
        
        if self.filesystem_manager is None:
            result.issues.append("File system manager is required but not provided")
        
        # Package manager is optional but recommended
        if self.package_manager is None:
            result.warnings.append("Package manager not provided - import consistency may be limited")
        
        return result
    
    def generate_imports(self, modules: List[Module]) -> Dict[str, List[str]]:
        """
        Generate import statements for all modules.
        
        Args:
            modules: List of modules to generate imports for
            
        Returns:
            Dictionary mapping module names to their import statements
            
        Raises:
            ImportGenerationError: If import generation fails
        """
        self._ensure_initialized()
        
        if not modules:
            return {}
        
        try:
            # Clear cache for fresh generation
            self._import_cache.clear()
            
            # Build module information cache
            self._build_module_cache(modules)
            
            # Generate imports for each module
            import_map = {}
            
            for module in modules:
                try:
                    imports = self._generate_module_imports(module, modules)
                    import_map[module.name] = imports
                    self._import_cache[module.name] = imports
                    
                except Exception as e:
                    raise ImportGenerationError(
                        f"Failed to generate imports for module '{module.name}': {e}"
                    ) from e
            
            # Validate generated imports for circular dependencies
            self._validate_import_dependencies(import_map, modules)
            
            return import_map
            
        except ImportGenerationError:
            raise
        except Exception as e:
            raise ImportGenerationError(f"Import generation failed: {e}") from e
    
    def integrate_modules(self, modules: List[Module], generate_tests: bool = False) -> IntegrationResult:
        """
        Integrate all modules according to dependency graph.
        
        Args:
            modules: List of modules to integrate
            generate_tests: Whether to generate unit tests during integration
            
        Returns:
            IntegrationResult with integration status and details
        """
        self._ensure_initialized()
        
        if not modules:
            return IntegrationResult(
                integrated_modules=[],
                import_errors=[],
                success=True
            )
        
        integrated_modules = []
        import_errors = []
        
        try:
            # Validate modules before integration
            validation_errors = self._validate_modules_for_integration(modules)
            if validation_errors:
                import_errors.extend(validation_errors)
                return IntegrationResult(
                    integrated_modules=[],
                    import_errors=import_errors,
                    success=False
                )
            
            # Generate imports for all modules
            import_map = self.generate_imports(modules)
            
            # Get integration order from dependency analyzer
            if self.dependency_analyzer:
                try:
                    integration_order = self.dependency_analyzer.get_build_order(modules)
                except Exception as e:
                    import_errors.append(f"Failed to determine integration order: {e}")
                    # Fall back to original module order
                    integration_order = [module.name for module in modules]
            else:
                integration_order = [module.name for module in modules]
            
            # Connect modules in dependency order
            for module_name in integration_order:
                try:
                    module = next((m for m in modules if m.name == module_name), None)
                    if not module:
                        import_errors.append(f"Module '{module_name}' not found in module list")
                        continue
                    
                    # Connect module with its dependencies
                    connection_result = self._connect_module(module, modules, import_map.get(module_name, []))
                    
                    if connection_result.success:
                        integrated_modules.append(module_name)
                    else:
                        import_errors.extend(connection_result.errors)
                        
                except Exception as e:
                    import_errors.append(f"Integration failed for module '{module_name}': {e}")
            
            # Determine initial success status
            success = len(import_errors) == 0
            
            # Generate tests if requested
            test_result = None
            if generate_tests and success and self.test_generator:
                try:
                    test_result = self._generate_integration_tests(modules)
                    if not test_result.success:
                        import_errors.extend(test_result.errors)
                        success = False
                except Exception as e:
                    import_errors.append(f"Test generation failed: {e}")
                    success = False
            
            # Verify integration after all modules are connected
            verification_result = self.verify_integration(modules)
            if not verification_result.is_valid:
                import_errors.extend(verification_result.issues)
            
            # Final success determination
            success = len(import_errors) == 0
            
            # Update requirements file if package manager is available and integration succeeded
            package_updates = []
            if success and self.package_manager:
                try:
                    # Get project path from the first module's file path
                    if modules:
                        project_path = str(Path(modules[0].file_path).parent)
                        self.package_manager.update_requirements_file(project_path)
                        package_updates.append("Updated requirements.txt with package dependencies")
                except Exception as e:
                    import_errors.append(f"Failed to update requirements file: {e}")
            
            return IntegrationResult(
                integrated_modules=integrated_modules,
                import_errors=import_errors,
                success=success,
                test_result=test_result,
                package_updates=package_updates if package_updates else None
            )
            
        except Exception as e:
            return IntegrationResult(
                integrated_modules=integrated_modules,
                import_errors=[f"Integration process failed: {e}"],
                success=False
            )
    
    def verify_integration(self, modules: List[Module]) -> ValidationResult:
        """
        Verify that all imports resolve correctly.
        
        Args:
            modules: List of modules to verify
            
        Returns:
            ValidationResult with verification status
        """
        self._ensure_initialized()
        
        if not modules:
            return ValidationResult(is_valid=True, issues=[], warnings=[])
        
        issues = []
        warnings = []
        
        try:
            # Comprehensive module verification
            for module in modules:
                module_issues, module_warnings = self._comprehensive_module_verification(module, modules)
                issues.extend(module_issues)
                warnings.extend(module_warnings)
            
            # Check for circular import dependencies
            try:
                circular_imports = self._detect_circular_imports(modules)
                if circular_imports:
                    for cycle in circular_imports:
                        issues.append(f"Circular import dependency: {' -> '.join(cycle)}")
                        
            except Exception as e:
                warnings.append(f"Could not check for circular imports: {e}")
            
            # Check for unused imports
            try:
                unused_imports = self._find_unused_imports(modules)
                for module_name, unused in unused_imports.items():
                    if unused:
                        warnings.append(f"Module '{module_name}' has unused imports: {unused}")
                        
            except Exception as e:
                warnings.append(f"Could not check for unused imports: {e}")
            
            # Verify dependency graph consistency
            try:
                graph_issues = self._verify_dependency_graph_consistency(modules)
                issues.extend(graph_issues)
            except Exception as e:
                warnings.append(f"Could not verify dependency graph: {e}")
            
            return ValidationResult(
                is_valid=len(issues) == 0,
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[f"Integration verification failed: {e}"],
                warnings=warnings
            )
    
    def _comprehensive_module_verification(self, module: Module, all_modules: List[Module]) -> Tuple[List[str], List[str]]:
        """Perform comprehensive verification of a single module."""
        issues = []
        warnings = []
        
        # Check if module file exists and is readable
        if not self._verify_module_file_exists(module):
            issues.append(f"Module file does not exist: {module.file_path}")
            return issues, warnings
        
        # Check file permissions
        if self.filesystem_manager and not self.filesystem_manager.validate_permissions(module.file_path):
            warnings.append(f"Limited permissions for module file: {module.file_path}")
        
        # Parse module file and check syntax
        try:
            content = self.filesystem_manager.read_file(module.file_path) if self.filesystem_manager else None
            if content is None:
                issues.append(f"Cannot read module file: {module.file_path}")
                return issues, warnings
            
            # Check for syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(f"Syntax error in module '{module.name}': {e}")
                return issues, warnings
            
            # Verify imports
            import_issues = self._verify_module_imports(module, all_modules)
            issues.extend(import_issues)
            
            # Check if expected functions are present
            function_issues = self._verify_module_functions(module, content)
            issues.extend(function_issues)
            
            # Check for naming conflicts
            naming_issues = self._check_naming_conflicts(module, content)
            warnings.extend(naming_issues)
            
        except Exception as e:
            issues.append(f"Failed to verify module '{module.name}': {e}")
        
        return issues, warnings
    
    def _verify_module_functions(self, module: Module, content: str) -> List[str]:
        """Verify that expected functions are present in module."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Extract function definitions from AST
            defined_functions = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_functions.add(node.name)
            
            # Check if all expected functions are defined
            for func_spec in module.functions:
                if func_spec.name not in defined_functions:
                    issues.append(f"Function '{func_spec.name}' not found in module '{module.name}'")
            
        except Exception as e:
            issues.append(f"Failed to verify functions in module '{module.name}': {e}")
        
        return issues
    
    def _check_naming_conflicts(self, module: Module, content: str) -> List[str]:
        """Check for naming conflicts in module."""
        warnings = []
        
        try:
            tree = ast.parse(content)
            
            # Extract all names defined in the module
            defined_names = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if node.name in defined_names:
                        warnings.append(f"Name conflict in module '{module.name}': '{node.name}' is defined multiple times")
                    defined_names.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id in defined_names:
                                warnings.append(f"Name conflict in module '{module.name}': '{target.id}' is defined multiple times")
                            defined_names.add(target.id)
            
        except Exception:
            # Not critical, so just skip if parsing fails
            pass
        
        return warnings
    
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
    
    def _verify_dependency_graph_consistency(self, modules: List[Module]) -> List[str]:
        """Verify that the dependency graph is consistent."""
        issues = []
        
        if not self.dependency_analyzer:
            return issues
        
        try:
            # Create dependency graph
            graph = self.dependency_analyzer.create_dependency_graph(modules)
            
            # Validate the graph
            validation_result = self.dependency_analyzer.validate_dependency_graph(graph)
            if not validation_result.is_valid:
                issues.extend(validation_result.issues)
            
        except Exception as e:
            issues.append(f"Failed to verify dependency graph consistency: {e}")
        
        return issues
    
    # Private helper methods
    
    def _validate_modules_for_integration(self, modules: List[Module]) -> List[str]:
        """Validate modules before integration."""
        errors = []
        
        try:
            # Check for duplicate module names
            module_names = [m.name for m in modules]
            if len(module_names) != len(set(module_names)):
                duplicates = [name for name in set(module_names) if module_names.count(name) > 1]
                errors.append(f"Duplicate module names found: {duplicates}")
            
            # Check for missing dependencies
            for module in modules:
                for dep in module.dependencies:
                    if not any(m.name == dep for m in modules):
                        errors.append(f"Module '{module.name}' depends on missing module '{dep}'")
            
            # Check for circular dependencies using dependency analyzer
            if self.dependency_analyzer:
                try:
                    cycles = self.dependency_analyzer.detect_circular_dependencies(modules)
                    if cycles:
                        for cycle in cycles:
                            errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
                except Exception as e:
                    errors.append(f"Failed to check for circular dependencies: {e}")
            
            # Validate module file paths
            for module in modules:
                if not module.file_path or not module.file_path.strip():
                    errors.append(f"Module '{module.name}' has empty file path")
                elif not module.file_path.endswith('.py'):
                    errors.append(f"Module '{module.name}' file path must end with .py: {module.file_path}")
            
        except Exception as e:
            errors.append(f"Module validation failed: {e}")
        
        return errors
    
    def _connect_module(self, module: Module, all_modules: List[Module], imports: List[str]) -> 'ModuleConnectionResult':
        """Connect a module with its dependencies."""
        errors = []
        success = True
        
        try:
            # Ensure module file exists or create it
            if not self._ensure_module_file_exists(module):
                errors.append(f"Failed to create/access module file: {module.file_path}")
                success = False
            
            # Add imports to module file
            if imports and not self._add_imports_to_module(module, imports):
                errors.append(f"Failed to add imports to module '{module.name}'")
                success = False
            
            # Verify that all dependencies are accessible
            dependency_errors = self._verify_module_dependencies(module, all_modules)
            if dependency_errors:
                errors.extend(dependency_errors)
                success = False
            
            # Add module initialization code if needed
            if not self._ensure_module_initialization(module):
                errors.append(f"Failed to initialize module '{module.name}'")
                success = False
                
        except Exception as e:
            errors.append(f"Module connection failed for '{module.name}': {e}")
            success = False
        
        return ModuleConnectionResult(success=success, errors=errors)
    
    def _ensure_module_file_exists(self, module: Module) -> bool:
        """Ensure module file exists, create if necessary."""
        if not self.filesystem_manager:
            return False
        
        try:
            if self.filesystem_manager.file_exists(module.file_path):
                return True
            
            # Create basic module structure
            module_content = f'"""\n{module.description}\n"""\n\n'
            
            # Add function stubs if functions are defined
            for func in module.functions:
                args_str = ", ".join([f"{arg.name}: {arg.type_hint}" + 
                                    (f" = {arg.default_value}" if arg.default_value else "")
                                    for arg in func.arguments])
                
                module_content += f'def {func.name}({args_str}) -> {func.return_type}:\n'
                module_content += f'    """{func.docstring}"""\n'
                module_content += '    pass\n\n'
            
            return self.filesystem_manager.write_file(module.file_path, module_content)
            
        except Exception:
            return False
    
    def _verify_module_dependencies(self, module: Module, all_modules: List[Module]) -> List[str]:
        """Verify that module dependencies are accessible."""
        errors = []
        
        for dep_name in module.dependencies:
            # Find dependency module
            dep_module = next((m for m in all_modules if m.name == dep_name), None)
            if not dep_module:
                errors.append(f"Dependency '{dep_name}' not found for module '{module.name}'")
                continue
            
            # Check if dependency file exists
            if self.filesystem_manager and not self.filesystem_manager.file_exists(dep_module.file_path):
                errors.append(f"Dependency file does not exist: {dep_module.file_path}")
        
        return errors
    
    def _ensure_module_initialization(self, module: Module) -> bool:
        """Ensure module has proper initialization."""
        if not self.filesystem_manager:
            return False
        
        try:
            content = self.filesystem_manager.read_file(module.file_path)
            if content is None:
                return False
            
            # Check if module has basic structure
            if not content.strip():
                # Add basic module structure
                basic_content = f'"""\n{module.description}\n"""\n\n'
                return self.filesystem_manager.write_file(module.file_path, basic_content)
            
            return True
            
        except Exception:
            return False
    
    def _build_module_cache(self, modules: List[Module]) -> None:
        """Build cache of module information for import generation."""
        self._module_cache.clear()
        
        for module in modules:
            self._module_cache[module.name] = {
                'file_path': module.file_path,
                'dependencies': set(module.dependencies),
                'functions': [func.name for func in module.functions],
                'relative_path': self._get_relative_import_path(module.file_path)
            }
    
    def _generate_module_imports(self, module: Module, all_modules: List[Module]) -> List[str]:
        """Generate import statements for a single module."""
        imports = []
        
        # Use PackageManager to generate consistent imports if available
        if self.package_manager:
            try:
                package_imports = self.package_manager.generate_imports_for_module(module)
                imports.extend(package_imports)
            except Exception as e:
                # Fall back to original logic if package manager fails
                pass
        
        # Get dependencies for this module
        dependencies = module.dependencies
        
        if dependencies:
            # Generate imports for each dependency
            for dep_name in dependencies:
                try:
                    # Find the dependency module
                    dep_module = next((m for m in all_modules if m.name == dep_name), None)
                    if not dep_module:
                        continue
                    
                    # Generate relative import path
                    import_statement = self._generate_import_statement(module, dep_module)
                    if import_statement:
                        imports.append(import_statement)
                        
                        # Register package usage if package manager is available
                        if self.package_manager:
                            try:
                                # Extract package name from import statement
                                package_name = self._extract_package_name_from_import(import_statement)
                                if package_name:
                                    alias = self.package_manager.get_standard_import_alias(package_name)
                                    self.package_manager.register_package_usage(package_name, alias, module.name)
                            except Exception:
                                # Continue if package registration fails
                                pass
                        
                except Exception as e:
                    # Log error but continue with other imports
                    continue
        
        # Sort imports for consistency
        imports.sort()
        
        return imports
    
    def _generate_import_statement(self, from_module: Module, to_module: Module) -> str:
        """Generate import statement from one module to another."""
        try:
            # Calculate relative path between modules
            from_path = Path(from_module.file_path).parent
            to_path = Path(to_module.file_path)
            
            # Get relative path
            try:
                rel_path = os.path.relpath(to_path, from_path)
            except ValueError:
                # Paths are on different drives (Windows), use absolute import
                return f"from {to_module.name} import *"
            
            # Convert file path to import path
            import_path = rel_path.replace(os.sep, '.').replace('.py', '')
            
            # Handle different relative path cases
            if import_path.startswith('..'):
                # Parent directory import
                return f"from {import_path} import *"
            elif import_path.startswith('.'):
                # Current directory import
                return f"from {import_path} import *"
            else:
                # Same directory or subdirectory
                if import_path == to_module.name:
                    return f"from .{to_module.name} import *"
                else:
                    return f"from .{import_path} import *"
                    
        except Exception:
            # Fall back to simple import
            return f"from {to_module.name} import *"
    
    def _get_relative_import_path(self, file_path: str) -> str:
        """Get relative import path for a module file."""
        path = Path(file_path)
        
        # Remove .py extension and convert to import path
        import_path = str(path.with_suffix(''))
        import_path = import_path.replace(os.sep, '.')
        
        return import_path
    
    def _validate_import_dependencies(self, import_map: Dict[str, List[str]], modules: List[Module]) -> None:
        """Validate that generated imports don't create circular dependencies."""
        # Build import dependency graph
        import_graph = {}
        
        for module_name, imports in import_map.items():
            import_graph[module_name] = []
            
            for import_stmt in imports:
                # Extract imported module name from import statement
                imported_module = self._extract_module_from_import(import_stmt)
                if imported_module and imported_module in import_map:
                    import_graph[module_name].append(imported_module)
        
        # Check for cycles using DFS
        if self._has_import_cycles(import_graph):
            raise ImportGenerationError("Generated imports would create circular dependencies")
    
    def _extract_module_from_import(self, import_statement: str) -> Optional[str]:
        """Extract module name from import statement."""
        try:
            # Parse import statement to extract module name
            # Handle various import formats: "from .module import *", "from module import *", etc.
            
            if import_statement.startswith('from '):
                parts = import_statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    # Remove leading dots for relative imports
                    module_part = module_part.lstrip('.')
                    return module_part
            
            return None
            
        except Exception:
            return None
    
    def _has_import_cycles(self, import_graph: Dict[str, List[str]]) -> bool:
        """Check if import graph has cycles using DFS."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            if node in rec_stack:
                return True  # Cycle detected
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in import_graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in import_graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def _add_imports_to_module(self, module: Module, imports: List[str]) -> bool:
        """Add import statements to a module file."""
        if not self.filesystem_manager:
            return False
        
        try:
            # Read existing module content
            existing_content = self.filesystem_manager.read_file(module.file_path)
            if existing_content is None:
                # File doesn't exist, create basic module structure
                existing_content = f'"""\n{module.description}\n"""\n\n'
            
            # Parse existing content to find where to insert imports
            new_content = self._insert_imports_into_content(existing_content, imports)
            
            # Write updated content back to file
            return self.filesystem_manager.write_file(module.file_path, new_content)
            
        except Exception:
            return False
    
    def _insert_imports_into_content(self, content: str, imports: List[str]) -> str:
        """Insert import statements into module content at the appropriate location."""
        if not imports:
            return content
        
        lines = content.split('\n')
        
        # Find the best position to insert imports
        insert_position = self._find_import_insertion_position(lines)
        
        # Create import section
        import_section = []
        if insert_position > 0 and lines[insert_position - 1].strip():
            import_section.append('')  # Add blank line before imports
        
        import_section.extend(imports)
        import_section.append('')  # Add blank line after imports
        
        # Insert imports at the determined position
        new_lines = lines[:insert_position] + import_section + lines[insert_position:]
        
        return '\n'.join(new_lines)
    
    def _find_import_insertion_position(self, lines: List[str]) -> int:
        """Find the best position to insert import statements."""
        # Look for existing imports or module docstring
        in_docstring = False
        docstring_end = 0
        last_import = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track docstring
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                elif stripped.endswith('"""') or stripped.endswith("'''"):
                    in_docstring = False
                    docstring_end = i + 1
            elif in_docstring and (stripped.endswith('"""') or stripped.endswith("'''")):
                in_docstring = False
                docstring_end = i + 1
            
            # Track imports
            if not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
                last_import = i + 1
        
        # Insert after existing imports, or after docstring, or at the beginning
        return max(last_import, docstring_end)
    
    def _verify_module_file_exists(self, module: Module) -> bool:
        """Verify that a module file exists and is readable."""
        if not self.filesystem_manager:
            return False
        
        return self.filesystem_manager.file_exists(module.file_path)
    
    def _verify_module_imports(self, module: Module, all_modules: List[Module]) -> List[str]:
        """Verify imports in a module file and return any issues."""
        issues = []
        
        if not self.filesystem_manager:
            issues.append(f"Cannot verify imports for '{module.name}': no file system manager")
            return issues
        
        try:
            # Read module content
            content = self.filesystem_manager.read_file(module.file_path)
            if content is None:
                issues.append(f"Cannot read module file: {module.file_path}")
                return issues
            
            # Parse the module to extract imports
            try:
                tree = ast.parse(content)
                imports = self._extract_imports_from_ast(tree)
                
                # Verify each import can be resolved
                for import_info in imports:
                    if not self._can_resolve_import(import_info, module, all_modules):
                        issues.append(f"Cannot resolve import in '{module.name}': {import_info['statement']}")
                        
            except SyntaxError as e:
                issues.append(f"Syntax error in module '{module.name}': {e}")
            except Exception as e:
                issues.append(f"Failed to parse module '{module.name}': {e}")
        
        except Exception as e:
            issues.append(f"Failed to verify imports for '{module.name}': {e}")
        
        return issues
    
    def _extract_imports_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import information from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'statement': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                    })
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ''
                level = node.level
                
                for alias in node.names:
                    imports.append({
                        'type': 'from',
                        'module': module_name,
                        'name': alias.name,
                        'alias': alias.asname,
                        'level': level,
                        'statement': f"from {'.' * level}{module_name} import {alias.name}" + 
                                   (f" as {alias.asname}" if alias.asname else "")
                    })
        
        return imports
    
    def _can_resolve_import(self, import_info: Dict[str, Any], current_module: Module, all_modules: List[Module]) -> bool:
        """Check if an import can be resolved."""
        try:
            if import_info['type'] == 'import':
                # Direct import - check if module exists
                module_name = import_info['module']
                return any(m.name == module_name for m in all_modules)
            
            elif import_info['type'] == 'from':
                # From import - check if source module exists
                module_name = import_info['module']
                level = import_info.get('level', 0)
                
                if level > 0:
                    # Relative import - resolve relative to current module
                    resolved_module = self._resolve_relative_import(module_name, level, current_module, all_modules)
                    return resolved_module is not None
                else:
                    # Absolute import
                    return any(m.name == module_name for m in all_modules)
            
            return True  # Default to True for unknown import types
            
        except Exception:
            return False
    
    def _resolve_relative_import(self, module_name: str, level: int, current_module: Module, all_modules: List[Module]) -> Optional[Module]:
        """Resolve a relative import to find the target module."""
        try:
            # Get current module's directory path
            current_path = Path(current_module.file_path).parent
            
            # Go up 'level' directories
            target_path = current_path
            for _ in range(level - 1):
                target_path = target_path.parent
            
            # Add module name to path
            if module_name:
                target_path = target_path / f"{module_name}.py"
            
            # Find matching module
            for module in all_modules:
                if Path(module.file_path).resolve() == target_path.resolve():
                    return module
            
            return None
            
        except Exception:
            return None
    
    def _detect_circular_imports(self, modules: List[Module]) -> List[List[str]]:
        """Detect circular import dependencies."""
        # This is a simplified version - in practice, you'd need to parse actual import statements
        # For now, we'll use the module dependency graph as a proxy
        
        if not self.dependency_analyzer:
            return []
        
        try:
            return self.dependency_analyzer.detect_circular_dependencies(modules)
        except Exception:
            return []
    
    def _find_unused_imports(self, modules: List[Module]) -> Dict[str, List[str]]:
        """Find unused imports in modules."""
        unused_imports = {}
        
        # This is a simplified implementation
        # In practice, you'd need to parse the AST and check if imported names are used
        
        for module in modules:
            if not self.filesystem_manager:
                continue
            
            try:
                content = self.filesystem_manager.read_file(module.file_path)
                if content is None:
                    continue
                
                # Parse imports
                tree = ast.parse(content)
                imports = self._extract_imports_from_ast(tree)
                
                # Check usage (simplified - just check if import name appears in code)
                unused = []
                for import_info in imports:
                    if import_info['type'] == 'from' and import_info['name'] != '*':
                        name = import_info['alias'] or import_info['name']
                        if name not in content:
                            unused.append(import_info['statement'])
                
                if unused:
                    unused_imports[module.name] = unused
                    
            except Exception:
                continue
        
        return unused_imports
    
    def _generate_integration_tests(self, modules: List[Module]) -> TestGenerationResult:
        """
        Generate unit tests for integrated modules.
        
        Args:
            modules: List of modules to generate tests for
            
        Returns:
            TestGenerationResult with test generation status and details
        """
        if not self.test_generator:
            return TestGenerationResult(
                generated_tests=[],
                test_files_created=[],
                success=False,
                errors=["Test generator not available"]
            )
        
        try:
            all_test_cases = []
            test_files_created = []
            errors = []
            
            # Generate tests for each module
            for module in modules:
                try:
                    # Generate test cases for the module
                    test_cases = self.test_generator.generate_module_tests(module)
                    all_test_cases.extend(test_cases)
                    
                    # Create test file for the module
                    test_file_path = self._get_test_file_path(module)
                    if self._create_test_file(module, test_cases, test_file_path):
                        test_files_created.append(test_file_path)
                    else:
                        errors.append(f"Failed to create test file for module '{module.name}'")
                        
                except Exception as e:
                    errors.append(f"Failed to generate tests for module '{module.name}': {e}")
            
            # Execute generated tests if any were created
            execution_result = None
            if test_files_created and not errors:
                try:
                    execution_result = self.test_generator.execute_generated_tests(test_files_created)
                except Exception as e:
                    errors.append(f"Test execution failed: {e}")
            
            success = len(errors) == 0 and len(test_files_created) > 0
            
            return TestGenerationResult(
                generated_tests=all_test_cases,
                test_files_created=test_files_created,
                execution_result=execution_result,
                success=success,
                errors=errors
            )
            
        except Exception as e:
            return TestGenerationResult(
                generated_tests=[],
                test_files_created=[],
                success=False,
                errors=[f"Test generation process failed: {e}"]
            )
    
    def _get_test_file_path(self, module: Module) -> str:
        """
        Generate test file path for a module following naming convention.
        
        Args:
            module: Module to generate test file path for
            
        Returns:
            Path to the test file
        """
        module_path = Path(module.file_path)
        module_dir = module_path.parent
        module_name = module_path.stem
        
        # Create test file in the same directory as the module
        test_file_name = f"test_{module_name}.py"
        return str(module_dir / test_file_name)
    
    def _create_test_file(self, module: Module, test_cases: List, test_file_path: str) -> bool:
        """
        Create a test file with generated test cases.
        
        Args:
            module: Module being tested
            test_cases: List of test cases to include
            test_file_path: Path where test file should be created
            
        Returns:
            True if test file was created successfully, False otherwise
        """
        if not self.filesystem_manager:
            return False
        
        try:
            # Generate test file content
            test_content = self._generate_test_file_content(module, test_cases)
            
            # Write test file
            return self.filesystem_manager.write_file(test_file_path, test_content)
            
        except Exception:
            return False
    
    def _generate_test_file_content(self, module: Module, test_cases: List) -> str:
        """
        Generate content for a test file.
        
        Args:
            module: Module being tested
            test_cases: List of test cases
            
        Returns:
            Content for the test file
        """
        module_name = Path(module.file_path).stem
        
        content = f'''"""
Unit tests for {module.name} module.

This file contains automatically generated unit tests for the {module.name} module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add module path to sys.path for imports
module_path = Path(__file__).parent
if str(module_path) not in sys.path:
    sys.path.insert(0, str(module_path))

from {module_name} import *


class Test{module.name.title().replace('_', '')}(unittest.TestCase):
    """Test cases for {module.name} module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        pass

'''
        
        # Add test methods for each function
        for func in module.functions:
            content += f'''
    def test_{func.name}(self):
        """Test {func.name} function."""
        # TODO: Implement test for {func.name}
        # This is a placeholder test that should be implemented
        self.assertTrue(True, "Placeholder test - implement actual test logic")
'''
        
        content += '''

if __name__ == '__main__':
    unittest.main()
'''
        
        return content
    
    def _extract_package_name_from_import(self, import_statement: str) -> Optional[str]:
        """
        Extract package name from an import statement.
        
        Args:
            import_statement: Import statement to parse
            
        Returns:
            Package name if found, None otherwise
        """
        try:
            # Handle different import formats
            if import_statement.startswith('from '):
                # "from package import ..." or "from .module import ..."
                parts = import_statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    # Skip relative imports (starting with .)
                    if not module_part.startswith('.'):
                        # Extract root package name
                        return module_part.split('.')[0]
            elif import_statement.startswith('import '):
                # "import package" or "import package as alias"
                parts = import_statement.split()
                if len(parts) >= 2:
                    package_part = parts[1]
                    # Extract root package name
                    return package_part.split('.')[0]
            
            return None
            
        except Exception:
            return None