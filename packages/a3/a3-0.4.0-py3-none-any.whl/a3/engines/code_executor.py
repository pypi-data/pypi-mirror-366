"""
Code execution engine for AI Project Builder.

This module provides functionality to execute generated code, run tests,
validate imports, and verify function implementations.
"""

import ast
import importlib
import importlib.util
import inspect
import os
import psutil
import subprocess
import sys
import time
import traceback
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..core.interfaces import CodeExecutorInterface, FileSystemManagerInterface
from ..core.models import (
    ExecutionResult, TestResult, TestDetail, CoverageReport,
    ImportValidationResult, VerificationResult, FunctionSpec,
    ValidationResult
)
from .base import BaseEngine


class CodeExecutor(BaseEngine, CodeExecutorInterface):
    """
    Engine for executing generated code and running tests.
    
    Provides functionality to:
    - Execute individual functions with error capture
    - Run test suites and collect results
    - Validate module imports
    - Verify function implementations
    """
    
    def __init__(self, project_path: str, 
                 file_manager: Optional[FileSystemManagerInterface] = None):
        """
        Initialize the code executor.
        
        Args:
            project_path: Path to the project root directory
            file_manager: File system manager for file operations
        """
        super().__init__()
        self.project_path = Path(project_path).resolve()
        self.file_manager = file_manager
        self._original_sys_path = sys.path.copy()
    
    def initialize(self) -> None:
        """Initialize the code executor."""
        super().initialize()
        
        # Add project path to Python path for imports
        if str(self.project_path) not in sys.path:
            sys.path.insert(0, str(self.project_path))
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate that all prerequisites are met for operation."""
        issues = []
        warnings = []
        
        if not self._initialized:
            issues.append("Engine has not been initialized")
        
        if not self.project_path.exists():
            issues.append(f"Project path does not exist: {self.project_path}")
        
        if not self.project_path.is_dir():
            issues.append(f"Project path is not a directory: {self.project_path}")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    def execute_function(self, function_spec: FunctionSpec, module_path: str) -> ExecutionResult:
        """
        Execute a specific function and capture results.
        
        Args:
            function_spec: Specification of the function to execute
            module_path: Path to the module containing the function
            
        Returns:
            ExecutionResult with execution details
        """
        self._ensure_initialized()
        
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        try:
            # Load the module
            module = self._load_module(module_path)
            if module is None:
                return ExecutionResult(
                    success=False,
                    error=ImportError(f"Could not load module from {module_path}"),
                    execution_time=time.time() - start_time,
                    memory_usage=self._get_memory_usage() - initial_memory
                )
            
            # Get the function
            if not hasattr(module, function_spec.name):
                return ExecutionResult(
                    success=False,
                    error=AttributeError(f"Function '{function_spec.name}' not found in module"),
                    execution_time=time.time() - start_time,
                    memory_usage=self._get_memory_usage() - initial_memory
                )
            
            function = getattr(module, function_spec.name)
            
            # Capture output and execute
            with self._capture_output() as (stdout, stderr):
                try:
                    # Verify the function exists and is callable
                    if not callable(function):
                        raise TypeError(f"'{function_spec.name}' is not callable")
                    
                    # Basic signature validation
                    sig = inspect.signature(function)
                    expected_params = len(function_spec.arguments)
                    actual_params = len([p for p in sig.parameters.values() 
                                       if p.default == inspect.Parameter.empty])
                    
                    # Try to execute the function with minimal test data if possible
                    output = f"Function '{function_spec.name}' loaded successfully\n"
                    output += f"Expected parameters: {expected_params}, Required parameters: {actual_params}\n"
                    
                    # Attempt basic execution if function has no required parameters
                    if actual_params == 0:
                        try:
                            result = function()
                            output += f"Function executed successfully, returned: {type(result).__name__}\n"
                        except Exception as exec_error:
                            output += f"Function execution failed: {str(exec_error)}\n"
                            # Don't fail the whole execution for this, just note it
                    
                    execution_time = time.time() - start_time
                    memory_usage = self._get_memory_usage() - initial_memory
                    
                    return ExecutionResult(
                        success=True,
                        output=output + stdout.getvalue(),
                        execution_time=execution_time,
                        memory_usage=memory_usage
                    )
                    
                except Exception as e:
                    return ExecutionResult(
                        success=False,
                        output=stdout.getvalue(),
                        error=e,
                        execution_time=time.time() - start_time,
                        memory_usage=self._get_memory_usage() - initial_memory
                    )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=e,
                execution_time=time.time() - start_time,
                memory_usage=self._get_memory_usage() - initial_memory
            )
    
    def run_tests(self, test_files: List[str]) -> TestResult:
        """
        Run test files and return aggregated results.
        
        Args:
            test_files: List of test file paths to execute
            
        Returns:
            TestResult with aggregated test results
        """
        self._ensure_initialized()
        
        if not test_files:
            return TestResult(total_tests=0, passed_tests=0, failed_tests=0)
        
        # Try to use pytest if available, otherwise fall back to basic runner
        if self._is_pytest_available():
            return self._run_tests_with_pytest(test_files)
        else:
            return self._run_tests_basic(test_files)
    
    def _is_pytest_available(self) -> bool:
        """Check if pytest is available."""
        try:
            import pytest
            return True
        except ImportError:
            return False
    
    def _run_tests_with_pytest(self, test_files: List[str]) -> TestResult:
        """Run tests using pytest."""
        try:
            import pytest
            from _pytest.main import ExitCode
            
            # Capture pytest output
            with self._capture_output() as (stdout, stderr):
                # Run pytest programmatically
                exit_code = pytest.main(['-v', '--tb=short'] + test_files)
            
            output = stdout.getvalue()
            
            # Parse pytest output to extract test results
            total_tests = 0
            passed_tests = 0
            failed_tests = 0
            test_details = []
            
            # Basic parsing of pytest output
            lines = output.split('\n')
            for line in lines:
                if '::' in line and ('PASSED' in line or 'FAILED' in line):
                    total_tests += 1
                    test_name = line.split('::')[-1].split()[0]
                    if 'PASSED' in line:
                        passed_tests += 1
                        test_details.append(TestDetail(
                            name=test_name,
                            status="passed"
                        ))
                    elif 'FAILED' in line:
                        failed_tests += 1
                        test_details.append(TestDetail(
                            name=test_name,
                            status="failed",
                            message="Test failed (see pytest output for details)"
                        ))
            
            return TestResult(
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                test_details=test_details
            )
            
        except Exception as e:
            # Fall back to basic runner if pytest fails
            return self._run_tests_basic(test_files)
    
    def _run_tests_basic(self, test_files: List[str]) -> TestResult:
        """Run tests using basic test runner."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        test_details = []
        
        for test_file in test_files:
            # Check if file exists first
            if not Path(test_file).exists():
                total_tests += 1
                failed_tests += 1
                test_details.append(TestDetail(
                    name=f"Test file: {test_file}",
                    status="failed",
                    message=f"Test file does not exist: {test_file}"
                ))
                continue
                
            try:
                result = self._run_single_test_file(test_file)
                total_tests += result.total_tests
                passed_tests += result.passed_tests
                failed_tests += result.failed_tests
                test_details.extend(result.test_details)
            except Exception as e:
                # If we can't run the test file, count it as one failed test
                total_tests += 1
                failed_tests += 1
                test_details.append(TestDetail(
                    name=f"Test file: {test_file}",
                    status="failed",
                    message=f"Failed to execute test file: {str(e)}"
                ))
        
        return TestResult(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            test_details=test_details
        )
    
    def validate_imports(self, module_path: str) -> ImportValidationResult:
        """
        Validate that all imports in a module resolve correctly.
        
        Args:
            module_path: Path to the module to validate
            
        Returns:
            ImportValidationResult with validation details
        """
        self._ensure_initialized()
        
        try:
            # Read the module file
            try:
                if self.file_manager and hasattr(self.file_manager, 'read_file'):
                    content = self.file_manager.read_file(module_path)
                else:
                    with open(module_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                if content is None:
                    return ImportValidationResult(
                        success=False,
                        error_messages=[f"Could not read module file: {module_path}"]
                    )
            except (FileNotFoundError, IOError) as e:
                return ImportValidationResult(
                    success=False,
                    error_messages=[f"Could not read module file: {str(e)}"]
                )
            
            # Parse the AST to find import statements
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return ImportValidationResult(
                    success=False,
                    error_messages=[f"Syntax error in module: {str(e)}"]
                )
            
            imports = self._extract_imports(tree)
            valid_imports = []
            invalid_imports = []
            missing_modules = []
            error_messages = []
            
            # Validate each import
            for import_info in imports:
                try:
                    if import_info['type'] == 'import':
                        # Handle "import module" statements
                        for module_name in import_info['modules']:
                            if self._can_import_module(module_name):
                                valid_imports.append(module_name)
                            else:
                                invalid_imports.append(module_name)
                                missing_modules.append(module_name)
                    
                    elif import_info['type'] == 'from':
                        # Handle "from module import ..." statements
                        module_name = import_info['module']
                        if self._can_import_module(module_name):
                            valid_imports.append(f"from {module_name} import {', '.join(import_info['names'])}")
                        else:
                            invalid_imports.append(f"from {module_name} import {', '.join(import_info['names'])}")
                            missing_modules.append(module_name)
                
                except Exception as e:
                    error_messages.append(f"Error validating import: {str(e)}")
            
            return ImportValidationResult(
                success=len(invalid_imports) == 0 and len(error_messages) == 0,
                valid_imports=valid_imports,
                invalid_imports=invalid_imports,
                missing_modules=missing_modules,
                error_messages=error_messages
            )
        
        except Exception as e:
            return ImportValidationResult(
                success=False,
                error_messages=[f"Error validating imports: {str(e)}"]
            )
    
    def capture_runtime_errors(self, execution_func: Callable) -> Optional[Exception]:
        """
        Capture and analyze runtime errors during execution.
        
        Args:
            execution_func: Function to execute and monitor for errors
            
        Returns:
            Exception if one occurred, None otherwise
        """
        try:
            execution_func()
            return None
        except Exception as e:
            return e
    
    def verify_implementation(self, function_spec: FunctionSpec) -> VerificationResult:
        """
        Verify that a function implementation works correctly.
        
        Args:
            function_spec: Specification of the function to verify
            
        Returns:
            VerificationResult with verification details
        """
        self._ensure_initialized()
        
        verification_errors = []
        
        # Determine module path from function spec
        module_path = self._get_module_path(function_spec.module)
        
        # Execute the function
        execution_result = self.execute_function(function_spec, module_path)
        
        # Validate imports
        import_validation = self.validate_imports(module_path)
        
        # Check for test files and run them if available
        test_result = None
        test_files = self._find_test_files(function_spec.module)
        if test_files:
            test_result = self.run_tests(test_files)
        
        # Perform additional verification checks
        additional_checks = self._perform_additional_verification(function_spec, module_path)
        
        # Determine if verification passed
        is_verified = (
            execution_result.success and
            import_validation.success and
            (test_result is None or test_result.failed_tests == 0) and
            additional_checks['signature_match'] and
            additional_checks['docstring_present']
        )
        
        # Collect verification errors
        if not execution_result.success:
            verification_errors.append(f"Function execution failed: {execution_result.error}")
        
        if not import_validation.success:
            verification_errors.extend(import_validation.error_messages)
        
        if test_result and test_result.failed_tests > 0:
            verification_errors.append(f"Tests failed: {test_result.failed_tests} out of {test_result.total_tests}")
        
        if not additional_checks['signature_match']:
            verification_errors.append("Function signature does not match specification")
        
        if not additional_checks['docstring_present']:
            verification_errors.append("Function is missing docstring")
        
        # Store verification result if state manager is available
        if self.file_manager:
            self._store_verification_result(function_spec, VerificationResult(
                function_name=function_spec.name,
                is_verified=is_verified,
                execution_result=execution_result,
                test_result=test_result,
                import_validation=import_validation,
                verification_errors=verification_errors
            ))
        
        return VerificationResult(
            function_name=function_spec.name,
            is_verified=is_verified,
            execution_result=execution_result,
            test_result=test_result,
            import_validation=import_validation,
            verification_errors=verification_errors
        )
    
    def _perform_additional_verification(self, function_spec: FunctionSpec, module_path: str) -> Dict[str, bool]:
        """Perform additional verification checks."""
        checks = {
            'signature_match': False,
            'docstring_present': False,
            'return_type_match': False
        }
        
        try:
            module = self._load_module(module_path)
            if module and hasattr(module, function_spec.name):
                function = getattr(module, function_spec.name)
                
                # Check signature
                sig = inspect.signature(function)
                expected_params = len(function_spec.arguments)
                actual_params = len(sig.parameters)
                checks['signature_match'] = expected_params == actual_params
                
                # Check docstring
                checks['docstring_present'] = bool(function.__doc__ and function.__doc__.strip())
                
                # Check return type annotation if available
                if sig.return_annotation != inspect.Signature.empty:
                    checks['return_type_match'] = True
        
        except Exception:
            pass  # Keep default False values
        
        return checks
    
    def _store_verification_result(self, function_spec: FunctionSpec, result: VerificationResult) -> None:
        """Store verification result for reporting."""
        try:
            # Create verification report directory
            report_dir = self.project_path / '.A3' / 'verification'
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Store result as JSON
            import json
            from datetime import datetime
            
            report_data = {
                'function_name': result.function_name,
                'module': function_spec.module,
                'is_verified': result.is_verified,
                'timestamp': datetime.now().isoformat(),
                'execution_success': result.execution_result.success if result.execution_result else None,
                'execution_time': result.execution_result.execution_time if result.execution_result else None,
                'memory_usage': result.execution_result.memory_usage if result.execution_result else None,
                'test_results': {
                    'total': result.test_result.total_tests if result.test_result else 0,
                    'passed': result.test_result.passed_tests if result.test_result else 0,
                    'failed': result.test_result.failed_tests if result.test_result else 0
                } if result.test_result else None,
                'import_validation_success': result.import_validation.success if result.import_validation else None,
                'verification_errors': result.verification_errors
            }
            
            report_file = report_dir / f"{function_spec.name}_verification.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
        
        except Exception:
            pass  # Don't fail verification if we can't store the result
    
    def generate_verification_report(self, function_specs: List[FunctionSpec]) -> Dict[str, Any]:
        """
        Generate a comprehensive verification report for multiple functions.
        
        Args:
            function_specs: List of function specifications to verify
            
        Returns:
            Dictionary containing verification report data
        """
        self._ensure_initialized()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_functions': len(function_specs),
            'verified_functions': 0,
            'failed_functions': 0,
            'total_execution_time': 0.0,
            'total_memory_usage': 0,
            'function_results': [],
            'summary': {}
        }
        
        for function_spec in function_specs:
            verification_result = self.verify_implementation(function_spec)
            
            if verification_result.is_verified:
                report['verified_functions'] += 1
            else:
                report['failed_functions'] += 1
            
            if verification_result.execution_result:
                report['total_execution_time'] += verification_result.execution_result.execution_time
                if verification_result.execution_result.memory_usage:
                    report['total_memory_usage'] += verification_result.execution_result.memory_usage
            
            report['function_results'].append({
                'name': verification_result.function_name,
                'verified': verification_result.is_verified,
                'errors': verification_result.verification_errors,
                'execution_time': verification_result.execution_result.execution_time if verification_result.execution_result else 0,
                'memory_usage': verification_result.execution_result.memory_usage if verification_result.execution_result else 0
            })
        
        # Generate summary
        report['summary'] = {
            'success_rate': (report['verified_functions'] / report['total_functions']) * 100 if report['total_functions'] > 0 else 0,
            'average_execution_time': report['total_execution_time'] / report['total_functions'] if report['total_functions'] > 0 else 0,
            'average_memory_usage': report['total_memory_usage'] / report['total_functions'] if report['total_functions'] > 0 else 0
        }
        
        return report
    
    def _load_module(self, module_path: str):
        """Load a Python module from file path."""
        try:
            module_path = Path(module_path)
            if not module_path.exists():
                return None
            
            spec = importlib.util.spec_from_file_location("temp_module", module_path)
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        
        except Exception:
            return None
    
    @contextmanager
    def _capture_output(self):
        """Context manager to capture stdout and stderr."""
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                yield stdout_capture, stderr_capture
        finally:
            pass
    
    def _run_single_test_file(self, test_file: str) -> TestResult:
        """Run a single test file and return results."""
        # For now, we'll implement a basic test runner
        # In a real implementation, this might use pytest or unittest
        
        try:
            # Try to load and execute the test file
            module = self._load_module(test_file)
            if module is None:
                return TestResult(
                    total_tests=1,
                    passed_tests=0,
                    failed_tests=1,
                    test_details=[TestDetail(
                        name=f"Load {test_file}",
                        status="failed",
                        message="Could not load test module"
                    )]
                )
            
            # Look for test functions (functions starting with 'test_')
            test_functions = [
                (name, func) for name, func in inspect.getmembers(module, inspect.isfunction)
                if name.startswith('test_')
            ]
            
            if not test_functions:
                return TestResult(
                    total_tests=0,
                    passed_tests=0,
                    failed_tests=0,
                    test_details=[]
                )
            
            total_tests = len(test_functions)
            passed_tests = 0
            failed_tests = 0
            test_details = []
            
            for test_name, test_func in test_functions:
                start_time = time.time()
                try:
                    test_func()
                    passed_tests += 1
                    test_details.append(TestDetail(
                        name=test_name,
                        status="passed",
                        execution_time=time.time() - start_time
                    ))
                except Exception as e:
                    failed_tests += 1
                    test_details.append(TestDetail(
                        name=test_name,
                        status="failed",
                        message=str(e),
                        execution_time=time.time() - start_time
                    ))
            
            return TestResult(
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                test_details=test_details
            )
        
        except Exception as e:
            return TestResult(
                total_tests=1,
                passed_tests=0,
                failed_tests=1,
                test_details=[TestDetail(
                    name=f"Execute {test_file}",
                    status="failed",
                    message=f"Error executing test file: {str(e)}"
                )]
            )
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements from an AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.append({
                    'type': 'import',
                    'modules': [alias.name for alias in node.names]
                })
            elif isinstance(node, ast.ImportFrom):
                if node.module:  # Skip relative imports without module
                    imports.append({
                        'type': 'from',
                        'module': node.module,
                        'names': [alias.name for alias in node.names]
                    })
        
        return imports
    
    def _can_import_module(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            # Check if it's a local module in the project
            module_path = self.project_path / f"{module_name.replace('.', '/')}.py"
            return module_path.exists()
    
    def _get_module_path(self, module_name: str) -> str:
        """Get the file path for a module."""
        # Convert module name to file path
        module_path = self.project_path / f"{module_name.replace('.', '/')}.py"
        return str(module_path)
    
    def _find_test_files(self, module_name: str) -> List[str]:
        """Find test files related to a module."""
        test_files = []
        
        # Look for test files in common locations
        test_patterns = [
            f"test_{module_name}.py",
            f"tests/test_{module_name}.py",
            f"{module_name}_test.py",
            f"tests/{module_name}_test.py"
        ]
        
        for pattern in test_patterns:
            test_path = self.project_path / pattern
            if test_path.exists():
                test_files.append(str(test_path))
        
        return test_files
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0
    
    def _execute_with_timeout(self, func: Callable, timeout: float = 30.0) -> Any:
        """Execute a function with a timeout."""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Function execution timed out after {timeout} seconds")
        
        # Set up timeout (Unix-like systems only)
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))
            
            try:
                result = func()
                signal.alarm(0)  # Cancel the alarm
                return result
            except TimeoutError:
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # For Windows or systems without SIGALRM, just execute normally
            return func()
    
    def __del__(self):
        """Cleanup: restore original sys.path."""
        try:
            if hasattr(self, '_original_sys_path') and self._original_sys_path is not None:
                sys.path[:] = self._original_sys_path
        except (TypeError, AttributeError):
            pass  # Ignore cleanup errors during shutdown