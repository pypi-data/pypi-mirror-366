"""
Unit tests for Package Manager functionality.

This module tests the PackageManager class for alias resolution, package tracking,
requirements.txt generation, and import consistency validation.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from a3.managers.package_manager import PackageManager
from a3.core.models import PackageInfo, PackageRegistry, ValidationError


class TestPackageManager(unittest.TestCase):
    """Test cases for PackageManager functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Create .A3 directory
        self.a3_dir = self.project_path / ".A3"
        self.a3_dir.mkdir(exist_ok=True)
        
        # Initialize package manager
        self.package_manager = PackageManager(str(self.project_path))
        self.package_manager.initialize()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test package manager initialization."""
        # Test that manager is properly initialized
        self.assertTrue(self.package_manager._initialized)
        self.assertEqual(self.package_manager.project_path, self.project_path)
        self.assertTrue(self.a3_dir.exists())
        
        # Test that standard aliases are loaded
        self.assertIn("pandas", self.package_manager.registry.standard_aliases)
        self.assertEqual(self.package_manager.registry.standard_aliases["pandas"], "pd")
        self.assertIn("numpy", self.package_manager.registry.standard_aliases)
        self.assertEqual(self.package_manager.registry.standard_aliases["numpy"], "np")
    
    def test_standard_aliases_loading(self):
        """Test loading of standard package aliases."""
        # Test common data science packages
        expected_aliases = {
            "pandas": "pd",
            "numpy": "np",
            "matplotlib.pyplot": "plt",
            "seaborn": "sns",
            "requests": "requests",
            "json": "json",
            "os": "os",
            "sys": "sys"
        }
        
        for package, expected_alias in expected_aliases.items():
            self.assertEqual(
                self.package_manager.get_standard_import_alias(package),
                expected_alias,
                f"Standard alias for {package} should be {expected_alias}"
            )
    
    def test_register_package_usage_basic(self):
        """Test basic package usage registration."""
        # Register package usage
        self.package_manager.register_package_usage("pandas", "pd", "data_processor")
        
        # Verify package is registered
        self.assertIn("pandas", self.package_manager.registry.packages)
        package_info = self.package_manager.registry.packages["pandas"]
        self.assertEqual(package_info.name, "pandas")
        self.assertEqual(package_info.standard_alias, "pd")
        self.assertIn("data_processor", package_info.modules_using)
        self.assertEqual(package_info.import_count, 1)
        
        # Verify module imports are recorded
        self.assertIn("data_processor", self.package_manager.registry.module_imports)
        imports = self.package_manager.registry.module_imports["data_processor"]
        self.assertIn("import pandas as pd", imports)
    
    def test_register_package_usage_validation(self):
        """Test validation in package usage registration."""
        # Test empty package name
        with self.assertRaises(ValidationError):
            self.package_manager.register_package_usage("", "pd", "module")
        
        # Test empty module name
        with self.assertRaises(ValidationError):
            self.package_manager.register_package_usage("pandas", "pd", "")
        
        # Test whitespace-only names
        with self.assertRaises(ValidationError):
            self.package_manager.register_package_usage("   ", "pd", "module")
        
        with self.assertRaises(ValidationError):
            self.package_manager.register_package_usage("pandas", "pd", "   ")
    
    def test_register_package_usage_multiple_modules(self):
        """Test registering the same package across multiple modules."""
        # Register pandas in multiple modules
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("pandas", "pd", "module2")
        
        # Verify package info is updated correctly
        package_info = self.package_manager.registry.packages["pandas"]
        self.assertEqual(package_info.import_count, 2)
        self.assertIn("module1", package_info.modules_using)
        self.assertIn("module2", package_info.modules_using)
        
        # Verify both modules have imports
        self.assertIn("module1", self.package_manager.registry.module_imports)
        self.assertIn("module2", self.package_manager.registry.module_imports)
    
    def test_register_package_usage_new_package(self):
        """Test registering usage of a new package not in standard aliases."""
        # Register a custom package
        self.package_manager.register_package_usage("custom_package", "cp", "test_module")
        
        # Verify package is registered
        self.assertIn("custom_package", self.package_manager.registry.packages)
        package_info = self.package_manager.registry.packages["custom_package"]
        
        # For new packages, get_standard_import_alias returns the package name itself
        # So the standard_alias will be the package name, not the provided alias
        self.assertEqual(package_info.standard_alias, "custom_package")
        
        # But the import statement should use the provided alias
        imports = self.package_manager.generate_imports_for_module("test_module")
        self.assertEqual(imports, ["import custom_package as cp"])
    
    def test_get_standard_import_alias(self):
        """Test getting standard import aliases."""
        # Test known packages
        self.assertEqual(self.package_manager.get_standard_import_alias("pandas"), "pd")
        self.assertEqual(self.package_manager.get_standard_import_alias("numpy"), "np")
        self.assertEqual(self.package_manager.get_standard_import_alias("requests"), "requests")
        
        # Test submodules
        self.assertEqual(self.package_manager.get_standard_import_alias("matplotlib.pyplot"), "plt")
        
        # Test unknown package (should return package name)
        self.assertEqual(
            self.package_manager.get_standard_import_alias("unknown_package"),
            "unknown_package"
        )
        
        # Test empty/invalid input
        self.assertEqual(self.package_manager.get_standard_import_alias(""), "")
        self.assertEqual(self.package_manager.get_standard_import_alias("   "), "")
    
    def test_generate_imports_for_module(self):
        """Test generating import statements for a module."""
        # Register some packages for a module
        self.package_manager.register_package_usage("pandas", "pd", "test_module")
        self.package_manager.register_package_usage("numpy", "np", "test_module")
        self.package_manager.register_package_usage("requests", "", "test_module")
        
        # Generate imports
        imports = self.package_manager.generate_imports_for_module("test_module")
        
        # Verify imports are generated correctly and sorted
        expected_imports = [
            "import numpy as np",
            "import pandas as pd",
            "import requests"
        ]
        self.assertEqual(imports, expected_imports)
    
    def test_generate_imports_for_module_object(self):
        """Test generating imports for a module object."""
        # Create mock module object
        mock_module = Mock()
        mock_module.name = "test_module"
        
        # Register package usage
        self.package_manager.register_package_usage("pandas", "pd", "test_module")
        
        # Generate imports using module object
        imports = self.package_manager.generate_imports_for_module(mock_module)
        
        # Verify imports are generated
        self.assertEqual(imports, ["import pandas as pd"])
    
    def test_generate_imports_for_nonexistent_module(self):
        """Test generating imports for a module that doesn't exist."""
        imports = self.package_manager.generate_imports_for_module("nonexistent_module")
        self.assertEqual(imports, [])
    
    def test_update_requirements_file(self):
        """Test updating requirements.txt file."""
        # Register some packages
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("requests", "", "module2")
        self.package_manager.register_package_usage("os", "", "module3")  # Built-in, should be excluded
        
        # Update requirements file
        self.package_manager.update_requirements_file(str(self.project_path))
        
        # Verify requirements.txt is created
        requirements_file = self.project_path / "requirements.txt"
        self.assertTrue(requirements_file.exists())
        
        # Verify content
        with open(requirements_file, 'r') as f:
            content = f.read().strip().split('\n')
        
        # Should contain external packages but not built-ins
        self.assertIn("pandas", content)
        self.assertIn("requests", content)
        self.assertNotIn("os", content)
        
        # Verify registry is updated
        self.assertIn("pandas", self.package_manager.registry.requirements)
        self.assertIn("requests", self.package_manager.registry.requirements)
    
    def test_update_requirements_file_with_versions(self):
        """Test updating requirements.txt with package versions."""
        # Register package with version
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        package_info = self.package_manager.registry.packages["pandas"]
        package_info.version = "1.5.0"
        
        # Update requirements file
        self.package_manager.update_requirements_file(str(self.project_path))
        
        # Verify versioned requirement
        requirements_file = self.project_path / "requirements.txt"
        with open(requirements_file, 'r') as f:
            content = f.read().strip()
        
        self.assertIn("pandas==1.5.0", content)
    
    def test_validate_import_consistency(self):
        """Test import consistency validation."""
        # The system automatically uses standard aliases, so we need to manually create inconsistent imports
        # to test the validation
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        
        # Manually create an inconsistent import to test validation
        self.package_manager.registry.module_imports["module1"] = [
            "import pandas as pandas",  # Wrong alias
            "import numpy as np"        # Correct alias
        ]
        
        # Validate consistency
        warnings = self.package_manager.validate_import_consistency("module1")
        
        # Should have warning for pandas but not numpy
        self.assertTrue(len(warnings) > 0)
        self.assertTrue(any("pandas" in warning and "standard alias is 'pd'" in warning for warning in warnings))
        self.assertFalse(any("numpy" in warning for warning in warnings))
    
    def test_validate_import_consistency_no_alias_needed(self):
        """Test validation when no alias is needed but one is missing."""
        # Register package that should have alias but doesn't
        self.package_manager.register_package_usage("pandas", "", "module1")
        
        # Manually set import without alias
        self.package_manager.registry.module_imports["module1"] = ["import pandas"]
        
        # Validate consistency
        warnings = self.package_manager.validate_import_consistency("module1")
        
        # Should have warning about missing alias
        self.assertTrue(len(warnings) > 0)
        self.assertTrue(any("without alias" in warning for warning in warnings))
    
    def test_get_package_usage_stats(self):
        """Test getting package usage statistics."""
        # Register some packages
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("pandas", "pd", "module2")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        
        # Get stats
        stats = self.package_manager.get_package_usage_stats()
        
        # Verify pandas stats
        self.assertIn("pandas", stats)
        pandas_stats = stats["pandas"]
        self.assertEqual(pandas_stats["standard_alias"], "pd")
        self.assertEqual(pandas_stats["import_count"], 2)
        self.assertEqual(pandas_stats["modules_using"], 2)
        self.assertIn("module1", pandas_stats["module_names"])
        self.assertIn("module2", pandas_stats["module_names"])
        
        # Verify numpy stats
        self.assertIn("numpy", stats)
        numpy_stats = stats["numpy"]
        self.assertEqual(numpy_stats["import_count"], 1)
        self.assertEqual(numpy_stats["modules_using"], 1)
    
    def test_get_module_dependencies(self):
        """Test getting module dependencies."""
        # Register packages for modules
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        self.package_manager.register_package_usage("requests", "", "module2")
        
        # Get dependencies for module1
        deps = self.package_manager.get_module_dependencies("module1")
        
        # Should return sorted list of packages
        expected_deps = ["numpy", "pandas"]
        self.assertEqual(deps, expected_deps)
        
        # Get dependencies for module2
        deps2 = self.package_manager.get_module_dependencies("module2")
        self.assertEqual(deps2, ["requests"])
        
        # Get dependencies for nonexistent module
        deps3 = self.package_manager.get_module_dependencies("nonexistent")
        self.assertEqual(deps3, [])
    
    def test_cleanup_unused_packages(self):
        """Test cleaning up unused packages."""
        # Register some packages
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        
        # Manually create an unused package
        unused_package = PackageInfo(name="unused_package", standard_alias="up")
        self.package_manager.registry.packages["unused_package"] = unused_package
        self.package_manager.registry.standard_aliases["unused_package"] = "up"
        
        # Clean up unused packages
        removed = self.package_manager.cleanup_unused_packages()
        
        # Verify unused package was removed
        self.assertIn("unused_package", removed)
        self.assertNotIn("unused_package", self.package_manager.registry.packages)
        self.assertNotIn("unused_package", self.package_manager.registry.standard_aliases)
        
        # Verify used packages remain
        self.assertIn("pandas", self.package_manager.registry.packages)
        self.assertIn("numpy", self.package_manager.registry.packages)
    
    def test_suggest_import_corrections(self):
        """Test suggesting import corrections."""
        # Register packages normally
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        
        # Manually create incorrect imports to test correction suggestions
        self.package_manager.registry.module_imports["module1"] = [
            "import pandas as pandas",  # Wrong
            "import numpy as np"        # Correct
        ]
        
        # Get correction suggestions
        corrections = self.package_manager.suggest_import_corrections("module1")
        
        # Should suggest correction for pandas but keep numpy as is
        self.assertIn("import pandas as pd", corrections)
        self.assertIn("import numpy as np", corrections)
        self.assertNotIn("import pandas as pandas", corrections)
    
    def test_auto_correct_imports(self):
        """Test automatic import correction."""
        # Register package normally
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        
        # Manually create incorrect import to test correction
        self.package_manager.registry.module_imports["module1"] = ["import pandas as pandas"]
        
        # Auto-correct imports
        corrected = self.package_manager.auto_correct_imports("module1")
        
        # Should return True indicating corrections were made
        self.assertTrue(corrected)
        
        # Verify imports were corrected
        imports = self.package_manager.generate_imports_for_module("module1")
        self.assertEqual(imports, ["import pandas as pd"])
        
        # Test with already correct imports
        corrected_again = self.package_manager.auto_correct_imports("module1")
        self.assertFalse(corrected_again)  # No corrections needed
    
    def test_get_import_summary(self):
        """Test getting import usage summary."""
        # Register packages across multiple modules
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("pandas", "pd", "module2")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        self.package_manager.register_package_usage("requests", "", "module3")
        
        # Get summary
        summary = self.package_manager.get_import_summary()
        
        # Verify summary structure
        self.assertIn("total_modules", summary)
        self.assertIn("total_packages", summary)
        self.assertIn("total_imports", summary)
        self.assertIn("most_used_packages", summary)
        self.assertIn("modules_with_most_imports", summary)
        self.assertIn("consistency_warnings", summary)
        
        # Verify values
        self.assertEqual(summary["total_modules"], 3)
        self.assertEqual(summary["total_packages"], 3)
        self.assertEqual(summary["total_imports"], 4)
        
        # Most used package should be pandas
        most_used = summary["most_used_packages"][0]
        self.assertEqual(most_used[0], "pandas")
        self.assertEqual(most_used[1], 2)
    
    def test_generate_all_imports(self):
        """Test generating imports for all modules."""
        # Register packages for multiple modules
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module1")
        self.package_manager.register_package_usage("requests", "", "module2")
        
        # Generate all imports
        all_imports = self.package_manager.generate_all_imports()
        
        # Verify structure
        self.assertIn("module1", all_imports)
        self.assertIn("module2", all_imports)
        
        # Verify content
        self.assertEqual(len(all_imports["module1"]), 2)
        self.assertEqual(len(all_imports["module2"]), 1)
        self.assertIn("import pandas as pd", all_imports["module1"])
        self.assertIn("import requests", all_imports["module2"])
    
    def test_validate_all_imports(self):
        """Test validating imports for all modules."""
        # Register packages normally
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module2")
        
        # Manually create inconsistent imports to test validation
        self.package_manager.registry.module_imports["module1"] = ["import pandas as pandas"]  # Wrong
        self.package_manager.registry.module_imports["module2"] = ["import numpy as np"]       # Correct
        
        # Validate all imports
        all_warnings = self.package_manager.validate_all_imports()
        
        # Should have warnings for module1 but not module2
        self.assertIn("module1", all_warnings)
        self.assertNotIn("module2", all_warnings)
        
        # Verify warning content
        warnings = all_warnings["module1"]
        self.assertTrue(len(warnings) > 0)
        self.assertTrue(any("pandas" in warning for warning in warnings))
    
    def test_reset_registry(self):
        """Test resetting the package registry."""
        # Register some packages
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("numpy", "np", "module2")
        
        # Verify packages are registered
        self.assertIn("pandas", self.package_manager.registry.packages)
        self.assertIn("module1", self.package_manager.registry.module_imports)
        
        # Reset registry
        self.package_manager.reset_registry()
        
        # Verify registry is reset but standard aliases remain
        self.assertNotIn("module1", self.package_manager.registry.module_imports)
        self.assertEqual(len(self.package_manager.registry.module_imports), 0)
        
        # Standard aliases should still be loaded
        self.assertIn("pandas", self.package_manager.registry.standard_aliases)
        self.assertEqual(self.package_manager.registry.standard_aliases["pandas"], "pd")


class TestPackageManagerPersistence(unittest.TestCase):
    """Test cases for PackageManager persistence functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.a3_dir = self.project_path / ".A3"
        self.a3_dir.mkdir(exist_ok=True)
        self.registry_file = self.a3_dir / "package_registry.json"
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_registry(self):
        """Test saving and loading package registry."""
        # Create package manager and register some packages
        pm1 = PackageManager(str(self.project_path))
        pm1.initialize()
        pm1.register_package_usage("pandas", "pd", "module1")
        pm1.register_package_usage("numpy", "np", "module2")
        
        # Verify registry file is created
        self.assertTrue(self.registry_file.exists())
        
        # Create new package manager instance
        pm2 = PackageManager(str(self.project_path))
        pm2.initialize()
        
        # Verify data is loaded correctly
        self.assertIn("pandas", pm2.registry.packages)
        self.assertIn("numpy", pm2.registry.packages)
        self.assertIn("module1", pm2.registry.module_imports)
        self.assertIn("module2", pm2.registry.module_imports)
        
        # Verify package info is preserved
        pandas_info = pm2.registry.packages["pandas"]
        self.assertEqual(pandas_info.name, "pandas")
        self.assertEqual(pandas_info.standard_alias, "pd")
        self.assertEqual(pandas_info.import_count, 1)
        self.assertIn("module1", pandas_info.modules_using)
    
    def test_load_corrupted_registry(self):
        """Test handling of corrupted registry file."""
        # Create corrupted registry file
        with open(self.registry_file, 'w') as f:
            f.write("invalid json content")
        
        # Create package manager - should handle corruption gracefully
        pm = PackageManager(str(self.project_path))
        pm.initialize()
        
        # Should still have standard aliases loaded
        self.assertIn("pandas", pm.registry.standard_aliases)
        self.assertEqual(pm.registry.standard_aliases["pandas"], "pd")
        
        # Should have empty module imports
        self.assertEqual(len(pm.registry.module_imports), 0)
    
    def test_registry_file_format(self):
        """Test the format of saved registry file."""
        # Create package manager and register packages
        pm = PackageManager(str(self.project_path))
        pm.initialize()
        pm.register_package_usage("pandas", "pd", "module1")
        
        # Load and verify JSON structure
        with open(self.registry_file, 'r') as f:
            data = json.load(f)
        
        # Verify required fields
        required_fields = ['project_path', 'packages', 'standard_aliases', 
                          'module_imports', 'requirements', 'last_updated']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Verify package structure
        self.assertIn("pandas", data["packages"])
        pandas_data = data["packages"]["pandas"]
        required_package_fields = ['name', 'standard_alias', 'version', 
                                 'modules_using', 'import_count', 'last_used']
        for field in required_package_fields:
            self.assertIn(field, pandas_data)
    
    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_save_registry_error_handling(self, mock_open):
        """Test error handling when saving registry fails."""
        pm = PackageManager(str(self.project_path))
        pm.initialize()
        
        # This should not raise an exception, just print a warning
        pm.register_package_usage("pandas", "pd", "module1")
        
        # Verify the operation completed despite save failure
        self.assertIn("pandas", pm.registry.packages)


class TestPackageManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for PackageManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.package_manager = PackageManager(str(self.project_path))
        self.package_manager.initialize()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_uninitialized_manager_operations(self):
        """Test operations on uninitialized manager."""
        # Create uninitialized manager
        pm = PackageManager(str(self.project_path))
        
        # Operations should raise RuntimeError
        with self.assertRaises(RuntimeError):
            pm.register_package_usage("pandas", "pd", "module1")
        
        with self.assertRaises(RuntimeError):
            pm.generate_imports_for_module("module1")
        
        with self.assertRaises(RuntimeError):
            pm.get_package_usage_stats()
    
    def test_submodule_alias_resolution(self):
        """Test alias resolution for submodules."""
        # Test matplotlib.pyplot should resolve to plt
        alias = self.package_manager.get_standard_import_alias("matplotlib.pyplot")
        self.assertEqual(alias, "plt")
        
        # Test unknown submodule should use parent if available
        self.package_manager.registry.standard_aliases["parent"] = "p"
        alias = self.package_manager.get_standard_import_alias("parent.submodule")
        self.assertEqual(alias, "p")
        
        # Test unknown parent should return full name
        alias = self.package_manager.get_standard_import_alias("unknown.submodule")
        self.assertEqual(alias, "unknown.submodule")
    
    def test_import_statement_generation_edge_cases(self):
        """Test import statement generation edge cases."""
        # Test package with same name as alias
        import_stmt = self.package_manager._generate_import_statement("json", "json")
        self.assertEqual(import_stmt, "import json")
        
        # Test package with different alias
        import_stmt = self.package_manager._generate_import_statement("pandas", "pd")
        self.assertEqual(import_stmt, "import pandas as pd")
        
        # Test package with no provided alias but has standard alias
        import_stmt = self.package_manager._generate_import_statement("pandas", "")
        self.assertEqual(import_stmt, "import pandas as pd")
    
    def test_requirements_file_builtin_filtering(self):
        """Test that built-in modules are filtered from requirements.txt."""
        # Register mix of built-in and external packages
        builtin_packages = ["os", "sys", "json", "datetime", "pathlib", "re"]
        external_packages = ["pandas", "requests", "flask"]
        
        for pkg in builtin_packages:
            self.package_manager.register_package_usage(pkg, "", "test_module")
        
        for pkg in external_packages:
            self.package_manager.register_package_usage(pkg, "", "test_module")
        
        # Update requirements
        self.package_manager.update_requirements_file(str(self.project_path))
        
        # Verify only external packages are in requirements
        requirements_file = self.project_path / "requirements.txt"
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        for pkg in external_packages:
            self.assertIn(pkg, content)
        
        for pkg in builtin_packages:
            # Check that the package name is not in the content as a standalone line
            lines = content.strip().split('\n')
            self.assertNotIn(pkg, lines, f"Built-in package '{pkg}' should not be in requirements.txt")
    
    def test_duplicate_import_prevention(self):
        """Test that duplicate imports are not added."""
        # Register same package multiple times for same module
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        self.package_manager.register_package_usage("pandas", "pd", "module1")
        
        # Should only have one import statement
        imports = self.package_manager.generate_imports_for_module("module1")
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0], "import pandas as pd")
        
        # But import count should reflect multiple registrations
        package_info = self.package_manager.registry.packages["pandas"]
        self.assertEqual(package_info.import_count, 3)
    
    def test_empty_module_imports_handling(self):
        """Test handling of modules with no imports."""
        # Test generating imports for module with no registered packages
        imports = self.package_manager.generate_imports_for_module("empty_module")
        self.assertEqual(imports, [])
        
        # Test validation for module with no imports
        warnings = self.package_manager.validate_import_consistency("empty_module")
        self.assertEqual(warnings, [])
        
        # Test dependencies for module with no imports
        deps = self.package_manager.get_module_dependencies("empty_module")
        self.assertEqual(deps, [])


if __name__ == '__main__':
    unittest.main()