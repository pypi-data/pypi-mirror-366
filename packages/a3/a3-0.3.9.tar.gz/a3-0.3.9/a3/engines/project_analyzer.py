"""
Project analyzer implementation for AI Project Builder.

This module provides the ProjectAnalyzer class that analyzes existing codebases,
generates documentation, and enables intelligent modifications.
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import defaultdict
import importlib.util

from .base import BaseProjectAnalyzer
from .database_analyzer import DatabaseAnalyzer
from ..core.interfaces import ProjectAnalyzerInterface, AIClientInterface, DependencyAnalyzerInterface
from ..core.models import (
    ProjectStructure, SourceFile, TestFile, ConfigFile, DocumentationFile,
    ProjectDocumentation, CodePatterns, CodingConventions, ModificationPlan,
    ModificationResult, DependencyGraph, ValidationResult, Module, FunctionSpec,
    DataSourceAnalysis, DatabaseSchema, DatabaseConnection
)
from ..managers.dependency import DependencyAnalyzer
from ..managers.filesystem import FileSystemManager
from ..managers.data_source_manager import DataSourceManager


class ProjectAnalysisError(Exception):
    """Base exception for project analysis errors."""
    pass


class ProjectAnalyzer(BaseProjectAnalyzer, ProjectAnalyzerInterface):
    """
    Analyzer for existing codebases with documentation and modification capabilities.
    
    Provides comprehensive project analysis including structure scanning,
    dependency analysis, documentation generation, and intelligent modifications.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 dependency_analyzer: Optional[DependencyAnalyzerInterface] = None,
                 filesystem_manager: Optional[FileSystemManager] = None,
                 database_analyzer: Optional[DatabaseAnalyzer] = None):
        """
        Initialize the project analyzer.
        
        Args:
            ai_client: Client for AI service interactions
            dependency_analyzer: Analyzer for module dependencies
            filesystem_manager: Manager for file system operations
            database_analyzer: Analyzer for database schema analysis
        """
        super().__init__(ai_client)
        self.dependency_analyzer = dependency_analyzer
        self.filesystem_manager = filesystem_manager
        self.database_analyzer = database_analyzer or DatabaseAnalyzer(ai_client)
        
        # File extensions to analyze
        self.source_extensions = {'.py'}
        self.test_extensions = {'.py'}
        self.config_extensions = {'.toml', '.cfg', '.ini', '.yaml', '.yml', '.json', '.txt'}
        self.doc_extensions = {'.md', '.rst', '.txt'}
        
        # Patterns for identifying file types
        self.test_patterns = [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'tests?\.py$',
            r'.*tests?/.*\.py$'
        ]
        
        self.config_patterns = [
            r'setup\.py$',
            r'pyproject\.toml$',
            r'requirements.*\.txt$',
            r'.*\.cfg$',
            r'.*\.ini$',
            r'.*config.*\.(yaml|yml|json)$'
        ]
        
        self.doc_patterns = [
            r'README.*\.(md|rst|txt)$',
            r'CHANGELOG.*\.(md|rst|txt)$',
            r'LICENSE.*$',
            r'.*\.md$',
            r'.*\.rst$',
            r'docs?/.*\.(md|rst|txt)$'
        ]
    
    def initialize(self) -> None:
        """Initialize the project analyzer and its dependencies."""
        super().initialize()
        if self.database_analyzer:
            self.database_analyzer.initialize()
    
    def scan_project_folder(self, project_path: str, database_connection_string: Optional[str] = None) -> ProjectStructure:
        """
        Scan a project folder and identify all source files.
        
        Args:
            project_path: Path to the project directory
            database_connection_string: Optional PostgreSQL connection string for database analysis
            
        Returns:
            ProjectStructure with analyzed files and structure
        """
        self._ensure_initialized()
        
        project_root = Path(project_path).resolve()
        if not project_root.exists():
            raise ProjectAnalysisError(f"Project path does not exist: {project_path}")
        
        if not project_root.is_dir():
            raise ProjectAnalysisError(f"Project path is not a directory: {project_path}")
        
        # Initialize structure
        structure = ProjectStructure(root_path=str(project_root))
        
        # Scan all files recursively
        for file_path in self._scan_files_recursively(project_root):
            relative_path = str(file_path.relative_to(project_root))
            
            # Skip hidden files and directories (except .A3)
            if any(part.startswith('.') and part != '.A3' for part in file_path.parts):
                continue
            
            # Skip __pycache__ directories
            if '__pycache__' in file_path.parts:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue  # Skip files that can't be read
            
            # Categorize file based on patterns and extensions
            if self._is_source_file(file_path, relative_path):
                source_file = self._analyze_source_file(file_path, relative_path, content)
                structure.source_files.append(source_file)
            
            elif self._is_test_file(file_path, relative_path):
                test_file = self._analyze_test_file(file_path, relative_path, content)
                structure.test_files.append(test_file)
            
            elif self._is_config_file(file_path, relative_path):
                config_file = self._analyze_config_file(file_path, relative_path, content)
                structure.config_files.append(config_file)
            
            elif self._is_doc_file(file_path, relative_path):
                doc_file = self._analyze_doc_file(file_path, relative_path, content)
                structure.documentation_files.append(doc_file)
        
        # Build dependency graph from source files
        structure.dependency_graph = self._build_dependency_graph_from_files(structure.source_files)
        
        # Scan for data sources
        structure.data_source_analysis = self._scan_data_sources(project_root)
        
        # Analyze database schema if connection string provided
        structure.database_analysis = self._analyze_database_schema(database_connection_string)
        
        # Validate the structure
        structure.validate()
        
        return structure
    
    def generate_project_documentation(self, project_structure: ProjectStructure) -> ProjectDocumentation:
        """
        Generate comprehensive documentation following the same standards as its own projects.
        
        Args:
            project_structure: Analyzed project structure
            
        Returns:
            ProjectDocumentation with generated documentation
        """
        self._ensure_initialized()
        
        if not self.ai_client:
            raise ProjectAnalysisError("AI client is required for documentation generation")
        
        # Generate overview
        overview = self._generate_project_overview(project_structure)
        
        # Generate architecture description
        architecture = self._generate_architecture_description(project_structure)
        
        # Generate module descriptions
        module_descriptions = self._generate_module_descriptions(project_structure)
        
        # Generate function descriptions
        function_descriptions = self._generate_function_descriptions(project_structure)
        
        # Generate dependency analysis
        dependency_analysis = self._generate_dependency_analysis(project_structure)
        
        # Generate usage examples
        usage_examples = self._generate_usage_examples(project_structure)
        
        # Generate database documentation
        database_documentation = self._generate_database_documentation(project_structure)
        
        return ProjectDocumentation(
            overview=overview,
            architecture_description=architecture,
            module_descriptions=module_descriptions,
            function_descriptions=function_descriptions,
            dependency_analysis=dependency_analysis,
            usage_examples=usage_examples,
            database_documentation=database_documentation
        )
    
    def build_dependency_graph(self, project_structure: ProjectStructure) -> DependencyGraph:
        """
        Analyze import relationships and create visual dependency maps.
        
        Args:
            project_structure: Analyzed project structure
            
        Returns:
            DependencyGraph representing module relationships
        """
        return self._build_dependency_graph_from_files(project_structure.source_files)
    
    def analyze_code_patterns(self, project_structure: ProjectStructure) -> CodePatterns:
        """
        Analyze code patterns and conventions in the project.
        
        Args:
            project_structure: Analyzed project structure
            
        Returns:
            CodePatterns with identified patterns and conventions
        """
        self._ensure_initialized()
        
        # Analyze coding conventions
        conventions = self._analyze_coding_conventions(project_structure)
        
        # Identify architectural patterns
        architectural_patterns = self._identify_architectural_patterns(project_structure)
        
        # Identify design patterns
        design_patterns = self._identify_design_patterns(project_structure)
        
        # Find common utilities
        common_utilities = self._find_common_utilities(project_structure)
        
        # Analyze test patterns
        test_patterns = self._analyze_test_patterns(project_structure)
        
        return CodePatterns(
            architectural_patterns=architectural_patterns,
            design_patterns=design_patterns,
            coding_conventions=conventions,
            common_utilities=common_utilities,
            test_patterns=test_patterns
        )
    
    def suggest_modifications(self, user_prompt: str, project_structure: ProjectStructure) -> ModificationPlan:
        """
        Make targeted changes based on the analyzed project structure.
        
        Args:
            user_prompt: User's description of desired modifications
            project_structure: Analyzed project structure
            
        Returns:
            ModificationPlan with planned changes
        """
        self._ensure_initialized()
        
        if not self.ai_client:
            raise ProjectAnalysisError("AI client is required for modification suggestions")
        
        # Analyze the user prompt to understand intent
        modification_intent = self._analyze_modification_intent(user_prompt, project_structure)
        
        # Identify target files for modification
        target_files = self._identify_target_files(modification_intent, project_structure)
        
        # Plan specific changes
        planned_changes = self._plan_specific_changes(modification_intent, target_files, project_structure)
        
        # Estimate impact
        impact = self._estimate_modification_impact(planned_changes, project_structure)
        
        # Identify affected dependencies
        affected_deps = self._identify_affected_dependencies(target_files, project_structure)
        
        return ModificationPlan(
            user_prompt=user_prompt,
            target_files=target_files,
            planned_changes=planned_changes,
            estimated_impact=impact,
            backup_required=True,
            dependencies_affected=affected_deps
        )
    
    def apply_modifications(self, modification_plan: ModificationPlan) -> ModificationResult:
        """
        Apply the planned modifications to the project.
        
        Args:
            modification_plan: Plan with modifications to apply
            
        Returns:
            ModificationResult with application results
        """
        self._ensure_initialized()
        
        if not self.filesystem_manager:
            raise ProjectAnalysisError("Filesystem manager is required for applying modifications")
        
        modified_files = []
        errors = []
        warnings = []
        backup_location = None
        
        try:
            # Create backup if required
            if modification_plan.backup_required:
                backup_location = self._create_backup(modification_plan.target_files)
            
            # Apply each planned change
            for change in modification_plan.planned_changes:
                try:
                    file_path = change.get('file_path')
                    if not file_path:
                        errors.append("Change missing file_path")
                        continue
                    
                    success = self._apply_single_change(change)
                    if success:
                        modified_files.append(file_path)
                    else:
                        errors.append(f"Failed to apply change to {file_path}")
                
                except Exception as e:
                    errors.append(f"Error applying change to {change.get('file_path', 'unknown')}: {str(e)}")
            
            return ModificationResult(
                success=len(errors) == 0,
                modified_files=modified_files,
                errors=errors,
                warnings=warnings,
                backup_location=backup_location
            )
        
        except Exception as e:
            return ModificationResult(
                success=False,
                modified_files=modified_files,
                errors=[f"Modification application failed: {str(e)}"],
                warnings=warnings,
                backup_location=backup_location
            )
    
    def validate_style_consistency(self, project_structure: ProjectStructure, 
                                  modifications: ModificationPlan) -> ValidationResult:
        """
        Validate that modifications maintain consistency with existing codebase style.
        
        Args:
            project_structure: Analyzed project structure
            modifications: Planned modifications
            
        Returns:
            ValidationResult with consistency validation
        """
        self._ensure_initialized()
        
        issues = []
        warnings = []
        
        # Analyze existing code patterns
        existing_patterns = self.analyze_code_patterns(project_structure)
        
        # Check each planned change for consistency
        for change in modifications.planned_changes:
            consistency_issues = self._check_change_consistency(change, existing_patterns)
            issues.extend(consistency_issues)
        
        # Check naming conventions
        naming_issues = self._check_naming_consistency(modifications, existing_patterns.coding_conventions)
        issues.extend(naming_issues)
        
        # Check import style consistency
        import_issues = self._check_import_consistency(modifications, existing_patterns.coding_conventions)
        warnings.extend(import_issues)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    # Private helper methods
    
    def _scan_files_recursively(self, root_path: Path) -> List[Path]:
        """Recursively scan all files in the project directory."""
        files = []
        for item in root_path.rglob('*'):
            if item.is_file():
                files.append(item)
        return files
    
    def _is_source_file(self, file_path: Path, relative_path: str) -> bool:
        """Check if a file is a source code file."""
        if file_path.suffix not in self.source_extensions:
            return False
        
        # Exclude test files
        if self._is_test_file(file_path, relative_path):
            return False
        
        return True
    
    def _is_test_file(self, file_path: Path, relative_path: str) -> bool:
        """Check if a file is a test file."""
        if file_path.suffix not in self.test_extensions:
            return False
        
        for pattern in self.test_patterns:
            if re.search(pattern, relative_path, re.IGNORECASE):
                return True
        
        return False
    
    def _is_config_file(self, file_path: Path, relative_path: str) -> bool:
        """Check if a file is a configuration file."""
        # First check patterns (which includes setup.py)
        for pattern in self.config_patterns:
            if re.search(pattern, relative_path, re.IGNORECASE):
                return True
        
        # Then check extensions for other config files
        if file_path.suffix in self.config_extensions:
            return True
        
        return False
    
    def _is_doc_file(self, file_path: Path, relative_path: str) -> bool:
        """Check if a file is a documentation file."""
        if file_path.suffix not in self.doc_extensions:
            return False
        
        for pattern in self.doc_patterns:
            if re.search(pattern, relative_path, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_source_file(self, file_path: Path, relative_path: str, content: str) -> SourceFile:
        """Analyze a source code file and extract information."""
        functions = []
        classes = []
        imports = []
        lines_of_code = 0
        complexity_score = 0.0
        
        try:
            # Parse the AST
            tree = ast.parse(content)
            
            # Extract functions, classes, and imports
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}" if module else alias.name)
            
            # Calculate lines of code (non-empty, non-comment lines)
            lines = content.split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    lines_of_code += 1
            
            # Simple complexity score based on control structures
            complexity_score = self._calculate_complexity_score(tree)
        
        except SyntaxError:
            # Handle files with syntax errors gracefully
            pass
        
        return SourceFile(
            path=relative_path,
            content=content,
            language="python",
            functions=functions,
            classes=classes,
            imports=imports,
            lines_of_code=lines_of_code,
            complexity_score=complexity_score
        )
    
    def _analyze_test_file(self, file_path: Path, relative_path: str, content: str) -> TestFile:
        """Analyze a test file and extract test information."""
        test_functions = []
        tested_modules = []
        test_framework = "pytest"  # Default assumption
        
        try:
            tree = ast.parse(content)
            
            # Extract test functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_') or node.name.endswith('_test'):
                        test_functions.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Detect test framework
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if 'unittest' in alias.name:
                                test_framework = "unittest"
                            elif 'pytest' in alias.name:
                                test_framework = "pytest"
                    else:
                        module = node.module or ''
                        if 'unittest' in module:
                            test_framework = "unittest"
                        elif 'pytest' in module:
                            test_framework = "pytest"
                        
                        # Try to identify tested modules from imports
                        if not module.startswith(('unittest', 'pytest', 'mock', 'test')):
                            tested_modules.append(module)
        
        except SyntaxError:
            pass
        
        return TestFile(
            path=relative_path,
            content=content,
            test_functions=test_functions,
            tested_modules=tested_modules,
            test_framework=test_framework
        )
    
    def _analyze_config_file(self, file_path: Path, relative_path: str, content: str) -> ConfigFile:
        """Analyze a configuration file."""
        config_type = self._determine_config_type(file_path)
        parsed_config = {}
        
        try:
            if config_type == 'pyproject.toml':
                try:
                    import tomllib
                    parsed_config = tomllib.loads(content)
                except ImportError:
                    # tomllib is only available in Python 3.11+
                    try:
                        import tomli as tomllib
                        parsed_config = tomllib.loads(content)
                    except ImportError:
                        pass  # TOML parsing not available
            elif config_type.endswith('.json'):
                import json
                parsed_config = json.loads(content)
            elif config_type.endswith(('.yaml', '.yml')):
                try:
                    import yaml
                    parsed_config = yaml.safe_load(content)
                except ImportError:
                    pass  # YAML not available
        except Exception:
            pass  # Parsing failed, leave empty
        
        return ConfigFile(
            path=relative_path,
            content=content,
            config_type=config_type,
            parsed_config=parsed_config
        )
    
    def _analyze_doc_file(self, file_path: Path, relative_path: str, content: str) -> DocumentationFile:
        """Analyze a documentation file."""
        doc_type = self._determine_doc_type(file_path)
        sections = []
        
        # Extract sections from markdown/rst files
        if doc_type in ['README', 'CHANGELOG'] or file_path.suffix in ['.md', '.rst']:
            sections = self._extract_doc_sections(content)
        
        return DocumentationFile(
            path=relative_path,
            content=content,
            doc_type=doc_type,
            sections=sections
        )
    
    def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """Calculate a simple complexity score for the AST."""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 0.5  # Functions add some complexity
        
        return complexity
    
    def _determine_config_type(self, file_path: Path) -> str:
        """Determine the type of configuration file."""
        name = file_path.name.lower()
        
        if name == 'pyproject.toml':
            return 'pyproject.toml'
        elif name == 'setup.py':
            return 'setup.py'
        elif name.startswith('requirements'):
            return 'requirements.txt'
        elif name.endswith('.toml'):
            return 'toml'
        elif name.endswith('.json'):
            return 'json'
        elif name.endswith(('.yaml', '.yml')):
            return 'yaml'
        elif name.endswith(('.cfg', '.ini')):
            return 'ini'
        else:
            return 'unknown'
    
    def _determine_doc_type(self, file_path: Path) -> str:
        """Determine the type of documentation file."""
        name = file_path.name.lower()
        
        if name.startswith('readme'):
            return 'README'
        elif name.startswith('changelog'):
            return 'CHANGELOG'
        elif name.startswith('license'):
            return 'LICENSE'
        elif 'api' in name:
            return 'API'
        else:
            return 'GENERAL'
    
    def _extract_doc_sections(self, content: str) -> List[str]:
        """Extract section headers from documentation content."""
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            # Markdown headers
            if stripped.startswith('#'):
                header = stripped.lstrip('#').strip()
                if header:
                    sections.append(header)
            # RST headers (simplified detection)
            elif len(stripped) > 0 and len(lines) > lines.index(line) + 1:
                next_line = lines[lines.index(line) + 1].strip()
                if next_line and all(c in '=-~^' for c in next_line) and len(next_line) >= len(stripped):
                    sections.append(stripped)
        
        return sections
    
    def _build_dependency_graph_from_files(self, source_files: List[SourceFile]) -> DependencyGraph:
        """Build a dependency graph from analyzed source files."""
        nodes = []
        edges = []
        
        # Create modules from source files
        modules = []
        for source_file in source_files:
            # Convert file path to module name
            module_name = source_file.path.replace('/', '.').replace('\\', '.').replace('.py', '')
            if module_name.startswith('.'):
                module_name = module_name[1:]
            
            # Handle __init__.py files - use parent directory name
            if module_name.endswith('.__init__'):
                module_name = module_name[:-9]  # Remove .__init__
            
            # Skip empty module names
            if not module_name:
                continue
            
            nodes.append(module_name)
            
            # Create module dependencies from imports
            dependencies = []
            for import_name in source_file.imports:
                # Filter to only internal imports (heuristic)
                if not self._is_external_import(import_name, source_files):
                    dependencies.append(import_name)
            
            modules.append(Module(
                name=module_name,
                description=f"Module from {source_file.path}",
                file_path=source_file.path,
                dependencies=dependencies
            ))
        
        # Build edges from module dependencies
        for module in modules:
            for dep in module.dependencies:
                if dep in nodes:
                    edges.append((module.name, dep))
        
        return DependencyGraph(nodes=nodes, edges=edges)
    
    def _is_external_import(self, import_name: str, source_files: List[SourceFile]) -> bool:
        """Check if an import is external (not part of the project)."""
        # Common external libraries
        external_libs = {
            'os', 'sys', 'json', 'ast', 're', 'pathlib', 'typing', 'collections',
            'datetime', 'time', 'math', 'random', 'itertools', 'functools',
            'unittest', 'pytest', 'numpy', 'pandas', 'requests', 'flask', 'django'
        }
        
        # Check if it's a standard library or common external package
        base_import = import_name.split('.')[0]
        if base_import in external_libs:
            return True
        
        # Check if it matches any source file in the project
        for source_file in source_files:
            module_name = source_file.path.replace('/', '.').replace('\\', '.').replace('.py', '')
            if module_name.startswith('.'):
                module_name = module_name[1:]
            
            if import_name.startswith(module_name):
                return False
        
        return True
    
    def _generate_project_overview(self, project_structure: ProjectStructure) -> str:
        """Generate a project overview using AI."""
        if not self.ai_client:
            return "Project overview generation requires AI client."
        
        # Prepare context about the project
        context = f"""
        Project Structure Analysis:
        - Root path: {project_structure.root_path}
        - Source files: {len(project_structure.source_files)}
        - Test files: {len(project_structure.test_files)}
        - Config files: {len(project_structure.config_files)}
        - Documentation files: {len(project_structure.documentation_files)}
        
        Key modules:
        """
        
        for source_file in project_structure.source_files[:10]:  # Limit to first 10
            context += f"- {source_file.path}: {len(source_file.functions)} functions, {len(source_file.classes)} classes\n"
        
        prompt = f"""
        Based on the following project structure analysis, generate a comprehensive project overview:
        
        {context}
        
        Please provide:
        1. A brief description of what this project appears to do
        2. The main components and their purposes
        3. The overall architecture style
        4. Key technologies and frameworks used
        
        Keep the overview concise but informative.
        """
        
        try:
            # Check fallback configuration
            from ..config import A3Config
            config = A3Config.load()
            use_fallbacks = config.use_fallback_models
            
            return self.ai_client.generate_with_retry(prompt, use_fallbacks=use_fallbacks)
        except Exception:
            return "Unable to generate project overview due to AI service error."
    
    def _generate_architecture_description(self, project_structure: ProjectStructure) -> str:
        """Generate architecture description using AI."""
        if not self.ai_client:
            return "Architecture description generation requires AI client."
        
        # Analyze the dependency graph
        graph_info = f"Dependency graph has {len(project_structure.dependency_graph.nodes)} modules with {len(project_structure.dependency_graph.edges)} dependencies."
        
        prompt = f"""
        Based on the project structure with {len(project_structure.source_files)} source files and the following dependency information:
        
        {graph_info}
        
        Generate a detailed architecture description that covers:
        1. Overall architectural pattern (MVC, layered, microservices, etc.)
        2. Module organization and separation of concerns
        3. Data flow and component interactions
        4. Key design decisions evident from the structure
        
        Focus on the structural aspects visible from the codebase organization.
        """
        
        try:
            # Check fallback configuration
            from ..config import A3Config
            config = A3Config.load()
            use_fallbacks = config.use_fallback_models
            
            return self.ai_client.generate_with_retry(prompt, use_fallbacks=use_fallbacks)
        except Exception:
            return "Unable to generate architecture description due to AI service error."
    
    def _generate_module_descriptions(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """Generate descriptions for each module."""
        descriptions = {}
        
        if not self.ai_client:
            return descriptions
        
        for source_file in project_structure.source_files:
            module_name = source_file.path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            prompt = f"""
            Analyze this Python module and provide a concise description:
            
            File: {source_file.path}
            Functions: {', '.join(source_file.functions[:10])}
            Classes: {', '.join(source_file.classes[:10])}
            Lines of code: {source_file.lines_of_code}
            
            Provide a 2-3 sentence description of what this module does and its role in the project.
            """
            
            try:
                # Check fallback configuration
                from ..config import A3Config
                config = A3Config.load()
                use_fallbacks = config.use_fallback_models
                
                descriptions[module_name] = self.ai_client.generate_with_retry(prompt, use_fallbacks=use_fallbacks)
            except Exception:
                descriptions[module_name] = f"Module at {source_file.path} with {len(source_file.functions)} functions and {len(source_file.classes)} classes."
        
        return descriptions
    
    def _generate_function_descriptions(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """Generate descriptions for key functions."""
        descriptions = {}
        
        if not self.ai_client:
            return descriptions
        
        # Focus on modules with the most functions
        sorted_files = sorted(project_structure.source_files, 
                            key=lambda f: len(f.functions), reverse=True)
        
        for source_file in sorted_files[:5]:  # Top 5 modules
            for func_name in source_file.functions[:3]:  # Top 3 functions per module
                key = f"{source_file.path}::{func_name}"
                descriptions[key] = f"Function {func_name} in {source_file.path}"
        
        return descriptions
    
    def _generate_dependency_analysis(self, project_structure: ProjectStructure) -> str:
        """Generate dependency analysis description."""
        graph = project_structure.dependency_graph
        
        analysis = f"""
        Dependency Analysis:
        - Total modules: {len(graph.nodes)}
        - Total dependencies: {len(graph.edges)}
        - Has circular dependencies: {'Yes' if graph.has_cycles() else 'No'}
        """
        
        if graph.has_cycles():
            analysis += "\n- Warning: Circular dependencies detected which may indicate design issues."
        
        # Add build order if no cycles
        if not graph.has_cycles():
            build_order = graph.topological_sort()
            analysis += f"\n- Recommended build order: {' -> '.join(build_order[:5])}{'...' if len(build_order) > 5 else ''}"
        
        return analysis
    
    def _generate_usage_examples(self, project_structure: ProjectStructure) -> List[str]:
        """Generate usage examples for the project."""
        examples = []
        
        # Look for main entry points
        for source_file in project_structure.source_files:
            if 'main' in source_file.path.lower() or '__main__' in source_file.content:
                examples.append(f"# Run the main module\npython {source_file.path}")
        
        # Look for setup.py or pyproject.toml
        for config_file in project_structure.config_files:
            if config_file.config_type == 'setup.py':
                examples.append("# Install the package\npip install -e .")
            elif config_file.config_type == 'pyproject.toml':
                examples.append("# Install with pip\npip install .")
        
        if not examples:
            examples.append("# Usage examples not automatically detected")
        
        return examples
    
    def _analyze_coding_conventions(self, project_structure: ProjectStructure) -> CodingConventions:
        """Analyze coding conventions used in the project."""
        conventions = CodingConventions()
        
        total_functions = 0
        functions_with_type_hints = 0
        line_lengths = []
        
        for source_file in project_structure.source_files:
            try:
                tree = ast.parse(source_file.content)
                
                # Analyze function definitions for type hints
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        
                        # Check for type hints
                        has_type_hints = (
                            node.returns is not None or
                            any(arg.annotation is not None for arg in node.args.args)
                        )
                        if has_type_hints:
                            functions_with_type_hints += 1
                
                # Analyze line lengths
                lines = source_file.content.split('\n')
                for line in lines:
                    if line.strip():  # Non-empty lines
                        line_lengths.append(len(line))
            
            except SyntaxError:
                continue
        
        # Calculate type hints usage
        if total_functions > 0:
            conventions.type_hints_usage = functions_with_type_hints / total_functions
        
        # Calculate average line length
        if line_lengths:
            avg_line_length = sum(line_lengths) / len(line_lengths)
            conventions.line_length = int(avg_line_length)
        
        return conventions
    
    def _identify_architectural_patterns(self, project_structure: ProjectStructure) -> List[str]:
        """Identify architectural patterns in the project."""
        patterns = []
        
        # Look for common directory structures
        paths = [f.path for f in project_structure.source_files]
        
        if any('models' in path for path in paths):
            patterns.append("Model-based architecture")
        
        if any('views' in path for path in paths) and any('controllers' in path for path in paths):
            patterns.append("MVC pattern")
        
        if any('services' in path for path in paths):
            patterns.append("Service layer pattern")
        
        if any('repositories' in path for path in paths):
            patterns.append("Repository pattern")
        
        if any('factories' in path for path in paths):
            patterns.append("Factory pattern")
        
        return patterns
    
    def _identify_design_patterns(self, project_structure: ProjectStructure) -> List[str]:
        """Identify design patterns in the code."""
        patterns = []
        
        # Look for common class naming patterns
        all_classes = []
        for source_file in project_structure.source_files:
            all_classes.extend(source_file.classes)
        
        class_names = [name.lower() for name in all_classes]
        
        if any('factory' in name for name in class_names):
            patterns.append("Factory pattern")
        
        if any('builder' in name for name in class_names):
            patterns.append("Builder pattern")
        
        if any('observer' in name for name in class_names):
            patterns.append("Observer pattern")
        
        if any('singleton' in name for name in class_names):
            patterns.append("Singleton pattern")
        
        if any('adapter' in name for name in class_names):
            patterns.append("Adapter pattern")
        
        return patterns
    
    def _find_common_utilities(self, project_structure: ProjectStructure) -> List[str]:
        """Find common utility functions and modules."""
        utilities = []
        
        for source_file in project_structure.source_files:
            if 'util' in source_file.path.lower() or 'helper' in source_file.path.lower():
                utilities.extend(source_file.functions)
        
        return utilities[:10]  # Limit to first 10
    
    def _analyze_test_patterns(self, project_structure: ProjectStructure) -> List[str]:
        """Analyze testing patterns used in the project."""
        patterns = []
        
        if not project_structure.test_files:
            return ["No tests found"]
        
        # Analyze test frameworks
        frameworks = set()
        for test_file in project_structure.test_files:
            frameworks.add(test_file.test_framework)
        
        patterns.extend([f"{fw} testing" for fw in frameworks])
        
        # Analyze test organization
        test_paths = [f.path for f in project_structure.test_files]
        if any('unit' in path for path in test_paths):
            patterns.append("Unit testing")
        
        if any('integration' in path for path in test_paths):
            patterns.append("Integration testing")
        
        if any('e2e' in path or 'end_to_end' in path for path in test_paths):
            patterns.append("End-to-end testing")
        
        return patterns
    
    def _analyze_modification_intent(self, user_prompt: str, project_structure: ProjectStructure) -> Dict[str, Any]:
        """Analyze user prompt to understand modification intent."""
        # This is a simplified implementation
        # In a real implementation, this would use NLP or AI to understand intent
        
        intent = {
            'type': 'unknown',
            'scope': 'unknown',
            'keywords': user_prompt.lower().split()
        }
        
        # Simple keyword-based analysis
        if any(word in user_prompt.lower() for word in ['add', 'create', 'new']):
            intent['type'] = 'addition'
        elif any(word in user_prompt.lower() for word in ['remove', 'delete', 'drop']):
            intent['type'] = 'removal'
        elif any(word in user_prompt.lower() for word in ['modify', 'change', 'update', 'fix']):
            intent['type'] = 'modification'
        elif any(word in user_prompt.lower() for word in ['refactor', 'restructure']):
            intent['type'] = 'refactoring'
        
        return intent
    
    def _identify_target_files(self, modification_intent: Dict[str, Any], 
                              project_structure: ProjectStructure) -> List[str]:
        """Identify which files should be targeted for modification."""
        target_files = []
        
        # Simple heuristic based on keywords
        keywords = modification_intent.get('keywords', [])
        
        for source_file in project_structure.source_files:
            # Check if any keywords match file path or function names
            if any(keyword in source_file.path.lower() for keyword in keywords):
                target_files.append(source_file.path)
            elif any(keyword in func.lower() for func in source_file.functions for keyword in keywords):
                target_files.append(source_file.path)
        
        # If no specific targets found, suggest main modules
        if not target_files:
            # Sort by complexity/size and suggest top candidates
            sorted_files = sorted(project_structure.source_files, 
                                key=lambda f: len(f.functions) + len(f.classes), 
                                reverse=True)
            target_files = [f.path for f in sorted_files[:3]]
        
        return target_files
    
    def _plan_specific_changes(self, modification_intent: Dict[str, Any], 
                              target_files: List[str], 
                              project_structure: ProjectStructure) -> List[Dict[str, str]]:
        """Plan specific changes for the target files."""
        changes = []
        
        for file_path in target_files:
            change = {
                'file_path': file_path,
                'change_type': modification_intent.get('type', 'modification'),
                'description': f"Planned {modification_intent.get('type', 'modification')} for {file_path}",
                'details': 'Specific implementation details would be generated by AI'
            }
            changes.append(change)
        
        return changes
    
    def _estimate_modification_impact(self, planned_changes: List[Dict[str, str]], 
                                    project_structure: ProjectStructure) -> str:
        """Estimate the impact of planned modifications."""
        if len(planned_changes) <= 1:
            return "low"
        elif len(planned_changes) <= 3:
            return "medium"
        else:
            return "high"
    
    def _identify_affected_dependencies(self, target_files: List[str], 
                                       project_structure: ProjectStructure) -> List[str]:
        """Identify dependencies that might be affected by modifications."""
        affected = []
        
        # Convert file paths to module names
        target_modules = []
        for file_path in target_files:
            module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            if module_name.startswith('.'):
                module_name = module_name[1:]
            target_modules.append(module_name)
        
        # Find modules that depend on target modules
        graph = project_structure.dependency_graph
        for target_module in target_modules:
            for from_module, to_module in graph.edges:
                if to_module == target_module and from_module not in affected:
                    affected.append(from_module)
        
        return affected
    
    def _create_backup(self, target_files: List[str]) -> str:
        """Create backup of target files."""
        # This would create actual backups in a real implementation
        return f"backup_location_for_{len(target_files)}_files"
    
    def get_data_handling_templates(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """
        Generate data handling function templates based on discovered data sources.
        
        Args:
            project_structure: Analyzed project structure
            
        Returns:
            Dict mapping template names to template code
        """
        if not project_structure.data_source_analysis:
            return {}
        
        try:
            data_source_manager = DataSourceManager(project_structure.root_path)
            return data_source_manager.generate_data_handling_templates(
                project_structure.data_source_analysis
            )
        except Exception as e:
            print(f"Warning: Failed to generate data handling templates: {e}")
            return {}

    def _scan_data_sources(self, project_root: Path) -> Optional[DataSourceAnalysis]:
        """
        Scan project for data source files and analyze them.
        
        Args:
            project_root: Path to the project root directory
            
        Returns:
            DataSourceAnalysis or None if no data sources found
        """
        try:
            data_source_manager = DataSourceManager(str(project_root))
            analysis = data_source_manager.scan_project_data_sources()
            
            # Only return analysis if we found data sources
            if analysis.unified_metadata:
                return analysis
            else:
                return None
                
        except Exception as e:
            # Log the error but don't fail the entire project analysis
            print(f"Warning: Data source analysis failed: {e}")
            return None

    def _analyze_database_schema(self, connection_string: Optional[str]) -> Optional[DatabaseSchema]:
        """
        Analyze database schema if connection string is provided.
        
        Args:
            connection_string: Optional PostgreSQL connection string
            
        Returns:
            DatabaseSchema or None if no connection string provided or analysis fails
        """
        if not connection_string:
            return None
        
        try:
            # Connect to database
            connection = self.database_analyzer.connect_to_database(connection_string)
            
            # Analyze schema
            schema = self.database_analyzer.analyze_database_schema(connection)
            
            return schema
            
        except Exception as e:
            # Log the error but don't fail the entire project analysis
            print(f"Warning: Database analysis failed: {e}")
            return None

    def _generate_database_documentation(self, project_structure: ProjectStructure) -> str:
        """
        Generate database documentation from analyzed schema.
        
        Args:
            project_structure: Analyzed project structure
            
        Returns:
            String containing database documentation
        """
        if not project_structure.database_analysis:
            return ""
        
        schema = project_structure.database_analysis
        
        # Generate basic documentation without AI
        doc_lines = []
        doc_lines.append("# Database Schema")
        doc_lines.append("")
        doc_lines.append(f"**Database:** {schema.database_name}")
        doc_lines.append(f"**Host:** {schema.host}:{schema.port}")
        doc_lines.append(f"**Version:** {schema.version}")
        doc_lines.append("")
        
        if schema.tables:
            doc_lines.append("## Tables")
            doc_lines.append("")
            
            for table in schema.tables:
                doc_lines.append(f"### {table.name}")
                if table.description:
                    doc_lines.append(f"*{table.description}*")
                doc_lines.append("")
                
                if table.columns:
                    doc_lines.append("| Column | Type | Nullable | Default | Description |")
                    doc_lines.append("|--------|------|----------|---------|-------------|")
                    
                    for column in table.columns:
                        nullable = "Yes" if column.is_nullable else "No"
                        default = column.default_value or ""
                        description = column.description or ""
                        doc_lines.append(f"| {column.name} | {column.data_type} | {nullable} | {default} | {description} |")
                    
                    doc_lines.append("")
        
        if schema.relationships:
            doc_lines.append("## Relationships")
            doc_lines.append("")
            
            for rel in schema.relationships:
                from_cols = ", ".join(rel.from_columns)
                to_cols = ", ".join(rel.to_columns)
                doc_lines.append(f"- **{rel.from_table}.{from_cols}** → **{rel.to_table}.{to_cols}** ({rel.relationship_type})")
            
            doc_lines.append("")
        
        return "\n".join(doc_lines)

    def _apply_single_change(self, change: Dict[str, str]) -> bool:
        """Apply a single change to a file."""
        # This would apply actual changes in a real implementation
        # For now, just return success
        return True
    
    def _check_change_consistency(self, change: Dict[str, str], 
                                 existing_patterns: CodePatterns) -> List[str]:
        """Check if a change is consistent with existing patterns."""
        issues = []
        
        # This would perform actual consistency checks
        # For now, return empty list
        
        return issues
    
    def _check_naming_consistency(self, modifications: ModificationPlan, 
                                 conventions: CodingConventions) -> List[str]:
        """Check naming consistency with existing conventions."""
        issues = []
        
        # This would check naming patterns
        # For now, return empty list
        
        return issues
    
    def _check_import_consistency(self, modifications: ModificationPlan, 
                                 conventions: CodingConventions) -> List[str]:
        """Check import style consistency."""
        warnings = []
        
        # This would check import patterns
        # For now, return empty list
        
        return warnings