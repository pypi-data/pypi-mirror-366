#!/usr/bin/env python3
"""
Basic test for DataSourceManager functionality.
"""

import json
import csv
import tempfile
import os
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, '.')

from a3.managers.data_source_manager import DataSourceManager

def test_csv_analysis():
    """Test CSV file analysis."""
    print("Testing CSV analysis...")
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'age', 'city'])
        writer.writerow(['John', '25', 'New York'])
        writer.writerow(['Jane', '30', 'Los Angeles'])
        writer.writerow(['Bob', '35', 'Chicago'])
        csv_path = f.name
    
    try:
        manager = DataSourceManager('.')
        metadata = manager.analyze_data_file(csv_path)
        
        print(f"File type: {metadata.file_type}")
        print(f"Schema: {metadata.schema}")
        print(f"Statistics: {metadata.statistics}")
        print("CSV analysis successful!")
        
    finally:
        os.unlink(csv_path)

def test_json_analysis():
    """Test JSON file analysis."""
    print("\nTesting JSON analysis...")
    
    # Create a temporary JSON file
    test_data = {
        "users": [
            {"name": "John", "age": 25, "active": True},
            {"name": "Jane", "age": 30, "active": False}
        ],
        "metadata": {
            "version": "1.0",
            "created": "2024-01-01"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        json_path = f.name
    
    try:
        manager = DataSourceManager('.')
        metadata = manager.analyze_data_file(json_path)
        
        print(f"File type: {metadata.file_type}")
        print(f"Schema: {metadata.schema}")
        print(f"Statistics: {metadata.statistics}")
        print("JSON analysis successful!")
        
    finally:
        os.unlink(json_path)

if __name__ == "__main__":
    test_csv_analysis()
    test_json_analysis()
    print("\nBasic tests completed!")