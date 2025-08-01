#!/usr/bin/env python3
"""
Command Line Interface for AI Project Builder (A3).

This module provides CLI commands for project creation, analysis, and debugging.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional

from .core.api import A3, A3Error
from .core.models import ProjectPhase
from .config import A3Config


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_api_key() -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv('A3_API_KEY') or os.getenv('OPENROUTER_API_KEY')


def resolve_project_path(path: str, workspace: Optional[str] = None, config: Optional[A3Config] = None) -> str:
    """Resolve project path with workspace support."""
    # Priority: explicit workspace > config workspace > no workspace
    effective_workspace = workspace or (config.default_workspace if config else None)
    
    if effective_workspace and not os.path.isabs(path):
        return str(Path(effective_workspace) / path)
    return path


def handle_error(error: Exception) -> None:
    """Handle and display errors in a user-friendly way."""
    if isinstance(error, A3Error):
        print(f"\n{error.get_user_message()}", file=sys.stderr)
    else:
        print(f"\nUnexpected error: {error}", file=sys.stderr)
        print("Please report this issue if it persists.", file=sys.stderr)
    sys.exit(1)


def create_project_command(args) -> None:
    """Handle the create project command."""
    try:
        # Resolve project path with workspace support
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        
        # Ensure target directory exists
        target_path = Path(project_path).resolve()
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {target_path}")
        
        # Initialize A3 with resolved path
        a3 = A3(str(target_path))
        
        # Set API key (priority: CLI arg > config > environment)
        api_key = args.api_key or args.config.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required. Set A3_API_KEY environment variable, use --api-key option, or configure with 'a3 config set api_key YOUR_KEY'.")
            print("Get your API key from: https://openrouter.ai/")
            sys.exit(1)
        
        a3.set_api_key(api_key)
        
        print(f"Creating project in: {Path(project_path).resolve()}")
        print(f"Objective: {args.objective}")
        if hasattr(args, 'template') and args.template:
            print(f"Using template: {args.template}")
        print()
        
        # Execute the full pipeline
        if args.plan_only:
            print("Generating project plan...")
            plan = a3.plan(args.objective, project_path)
            print(f"✓ Plan generated with {len(plan.modules)} modules and {plan.estimated_functions} functions")
        else:
            print("Generating project plan...")
            plan = a3.plan(args.objective, project_path)
            print(f"✓ Plan generated with {len(plan.modules)} modules and {plan.estimated_functions} functions")
            
            print("Generating function specifications...")
            specs = a3.generate_specs(project_path)
            print(f"✓ Generated specifications for {len(specs.functions)} functions")
            
            print("Implementing functions...")
            impl_result = a3.implement(project_path)
            print(f"✓ Implemented {len(impl_result.implemented_functions)} functions")
            if impl_result.failed_functions:
                print(f"⚠ {len(impl_result.failed_functions)} functions failed to implement")
            
            print("Integrating modules...")
            integration_result = a3.integrate(project_path)
            if integration_result.success:
                print("✓ Project integration completed successfully")
            else:
                print("⚠ Integration completed with some issues")
                for error in integration_result.import_errors:
                    print(f"  - {error}")
        
        print(f"\nProject created successfully in: {Path(project_path).resolve()}")
        
    except Exception as e:
        handle_error(e)


def init_project_command(args) -> None:
    """Handle the init project command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        target_path = Path(project_path).resolve()
        
        # Check if directory exists
        if not target_path.exists():
            print(f"Error: Directory does not exist: {target_path}")
            print("Use 'a3 create' to create a new project, or create the directory first.")
            sys.exit(1)
        
        # Check if A3 is already initialized
        a3_dir = target_path / '.A3'
        if a3_dir.exists() and not args.force:
            print(f"A3 is already initialized in: {target_path}")
            print("Use --force to reinitialize, or 'a3 status' to check current state.")
            sys.exit(1)
        
        # Initialize A3
        a3 = A3(project_path)
        print(f"✓ A3 initialized in: {target_path}")
        print("You can now use 'a3 create' to start building a project.")
        
    except Exception as e:
        handle_error(e)


def status_command(args) -> None:
    """Handle the status command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        a3 = A3(project_path)
        status = a3.status(project_path)
        
        print(f"Project Status: {Path(project_path).resolve()}")
        print(f"Active: {'Yes' if status.is_active else 'No'}")
        
        if status.progress:
            print(f"Current Phase: {status.progress.current_phase.value.title()}")
            print(f"Progress: {status.progress.implemented_functions}/{status.progress.total_functions} functions")
            if status.progress.failed_functions:
                print(f"Failed Functions: {len(status.progress.failed_functions)}")
        
        if status.errors:
            print("Errors:")
            for error in status.errors:
                print(f"  - {error}")
        
        if status.next_action:
            print(f"Next Action: {status.next_action}")
        
        if status.can_resume:
            print("\nProject can be resumed with: a3 resume")
        
    except Exception as e:
        handle_error(e)


def resume_command(args) -> None:
    """Handle the resume command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        a3 = A3(project_path)
        
        # Set API key (priority: CLI arg > config > environment)
        api_key = args.api_key or args.config.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required. Set A3_API_KEY environment variable, use --api-key option, or configure with 'a3 config set api_key YOUR_KEY'.")
            sys.exit(1)
        
        a3.set_api_key(api_key)
        
        print(f"Resuming project in: {Path(project_path).resolve()}")
        
        result = a3.resume(project_path)
        
        if result.success:
            print("✓ Project resumed and completed successfully")
        else:
            print(f"⚠ Project resumption completed with issues: {result.message}")
            if result.errors:
                for error in result.errors:
                    print(f"  - {error}")
        
    except Exception as e:
        handle_error(e)


def analyze_project_command(args) -> None:
    """Handle the analyze project command."""
    try:
        # Import project analyzer
        from .engines.project_analyzer import ProjectAnalyzer
        from .clients.openrouter import OpenRouterClient
        from .managers.dependency import DependencyAnalyzer
        
        # Set API key
        api_key = args.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required for project analysis. Set A3_API_KEY environment variable or use --api-key option.")
            sys.exit(1)
        
        # Initialize components
        client = OpenRouterClient(api_key)
        dependency_analyzer = DependencyAnalyzer()
        analyzer = ProjectAnalyzer(client, dependency_analyzer)
        
        print(f"Analyzing project: {Path(args.path).resolve()}")
        
        # Scan project structure
        project_structure = analyzer.scan_project_folder(args.path)
        print(f"✓ Found {len(project_structure.source_files)} source files")
        
        # Generate documentation if requested
        if args.generate_docs:
            print("Generating project documentation...")
            documentation = analyzer.generate_project_documentation(project_structure)
            
            # Save documentation
            docs_path = Path(args.path) / "PROJECT_ANALYSIS.md"
            with open(docs_path, 'w', encoding='utf-8') as f:
                f.write(documentation.content)
            print(f"✓ Documentation saved to: {docs_path}")
        
        # Build dependency graph if requested
        if args.dependency_graph:
            print("Building dependency graph...")
            dep_graph = analyzer.build_dependency_graph(project_structure)
            print(f"✓ Dependency graph created with {len(dep_graph.nodes)} modules")
            
            # Save dependency graph visualization
            graph_path = Path(args.path) / "dependency_graph.txt"
            with open(graph_path, 'w', encoding='utf-8') as f:
                f.write("Dependency Graph:\n")
                f.write("================\n\n")
                for node in dep_graph.nodes:
                    deps = dep_graph.get_dependencies(node)
                    f.write(f"{node}:\n")
                    if deps:
                        for dep in deps:
                            f.write(f"  -> {dep}\n")
                    else:
                        f.write("  (no dependencies)\n")
                    f.write("\n")
            print(f"✓ Dependency graph saved to: {graph_path}")
        
        # Analyze code patterns if requested
        if args.code_patterns:
            print("Analyzing code patterns...")
            patterns = analyzer.analyze_code_patterns(project_structure)
            
            patterns_path = Path(args.path) / "code_patterns.txt"
            with open(patterns_path, 'w', encoding='utf-8') as f:
                f.write("Code Patterns Analysis:\n")
                f.write("======================\n\n")
                f.write(f"Architectural Patterns: {', '.join(patterns.architectural_patterns)}\n")
                f.write(f"Design Patterns: {', '.join(patterns.design_patterns)}\n")
                f.write(f"Common Utilities: {', '.join(patterns.common_utilities)}\n")
                f.write(f"Test Patterns: {', '.join(patterns.test_patterns)}\n")
            print(f"✓ Code patterns analysis saved to: {patterns_path}")
        
        print("\nProject analysis completed successfully!")
        
    except Exception as e:
        handle_error(e)


def debug_project_command(args) -> None:
    """Handle the debug project command."""
    try:
        # Import debug analyzer
        from .engines.debug_analyzer import DebugAnalyzer
        from .engines.code_executor import CodeExecutor
        from .managers.filesystem import FileSystemManager
        from .clients.openrouter import OpenRouterClient
        
        # Set API key
        api_key = args.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required for debugging. Set A3_API_KEY environment variable or use --api-key option.")
            sys.exit(1)
        
        # Initialize components
        client = OpenRouterClient(api_key)
        file_manager = FileSystemManager(args.path)
        executor = CodeExecutor(args.path, file_manager)
        debug_analyzer = DebugAnalyzer(client)
        
        print(f"Debugging project: {Path(args.path).resolve()}")
        
        if args.execute_tests:
            print("Executing tests...")
            # Find test files
            test_files = []
            for root, dirs, files in os.walk(args.path):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))
            
            if test_files:
                test_result = executor.run_tests(test_files)
                print(f"✓ Tests executed: {test_result.passed_tests}/{test_result.total_tests} passed")
                
                if test_result.failed_tests > 0:
                    print("Failed tests:")
                    for detail in test_result.test_details:
                        if not detail.passed:
                            print(f"  - {detail.name}: {detail.error}")
            else:
                print("No test files found")
        
        if args.validate_imports:
            print("Validating imports...")
            # Find Python files
            python_files = []
            for root, dirs, files in os.walk(args.path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('test_'):
                        python_files.append(os.path.join(root, file))
            
            import_errors = []
            for py_file in python_files:
                try:
                    result = executor.validate_imports(py_file)
                    if not result.valid:
                        import_errors.extend(result.errors)
                except Exception as e:
                    import_errors.append(f"{py_file}: {e}")
            
            if import_errors:
                print("Import validation errors:")
                for error in import_errors:
                    print(f"  - {error}")
            else:
                print("✓ All imports are valid")
        
        print("\nDebugging completed!")
        
    except Exception as e:
        handle_error(e)


def config_show_command(args) -> None:
    """Handle the config show command."""
    try:
        config = A3Config.load()
        
        print("A3 Configuration:")
        print("=================")
        print(f"API Key: {'Set' if config.api_key else 'Not set'}")
        print(f"Model: {config.model}")
        print(f"Max Retries: {config.max_retries}")
        print(f"Default Workspace: {config.default_workspace or 'Not set'}")
        print(f"Auto Install Dependencies: {config.auto_install_deps}")
        print(f"Generate Tests: {config.generate_tests}")
        print(f"Code Style: {config.code_style}")
        print(f"Line Length: {config.line_length}")
        print(f"Type Checking: {config.type_checking}")
        print(f"Enforce Single Responsibility: {config.enforce_single_responsibility}")
        print(f"Max Functions Per Module: {config.max_functions_per_module}")
        
    except Exception as e:
        handle_error(e)


def config_set_command(args) -> None:
    """Handle the config set command."""
    try:
        config = A3Config.load()
        
        # Validate key
        if not hasattr(config, args.key):
            print(f"Error: Unknown configuration key '{args.key}'")
            print("Available keys: api_key, model, max_retries, default_workspace, auto_install_deps, generate_tests, code_style, line_length, type_checking, enforce_single_responsibility, max_functions_per_module")
            sys.exit(1)
        
        # Convert value to appropriate type
        current_value = getattr(config, args.key)
        if isinstance(current_value, bool):
            value = args.value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current_value, int):
            try:
                value = int(args.value)
            except ValueError:
                print(f"Error: '{args.key}' requires an integer value")
                sys.exit(1)
        else:
            value = args.value
        
        # Set the value
        setattr(config, args.key, value)
        
        # Save configuration
        if args.global_config:
            config_path = Path.home() / '.a3config.json'
        else:
            config_path = Path.cwd() / '.a3config.json'
        
        config.save(str(config_path))
        print(f"✓ Set {args.key} = {value}")
        print(f"Configuration saved to: {config_path}")
        
    except Exception as e:
        handle_error(e)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Project Builder (A3) - Automated project creation through AI-powered planning and code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  a3 create "A web scraper for news articles" --path ./news-scraper
  a3 status --path ./my-project
  a3 resume --path ./my-project
  a3 analyze ./existing-project --generate-docs --dependency-graph
  a3 debug ./my-project --execute-tests --validate-imports

Environment Variables:
  A3_API_KEY or OPENROUTER_API_KEY: Your OpenRouter API key
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--api-key', help='OpenRouter API key (overrides environment variable)')
    parser.add_argument('--workspace', help='Set default workspace directory for all operations')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('objective', help='High-level description of the project')
    create_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    create_parser.add_argument('--plan-only', action='store_true', help='Only generate the project plan')
    create_parser.add_argument('--template', choices=['web-api', 'cli-tool', 'data-pipeline', 'ml-project'], 
                              help='Use a predefined project template')
    create_parser.add_argument('--auto-install', action='store_true', 
                              help='Automatically install dependencies after creation')
    create_parser.set_defaults(func=create_project_command)
    
    # Init command - initialize A3 in existing directory
    init_parser = subparsers.add_parser('init', help='Initialize A3 in an existing project directory')
    init_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    init_parser.add_argument('--force', action='store_true', help='Force initialization even if A3 files exist')
    init_parser.set_defaults(func=init_project_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check project status')
    status_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    status_parser.set_defaults(func=status_command)
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume an interrupted project')
    resume_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    resume_parser.set_defaults(func=resume_command)
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze an existing project')
    analyze_parser.add_argument('path', help='Project directory path to analyze')
    analyze_parser.add_argument('--generate-docs', action='store_true', help='Generate project documentation')
    analyze_parser.add_argument('--dependency-graph', action='store_true', help='Create dependency graph')
    analyze_parser.add_argument('--code-patterns', action='store_true', help='Analyze code patterns')
    analyze_parser.set_defaults(func=analyze_project_command)
    
    # Debug command
    debug_parser = subparsers.add_parser('debug', help='Debug and test project code')
    debug_parser.add_argument('path', help='Project directory path to debug')
    debug_parser.add_argument('--execute-tests', action='store_true', help='Execute all tests')
    debug_parser.add_argument('--validate-imports', action='store_true', help='Validate all imports')
    debug_parser.set_defaults(func=debug_project_command)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage A3 configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Configuration actions')
    
    # Config show
    config_show_parser = config_subparsers.add_parser('show', help='Show current configuration')
    config_show_parser.set_defaults(func=config_show_command)
    
    # Config set
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', help='Configuration key')
    config_set_parser.add_argument('value', help='Configuration value')
    config_set_parser.add_argument('--global', action='store_true', dest='global_config', 
                                  help='Set global configuration')
    config_set_parser.set_defaults(func=config_set_command)
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Load configuration
    config = A3Config.load()
    
    # Apply workspace from config if not specified
    if hasattr(args, 'workspace') and not args.workspace:
        args.workspace = config.default_workspace
    
    # Store config in args for command functions
    args.config = config
    
    # Handle no command
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


def analyze_project() -> None:
    """Entry point for a3-analyze command."""
    parser = argparse.ArgumentParser(description="Analyze an existing project")
    parser.add_argument('path', help='Project directory path to analyze')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--generate-docs', action='store_true', help='Generate project documentation')
    parser.add_argument('--dependency-graph', action='store_true', help='Create dependency graph')
    parser.add_argument('--code-patterns', action='store_true', help='Analyze code patterns')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    analyze_project_command(args)


def debug_project() -> None:
    """Entry point for a3-debug command."""
    parser = argparse.ArgumentParser(description="Debug and test project code")
    parser.add_argument('path', help='Project directory path to debug')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--execute-tests', action='store_true', help='Execute all tests')
    parser.add_argument('--validate-imports', action='store_true', help='Validate all imports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    debug_project_command(args)


if __name__ == '__main__':
    main()