# AI Project Builder (A3)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A3 is a Python package that automates the creation of modular coding projects through AI-powered planning, function definition, and code generation. Transform high-level project objectives into fully implemented, tested, and integrated Python projects.

## Features

- **Automated Project Planning**: Generate comprehensive project plans from simple objectives
- **Enhanced Function-Level Dependencies**: Track dependencies at the function level for optimal implementation ordering
- **AI-Powered Code Generation**: Automatically implement functions with proper type hints and documentation
- **Intelligent Dependency Management**: Handle imports and module connections with enhanced analysis
- **Parallel Implementation Support**: Identify functions that can be implemented simultaneously
- **Critical Path Analysis**: Optimize project timelines with dependency-aware scheduling
- **Code Execution & Testing**: Execute generated code and run tests for verification
- **Debug Analysis**: Comprehensive debugging with AI-powered code revision
- **Project Analysis**: Analyze existing codebases and generate documentation
- **Performance Optimization**: Up to 50% faster implementation through intelligent parallelization
- **Single-Responsibility Enforcement**: Ensure functions follow best practices
- **State Management**: Resume interrupted projects and track progress

## Quick Start

### Installation

```bash
pip install a3
```

### Set up your API key

Get your API key from [OpenRouter](https://openrouter.ai/) and set it as an environment variable:

```bash
export A3_API_KEY="your-api-key-here"
```

### Create your first project

```python
from a3 import A3

# Initialize A3
a3 = A3()
a3.set_api_key("your-api-key")

# Create a complete project from a simple objective
plan = a3.plan("A web scraper for news articles with sentiment analysis")
specs = a3.generate_specs()
implementation = a3.implement()
integration = a3.integrate()

print("Project created successfully!")
```

### Using the CLI

```bash
# Create a new project
a3 create "A REST API for user management" --path ./user-api

# Check project status
a3 status --path ./user-api

# Resume an interrupted project
a3 resume --path ./user-api

# Analyze an existing project
a3 analyze ./existing-project --generate-docs --dependency-graph

# Debug and test project code
a3 debug ./my-project --execute-tests --validate-imports
```

## Core Concepts

### Project Phases

A3 follows a structured workflow with distinct phases:

1. **Planning**: Generate project structure and module breakdown
2. **Specification**: Create detailed function signatures and documentation
3. **Implementation**: Generate actual code for all functions
4. **Testing**: Execute code and run tests for verification
5. **Integration**: Handle imports and module connections
6. **Completion**: Finalize the project

### Single-Responsibility Principle

A3 enforces the single-responsibility principle by:
- Analyzing function complexity during planning
- Breaking down complex functions into smaller, focused units
- Validating implementations against single-responsibility criteria
- Providing refactoring suggestions when needed

### State Management

All project state is maintained in a `.A3` directory within your project:
- Project plans and progress tracking
- Function specifications and implementation status
- Checkpoints for recovery and resumption
- Debug information and error logs

## API Reference

### Core API

#### A3 Class

The main interface for AI Project Builder.

```python
class A3:
    def __init__(self, project_path: str = ".")
    def set_api_key(self, api_key: str) -> None
    def plan(self, objective: str, project_path: str = ".") -> ProjectPlan
    def generate_specs(self, project_path: str = ".") -> SpecificationSet
    def implement(self, project_path: str = ".") -> ImplementationResult
    def integrate(self, project_path: str = ".") -> IntegrationResult
    def status(self, project_path: str = ".") -> ProjectStatus
    def resume(self, project_path: str = ".") -> ProjectResult
```

#### Key Methods

**`plan(objective: str) -> ProjectPlan`**
Generate a comprehensive project plan from a high-level objective.

```python
plan = a3.plan("A machine learning pipeline for image classification")
print(f"Generated {len(plan.modules)} modules with {plan.estimated_functions} functions")
```

**`generate_specs() -> SpecificationSet`**
Create detailed function specifications with type hints and documentation.

```python
specs = a3.generate_specs()
print(f"Generated specifications for {len(specs.functions)} functions")
```

**`implement() -> ImplementationResult`**
Implement all functions based on their specifications.

```python
result = a3.implement()
print(f"Implemented {len(result.implemented_functions)} functions")
print(f"Success rate: {result.success_rate:.2%}")
```

**`integrate() -> IntegrationResult`**
Handle imports and module connections automatically.

```python
result = a3.integrate()
if result.success:
    print("Integration completed successfully")
```

### Enhanced Dependency System

A3 now includes an advanced function-level dependency system that provides significant performance improvements:

```python
# Analyze project dependencies
analysis = a3.analyze_dependencies()
print(f"Functions can be implemented in {len(analysis['parallel_implementation_groups'])} parallel batches")

# Get implementation strategy
strategy = a3.get_implementation_strategy()
print(f"Critical path: {' → '.join(strategy['critical_path'])}")
print(f"Speed improvement: {strategy['estimated_implementation_time']['parallelization_benefit']:.1f}%")

# Access enhanced dependency graph
enhanced_graph = a3.get_enhanced_dependency_graph()
complexity = enhanced_graph.analyze_dependency_complexity()
print(f"Dependency density: {complexity['dependency_density']:.2f}")
```

#### Key Benefits:
- **Up to 50% faster implementation** through intelligent parallelization
- **Function-level dependency tracking** with confidence scoring
- **Optimal implementation ordering** based on actual dependencies
- **Parallel implementation groups** for concurrent development
- **Critical path analysis** for project planning
- **Dependency complexity metrics** for project assessment

### Enhanced Features

#### Code Execution and Testing

A3 can execute generated code and run tests for verification:

```python
from a3.engines.code_executor import CodeExecutor
from a3.managers.filesystem import FileSystemManager

file_manager = FileSystemManager("./my-project")
executor = CodeExecutor("./my-project", file_manager)

# Execute a specific function
result = executor.execute_function(function_spec, "module.py")
if result.success:
    print(f"Function executed successfully: {result.output}")

# Run all tests
test_result = executor.run_tests(["test_module.py"])
print(f"Tests: {test_result.passed_tests}/{test_result.total_tests} passed")
```

#### Debug Analysis

Comprehensive debugging with AI-powered code revision:

```python
from a3.engines.debug_analyzer import DebugAnalyzer
from a3.clients.openrouter import OpenRouterClient

client = OpenRouterClient("your-api-key")
debug_analyzer = DebugAnalyzer(client)

# Analyze an exception
try:
    # Some code that fails
    pass
except Exception as e:
    analysis = debug_analyzer.analyze_traceback(e)
    print(f"Root cause: {analysis.root_cause}")
    
    # Get AI-powered revision suggestions
    context = debug_analyzer.generate_debug_context(e, function_spec)
    revision = debug_analyzer.suggest_code_revision(context)
    print(f"Suggested fix: {revision.revised_code}")
```

#### Project Analysis

Analyze existing codebases and generate documentation:

```python
from a3.engines.project_analyzer import ProjectAnalyzer
from a3.managers.dependency import DependencyAnalyzer

dependency_analyzer = DependencyAnalyzer()
analyzer = ProjectAnalyzer(client, dependency_analyzer)

# Scan project structure
structure = analyzer.scan_project_folder("./existing-project")
print(f"Found {len(structure.source_files)} source files")

# Generate documentation
docs = analyzer.generate_project_documentation(structure)
with open("PROJECT_DOCS.md", "w") as f:
    f.write(docs.content)

# Build dependency graph
graph = analyzer.build_dependency_graph(structure)
print(f"Dependency graph: {len(graph.nodes)} modules, {len(graph.edges)} dependencies")
```

## Data Models

### Core Models

**ProjectPlan**
```python
@dataclass
class ProjectPlan:
    objective: str
    modules: List[Module]
    dependency_graph: DependencyGraph
    estimated_functions: int
    created_at: datetime
```

**Module**
```python
@dataclass
class Module:
    name: str
    description: str
    file_path: str
    dependencies: List[str]
    functions: List[FunctionSpec]
```

**FunctionSpec**
```python
@dataclass
class FunctionSpec:
    name: str
    module: str
    docstring: str
    arguments: List[Argument]
    return_type: str
    implementation_status: ImplementationStatus
```

### Enhanced Models

**ExecutionResult**
```python
@dataclass
class ExecutionResult:
    success: bool
    output: Optional[str]
    error: Optional[Exception]
    execution_time: float
    memory_usage: Optional[int]
```

**DebugContext**
```python
@dataclass
class DebugContext:
    function_spec: FunctionSpec
    traceback_analysis: TracebackAnalysis
    function_inspection: FunctionInspection
    parsed_docstring: Optional[ParsedDocstring]
    related_code: List[str]
```

**ProjectStructure**
```python
@dataclass
class ProjectStructure:
    root_path: str
    source_files: List[SourceFile]
    test_files: List[TestFile]
    config_files: List[ConfigFile]
    documentation_files: List[DocumentationFile]
    dependency_graph: DependencyGraph
```

## CLI Reference

### Commands

**Create a new project**
```bash
a3 create "Project description" [options]

Options:
  --path PATH        Project directory (default: current directory)
  --plan-only        Only generate the project plan
  --api-key KEY      OpenRouter API key (overrides environment variable)
```

**Check project status**
```bash
a3 status [options]

Options:
  --path PATH        Project directory (default: current directory)
```

**Resume interrupted project**
```bash
a3 resume [options]

Options:
  --path PATH        Project directory (default: current directory)
  --api-key KEY      OpenRouter API key
```

**Analyze existing project**
```bash
a3 analyze PATH [options]

Options:
  --generate-docs    Generate project documentation
  --dependency-graph Create dependency graph visualization
  --code-patterns    Analyze code patterns and conventions
  --api-key KEY      OpenRouter API key
```

**Debug and test project**
```bash
a3 debug PATH [options]

Options:
  --execute-tests    Execute all test files
  --validate-imports Validate all import statements
  --api-key KEY      OpenRouter API key
```

### Standalone Commands

**Project Analysis**
```bash
a3-analyze ./my-project --generate-docs --dependency-graph
```

**Project Debugging**
```bash
a3-debug ./my-project --execute-tests --validate-imports
```

## Configuration

### Environment Variables

- `A3_API_KEY` or `OPENROUTER_API_KEY`: Your OpenRouter API key
- `A3_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `A3_MAX_RETRIES`: Maximum API retry attempts (default: 3)

### Project Configuration

Create a `.a3config.json` file in your project root:

```json
{
  "model": "anthropic/claude-3-sonnet",
  "max_functions_per_module": 10,
  "enforce_single_responsibility": true,
  "generate_tests": true,
  "code_style": "black",
  "type_checking": "strict"
}
```

## Examples

### Example 1: Web Scraper

```python
from a3 import A3

a3 = A3()
a3.set_api_key("your-api-key")

# Create a web scraper project
plan = a3.plan("""
A web scraper that:
- Scrapes news articles from multiple sources
- Extracts title, content, and metadata
- Performs sentiment analysis on articles
- Stores results in a database
- Provides a REST API for querying articles
""")

# Generate and implement
specs = a3.generate_specs()
implementation = a3.implement()
integration = a3.integrate()

print("Web scraper project created!")
```

### Example 2: Machine Learning Pipeline

```python
# Create an ML pipeline
plan = a3.plan("""
A machine learning pipeline for image classification:
- Data loading and preprocessing
- Feature extraction using CNN
- Model training with cross-validation
- Model evaluation and metrics
- Prediction API with confidence scores
""")

# The system will create modules like:
# - data_loader.py
# - preprocessor.py
# - feature_extractor.py
# - model_trainer.py
# - evaluator.py
# - prediction_api.py
```

### Example 3: Analyzing Existing Project

```python
from a3.engines.project_analyzer import ProjectAnalyzer
from a3.clients.openrouter import OpenRouterClient
from a3.managers.dependency import DependencyAnalyzer

client = OpenRouterClient("your-api-key")
dependency_analyzer = DependencyAnalyzer()
analyzer = ProjectAnalyzer(client, dependency_analyzer)

# Analyze existing codebase
structure = analyzer.scan_project_folder("./legacy-project")

# Generate comprehensive documentation
docs = analyzer.generate_project_documentation(structure)

# Suggest modifications
modifications = analyzer.suggest_modifications(
    "Add logging and error handling to all functions",
    structure
)
```

## Best Practices

### Project Objectives

Write clear, specific objectives:

**Good:**
```python
a3.plan("A REST API for user management with authentication, CRUD operations, and role-based access control")
```

**Better:**
```python
a3.plan("""
A user management system with:
- JWT-based authentication
- CRUD operations for users
- Role-based access control (admin, user, guest)
- Password hashing and validation
- Email verification
- Rate limiting
- Comprehensive logging
""")
```

### Error Handling

Always handle A3 exceptions:

```python
from a3 import A3, A3Error, ConfigurationError, OperationError

try:
    a3 = A3()
    a3.set_api_key("your-key")
    plan = a3.plan("Your objective")
except ConfigurationError as e:
    print(f"Configuration issue: {e.get_user_message()}")
except OperationError as e:
    print(f"Operation failed: {e.get_user_message()}")
except A3Error as e:
    print(f"A3 error: {e.get_user_message()}")
```

### Project Structure

A3 creates well-organized project structures:

```
my-project/
├── .A3/                    # A3 state and progress
│   ├── project_plan.json
│   ├── progress.json
│   └── checkpoints/
├── src/                    # Source code
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── tests/                  # Test files
│   ├── test_module1.py
│   └── test_module2.py
├── requirements.txt        # Dependencies
└── README.md              # Project documentation
```

## Troubleshooting

### Common Issues

**API Key Issues**
```
Error: Invalid API key provided
```
- Verify your API key at https://openrouter.ai/keys
- Check environment variable: `echo $A3_API_KEY`
- Ensure key has sufficient credits

**Project State Issues**
```
Error: Project state is corrupted
```
- Check `.A3` directory permissions
- Restore from checkpoint: `a3 resume --path ./project`
- Start fresh if needed: remove `.A3` directory

**Import Errors**
```
Error: Module import failed
```
- Run: `a3 debug ./project --validate-imports`
- Check dependency graph for circular imports
- Verify all required modules are implemented

**Code Execution Failures**
```
Error: Function execution failed
```
- Run: `a3 debug ./project --execute-tests`
- Check function implementations for syntax errors
- Review debug analysis for specific issues

### Debug Workflow

1. **Check Status**
   ```bash
   a3 status --path ./project
   ```

2. **Validate Imports**
   ```bash
   a3 debug ./project --validate-imports
   ```

3. **Execute Tests**
   ```bash
   a3 debug ./project --execute-tests
   ```

4. **Analyze Issues**
   ```python
   from a3.engines.debug_analyzer import DebugAnalyzer
   # Use debug analyzer for detailed error analysis
   ```

5. **Resume or Restart**
   ```bash
   a3 resume --path ./project
   # or start fresh if needed
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=a3 --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.