"""
Unit tests for the ProjectAnalyzer class.

This module tests the project analysis functionality including
structure scanning, documentation generation, and modification capabilities.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from a3.engines.project_analyzer import ProjectAnalyzer, ProjectAnalysisError
from a3.core.models import (
    ProjectStructure, SourceFile, TestFile, ConfigFile, DocumentationFile,
    ProjectDocumentation, CodePatterns, CodingConventions, ModificationPlan,
    ModificationResult, DependencyGraph, ValidationResult
)
from a3.core.interfaces import AIClientInterface, DependencyAnalyzerInterface
from a3.managers.filesystem import FileSystemManager


class TestProjectAnalyzer:
    """Test cases for ProjectAnalyzer class."""
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        client = Mock(spec=AIClientInterface)
        client.validate_api_key.return_value = True
        client.generate_with_retry.return_value = "Generated content"
        return client
    
    @pytest.fixture
    def mock_dependency_analyzer(self):
        """Create a mock dependency analyzer."""
        analyzer = Mock(spec=DependencyAnalyzerInterface)
        return analyzer
    
    @pytest.fixture
    def mock_filesystem_manager(self):
        """Create a mock filesystem manager."""
        manager = Mock(spec=FileSystemManager)
        return manager
    
    @pytest.fixture
    def project_analyzer(self, mock_ai_client, mock_dependency_analyzer, mock_filesystem_manager):
        """Create a ProjectAnalyzer instance with mocked dependencies."""
        analyzer = ProjectAnalyzer(
            ai_client=mock_ai_client,
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        analyzer.initialize()
        return analyzer
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sample Python files
            (project_path / "main.py").write_text("""
def main():
    '''Main function'''
    print("Hello World")

class MainClass:
    def method1(self):
        pass

if __name__ == "__main__":
    main()
""")
            
            (project_path / "utils.py").write_text("""
import os
import sys

def helper_function(arg1: str, arg2: int = 0) -> str:
    '''Helper function with type hints'''
    return f"{arg1}_{arg2}"

class UtilityClass:
    def __init__(self):
        self.value = 0
""")
            
            # Create test file
            (project_path / "test_main.py").write_text("""
import pytest
from main import main, MainClass

def test_main():
    '''Test main function'''
    assert main() is None

def test_main_class():
    '''Test MainClass'''
    obj = MainClass()
    assert obj is not None
""")
            
            # Create config file
            (project_path / "pyproject.toml").write_text("""
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
""")
            
            # Create documentation
            (project_path / "README.md").write_text("""
# Test Project

This is a test project for unit testing.

## Features

- Feature 1
- Feature 2

## Usage

Run with `python main.py`
""")
            
            yield project_path
    
    def test_initialization(self, mock_ai_client):
        """Test ProjectAnalyzer initialization."""
        analyzer = ProjectAnalyzer(ai_client=mock_ai_client)
        analyzer.initialize()
        
        assert analyzer.ai_client == mock_ai_client
        assert analyzer._initialized is True
    
    def test_initialization_without_ai_client(self):
        """Test initialization without AI client."""
        analyzer = ProjectAnalyzer()
        
        # Should not raise an error
        analyzer.initialize()
        assert analyzer._initialized is True
    
    def test_scan_project_folder_success(self, project_analyzer, temp_project_dir):
        """Test successful project folder scanning."""
        structure = project_analyzer.scan_project_folder(str(temp_project_dir))
        
        assert isinstance(structure, ProjectStructure)
        assert structure.root_path == str(temp_project_dir)
        assert len(structure.source_files) >= 2  # main.py, utils.py
        assert len(structure.test_files) >= 1    # test_main.py
        assert len(structure.config_files) >= 1  # pyproject.toml
        assert len(structure.documentation_files) >= 1  # README.md
        
        # Check source file analysis
        main_file = next((f for f in structure.source_files if f.path == "main.py"), None)
        assert main_file is not None
        assert "main" in main_file.functions
        assert "MainClass" in main_file.classes
        assert main_file.lines_of_code > 0
    
    def test_scan_project_folder_nonexistent_path(self, project_analyzer):
        """Test scanning non-existent project path."""
        with pytest.raises(ProjectAnalysisError, match="Project path does not exist"):
            project_analyzer.scan_project_folder("/nonexistent/path")
    
    def test_scan_project_folder_file_instead_of_directory(self, project_analyzer, temp_project_dir):
        """Test scanning a file instead of directory."""
        file_path = temp_project_dir / "main.py"
        
        with pytest.raises(ProjectAnalysisError, match="Project path is not a directory"):
            project_analyzer.scan_project_folder(str(file_path))
    
    def test_analyze_source_file(self, project_analyzer):
        """Test source file analysis."""
        content = """
import os
from typing import List

def function1(arg: str) -> int:
    '''Function with type hints'''
    return len(arg)

class TestClass:
    def method1(self):
        pass
    
    def method2(self, x: int) -> str:
        return str(x)
"""
        
        file_path = Path("test.py")
        source_file = project_analyzer._analyze_source_file(file_path, "test.py", content)
        
        assert source_file.path == "test.py"
        assert source_file.language == "python"
        assert "function1" in source_file.functions
        assert "TestClass" in source_file.classes
        assert "os" in source_file.imports
        assert "typing.List" in source_file.imports
        assert source_file.lines_of_code > 0
        assert source_file.complexity_score > 0
    
    def test_analyze_source_file_with_syntax_error(self, project_analyzer):
        """Test source file analysis with syntax errors."""
        content = """
def broken_function(
    # Missing closing parenthesis and colon
    pass
"""
        
        file_path = Path("broken.py")
        source_file = project_analyzer._analyze_source_file(file_path, "broken.py", content)
        
        # Should handle syntax errors gracefully
        assert source_file.path == "broken.py"
        assert source_file.functions == []
        assert source_file.classes == []
    
    def test_analyze_test_file(self, project_analyzer):
        """Test test file analysis."""
        content = """
import pytest
import unittest
from main import MainClass

def test_function1():
    assert True

def test_function2():
    pass

class TestMainClass(unittest.TestCase):
    def test_method(self):
        pass
"""
        
        file_path = Path("test_example.py")
        test_file = project_analyzer._analyze_test_file(file_path, "test_example.py", content)
        
        assert test_file.path == "test_example.py"
        assert "test_function1" in test_file.test_functions
        assert "test_function2" in test_file.test_functions
        assert "main" in test_file.tested_modules
        assert test_file.test_framework in ["pytest", "unittest"]
    
    def test_analyze_config_file_toml(self, project_analyzer):
        """Test TOML config file analysis."""
        content = """
[build-system]
requires = ["setuptools"]

[project]
name = "test"
version = "1.0.0"
"""
        
        file_path = Path("pyproject.toml")
        config_file = project_analyzer._analyze_config_file(file_path, "pyproject.toml", content)
        
        assert config_file.path == "pyproject.toml"
        assert config_file.config_type == "pyproject.toml"
        # Note: parsed_config might be empty if tomllib/tomli not available
    
    def test_analyze_doc_file_markdown(self, project_analyzer):
        """Test markdown documentation file analysis."""
        content = """
# Main Title

This is the introduction.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

### Subsection

More content.
"""
        
        file_path = Path("README.md")
        doc_file = project_analyzer._analyze_doc_file(file_path, "README.md", content)
        
        assert doc_file.path == "README.md"
        assert doc_file.doc_type == "README"
        assert "Main Title" in doc_file.sections
        assert "Section 1" in doc_file.sections
        assert "Section 2" in doc_file.sections
    
    def test_file_type_identification(self, project_analyzer):
        """Test file type identification methods."""
        # Test source file identification
        assert project_analyzer._is_source_file(Path("main.py"), "main.py") is True
        assert project_analyzer._is_source_file(Path("test_main.py"), "test_main.py") is False  # Test file
        assert project_analyzer._is_source_file(Path("config.txt"), "config.txt") is False
        
        # Test test file identification
        assert project_analyzer._is_test_file(Path("test_main.py"), "test_main.py") is True
        assert project_analyzer._is_test_file(Path("main_test.py"), "main_test.py") is True
        assert project_analyzer._is_test_file(Path("tests.py"), "tests.py") is True
        assert project_analyzer._is_test_file(Path("main.py"), "main.py") is False
        
        # Test config file identification
        assert project_analyzer._is_config_file(Path("pyproject.toml"), "pyproject.toml") is True
        assert project_analyzer._is_config_file(Path("setup.py"), "setup.py") is True
        assert project_analyzer._is_config_file(Path("requirements.txt"), "requirements.txt") is True
        assert project_analyzer._is_config_file(Path("main.py"), "main.py") is False
        
        # Test doc file identification
        assert project_analyzer._is_doc_file(Path("README.md"), "README.md") is True
        assert project_analyzer._is_doc_file(Path("CHANGELOG.rst"), "CHANGELOG.rst") is True
        assert project_analyzer._is_doc_file(Path("main.py"), "main.py") is False
    
    def test_build_dependency_graph_from_files(self, project_analyzer):
        """Test dependency graph building from source files."""
        source_files = [
            SourceFile(
                path="main.py",
                content="",
                functions=["main"],
                classes=["MainClass"],
                imports=["utils", "os", "sys"]
            ),
            SourceFile(
                path="utils.py",
                content="",
                functions=["helper"],
                classes=["UtilityClass"],
                imports=["os", "json"]
            )
        ]
        
        graph = project_analyzer._build_dependency_graph_from_files(source_files)
        
        assert isinstance(graph, DependencyGraph)
        assert "main" in graph.nodes
        assert "utils" in graph.nodes
        # Should have dependency from main to utils
        assert ("main", "utils") in graph.edges
    
    def test_generate_project_documentation(self, project_analyzer, temp_project_dir):
        """Test project documentation generation."""
        structure = project_analyzer.scan_project_folder(str(temp_project_dir))
        documentation = project_analyzer.generate_project_documentation(structure)
        
        assert isinstance(documentation, ProjectDocumentation)
        assert documentation.overview == "Generated content"  # From mock
        assert documentation.architecture_description == "Generated content"
        assert len(documentation.module_descriptions) > 0
        assert len(documentation.usage_examples) > 0
    
    def test_generate_project_documentation_without_ai_client(self, temp_project_dir):
        """Test documentation generation without AI client."""
        analyzer = ProjectAnalyzer()
        analyzer.initialize()
        
        structure = analyzer.scan_project_folder(str(temp_project_dir))
        
        with pytest.raises(ProjectAnalysisError, match="AI client is required"):
            analyzer.generate_project_documentation(structure)
    
    def test_analyze_code_patterns(self, project_analyzer, temp_project_dir):
        """Test code pattern analysis."""
        structure = project_analyzer.scan_project_folder(str(temp_project_dir))
        patterns = project_analyzer.analyze_code_patterns(structure)
        
        assert isinstance(patterns, CodePatterns)
        assert isinstance(patterns.coding_conventions, CodingConventions)
        assert isinstance(patterns.architectural_patterns, list)
        assert isinstance(patterns.design_patterns, list)
        assert isinstance(patterns.common_utilities, list)
        assert isinstance(patterns.test_patterns, list)
    
    def test_suggest_modifications(self, project_analyzer, temp_project_dir):
        """Test modification suggestions."""
        structure = project_analyzer.scan_project_folder(str(temp_project_dir))
        
        user_prompt = "Add a new function to handle user input"
        plan = project_analyzer.suggest_modifications(user_prompt, structure)
        
        assert isinstance(plan, ModificationPlan)
        assert plan.user_prompt == user_prompt
        assert len(plan.target_files) > 0
        assert len(plan.planned_changes) > 0
        assert plan.estimated_impact in ["low", "medium", "high"]
        assert plan.backup_required is True
    
    def test_suggest_modifications_without_ai_client(self, temp_project_dir):
        """Test modification suggestions without AI client."""
        analyzer = ProjectAnalyzer()
        analyzer.initialize()
        
        structure = analyzer.scan_project_folder(str(temp_project_dir))
        
        with pytest.raises(ProjectAnalysisError, match="AI client is required"):
            analyzer.suggest_modifications("Add new feature", structure)
    
    def test_apply_modifications(self, project_analyzer, temp_project_dir):
        """Test applying modifications."""
        structure = project_analyzer.scan_project_folder(str(temp_project_dir))
        
        # Create a simple modification plan
        plan = ModificationPlan(
            user_prompt="Test modification",
            target_files=["main.py"],
            planned_changes=[{
                'file_path': 'main.py',
                'change_type': 'modification',
                'description': 'Test change'
            }],
            estimated_impact="low"
        )
        
        result = project_analyzer.apply_modifications(plan)
        
        assert isinstance(result, ModificationResult)
        assert result.success is True
        assert len(result.modified_files) > 0
        assert result.backup_location is not None
    
    def test_apply_modifications_without_filesystem_manager(self, temp_project_dir):
        """Test applying modifications without filesystem manager."""
        analyzer = ProjectAnalyzer()
        analyzer.initialize()
        
        plan = ModificationPlan(
            user_prompt="Test modification",
            target_files=["main.py"],
            planned_changes=[{
                'file_path': 'main.py',
                'change_type': 'modification',
                'description': 'Test change'
            }]
        )
        
        with pytest.raises(ProjectAnalysisError, match="Filesystem manager is required"):
            analyzer.apply_modifications(plan)
    
    def test_validate_style_consistency(self, project_analyzer, temp_project_dir):
        """Test style consistency validation."""
        structure = project_analyzer.scan_project_folder(str(temp_project_dir))
        
        plan = ModificationPlan(
            user_prompt="Test modification",
            target_files=["main.py"],
            planned_changes=[{
                'file_path': 'main.py',
                'change_type': 'modification',
                'description': 'Test change'
            }]
        )
        
        result = project_analyzer.validate_style_consistency(structure, plan)
        
        assert isinstance(result, ValidationResult)
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.issues, list)
        assert isinstance(result.warnings, list)
    
    def test_coding_conventions_analysis(self, project_analyzer):
        """Test coding conventions analysis."""
        source_files = [
            SourceFile(
                path="typed.py",
                content="""
def typed_function(arg: str) -> int:
    return len(arg)

def untyped_function(arg):
    return str(arg)
""",
                functions=["typed_function", "untyped_function"],
                classes=[],
                imports=[]
            )
        ]
        
        structure = ProjectStructure(
            root_path="/test",
            source_files=source_files
        )
        
        conventions = project_analyzer._analyze_coding_conventions(structure)
        
        assert isinstance(conventions, CodingConventions)
        assert 0.0 <= conventions.type_hints_usage <= 1.0
        assert conventions.line_length > 0
    
    def test_architectural_pattern_identification(self, project_analyzer):
        """Test architectural pattern identification."""
        source_files = [
            SourceFile(path="models/user.py", content="", functions=[], classes=[], imports=[]),
            SourceFile(path="views/user_view.py", content="", functions=[], classes=[], imports=[]),
            SourceFile(path="controllers/user_controller.py", content="", functions=[], classes=[], imports=[]),
            SourceFile(path="services/user_service.py", content="", functions=[], classes=[], imports=[]),
        ]
        
        structure = ProjectStructure(
            root_path="/test",
            source_files=source_files
        )
        
        patterns = project_analyzer._identify_architectural_patterns(structure)
        
        assert "Model-based architecture" in patterns
        assert "MVC pattern" in patterns
        assert "Service layer pattern" in patterns
    
    def test_design_pattern_identification(self, project_analyzer):
        """Test design pattern identification."""
        source_files = [
            SourceFile(
                path="patterns.py",
                content="",
                functions=[],
                classes=["UserFactory", "ConfigBuilder", "EventObserver", "DatabaseSingleton"],
                imports=[]
            )
        ]
        
        structure = ProjectStructure(
            root_path="/test",
            source_files=source_files
        )
        
        patterns = project_analyzer._identify_design_patterns(structure)
        
        assert "Factory pattern" in patterns
        assert "Builder pattern" in patterns
        assert "Observer pattern" in patterns
        assert "Singleton pattern" in patterns
    
    def test_external_import_detection(self, project_analyzer):
        """Test external import detection."""
        source_files = [
            SourceFile(path="main.py", content="", functions=[], classes=[], imports=[]),
            SourceFile(path="utils.py", content="", functions=[], classes=[], imports=[])
        ]
        
        # Test standard library imports
        assert project_analyzer._is_external_import("os", source_files) is True
        assert project_analyzer._is_external_import("sys", source_files) is True
        assert project_analyzer._is_external_import("json", source_files) is True
        
        # Test external package imports
        assert project_analyzer._is_external_import("requests", source_files) is True
        assert project_analyzer._is_external_import("numpy", source_files) is True
        
        # Test internal imports (should be False for external)
        assert project_analyzer._is_external_import("main", source_files) is False
        assert project_analyzer._is_external_import("utils", source_files) is False
    
    def test_complexity_score_calculation(self, project_analyzer):
        """Test complexity score calculation."""
        import ast
        
        # Simple function with no control structures
        simple_code = """
def simple_function():
    return 42
"""
        simple_tree = ast.parse(simple_code)
        simple_score = project_analyzer._calculate_complexity_score(simple_tree)
        assert simple_score == 0.5  # Just the function definition
        
        # Complex function with control structures
        complex_code = """
def complex_function(x):
    if x > 0:
        for i in range(x):
            try:
                with open('file.txt') as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
            except IOError:
                pass
    return x
"""
        complex_tree = ast.parse(complex_code)
        complex_score = project_analyzer._calculate_complexity_score(complex_tree)
        assert complex_score > simple_score
    
    def test_doc_section_extraction(self, project_analyzer):
        """Test documentation section extraction."""
        markdown_content = """
# Main Title

Introduction paragraph.

## Section 1

Content for section 1.

### Subsection 1.1

Subsection content.

## Section 2

Content for section 2.
"""
        
        sections = project_analyzer._extract_doc_sections(markdown_content)
        
        assert "Main Title" in sections
        assert "Section 1" in sections
        assert "Subsection 1.1" in sections
        assert "Section 2" in sections
    
    def test_modification_intent_analysis(self, project_analyzer):
        """Test modification intent analysis."""
        # Test addition intent
        add_intent = project_analyzer._analyze_modification_intent(
            "Add a new function to handle user authentication",
            ProjectStructure(root_path="/test")
        )
        assert add_intent['type'] == 'addition'
        
        # Test modification intent
        modify_intent = project_analyzer._analyze_modification_intent(
            "Modify the existing login function to use OAuth",
            ProjectStructure(root_path="/test")
        )
        assert modify_intent['type'] == 'modification'
        
        # Test removal intent
        remove_intent = project_analyzer._analyze_modification_intent(
            "Remove the deprecated helper functions",
            ProjectStructure(root_path="/test")
        )
        assert remove_intent['type'] == 'removal'
        
        # Test refactoring intent
        refactor_intent = project_analyzer._analyze_modification_intent(
            "Refactor the database connection code",
            ProjectStructure(root_path="/test")
        )
        assert refactor_intent['type'] == 'refactoring'
    
    def test_target_file_identification(self, project_analyzer):
        """Test target file identification for modifications."""
        source_files = [
            SourceFile(
                path="auth.py",
                content="",
                functions=["login", "logout", "authenticate"],
                classes=["AuthManager"],
                imports=[]
            ),
            SourceFile(
                path="database.py",
                content="",
                functions=["connect", "query", "close"],
                classes=["DatabaseManager"],
                imports=[]
            )
        ]
        
        structure = ProjectStructure(
            root_path="/test",
            source_files=source_files
        )
        
        # Test keyword-based targeting
        auth_intent = {'keywords': ['auth', 'login']}
        auth_targets = project_analyzer._identify_target_files(auth_intent, structure)
        assert "auth.py" in auth_targets
        
        db_intent = {'keywords': ['database', 'query']}
        db_targets = project_analyzer._identify_target_files(db_intent, structure)
        assert "database.py" in db_targets
    
    def test_impact_estimation(self, project_analyzer):
        """Test modification impact estimation."""
        # Low impact - single change
        low_changes = [{'file_path': 'main.py', 'change_type': 'modification'}]
        low_impact = project_analyzer._estimate_modification_impact(low_changes, None)
        assert low_impact == "low"
        
        # Medium impact - few changes
        medium_changes = [
            {'file_path': 'main.py', 'change_type': 'modification'},
            {'file_path': 'utils.py', 'change_type': 'modification'}
        ]
        medium_impact = project_analyzer._estimate_modification_impact(medium_changes, None)
        assert medium_impact == "medium"
        
        # High impact - many changes
        high_changes = [
            {'file_path': f'file{i}.py', 'change_type': 'modification'}
            for i in range(5)
        ]
        high_impact = project_analyzer._estimate_modification_impact(high_changes, None)
        assert high_impact == "high"
    
    def test_affected_dependencies_identification(self, project_analyzer):
        """Test identification of affected dependencies."""
        graph = DependencyGraph(
            nodes=["main", "utils", "auth", "database"],
            edges=[("main", "utils"), ("main", "auth"), ("auth", "database")]
        )
        
        structure = ProjectStructure(
            root_path="/test",
            dependency_graph=graph
        )
        
        # Test dependencies affected by modifying utils
        affected = project_analyzer._identify_affected_dependencies(["utils.py"], structure)
        assert "main" in affected  # main depends on utils
        
        # Test dependencies affected by modifying database
        affected = project_analyzer._identify_affected_dependencies(["database.py"], structure)
        assert "auth" in affected  # auth depends on database


if __name__ == "__main__":
    pytest.main([__file__])