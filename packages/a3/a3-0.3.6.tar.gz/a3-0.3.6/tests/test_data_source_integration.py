#!/usr/bin/env python3
"""
Test data source integration into code generation.
"""

import tempfile
import os
import csv
import json
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, '.')

from a3.engines.project_analyzer import ProjectAnalyzer

def test_data_source_integration():
    """Test complete data source integration."""
    print("Testing data source integration...")
    
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create some sample data files
        
        # CSV file
        csv_path = project_path / "sales_data.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['product', 'price', 'quantity', 'date'])
            writer.writerow(['Widget A', '10.99', '100', '2024-01-15'])
            writer.writerow(['Widget B', '15.50', '50', '2024-01-16'])
        
        # JSON file
        json_path = project_path / "config.json"
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "mydb"
            },
            "features": ["feature1", "feature2", "feature3"]
        }
        with open(json_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Create a simple Python file
        py_path = project_path / "main.py"
        with open(py_path, 'w') as f:
            f.write('''
def main():
    """Main function."""
    print("Hello, world!")

if __name__ == "__main__":
    main()
''')
        
        # Analyze the project
        analyzer = ProjectAnalyzer()
        analyzer.initialize()
        project_structure = analyzer.scan_project_folder(str(project_path))
        
        # Check that data sources were found
        print(f"Data source analysis found: {project_structure.data_source_analysis is not None}")
        
        if project_structure.data_source_analysis:
            analysis = project_structure.data_source_analysis
            print(f"CSV files found: {len(analysis.csv_files)}")
            print(f"JSON files found: {len(analysis.json_files)}")
            print(f"Total data sources: {len(analysis.unified_metadata)}")
            
            # Test template generation
            templates = analyzer.get_data_handling_templates(project_structure)
            print(f"Generated templates: {list(templates.keys())}")
            
            # Show a sample template
            if templates:
                first_template_name = list(templates.keys())[0]
                first_template = templates[first_template_name]
                print(f"\nSample template ({first_template_name}):")
                print("=" * 50)
                print(first_template[:500] + "..." if len(first_template) > 500 else first_template)
                print("=" * 50)
        
        print("Data source integration test completed!")

def test_data_source_metadata_access():
    """Test accessing data source metadata for code generation."""
    print("\nTesting data source metadata access...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create a CSV with specific structure
        csv_path = project_path / "users.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'name', 'email', 'age', 'active'])
            writer.writerow(['1', 'John Doe', 'john@example.com', '25', 'True'])
            writer.writerow(['2', 'Jane Smith', 'jane@example.com', '30', 'False'])
        
        # Analyze the project
        analyzer = ProjectAnalyzer()
        analyzer.initialize()
        project_structure = analyzer.scan_project_folder(str(project_path))
        
        if project_structure.data_source_analysis:
            # Access specific metadata
            csv_files = project_structure.data_source_analysis.csv_files
            if csv_files:
                csv_meta = csv_files[0]
                print(f"CSV columns: {csv_meta.columns}")
                print(f"CSV data types: {csv_meta.data_types}")
                print(f"CSV row count: {csv_meta.row_count}")
                print(f"Sample data: {csv_meta.sample_data[0] if csv_meta.sample_data else 'None'}")
                
                # Show how this could be used in code generation
                print("\nThis metadata could be used to generate:")
                print("- Database models with correct field types")
                print("- Data validation functions")
                print("- API endpoints with proper schemas")
                print("- Data processing pipelines")
        
        print("Metadata access test completed!")

if __name__ == "__main__":
    test_data_source_integration()
    test_data_source_metadata_access()
    print("\nAll integration tests completed!")