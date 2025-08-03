"""
Package Manager for AI Project Builder.

This module provides functionality for tracking and managing package imports
with consistent naming conventions across the project.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .base import BasePackageManager
from ..core.models import PackageInfo, PackageRegistry, ValidationError


class PackageManager(BasePackageManager):
    """
    Manages package imports and ensures consistent naming conventions.
    
    This manager tracks package usage across modules, maintains standard
    import aliases, and generates consistent import statements without
    requiring LLM calls during integration.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the package manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        self.registry = PackageRegistry(project_path=str(self.project_path))
        self._load_standard_aliases()
        self._registry_file = self.project_path / ".A3" / "package_registry.json"
    
    def initialize(self) -> None:
        """Initialize the package manager and load existing registry."""
        super().initialize()
        
        # Ensure .A3 directory exists
        a3_dir = self.project_path / ".A3"
        a3_dir.mkdir(exist_ok=True)
        
        # Load existing registry if it exists
        self._load_registry()
    
    def _load_standard_aliases(self) -> None:
        """Load standard package aliases mapping."""
        # Standard aliases for common packages
        standard_aliases = {
            # Data Science & Analytics
            "pandas": "pd",
            "numpy": "np",
            "matplotlib": "plt",
            "matplotlib.pyplot": "plt",
            "seaborn": "sns",
            "plotly": "plotly",
            "plotly.express": "px",
            "plotly.graph_objects": "go",
            "scipy": "scipy",
            "scikit-learn": "sklearn",
            "sklearn": "sklearn",
            
            # Web & HTTP
            "requests": "requests",
            "urllib": "urllib",
            "flask": "flask",
            "django": "django",
            "fastapi": "fastapi",
            "aiohttp": "aiohttp",
            
            # Database
            "sqlalchemy": "sqlalchemy",
            "psycopg2": "psycopg2",
            "pymongo": "pymongo",
            "redis": "redis",
            
            # Utilities
            "json": "json",
            "os": "os",
            "sys": "sys",
            "re": "re",
            "datetime": "datetime",
            "pathlib": "pathlib",
            "collections": "collections",
            "itertools": "itertools",
            "functools": "functools",
            "typing": "typing",
            
            # Testing
            "pytest": "pytest",
            "unittest": "unittest",
            "mock": "mock",
            
            # Async
            "asyncio": "asyncio",
            "concurrent": "concurrent",
            "threading": "threading",
            "multiprocessing": "multiprocessing",
            
            # File formats
            "yaml": "yaml",
            "toml": "toml",
            "csv": "csv",
            "xml": "xml",
            
            # Logging
            "logging": "logging",
            "loguru": "loguru",
            
            # Configuration
            "configparser": "configparser",
            "argparse": "argparse",
            "click": "click",
            
            # Machine Learning
            "tensorflow": "tf",
            "torch": "torch",
            "transformers": "transformers",
            "huggingface_hub": "huggingface_hub"
        }
        
        # Update registry with standard aliases
        for package_name, alias in standard_aliases.items():
            self.registry.standard_aliases[package_name] = alias
            
            # Create PackageInfo if not exists
            if package_name not in self.registry.packages:
                package_info = PackageInfo(
                    name=package_name,
                    standard_alias=alias
                )
                self.registry.packages[package_name] = package_info
    
    def _load_registry(self) -> None:
        """Load package registry from file if it exists."""
        if self._registry_file.exists():
            try:
                with open(self._registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Reconstruct registry from JSON data
                self.registry.project_path = data.get('project_path', str(self.project_path))
                self.registry.requirements = data.get('requirements', [])
                self.registry.module_imports = data.get('module_imports', {})
                
                # Reconstruct packages
                packages_data = data.get('packages', {})
                for package_name, package_data in packages_data.items():
                    package_info = PackageInfo(
                        name=package_data['name'],
                        standard_alias=package_data['standard_alias'],
                        version=package_data.get('version'),
                        modules_using=package_data.get('modules_using', []),
                        import_count=package_data.get('import_count', 0),
                        last_used=datetime.fromisoformat(package_data.get('last_used', datetime.now().isoformat()))
                    )
                    self.registry.packages[package_name] = package_info
                
                # Update standard aliases from loaded packages
                for package_name, package_info in self.registry.packages.items():
                    self.registry.standard_aliases[package_name] = package_info.standard_alias
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # If registry file is corrupted, start fresh but log warning
                print(f"Warning: Could not load package registry: {e}. Starting with fresh registry.")
    
    def _save_registry(self) -> None:
        """Save package registry to file."""
        try:
            # Prepare data for JSON serialization
            packages_data = {}
            for package_name, package_info in self.registry.packages.items():
                packages_data[package_name] = {
                    'name': package_info.name,
                    'standard_alias': package_info.standard_alias,
                    'version': package_info.version,
                    'modules_using': package_info.modules_using,
                    'import_count': package_info.import_count,
                    'last_used': package_info.last_used.isoformat()
                }
            
            registry_data = {
                'project_path': self.registry.project_path,
                'packages': packages_data,
                'standard_aliases': self.registry.standard_aliases,
                'module_imports': self.registry.module_imports,
                'requirements': self.registry.requirements,
                'last_updated': self.registry.last_updated.isoformat()
            }
            
            # Ensure directory exists
            self._registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(self._registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
                
        except (OSError, ValueError) as e:
            print(f"Warning: Could not save package registry: {e}")
    
    def register_package_usage(self, package_name: str, alias: str, module: str) -> None:
        """
        Register package usage in a module.
        
        Args:
            package_name: Name of the package being used
            alias: Alias used for the package import
            module: Name of the module using the package
        """
        self._ensure_initialized()
        
        if not package_name or not package_name.strip():
            raise ValidationError("Package name cannot be empty")
        
        if not module or not module.strip():
            raise ValidationError("Module name cannot be empty")
        
        # Clean inputs
        package_name = package_name.strip()
        alias = alias.strip() if alias else ""
        module = module.strip()
        
        # Get or create package info
        if package_name not in self.registry.packages:
            # Determine standard alias
            standard_alias = self.get_standard_import_alias(package_name)
            if not standard_alias:
                # Use provided alias or package name as fallback
                standard_alias = alias if alias else package_name
            
            package_info = PackageInfo(
                name=package_name,
                standard_alias=standard_alias
            )
            self.registry.packages[package_name] = package_info
            self.registry.standard_aliases[package_name] = standard_alias
        
        # Register usage
        self.registry.register_usage(package_name, module)
        
        # Update module imports
        if module not in self.registry.module_imports:
            self.registry.module_imports[module] = []
        
        # Generate import statement
        import_statement = self._generate_import_statement(package_name, alias)
        if import_statement not in self.registry.module_imports[module]:
            self.registry.module_imports[module].append(import_statement)
        
        # Save registry
        self._save_registry()
    
    def get_standard_import_alias(self, package_name: str) -> str:
        """
        Get the standard import alias for a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Standard alias for the package
        """
        if not package_name or not package_name.strip():
            return ""
        
        package_name = package_name.strip()
        
        # Check if we have a standard alias
        if package_name in self.registry.standard_aliases:
            return self.registry.standard_aliases[package_name]
        
        # For submodules, try to find parent package alias
        if '.' in package_name:
            parent_package = package_name.split('.')[0]
            if parent_package in self.registry.standard_aliases:
                return self.registry.standard_aliases[parent_package]
        
        # Default to package name if no standard alias found
        return package_name
    
    def generate_imports_for_module(self, module) -> List[str]:
        """
        Generate consistent import statements for a module.
        
        Args:
            module: Module object or module name
            
        Returns:
            List of import statements
        """
        self._ensure_initialized()
        
        # Handle both Module objects and string names
        if hasattr(module, 'name'):
            module_name = module.name
        else:
            module_name = str(module)
        
        if module_name not in self.registry.module_imports:
            return []
        
        # Get imports for this module
        imports = self.registry.module_imports[module_name].copy()
        
        # Sort imports for consistency
        imports.sort()
        
        return imports
    
    def update_requirements_file(self, project_path: str) -> None:
        """
        Update the requirements.txt file with all used packages.
        
        Args:
            project_path: Path to the project directory
        """
        self._ensure_initialized()
        
        project_dir = Path(project_path)
        requirements_file = project_dir / "requirements.txt"
        
        # Collect all packages that are not built-in
        builtin_modules = {
            'os', 'sys', 're', 'json', 'datetime', 'pathlib', 'collections',
            'itertools', 'functools', 'typing', 'unittest', 'csv', 'xml',
            'logging', 'configparser', 'argparse', 'asyncio', 'concurrent',
            'threading', 'multiprocessing', 'urllib'
        }
        
        external_packages = []
        for package_name, package_info in self.registry.packages.items():
            # Skip built-in modules
            if package_name in builtin_modules:
                continue
            
            # Skip submodules of built-in packages
            if '.' in package_name:
                parent = package_name.split('.')[0]
                if parent in builtin_modules:
                    continue
            
            # Only include packages that are actually used
            if package_info.import_count > 0:
                if package_info.version:
                    external_packages.append(f"{package_name}=={package_info.version}")
                else:
                    external_packages.append(package_name)
        
        # Sort packages for consistency
        external_packages.sort()
        
        # Update registry requirements
        self.registry.requirements = external_packages
        
        # Write to requirements.txt
        try:
            with open(requirements_file, 'w', encoding='utf-8') as f:
                for package in external_packages:
                    f.write(f"{package}\n")
        except OSError as e:
            print(f"Warning: Could not write requirements.txt: {e}")
        
        # Save registry
        self._save_registry()
    
    def _generate_import_statement(self, package_name: str, provided_alias: str = "") -> str:
        """
        Generate a consistent import statement for a package.
        
        Args:
            package_name: Name of the package
            provided_alias: Alias provided by the user (optional)
            
        Returns:
            Import statement string
        """
        standard_alias = self.get_standard_import_alias(package_name)
        
        # Use standard alias if available, otherwise use provided alias
        alias_to_use = standard_alias if standard_alias != package_name else provided_alias
        
        if alias_to_use and alias_to_use != package_name:
            return f"import {package_name} as {alias_to_use}"
        else:
            return f"import {package_name}"
    
    def validate_import_consistency(self, module_name: str) -> List[str]:
        """
        Validate import consistency for a module.
        
        Args:
            module_name: Name of the module to validate
            
        Returns:
            List of inconsistency warnings
        """
        self._ensure_initialized()
        
        warnings = []
        
        if module_name not in self.registry.module_imports:
            return warnings
        
        imports = self.registry.module_imports[module_name]
        
        # Check each import for consistency
        for import_stmt in imports:
            # Parse import statement
            if " as " in import_stmt:
                # Format: "import package as alias"
                parts = import_stmt.replace("import ", "").split(" as ")
                if len(parts) == 2:
                    package_name = parts[0].strip()
                    used_alias = parts[1].strip()
                    
                    standard_alias = self.get_standard_import_alias(package_name)
                    if standard_alias != package_name and used_alias != standard_alias:
                        warnings.append(
                            f"Module '{module_name}' uses alias '{used_alias}' for '{package_name}', "
                            f"but standard alias is '{standard_alias}'"
                        )
            else:
                # Format: "import package"
                package_name = import_stmt.replace("import ", "").strip()
                standard_alias = self.get_standard_import_alias(package_name)
                
                if standard_alias != package_name:
                    warnings.append(
                        f"Module '{module_name}' imports '{package_name}' without alias, "
                        f"but standard alias is '{standard_alias}'"
                    )
        
        return warnings
    
    def get_package_usage_stats(self) -> Dict[str, Dict[str, any]]:
        """
        Get usage statistics for all packages.
        
        Returns:
            Dictionary with package usage statistics
        """
        self._ensure_initialized()
        
        stats = {}
        
        for package_name, package_info in self.registry.packages.items():
            stats[package_name] = {
                'standard_alias': package_info.standard_alias,
                'version': package_info.version,
                'import_count': package_info.import_count,
                'modules_using': len(package_info.modules_using),
                'module_names': package_info.modules_using.copy(),
                'last_used': package_info.last_used.isoformat()
            }
        
        return stats
    
    def get_module_dependencies(self, module_name: str) -> List[str]:
        """
        Get list of packages that a module depends on.
        
        Args:
            module_name: Name of the module
            
        Returns:
            List of package names the module depends on
        """
        self._ensure_initialized()
        
        dependencies = []
        
        for package_name, package_info in self.registry.packages.items():
            if module_name in package_info.modules_using:
                dependencies.append(package_name)
        
        return sorted(dependencies)
    
    def cleanup_unused_packages(self) -> List[str]:
        """
        Remove packages that are no longer used by any module.
        
        Returns:
            List of removed package names
        """
        self._ensure_initialized()
        
        removed_packages = []
        packages_to_remove = []
        
        for package_name, package_info in self.registry.packages.items():
            if package_info.import_count == 0 or not package_info.modules_using:
                packages_to_remove.append(package_name)
        
        for package_name in packages_to_remove:
            del self.registry.packages[package_name]
            if package_name in self.registry.standard_aliases:
                del self.registry.standard_aliases[package_name]
            removed_packages.append(package_name)
        
        # Update requirements
        self.registry.requirements = [
            req for req in self.registry.requirements
            if not any(req.startswith(removed_pkg) for removed_pkg in removed_packages)
        ]
        
        if removed_packages:
            self._save_registry()
        
        return removed_packages
    
    def reset_registry(self) -> None:
        """Reset the package registry to initial state."""
        self.registry = PackageRegistry(project_path=str(self.project_path))
        self._load_standard_aliases()
        self._save_registry()
    
    def generate_all_imports(self) -> Dict[str, List[str]]:
        """
        Generate import statements for all modules in the project.
        
        Returns:
            Dictionary mapping module names to their import statements
        """
        self._ensure_initialized()
        
        all_imports = {}
        for module_name in self.registry.module_imports.keys():
            all_imports[module_name] = self.generate_imports_for_module(module_name)
        
        return all_imports
    
    def validate_all_imports(self) -> Dict[str, List[str]]:
        """
        Validate import consistency for all modules in the project.
        
        Returns:
            Dictionary mapping module names to their consistency warnings
        """
        self._ensure_initialized()
        
        all_warnings = {}
        for module_name in self.registry.module_imports.keys():
            warnings = self.validate_import_consistency(module_name)
            if warnings:
                all_warnings[module_name] = warnings
        
        return all_warnings
    
    def suggest_import_corrections(self, module_name: str) -> List[str]:
        """
        Suggest corrected import statements for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            List of suggested corrected import statements
        """
        self._ensure_initialized()
        
        if module_name not in self.registry.module_imports:
            return []
        
        corrected_imports = []
        imports = self.registry.module_imports[module_name]
        
        for import_stmt in imports:
            # Parse import statement
            if " as " in import_stmt:
                # Format: "import package as alias"
                parts = import_stmt.replace("import ", "").split(" as ")
                if len(parts) == 2:
                    package_name = parts[0].strip()
                    used_alias = parts[1].strip()
                    
                    standard_alias = self.get_standard_import_alias(package_name)
                    if standard_alias != package_name and used_alias != standard_alias:
                        corrected_imports.append(f"import {package_name} as {standard_alias}")
                    else:
                        corrected_imports.append(import_stmt)
                else:
                    corrected_imports.append(import_stmt)
            else:
                # Format: "import package"
                package_name = import_stmt.replace("import ", "").strip()
                standard_alias = self.get_standard_import_alias(package_name)
                
                if standard_alias != package_name:
                    corrected_imports.append(f"import {package_name} as {standard_alias}")
                else:
                    corrected_imports.append(import_stmt)
        
        return corrected_imports
    
    def auto_correct_imports(self, module_name: str) -> bool:
        """
        Automatically correct import statements for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            True if corrections were made, False otherwise
        """
        self._ensure_initialized()
        
        if module_name not in self.registry.module_imports:
            return False
        
        original_imports = self.registry.module_imports[module_name].copy()
        corrected_imports = self.suggest_import_corrections(module_name)
        
        if original_imports != corrected_imports:
            self.registry.module_imports[module_name] = corrected_imports
            self._save_registry()
            return True
        
        return False
    
    def get_import_summary(self) -> Dict[str, any]:
        """
        Get a summary of import usage across the project.
        
        Returns:
            Dictionary with import usage summary
        """
        self._ensure_initialized()
        
        total_modules = len(self.registry.module_imports)
        total_packages = len([pkg for pkg in self.registry.packages.values() if pkg.import_count > 0])
        total_imports = sum(len(imports) for imports in self.registry.module_imports.values())
        
        # Find most used packages
        most_used_packages = sorted(
            [(pkg.name, pkg.import_count) for pkg in self.registry.packages.values()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find modules with most imports
        modules_with_most_imports = sorted(
            [(module, len(imports)) for module, imports in self.registry.module_imports.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Check for consistency issues
        all_warnings = self.validate_all_imports()
        total_warnings = sum(len(warnings) for warnings in all_warnings.values())
        
        return {
            'total_modules': total_modules,
            'total_packages': total_packages,
            'total_imports': total_imports,
            'most_used_packages': most_used_packages,
            'modules_with_most_imports': modules_with_most_imports,
            'consistency_warnings': total_warnings,
            'modules_with_warnings': len(all_warnings),
            'registry_last_updated': self.registry.last_updated.isoformat()
        }