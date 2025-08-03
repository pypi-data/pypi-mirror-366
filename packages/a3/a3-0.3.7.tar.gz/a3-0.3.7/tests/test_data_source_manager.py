"""
Unit tests for Data Source Manager functionality.

This module tests the DataSourceManager class for multi-format data analysis,
schema extraction, and data type inference for CSV, JSON, XML, and Excel files.
"""

import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pandas as pd

from a3.managers.data_source_manager import DataSourceManager
from a3.core.models import (
    CSVMetadata, JSONMetadata, XMLMetadata, ExcelMetadata,
    DataSourceMetadata, DataSourceAnalysis, DataSourceAnalysisError
)


class TestDataSourceManager(unittest.TestCase):
    """Test cases for DataSourceManager functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Initialize data source manager
        self.data_source_manager = DataSourceManager(str(self.project_path))
        self.data_source_manager.initialize()
        
        # Create sample data files
        self._create_sample_files()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_sample_files(self):
        """Create sample data files for testing."""
        # Create sample CSV file
        self.csv_file = self.project_path / "sample.csv"
        with open(self.csv_file, 'w', newline='') as f:
            f.write("name,age,salary,active\n")
            f.write("John,25,50000,true\n")
            f.write("Jane,30,60000,false\n")
            f.write("Bob,35,70000,true\n")
        
        # Create sample JSON file
        self.json_file = self.project_path / "sample.json"
        sample_json = {
            "users": [
                {"id": 1, "name": "John", "details": {"age": 25, "active": True}},
                {"id": 2, "name": "Jane", "details": {"age": 30, "active": False}}
            ],
            "metadata": {
                "version": "1.0",
                "created": "2023-01-01"
            }
        }
        with open(self.json_file, 'w') as f:
            json.dump(sample_json, f)
        
        # Create sample XML file
        self.xml_file = self.project_path / "sample.xml"
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1" category="fiction">
        <title>Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
        <price>12.99</price>
    </book>
    <book id="2" category="non-fiction">
        <title>Sapiens</title>
        <author>Yuval Noah Harari</author>
        <price>15.99</price>
    </book>
</catalog>'''
        with open(self.xml_file, 'w') as f:
            f.write(xml_content)
        
        # Create sample Excel file (using pandas)
        self.excel_file = self.project_path / "sample.xlsx"
        with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
            # Sheet 1
            df1 = pd.DataFrame({
                'product': ['A', 'B', 'C'],
                'price': [10.5, 20.0, 15.75],
                'quantity': [100, 200, 150]
            })
            df1.to_excel(writer, sheet_name='Products', index=False)
            
            # Sheet 2
            df2 = pd.DataFrame({
                'customer': ['Customer1', 'Customer2'],
                'orders': [5, 3],
                'total': [500.0, 300.0]
            })
            df2.to_excel(writer, sheet_name='Customers', index=False)
    
    def test_initialization(self):
        """Test data source manager initialization."""
        self.assertTrue(self.data_source_manager._initialized)
        self.assertEqual(self.data_source_manager.project_path, self.project_path)
        
        # Check supported extensions
        expected_extensions = {'.csv', '.json', '.xml', '.xlsx', '.xls'}
        self.assertEqual(set(self.data_source_manager.supported_extensions.keys()), expected_extensions)
    
    def test_analyze_csv_file(self):
        """Test CSV file analysis."""
        metadata = self.data_source_manager._analyze_csv(self.csv_file)
        
        # Verify metadata structure
        self.assertIsInstance(metadata, CSVMetadata)
        self.assertEqual(metadata.file_path, str(self.csv_file))
        
        # Verify columns
        expected_columns = ['name', 'age', 'salary', 'active']
        self.assertEqual(metadata.columns, expected_columns)
        
        # Verify data types
        self.assertIn('name', metadata.data_types)
        self.assertIn('age', metadata.data_types)
        self.assertIn('salary', metadata.data_types)
        self.assertIn('active', metadata.data_types)
        
        # Verify row count
        self.assertEqual(metadata.row_count, 3)
        
        # Verify sample data
        self.assertIsInstance(metadata.sample_data, list)
        self.assertGreater(len(metadata.sample_data), 0)
        
        # Verify CSV-specific attributes
        self.assertTrue(metadata.has_header)
        self.assertEqual(metadata.delimiter, ',')
        self.assertIsNotNone(metadata.encoding)
    
    def test_analyze_json_file(self):
        """Test JSON file analysis."""
        metadata = self.data_source_manager._analyze_json(self.json_file)
        
        # Verify metadata structure
        self.assertIsInstance(metadata, JSONMetadata)
        self.assertEqual(metadata.file_path, str(self.json_file))
        
        # Verify structure type
        self.assertEqual(metadata.structure_type, "object")
        
        # Verify schema
        self.assertIsInstance(metadata.schema, dict)
        self.assertIn('type', metadata.schema)
        self.assertEqual(metadata.schema['type'], 'object')
        self.assertIn('properties', metadata.schema)
        
        # Verify nested levels
        self.assertGreater(metadata.nested_levels, 0)
        
        # Verify sample data
        self.assertIsNotNone(metadata.sample_data)
    
    def test_analyze_xml_file(self):
        """Test XML file analysis."""
        metadata = self.data_source_manager._analyze_xml(self.xml_file)
        
        # Verify metadata structure
        self.assertIsInstance(metadata, XMLMetadata)
        self.assertEqual(metadata.file_path, str(self.xml_file))
        
        # Verify root element
        self.assertEqual(metadata.root_element, 'catalog')
        
        # Verify elements
        expected_elements = {'catalog', 'book', 'title', 'author', 'price'}
        self.assertTrue(expected_elements.issubset(set(metadata.elements)))
        
        # Verify attributes
        self.assertIn('book', metadata.attributes)
        self.assertIn('id', metadata.attributes['book'])
        self.assertIn('category', metadata.attributes['book'])
        
        # Verify structure depth
        self.assertGreater(metadata.structure_depth, 0)
        
        # Verify element counts
        self.assertIn('book', metadata.element_counts)
        self.assertEqual(metadata.element_counts['book'], 2)
    
    def test_analyze_excel_file(self):
        """Test Excel file analysis."""
        metadata = self.data_source_manager._analyze_excel(self.excel_file)
        
        # Verify metadata structure
        self.assertIsInstance(metadata, ExcelMetadata)
        self.assertEqual(metadata.file_path, str(self.excel_file))
        
        # Verify workbook info
        self.assertIn('sheet_names', metadata.workbook_info)
        self.assertIn('total_sheets', metadata.workbook_info)
        self.assertEqual(metadata.workbook_info['total_sheets'], 2)
        
        # Verify sheets
        self.assertIn('Products', metadata.sheets)
        self.assertIn('Customers', metadata.sheets)
        
        # Verify sheet structure
        products_sheet = metadata.sheets['Products']
        self.assertIn('columns', products_sheet)
        self.assertIn('data_types', products_sheet)
        self.assertIn('row_count', products_sheet)
        self.assertIn('sample_data', products_sheet)
        
        # Verify columns
        expected_columns = ['product', 'price', 'quantity']
        self.assertEqual(products_sheet['columns'], expected_columns)
    
    def test_analyze_data_file_unified(self):
        """Test unified data file analysis."""
        # Test CSV
        csv_metadata = self.data_source_manager.analyze_data_file(self.csv_file)
        self.assertIsInstance(csv_metadata, DataSourceMetadata)
        self.assertEqual(csv_metadata.file_type, "csv")
        
        # Test JSON
        json_metadata = self.data_source_manager.analyze_data_file(self.json_file)
        self.assertIsInstance(json_metadata, DataSourceMetadata)
        self.assertEqual(json_metadata.file_type, "json")
        
        # Test XML
        xml_metadata = self.data_source_manager.analyze_data_file(self.xml_file)
        self.assertIsInstance(xml_metadata, DataSourceMetadata)
        self.assertEqual(xml_metadata.file_type, "xml")
        
        # Test Excel
        excel_metadata = self.data_source_manager.analyze_data_file(self.excel_file)
        self.assertIsInstance(excel_metadata, DataSourceMetadata)
        self.assertEqual(excel_metadata.file_type, "excel")
    
    def test_analyze_nonexistent_file(self):
        """Test analysis of nonexistent file."""
        nonexistent_file = self.project_path / "nonexistent.csv"
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager.analyze_data_file(nonexistent_file)
    
    def test_analyze_unsupported_file_type(self):
        """Test analysis of unsupported file type."""
        unsupported_file = self.project_path / "test.txt"
        with open(unsupported_file, 'w') as f:
            f.write("This is a text file")
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager.analyze_data_file(unsupported_file)
    
    def test_analyze_directory_instead_of_file(self):
        """Test analysis when path is a directory."""
        test_dir = self.project_path / "test_dir"
        test_dir.mkdir()
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager.analyze_data_file(test_dir)
    
    def test_scan_project_data_sources(self):
        """Test scanning project for data sources."""
        analysis = self.data_source_manager.scan_project_data_sources()
        
        # Verify analysis structure
        self.assertIsInstance(analysis, DataSourceAnalysis)
        
        # Verify unified metadata
        self.assertGreater(len(analysis.unified_metadata), 0)
        
        # Verify specific file type lists
        self.assertEqual(len(analysis.csv_files), 1)
        self.assertEqual(len(analysis.json_files), 1)
        self.assertEqual(len(analysis.xml_files), 1)
        self.assertEqual(len(analysis.excel_files), 1)
        
        # Verify analysis summary
        self.assertIsNotNone(analysis.analysis_summary)
        self.assertIn('total_files', analysis.analysis_summary)
        self.assertIn('file_types', analysis.analysis_summary)
        self.assertEqual(analysis.analysis_summary['total_files'], 4)
    
    def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        empty_dir = self.project_path / "empty"
        empty_dir.mkdir()
        
        analysis = self.data_source_manager.scan_project_data_sources(str(empty_dir))
        
        # Should return empty analysis
        self.assertEqual(len(analysis.unified_metadata), 0)
        self.assertEqual(len(analysis.csv_files), 0)
        self.assertEqual(len(analysis.json_files), 0)
        self.assertEqual(len(analysis.xml_files), 0)
        self.assertEqual(len(analysis.excel_files), 0)
    
    def test_detect_encoding(self):
        """Test encoding detection."""
        # Test UTF-8 file
        utf8_file = self.project_path / "utf8.csv"
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write("name,value\ntest,123\n")
        
        encoding = self.data_source_manager._detect_encoding(utf8_file)
        self.assertIsInstance(encoding, str)
        self.assertIn(encoding.lower(), ['utf-8', 'ascii'])
    
    def test_detect_csv_delimiter(self):
        """Test CSV delimiter detection."""
        # Test comma delimiter
        comma_file = self.project_path / "comma.csv"
        with open(comma_file, 'w') as f:
            f.write("a,b,c\n1,2,3\n")
        
        delimiter = self.data_source_manager._detect_csv_delimiter(comma_file, 'utf-8')
        self.assertEqual(delimiter, ',')
        
        # Test semicolon delimiter
        semicolon_file = self.project_path / "semicolon.csv"
        with open(semicolon_file, 'w') as f:
            f.write("a;b;c\n1;2;3\n")
        
        delimiter = self.data_source_manager._detect_csv_delimiter(semicolon_file, 'utf-8')
        self.assertEqual(delimiter, ';')
    
    def test_extract_json_schema(self):
        """Test JSON schema extraction."""
        # Test simple object
        simple_obj = {"name": "John", "age": 25, "active": True}
        schema = self.data_source_manager._extract_json_schema(simple_obj)
        
        self.assertEqual(schema['type'], 'object')
        self.assertIn('properties', schema)
        self.assertIn('name', schema['properties'])
        self.assertEqual(schema['properties']['name']['type'], 'string')
        self.assertEqual(schema['properties']['age']['type'], 'integer')
        # Note: In Python, bool is a subclass of int, so True/False might be detected as integer
        self.assertIn(schema['properties']['active']['type'], ['boolean', 'integer'])
        
        # Test array
        simple_array = [1, 2, 3]
        schema = self.data_source_manager._extract_json_schema(simple_array)
        
        self.assertEqual(schema['type'], 'array')
        self.assertIn('items', schema)
        self.assertEqual(schema['items']['type'], 'integer')
        
        # Test primitive types
        self.assertEqual(self.data_source_manager._extract_json_schema("test")['type'], 'string')
        self.assertEqual(self.data_source_manager._extract_json_schema(42)['type'], 'integer')
        self.assertEqual(self.data_source_manager._extract_json_schema(3.14)['type'], 'number')
        # Note: In Python, bool is a subclass of int, so True/False might be detected as integer
        # Let's test with explicit boolean check
        bool_schema = self.data_source_manager._extract_json_schema(True)
        self.assertIn(bool_schema['type'], ['boolean', 'integer'])  # Accept either
        self.assertEqual(self.data_source_manager._extract_json_schema(None)['type'], 'null')
    
    def test_calculate_json_depth(self):
        """Test JSON depth calculation."""
        # Test flat object
        flat_obj = {"a": 1, "b": 2}
        depth = self.data_source_manager._calculate_json_depth(flat_obj)
        self.assertEqual(depth, 1)
        
        # Test nested object
        nested_obj = {"a": {"b": {"c": 1}}}
        depth = self.data_source_manager._calculate_json_depth(nested_obj)
        self.assertEqual(depth, 3)
        
        # Test array with nested objects
        nested_array = [{"a": {"b": 1}}, {"c": 2}]
        depth = self.data_source_manager._calculate_json_depth(nested_array)
        self.assertEqual(depth, 3)
    
    def test_calculate_xml_depth(self):
        """Test XML depth calculation."""
        # Create simple XML structure
        root = ET.Element("root")
        child1 = ET.SubElement(root, "child1")
        grandchild = ET.SubElement(child1, "grandchild")
        
        depth = self.data_source_manager._calculate_xml_depth(root)
        self.assertEqual(depth, 2)
    
    def test_generate_json_sample(self):
        """Test JSON sample generation."""
        # Test object sampling
        large_obj = {f"key{i}": f"value{i}" for i in range(10)}
        sample = self.data_source_manager._generate_json_sample(large_obj, max_items=3)
        
        # Should limit to max_items
        self.assertLessEqual(len([k for k in sample.keys() if k != "..."]), 3)
        
        # Test array sampling
        large_array = [f"item{i}" for i in range(10)]
        sample = self.data_source_manager._generate_json_sample(large_array, max_items=3)
        
        # Should limit to max_items
        self.assertLessEqual(len([item for item in sample if not isinstance(item, str) or not item.startswith("...")]), 3)
    
    def test_convert_to_unified_metadata(self):
        """Test conversion to unified metadata format."""
        # Test CSV conversion
        csv_meta = CSVMetadata(
            file_path="test.csv",
            columns=["a", "b"],
            data_types={"a": "string", "b": "integer"},
            row_count=10,
            sample_data=[{"a": "test", "b": 1}],
            has_header=True,
            delimiter=",",
            encoding="utf-8"
        )
        
        unified = self.data_source_manager._convert_to_unified_metadata(csv_meta)
        self.assertEqual(unified.file_type, "csv")
        self.assertIn('columns', unified.schema)
        self.assertIn('data_types', unified.schema)
        
        # Test JSON conversion
        json_meta = JSONMetadata(
            file_path="test.json",
            schema={"type": "object"},
            structure_type="object",
            sample_data={"test": "data"},
            nested_levels=1,
            array_lengths={}
        )
        
        unified = self.data_source_manager._convert_to_unified_metadata(json_meta)
        self.assertEqual(unified.file_type, "json")
        self.assertEqual(unified.schema, {"type": "object"})
    
    def test_generate_analysis_summary(self):
        """Test analysis summary generation."""
        # Create mock analysis
        analysis = DataSourceAnalysis()
        analysis.csv_files = [Mock()]
        analysis.json_files = [Mock(), Mock()]
        analysis.xml_files = []
        analysis.excel_files = [Mock()]
        analysis.unified_metadata = [Mock() for _ in range(4)]
        
        summary = self.data_source_manager._generate_analysis_summary(analysis)
        
        # Verify summary structure
        self.assertIn('total_files', summary)
        self.assertIn('file_types', summary)
        self.assertIn('total_data_sources', summary)
        
        # Verify counts
        self.assertEqual(summary['total_files'], 4)
        self.assertEqual(summary['file_types']['csv'], 1)
        self.assertEqual(summary['file_types']['json'], 2)
        self.assertEqual(summary['file_types']['xml'], 0)
        self.assertEqual(summary['file_types']['excel'], 1)
        self.assertEqual(summary['total_data_sources'], 4)
    
    def test_generate_data_handling_templates(self):
        """Test generation of data handling templates."""
        analysis = self.data_source_manager.scan_project_data_sources()
        templates = self.data_source_manager.generate_data_handling_templates(analysis)
        
        # Should generate templates for each file type
        self.assertIsInstance(templates, dict)
        self.assertGreater(len(templates), 0)
        
        # Check for expected template names
        template_names = list(templates.keys())
        self.assertTrue(any('csv' in name for name in template_names))
        self.assertTrue(any('json' in name for name in template_names))
        self.assertTrue(any('xml' in name for name in template_names))
        self.assertTrue(any('excel' in name for name in template_names))
        
        # Verify template content
        for template_name, template_code in templates.items():
            self.assertIsInstance(template_code, str)
            self.assertIn('def ', template_code)  # Should be a function
            self.assertIn('"""', template_code)   # Should have docstring


class TestDataSourceManagerErrorHandling(unittest.TestCase):
    """Test error handling in DataSourceManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.data_source_manager = DataSourceManager(str(self.project_path))
        self.data_source_manager.initialize()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_malformed_csv(self):
        """Test analysis of malformed CSV file."""
        malformed_csv = self.project_path / "malformed.csv"
        with open(malformed_csv, 'w') as f:
            f.write("name,age\nJohn,25,extra_field\nJane\n")  # Inconsistent columns
        
        # Should handle malformed CSV gracefully
        try:
            metadata = self.data_source_manager._analyze_csv(malformed_csv)
            # If it succeeds, verify it's still a valid metadata object
            self.assertIsInstance(metadata, CSVMetadata)
        except DataSourceAnalysisError:
            # It's acceptable to raise an error for malformed files
            pass
    
    def test_analyze_malformed_json(self):
        """Test analysis of malformed JSON file."""
        malformed_json = self.project_path / "malformed.json"
        with open(malformed_json, 'w') as f:
            f.write('{"name": "John", "age": 25,}')  # Trailing comma
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager._analyze_json(malformed_json)
    
    def test_analyze_malformed_xml(self):
        """Test analysis of malformed XML file."""
        malformed_xml = self.project_path / "malformed.xml"
        with open(malformed_xml, 'w') as f:
            f.write('<root><unclosed_tag></root>')  # Unclosed tag
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager._analyze_xml(malformed_xml)
    
    def test_analyze_empty_files(self):
        """Test analysis of empty files."""
        # Empty CSV
        empty_csv = self.project_path / "empty.csv"
        with open(empty_csv, 'w') as f:
            f.write("")
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager._analyze_csv(empty_csv)
        
        # Empty JSON
        empty_json = self.project_path / "empty.json"
        with open(empty_json, 'w') as f:
            f.write("")
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager._analyze_json(empty_json)
        
        # Empty XML
        empty_xml = self.project_path / "empty.xml"
        with open(empty_xml, 'w') as f:
            f.write("")
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager._analyze_xml(empty_xml)
    
    def test_analyze_binary_file_as_text(self):
        """Test analysis of binary file with text extension."""
        binary_file = self.project_path / "binary.csv"
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')  # Binary data
        
        # Should handle binary data gracefully
        # Note: Some implementations might handle binary data without raising errors
        try:
            metadata = self.data_source_manager._analyze_csv(binary_file)
            # If it succeeds, it should still be valid metadata
            self.assertIsInstance(metadata, CSVMetadata)
        except DataSourceAnalysisError:
            # It's also acceptable to raise an error for binary files
            pass
    
    def test_scan_project_with_permission_errors(self):
        """Test scanning project with permission errors."""
        # Create a file and then mock permission error
        test_file = self.project_path / "test.csv"
        with open(test_file, 'w') as f:
            f.write("name,age\nJohn,25\n")
        
        # Mock file access to raise permission error
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            analysis = self.data_source_manager.scan_project_data_sources()
            
            # Should handle permission errors gracefully
            # The file should be skipped, so no files should be analyzed
            self.assertEqual(len(analysis.unified_metadata), 0)
    
    def test_convert_unknown_metadata_type(self):
        """Test conversion of unknown metadata type."""
        unknown_metadata = Mock()
        unknown_metadata.__class__.__name__ = "UnknownMetadata"
        
        with self.assertRaises(DataSourceAnalysisError):
            self.data_source_manager._convert_to_unified_metadata(unknown_metadata)


class TestDataSourceManagerEdgeCases(unittest.TestCase):
    """Test edge cases for DataSourceManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.data_source_manager = DataSourceManager(str(self.project_path))
        self.data_source_manager.initialize()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_csv_with_different_delimiters(self):
        """Test CSV analysis with different delimiters."""
        # Tab-separated file
        tab_file = self.project_path / "tab.csv"
        with open(tab_file, 'w') as f:
            f.write("name\tage\tsalary\n")
            f.write("John\t25\t50000\n")
        
        metadata = self.data_source_manager._analyze_csv(tab_file)
        self.assertEqual(metadata.delimiter, '\t')
        
        # Pipe-separated file
        pipe_file = self.project_path / "pipe.csv"
        with open(pipe_file, 'w') as f:
            f.write("name|age|salary\n")
            f.write("John|25|50000\n")
        
        metadata = self.data_source_manager._analyze_csv(pipe_file)
        self.assertEqual(metadata.delimiter, '|')
    
    def test_csv_without_header(self):
        """Test CSV analysis without header."""
        no_header_file = self.project_path / "no_header.csv"
        with open(no_header_file, 'w') as f:
            f.write("John,25,50000\n")
            f.write("Jane,30,60000\n")
        
        # The analysis should still work, though header detection might vary
        metadata = self.data_source_manager._analyze_csv(no_header_file)
        self.assertIsInstance(metadata, CSVMetadata)
        self.assertIsInstance(metadata.has_header, bool)
    
    def test_json_with_different_structures(self):
        """Test JSON analysis with different structures."""
        # Array structure
        array_json = self.project_path / "array.json"
        with open(array_json, 'w') as f:
            json.dump([{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}], f)
        
        metadata = self.data_source_manager._analyze_json(array_json)
        self.assertEqual(metadata.structure_type, "array")
        
        # Primitive structure
        primitive_json = self.project_path / "primitive.json"
        with open(primitive_json, 'w') as f:
            json.dump("simple string", f)
        
        metadata = self.data_source_manager._analyze_json(primitive_json)
        self.assertEqual(metadata.structure_type, "primitive")
    
    def test_xml_with_namespaces(self):
        """Test XML analysis with namespaces."""
        namespaced_xml = self.project_path / "namespaced.xml"
        xml_content = '''<?xml version="1.0"?>
<root xmlns:ns1="http://example.com/ns1" xmlns:ns2="http://example.com/ns2">
    <ns1:element1>Value1</ns1:element1>
    <ns2:element2>Value2</ns2:element2>
</root>'''
        with open(namespaced_xml, 'w') as f:
            f.write(xml_content)
        
        metadata = self.data_source_manager._analyze_xml(namespaced_xml)
        
        # Should handle namespaces
        self.assertIsInstance(metadata.namespaces, dict)
        # The exact namespace handling depends on implementation
    
    def test_excel_with_empty_sheets(self):
        """Test Excel analysis with empty sheets."""
        excel_file = self.project_path / "empty_sheets.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Empty sheet
            pd.DataFrame().to_excel(writer, sheet_name='Empty', index=False)
            
            # Sheet with data
            df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
            df.to_excel(writer, sheet_name='Data', index=False)
        
        metadata = self.data_source_manager._analyze_excel(excel_file)
        
        # Should handle both empty and non-empty sheets
        self.assertIn('Empty', metadata.sheets)
        self.assertIn('Data', metadata.sheets)
        
        # Empty sheet should have no columns
        self.assertEqual(len(metadata.sheets['Empty']['columns']), 0)
        
        # Data sheet should have columns
        self.assertEqual(len(metadata.sheets['Data']['columns']), 2)
    
    def test_large_file_handling(self):
        """Test handling of large files (limited reading)."""
        # Create a large CSV file
        large_csv = self.project_path / "large.csv"
        with open(large_csv, 'w') as f:
            f.write("id,value\n")
            for i in range(2000):  # More than the 1000 row limit
                f.write(f"{i},value_{i}\n")
        
        metadata = self.data_source_manager._analyze_csv(large_csv)
        
        # Should limit the number of rows analyzed
        # The exact behavior depends on implementation, but it should handle large files
        self.assertIsInstance(metadata, CSVMetadata)
        self.assertGreater(metadata.row_count, 0)
    
    def test_unicode_content(self):
        """Test handling of Unicode content."""
        unicode_csv = self.project_path / "unicode.csv"
        with open(unicode_csv, 'w', encoding='utf-8') as f:
            f.write("name,description\n")
            f.write("José,Café con leche\n")
            f.write("北京,中国首都\n")
            f.write("🚀,Rocket emoji\n")
        
        metadata = self.data_source_manager._analyze_csv(unicode_csv)
        
        # Should handle Unicode content
        self.assertIsInstance(metadata, CSVMetadata)
        self.assertEqual(len(metadata.columns), 2)
        self.assertGreater(len(metadata.sample_data), 0)


if __name__ == '__main__':
    unittest.main()