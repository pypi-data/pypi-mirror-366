#!/usr/bin/env python3
"""
Basic test for DatabaseAnalyzer implementation.

This test verifies that the DatabaseAnalyzer can be imported and instantiated
without errors, and that the basic structure is correct.
"""

import sys
import os

# Add the a3 package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_database_analyzer_import():
    """Test that DatabaseAnalyzer can be imported successfully."""
    try:
        from a3.engines.database_analyzer import DatabaseAnalyzer
        print("✓ DatabaseAnalyzer imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import DatabaseAnalyzer: {e}")
        return False

def test_database_analyzer_instantiation():
    """Test that DatabaseAnalyzer can be instantiated."""
    try:
        from a3.engines.database_analyzer import DatabaseAnalyzer
        analyzer = DatabaseAnalyzer()
        print("✓ DatabaseAnalyzer instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to instantiate DatabaseAnalyzer: {e}")
        return False

def test_database_models_import():
    """Test that database models can be imported."""
    try:
        from a3.core.models import (
            DatabaseConnection, DatabaseSchema, TableMetadata, 
            ColumnMetadata, DatabaseAnalysisResult
        )
        print("✓ Database models imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import database models: {e}")
        return False

def test_model_validation():
    """Test basic model validation."""
    try:
        from a3.core.models import ColumnMetadata
        
        # Test valid column
        column = ColumnMetadata(
            name="test_column",
            data_type="varchar",
            is_nullable=True
        )
        column.validate()
        print("✓ Column model validation works")
        
        # Test invalid column (should raise ValidationError)
        try:
            invalid_column = ColumnMetadata(
                name="",  # Empty name should be invalid
                data_type="varchar"
            )
            invalid_column.validate()
            print("✗ Column validation should have failed for empty name")
            return False
        except Exception:
            print("✓ Column validation correctly rejects invalid data")
        
        return True
    except Exception as e:
        print(f"✗ Model validation test failed: {e}")
        return False

def test_connection_string_parsing():
    """Test connection string parsing logic."""
    try:
        from a3.engines.database_analyzer import DatabaseAnalyzer
        from a3.core.models import DatabaseConnectionError
        
        analyzer = DatabaseAnalyzer()
        analyzer.initialize()  # Initialize the analyzer
        
        # Test invalid connection string (should raise error)
        try:
            analyzer.connect_to_database("invalid://connection/string")
            print("✗ Should have failed for invalid connection string")
            return False
        except DatabaseConnectionError as e:
            print("✓ Connection string validation works")
            return True
        except Exception as e:
            print(f"✗ Unexpected error in connection string test: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Connection string parsing test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("Running basic DatabaseAnalyzer tests...\n")
    
    tests = [
        test_database_analyzer_import,
        test_database_analyzer_instantiation,
        test_database_models_import,
        test_model_validation,
        test_connection_string_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())