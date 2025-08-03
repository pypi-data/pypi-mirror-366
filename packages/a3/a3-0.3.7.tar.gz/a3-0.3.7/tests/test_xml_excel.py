#!/usr/bin/env python3
"""
Test XML and Excel analysis capabilities.
"""

import tempfile
import os
from pathlib import Path
import pandas as pd

# Add the project root to Python path
import sys
sys.path.insert(0, '.')

from a3.managers.data_source_manager import DataSourceManager

def test_xml_analysis():
    """Test XML file analysis."""
    print("Testing XML analysis...")
    
    # Create a temporary XML file
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns:book="http://example.com/book">
    <book:item id="1" category="fiction">
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
        <price currency="USD">12.99</price>
        <availability>in-stock</availability>
    </book:item>
    <book:item id="2" category="non-fiction">
        <title>Sapiens</title>
        <author>Yuval Noah Harari</author>
        <price currency="USD">15.99</price>
        <availability>out-of-stock</availability>
    </book:item>
</catalog>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
        f.write(xml_content)
        xml_path = f.name
    
    try:
        manager = DataSourceManager('.')
        metadata = manager.analyze_data_file(xml_path)
        
        print(f"File type: {metadata.file_type}")
        print(f"Schema: {metadata.schema}")
        print(f"Statistics: {metadata.statistics}")
        print("XML analysis successful!")
        
    except Exception as e:
        print(f"XML analysis failed: {e}")
    finally:
        os.unlink(xml_path)

def test_excel_analysis():
    """Test Excel file analysis."""
    print("\nTesting Excel analysis...")
    
    # Create a temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        excel_path = f.name
    
    try:
        # Create sample data
        data1 = {
            'Product': ['Widget A', 'Widget B', 'Widget C'],
            'Price': [10.99, 15.50, 8.25],
            'Quantity': [100, 50, 200],
            'Available': [True, False, True]
        }
        
        data2 = {
            'Customer': ['John Doe', 'Jane Smith'],
            'Order_Date': ['2024-01-15', '2024-01-16'],
            'Total': [25.99, 45.75]
        }
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            pd.DataFrame(data1).to_excel(writer, sheet_name='Products', index=False)
            pd.DataFrame(data2).to_excel(writer, sheet_name='Orders', index=False)
        
        manager = DataSourceManager('.')
        metadata = manager.analyze_data_file(excel_path)
        
        print(f"File type: {metadata.file_type}")
        print(f"Schema: {metadata.schema}")
        print(f"Statistics: {metadata.statistics}")
        print("Excel analysis successful!")
        
    except Exception as e:
        print(f"Excel analysis failed: {e}")
    finally:
        if os.path.exists(excel_path):
            os.unlink(excel_path)

def test_data_sampling_and_statistics():
    """Test data sampling and statistics generation."""
    print("\nTesting data sampling and statistics...")
    
    # Create a larger CSV for statistics testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('name,age,salary,department\n')
        for i in range(100):
            f.write(f'Employee{i},{20+i%40},{30000+i*500},Dept{i%5}\n')
        csv_path = f.name
    
    try:
        manager = DataSourceManager('.')
        metadata = manager.analyze_data_file(csv_path)
        
        print(f"File type: {metadata.file_type}")
        print(f"Row count: {metadata.statistics['row_count']}")
        print(f"Column count: {metadata.statistics['column_count']}")
        print(f"Sample data rows: {len(metadata.sample_data['rows'])}")
        print("Data sampling and statistics successful!")
        
    except Exception as e:
        print(f"Data sampling test failed: {e}")
    finally:
        os.unlink(csv_path)

if __name__ == "__main__":
    test_xml_analysis()
    test_excel_analysis()
    test_data_sampling_and_statistics()
    print("\nXML and Excel tests completed!")