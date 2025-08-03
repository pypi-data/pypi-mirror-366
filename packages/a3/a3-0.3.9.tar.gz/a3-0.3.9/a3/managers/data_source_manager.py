"""
Data Source Manager for AI Project Builder.

This module provides functionality to analyze various data file formats
including CSV, JSON, XML, and Excel files to extract metadata and schema
information for use in code generation.
"""

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import logging

from .base import BaseDataSourceManager
from ..core.models import (
    CSVMetadata, JSONMetadata, XMLMetadata, ExcelMetadata,
    DataSourceMetadata, DataSourceAnalysis, DataSourceAnalysisError
)

logger = logging.getLogger(__name__)


class DataSourceManager(BaseDataSourceManager):
    """
    Manager for analyzing various data file formats.
    
    Supports CSV, JSON, XML, and Excel files with comprehensive
    metadata extraction and schema analysis.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the data source manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        self.supported_extensions = {
            '.csv': self._analyze_csv,
            '.json': self._analyze_json,
            '.xml': self._analyze_xml,
            '.xlsx': self._analyze_excel,
            '.xls': self._analyze_excel
        }
    
    def analyze_data_file(self, file_path: Union[str, Path]) -> DataSourceMetadata:
        """
        Analyze a single data file and extract metadata.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            DataSourceMetadata: Unified metadata for the file
            
        Raises:
            DataSourceAnalysisError: If analysis fails
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise DataSourceAnalysisError(f"File does not exist: {file_path}")
            
            if not file_path.is_file():
                raise DataSourceAnalysisError(f"Path is not a file: {file_path}")
            
            extension = file_path.suffix.lower()
            
            if extension not in self.supported_extensions:
                raise DataSourceAnalysisError(f"Unsupported file type: {extension}")
            
            # Analyze using appropriate method
            analyzer = self.supported_extensions[extension]
            specific_metadata = analyzer(file_path)
            
            # Convert to unified metadata
            return self._convert_to_unified_metadata(specific_metadata)
            
        except Exception as e:
            logger.error(f"Failed to analyze data file {file_path}: {str(e)}")
            raise DataSourceAnalysisError(f"Analysis failed for {file_path}: {str(e)}")
    
    def scan_project_data_sources(self, project_path: Optional[str] = None) -> DataSourceAnalysis:
        """
        Scan project directory for data source files and analyze them.
        
        Args:
            project_path: Path to scan (defaults to manager's project path)
            
        Returns:
            DataSourceAnalysis: Complete analysis of all found data sources
        """
        if project_path is None:
            project_path = self.project_path
        else:
            project_path = Path(project_path)
        
        analysis = DataSourceAnalysis()
        
        try:
            # Find all supported data files
            data_files = []
            for extension in self.supported_extensions.keys():
                data_files.extend(project_path.rglob(f"*{extension}"))
            
            logger.info(f"Found {len(data_files)} data files in {project_path}")
            
            # Analyze each file
            for file_path in data_files:
                try:
                    metadata = self.analyze_data_file(file_path)
                    analysis.unified_metadata.append(metadata)
                    
                    # Also add to specific type lists
                    if metadata.file_type == "csv":
                        csv_meta = self._analyze_csv(file_path)
                        analysis.csv_files.append(csv_meta)
                    elif metadata.file_type == "json":
                        json_meta = self._analyze_json(file_path)
                        analysis.json_files.append(json_meta)
                    elif metadata.file_type == "xml":
                        xml_meta = self._analyze_xml(file_path)
                        analysis.xml_files.append(xml_meta)
                    elif metadata.file_type == "excel":
                        excel_meta = self._analyze_excel(file_path)
                        analysis.excel_files.append(excel_meta)
                        
                except DataSourceAnalysisError as e:
                    logger.warning(f"Skipping file due to analysis error: {e}")
                    continue
            
            # Generate analysis summary
            analysis.analysis_summary = self._generate_analysis_summary(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to scan project data sources: {str(e)}")
            raise DataSourceAnalysisError(f"Project scan failed: {str(e)}")

    def _analyze_csv(self, file_path: Path) -> CSVMetadata:
        """
        Analyze a CSV file and extract metadata.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            CSVMetadata: Detailed CSV metadata
        """
        try:
            # Try to detect encoding
            encoding = self._detect_encoding(file_path)
            
            # Try to detect delimiter
            delimiter = self._detect_csv_delimiter(file_path, encoding)
            
            # Read CSV with pandas for comprehensive analysis
            df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, nrows=1000)
            
            # Extract basic information
            columns = df.columns.tolist()
            row_count = len(df)
            
            # Infer data types
            data_types = {}
            for col in columns:
                dtype = str(df[col].dtype)
                if dtype.startswith('int'):
                    data_types[col] = 'integer'
                elif dtype.startswith('float'):
                    data_types[col] = 'float'
                elif dtype == 'bool':
                    data_types[col] = 'boolean'
                elif dtype == 'datetime64[ns]':
                    data_types[col] = 'datetime'
                else:
                    data_types[col] = 'string'
            
            # Generate sample data (first 5 rows)
            sample_data = []
            for _, row in df.head(5).iterrows():
                sample_data.append(row.to_dict())
            
            # Check if file has header by comparing first row with column names
            has_header = True
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    first_line = f.readline().strip().split(delimiter)
                    # If first line matches column names, it's likely a header
                    has_header = first_line == columns
            except:
                has_header = True  # Default assumption
            
            return CSVMetadata(
                file_path=str(file_path),
                columns=columns,
                data_types=data_types,
                row_count=row_count,
                sample_data=sample_data,
                has_header=has_header,
                delimiter=delimiter,
                encoding=encoding
            )
            
        except Exception as e:
            raise DataSourceAnalysisError(f"CSV analysis failed for {file_path}: {str(e)}")

    def _analyze_json(self, file_path: Path) -> JSONMetadata:
        """
        Analyze a JSON file and extract metadata.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            JSONMetadata: Detailed JSON metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine structure type
            if isinstance(data, dict):
                structure_type = "object"
            elif isinstance(data, list):
                structure_type = "array"
            else:
                structure_type = "primitive"
            
            # Extract schema
            schema = self._extract_json_schema(data)
            
            # Calculate nested levels
            nested_levels = self._calculate_json_depth(data)
            
            # Calculate array lengths if applicable
            array_lengths = {}
            if structure_type == "array":
                array_lengths["root"] = len(data)
                # Find nested arrays
                self._find_array_lengths(data, array_lengths, "root")
            
            # Generate sample data (limited for large structures)
            sample_data = self._generate_json_sample(data)
            
            return JSONMetadata(
                file_path=str(file_path),
                schema=schema,
                structure_type=structure_type,
                sample_data=sample_data,
                nested_levels=nested_levels,
                array_lengths=array_lengths
            )
            
        except Exception as e:
            raise DataSourceAnalysisError(f"JSON analysis failed for {file_path}: {str(e)}")

    def _analyze_xml(self, file_path: Path) -> XMLMetadata:
        """
        Analyze an XML file and extract metadata.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            XMLMetadata: Detailed XML metadata
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract root element
            root_element = root.tag
            
            # Find all unique elements
            elements = set()
            attributes = {}
            element_counts = {}
            namespaces = {}
            
            # Traverse the tree
            for elem in root.iter():
                # Handle namespaces
                if '}' in elem.tag:
                    namespace, tag = elem.tag.split('}', 1)
                    namespace = namespace[1:]  # Remove leading '{'
                    namespaces[tag] = namespace
                    elements.add(tag)
                else:
                    elements.add(elem.tag)
                
                # Count elements
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                element_counts[tag_name] = element_counts.get(tag_name, 0) + 1
                
                # Extract attributes
                if elem.attrib:
                    if tag_name not in attributes:
                        attributes[tag_name] = []
                    for attr in elem.attrib.keys():
                        if attr not in attributes[tag_name]:
                            attributes[tag_name].append(attr)
            
            # Calculate structure depth
            structure_depth = self._calculate_xml_depth(root)
            
            return XMLMetadata(
                file_path=str(file_path),
                root_element=root_element,
                elements=list(elements),
                attributes=attributes,
                namespaces=namespaces,
                structure_depth=structure_depth,
                element_counts=element_counts
            )
            
        except Exception as e:
            raise DataSourceAnalysisError(f"XML analysis failed for {file_path}: {str(e)}")

    def _analyze_excel(self, file_path: Path) -> ExcelMetadata:
        """
        Analyze an Excel file and extract metadata.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            ExcelMetadata: Detailed Excel metadata
        """
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            
            sheets = {}
            workbook_info = {
                'sheet_names': excel_file.sheet_names,
                'total_sheets': len(excel_file.sheet_names)
            }
            
            # Analyze each sheet
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1000)
                    
                    # Extract sheet metadata
                    columns = df.columns.tolist()
                    row_count = len(df)
                    
                    # Infer data types
                    data_types = {}
                    for col in columns:
                        dtype = str(df[col].dtype)
                        if dtype.startswith('int'):
                            data_types[col] = 'integer'
                        elif dtype.startswith('float'):
                            data_types[col] = 'float'
                        elif dtype == 'bool':
                            data_types[col] = 'boolean'
                        elif dtype == 'datetime64[ns]':
                            data_types[col] = 'datetime'
                        else:
                            data_types[col] = 'string'
                    
                    # Generate sample data
                    sample_data = []
                    for _, row in df.head(3).iterrows():
                        sample_data.append(row.to_dict())
                    
                    sheets[sheet_name] = {
                        'columns': columns,
                        'data_types': data_types,
                        'row_count': row_count,
                        'sample_data': sample_data
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze sheet {sheet_name}: {str(e)}")
                    sheets[sheet_name] = {
                        'columns': [],
                        'data_types': {},
                        'row_count': 0,
                        'error': str(e)
                    }
            
            return ExcelMetadata(
                file_path=str(file_path),
                sheets=sheets,
                workbook_info=workbook_info
            )
            
        except Exception as e:
            raise DataSourceAnalysisError(f"Excel analysis failed for {file_path}: {str(e)}")

    def _convert_to_unified_metadata(self, specific_metadata) -> DataSourceMetadata:
        """
        Convert specific metadata to unified format.
        
        Args:
            specific_metadata: CSVMetadata, JSONMetadata, XMLMetadata, or ExcelMetadata
            
        Returns:
            DataSourceMetadata: Unified metadata
        """
        if isinstance(specific_metadata, CSVMetadata):
            return DataSourceMetadata(
                file_path=specific_metadata.file_path,
                file_type="csv",
                schema={
                    'columns': specific_metadata.columns,
                    'data_types': specific_metadata.data_types,
                    'has_header': specific_metadata.has_header,
                    'delimiter': specific_metadata.delimiter
                },
                sample_data={'rows': specific_metadata.sample_data[:3]},
                statistics={
                    'row_count': specific_metadata.row_count,
                    'column_count': len(specific_metadata.columns),
                    'encoding': specific_metadata.encoding
                }
            )
        
        elif isinstance(specific_metadata, JSONMetadata):
            return DataSourceMetadata(
                file_path=specific_metadata.file_path,
                file_type="json",
                schema=specific_metadata.schema,
                sample_data=specific_metadata.sample_data,
                statistics={
                    'structure_type': specific_metadata.structure_type,
                    'nested_levels': specific_metadata.nested_levels,
                    'array_lengths': specific_metadata.array_lengths
                }
            )
        
        elif isinstance(specific_metadata, XMLMetadata):
            return DataSourceMetadata(
                file_path=specific_metadata.file_path,
                file_type="xml",
                schema={
                    'root_element': specific_metadata.root_element,
                    'elements': specific_metadata.elements,
                    'attributes': specific_metadata.attributes,
                    'namespaces': specific_metadata.namespaces
                },
                statistics={
                    'structure_depth': specific_metadata.structure_depth,
                    'element_counts': specific_metadata.element_counts,
                    'total_elements': len(specific_metadata.elements)
                }
            )
        
        elif isinstance(specific_metadata, ExcelMetadata):
            return DataSourceMetadata(
                file_path=specific_metadata.file_path,
                file_type="excel",
                schema={
                    'sheets': {name: {
                        'columns': sheet_data.get('columns', []),
                        'data_types': sheet_data.get('data_types', {})
                    } for name, sheet_data in specific_metadata.sheets.items()},
                    'workbook_info': specific_metadata.workbook_info
                },
                sample_data={
                    'sheets': {name: sheet_data.get('sample_data', [])[:2] 
                              for name, sheet_data in specific_metadata.sheets.items()}
                },
                statistics={
                    'total_sheets': len(specific_metadata.sheets),
                    'sheet_names': list(specific_metadata.sheets.keys())
                }
            )
        
        else:
            raise DataSourceAnalysisError(f"Unknown metadata type: {type(specific_metadata)}")

    def _generate_analysis_summary(self, analysis: DataSourceAnalysis) -> Dict[str, Any]:
        """
        Generate a summary of the data source analysis.
        
        Args:
            analysis: Complete data source analysis
            
        Returns:
            Dict containing analysis summary
        """
        return {
            'total_files': len(analysis.unified_metadata),
            'file_types': {
                'csv': len(analysis.csv_files),
                'json': len(analysis.json_files),
                'xml': len(analysis.xml_files),
                'excel': len(analysis.excel_files)
            },
            'total_data_sources': sum([
                len(analysis.csv_files),
                len(analysis.json_files),
                len(analysis.xml_files),
                len(analysis.excel_files)
            ]),
            'analysis_timestamp': analysis.unified_metadata[0].analysis_timestamp if analysis.unified_metadata else None
        }

    # Helper methods
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Detected encoding
        """
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8') or 'utf-8'
        except ImportError:
            # Fallback if chardet is not available
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1000)
                    return encoding
                except UnicodeDecodeError:
                    continue
            return 'utf-8'  # Final fallback

    def _detect_csv_delimiter(self, file_path: Path, encoding: str) -> str:
        """
        Detect CSV delimiter.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            
        Returns:
            str: Detected delimiter
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(1024)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                return delimiter
        except:
            return ','  # Default fallback

    def _extract_json_schema(self, data: Any, max_depth: int = 3) -> Dict[str, Any]:
        """
        Extract schema from JSON data.
        
        Args:
            data: JSON data
            max_depth: Maximum depth to analyze
            
        Returns:
            Dict representing the schema
        """
        if max_depth <= 0:
            return {"type": "truncated"}
        
        if isinstance(data, dict):
            schema = {"type": "object", "properties": {}}
            for key, value in data.items():
                schema["properties"][key] = self._extract_json_schema(value, max_depth - 1)
            return schema
        
        elif isinstance(data, list):
            schema = {"type": "array"}
            if data:
                # Analyze first few items to determine array item schema
                item_schemas = []
                for item in data[:5]:  # Analyze first 5 items
                    item_schemas.append(self._extract_json_schema(item, max_depth - 1))
                
                # Try to find common schema
                if item_schemas:
                    schema["items"] = item_schemas[0]  # Use first item's schema
            return schema
        
        elif isinstance(data, str):
            return {"type": "string"}
        elif isinstance(data, int):
            return {"type": "integer"}
        elif isinstance(data, float):
            return {"type": "number"}
        elif isinstance(data, bool):
            return {"type": "boolean"}
        elif data is None:
            return {"type": "null"}
        else:
            return {"type": "unknown"}

    def _calculate_json_depth(self, data: Any, current_depth: int = 0) -> int:
        """
        Calculate the maximum depth of JSON structure.
        
        Args:
            data: JSON data
            current_depth: Current depth level
            
        Returns:
            int: Maximum depth
        """
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._calculate_json_depth(value, current_depth + 1) 
                      for value in data.values())
        
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._calculate_json_depth(item, current_depth + 1) 
                      for item in data)
        
        else:
            return current_depth

    def _find_array_lengths(self, data: Any, array_lengths: Dict[str, int], path: str):
        """
        Find lengths of all arrays in JSON structure.
        
        Args:
            data: JSON data
            array_lengths: Dictionary to store array lengths
            path: Current path in the structure
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}"
                if isinstance(value, list):
                    array_lengths[new_path] = len(value)
                self._find_array_lengths(value, array_lengths, new_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data[:3]):  # Analyze first 3 items
                new_path = f"{path}[{i}]"
                self._find_array_lengths(item, array_lengths, new_path)

    def _generate_json_sample(self, data: Any, max_items: int = 3) -> Dict[str, Any]:
        """
        Generate a sample of JSON data for preview.
        
        Args:
            data: JSON data
            max_items: Maximum items to include in sample
            
        Returns:
            Dict containing sample data
        """
        if isinstance(data, dict):
            sample = {}
            for i, (key, value) in enumerate(data.items()):
                if i >= max_items:
                    sample["..."] = f"and {len(data) - max_items} more items"
                    break
                sample[key] = self._generate_json_sample(value, max_items)
            return sample
        
        elif isinstance(data, list):
            sample = []
            for i, item in enumerate(data):
                if i >= max_items:
                    sample.append(f"... and {len(data) - max_items} more items")
                    break
                sample.append(self._generate_json_sample(item, max_items))
            return sample
        
        else:
            return data

    def _calculate_xml_depth(self, element, current_depth: int = 0) -> int:
        """
        Calculate the maximum depth of XML structure.
        
        Args:
            element: XML element
            current_depth: Current depth level
            
        Returns:
            int: Maximum depth
        """
        if len(element) == 0:
            return current_depth
        
        return max(self._calculate_xml_depth(child, current_depth + 1) 
                  for child in element)

    def generate_data_handling_templates(self, analysis: DataSourceAnalysis) -> Dict[str, str]:
        """
        Generate data handling function templates based on discovered data structures.
        
        Args:
            analysis: Complete data source analysis
            
        Returns:
            Dict mapping template names to template code
        """
        templates = {}
        
        # Generate CSV handling templates
        for csv_meta in analysis.csv_files:
            template_name = f"load_{Path(csv_meta.file_path).stem}_csv"
            templates[template_name] = self._generate_csv_template(csv_meta)
        
        # Generate JSON handling templates
        for json_meta in analysis.json_files:
            template_name = f"load_{Path(json_meta.file_path).stem}_json"
            templates[template_name] = self._generate_json_template(json_meta)
        
        # Generate XML handling templates
        for xml_meta in analysis.xml_files:
            template_name = f"load_{Path(xml_meta.file_path).stem}_xml"
            templates[template_name] = self._generate_xml_template(xml_meta)
        
        # Generate Excel handling templates
        for excel_meta in analysis.excel_files:
            template_name = f"load_{Path(excel_meta.file_path).stem}_excel"
            templates[template_name] = self._generate_excel_template(excel_meta)
        
        return templates
    
    def _generate_csv_template(self, csv_meta: CSVMetadata) -> str:
        """Generate a CSV loading function template."""
        file_stem = Path(csv_meta.file_path).stem
        
        # Generate type hints based on data types
        type_hints = []
        for col, dtype in csv_meta.data_types.items():
            if dtype == 'integer':
                type_hints.append(f"    # {col}: int")
            elif dtype == 'float':
                type_hints.append(f"    # {col}: float")
            elif dtype == 'boolean':
                type_hints.append(f"    # {col}: bool")
            elif dtype == 'datetime':
                type_hints.append(f"    # {col}: datetime")
            else:
                type_hints.append(f"    # {col}: str")
        
        template = f'''def load_{file_stem}_data(file_path: str = "{csv_meta.file_path}") -> pd.DataFrame:
    """
    Load and process {file_stem} CSV data.
    
    Expected columns:
{chr(10).join(type_hints)}
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed data
    """
    import pandas as pd
    
    # Load CSV with detected parameters
    df = pd.read_csv(
        file_path,
        delimiter="{csv_meta.delimiter}",
        encoding="{csv_meta.encoding}"
    )
    
    # Validate expected columns
    expected_columns = {csv_meta.columns}
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing expected columns: {{missing_columns}}")
    
    # Data type conversions
    type_conversions = {csv_meta.data_types}
    for col, dtype in type_conversions.items():
        if col in df.columns:
            if dtype == 'integer':
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            elif dtype == 'float':
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif dtype == 'boolean':
                df[col] = df[col].astype('boolean')
            elif dtype == 'datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df
'''
        return template
    
    def _generate_json_template(self, json_meta: JSONMetadata) -> str:
        """Generate a JSON loading function template."""
        file_stem = Path(json_meta.file_path).stem
        
        template = f'''def load_{file_stem}_data(file_path: str = "{json_meta.file_path}") -> Dict[str, Any]:
    """
    Load and process {file_stem} JSON data.
    
    Structure type: {json_meta.structure_type}
    Nested levels: {json_meta.nested_levels}
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict[str, Any]: Parsed JSON data
    """
    import json
    from typing import Dict, Any
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate structure type
    if isinstance(data, dict) and "{json_meta.structure_type}" != "object":
        raise ValueError(f"Expected {json_meta.structure_type} but got object")
    elif isinstance(data, list) and "{json_meta.structure_type}" != "array":
        raise ValueError(f"Expected {json_meta.structure_type} but got array")
    
    return data
'''
        return template
    
    def _generate_xml_template(self, xml_meta: XMLMetadata) -> str:
        """Generate an XML loading function template."""
        file_stem = Path(xml_meta.file_path).stem
        
        # Build template without nested f-strings to avoid formatting issues
        template = f'''def load_{file_stem}_data(file_path: str = "{xml_meta.file_path}") -> ET.Element:
    """
    Load and process {file_stem} XML data.
    
    Root element: {xml_meta.root_element}
    Elements: {xml_meta.elements}
    Structure depth: {xml_meta.structure_depth}
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        ET.Element: Parsed XML root element
    """
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Validate root element
    expected_root = "{xml_meta.root_element}"
    if root.tag != expected_root and not root.tag.endswith("}}" + expected_root):
        raise ValueError(f"Expected root element {{expected_root}} but got {{root.tag}}")
    
    return root

def extract_{file_stem}_elements(root: ET.Element) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract structured data from {file_stem} XML.
    
    Args:
        root: XML root element
        
    Returns:
        Dict containing extracted elements
    """
    from typing import Dict, List, Any
    
    result = {{}}
    
    # Extract elements based on discovered structure
    elements_to_extract = {xml_meta.elements}
    for element_name in elements_to_extract:
        elements = root.findall(f".//" + element_name)
        result[element_name] = []
        
        for elem in elements:
            elem_data = {{"text": elem.text or ""}}
            elem_data.update(elem.attrib)
            result[element_name].append(elem_data)
    
    return result
'''
        return template
    
    def _generate_excel_template(self, excel_meta: ExcelMetadata) -> str:
        """Generate an Excel loading function template."""
        file_stem = Path(excel_meta.file_path).stem
        
        sheet_info = []
        for sheet_name, sheet_data in excel_meta.sheets.items():
            columns = sheet_data.get('columns', [])
            sheet_info.append(f"    # {sheet_name}: {columns}")
        
        template = f'''def load_{file_stem}_data(file_path: str = "{excel_meta.file_path}", sheet_name: str = None) -> Dict[str, pd.DataFrame]:
    """
    Load and process {file_stem} Excel data.
    
    Available sheets:
{chr(10).join(sheet_info)}
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Specific sheet to load (None for all sheets)
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary of sheet names to DataFrames
    """
    import pandas as pd
    from typing import Dict
    
    if sheet_name:
        # Load specific sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return {{sheet_name: df}}
    else:
        # Load all sheets
        excel_file = pd.ExcelFile(file_path)
        sheets = {{}}
        
        for sheet in excel_file.sheet_names:
            sheets[sheet] = pd.read_excel(file_path, sheet_name=sheet)
        
        return sheets

def get_{file_stem}_sheet_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about sheets in {file_stem} Excel file.
    
    Returns:
        Dict containing sheet metadata
    """
    return {excel_meta.sheets}
'''
        return template