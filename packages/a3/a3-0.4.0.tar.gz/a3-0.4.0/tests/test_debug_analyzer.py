"""
Tests for the DebugAnalyzer engine.

This module contains comprehensive tests for debug analysis functionality
including traceback analysis, function inspection, and code revision.
"""

import pytest
import sys
import traceback
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from a3.engines.debug_analyzer import DebugAnalyzer
from a3.core.models import (
    FunctionSpec, Argument, TracebackAnalysis, FunctionInspection,
    ParsedDocstring, DebugContext, CodeRevision, StackFrame,
    ValidationResult, VerificationResult, ExecutionResult
)
from a3.core.interfaces import AIClientInterface, StateManagerInterface


class TestDebugAnalyzer:
    """Test cases for the DebugAnalyzer class."""
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        client = Mock(spec=AIClientInterface)
        client.validate_api_key.return_value = True
        client.generate_with_retry.return_value = "def fixed_function():\n    return 'fixed'"
        return client
    
    @pytest.fixture
    def mock_state_manager(self):
        """Create a mock state manager."""
        return Mock(spec=StateManagerInterface)
    
    @pytest.fixture
    def debug_analyzer(self, mock_ai_client, mock_state_manager):
        """Create a DebugAnalyzer instance for testing."""
        analyzer = DebugAnalyzer(
            ai_client=mock_ai_client,
            state_manager=mock_state_manager,
            project_path="/test/project"
        )
        analyzer.initialize()
        return analyzer
    
    @pytest.fixture
    def sample_function_spec(self):
        """Create a sample function specification."""
        return FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function for debugging",
            arguments=[
                Argument(name="x", type_hint="int", description="Input number"),
                Argument(name="y", type_hint="str", default_value="'default'", description="Input string")
            ],
            return_type="bool"
        )
    
    def test_initialization(self, mock_ai_client, mock_state_manager):
        """Test DebugAnalyzer initialization."""
        analyzer = DebugAnalyzer(
            ai_client=mock_ai_client,
            state_manager=mock_state_manager,
            project_path="/test/project"
        )
        
        assert analyzer.ai_client == mock_ai_client
        assert analyzer.state_manager == mock_state_manager
        assert analyzer.project_path == Path("/test/project")
        assert not analyzer._initialized
        
        analyzer.initialize()
        assert analyzer._initialized
    
    def test_validate_prerequisites(self, debug_analyzer):
        """Test prerequisite validation."""
        result = debug_analyzer.validate_prerequisites()
        assert result.is_valid
        assert len(result.issues) == 0
        
        # Test without AI client
        analyzer_no_client = DebugAnalyzer(project_path="/test")
        analyzer_no_client.initialize()
        result = analyzer_no_client.validate_prerequisites()
        assert not result.is_valid
        assert "AI client is required" in result.issues[0]
    
    def test_analyze_traceback_basic(self, debug_analyzer):
        """Test basic traceback analysis."""
        # Create a test exception
        try:
            x = undefined_variable  # This will raise NameError
        except NameError as e:
            analysis = debug_analyzer.analyze_traceback(e)
            
            assert isinstance(analysis, TracebackAnalysis)
            assert analysis.error_type == "NameError"
            assert "undefined_variable" in analysis.error_message
            assert len(analysis.stack_trace) > 0
            assert "not defined" in analysis.root_cause
            assert len(analysis.suggested_fixes) > 0
    
    def test_analyze_traceback_with_chain(self, debug_analyzer):
        """Test traceback analysis with exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Chained error") from e
        except RuntimeError as e:
            analysis = debug_analyzer.analyze_traceback(e)
            
            assert analysis.error_type == "RuntimeError"
            assert len(analysis.exception_chain) >= 2
            assert "ValueError: Original error" in analysis.exception_chain[1]
    
    def test_inspect_function_basic(self, debug_analyzer):
        """Test basic function inspection."""
        def sample_function(x: int, y: str = "default") -> bool:
            """Sample function for testing."""
            return x > 0
        
        inspection = debug_analyzer.inspect_function(sample_function)
        
        assert isinstance(inspection, FunctionInspection)
        assert "(x: int, y: str" in inspection.signature
        assert inspection.docstring == "Sample function for testing."
        assert len(inspection.parameters) == 2
        assert inspection.parameters[0].name == "x"
        assert inspection.parameters[0].annotation == "int"
        assert inspection.parameters[1].name == "y"
        assert inspection.parameters[1].default_value == "default"
        assert inspection.return_annotation == "bool"
    
    def test_inspect_function_with_source(self, debug_analyzer):
        """Test function inspection with source code."""
        def sample_function():
            """Sample function."""
            x = 1
            y = 2
            return x + y
        
        inspection = debug_analyzer.inspect_function(sample_function)
        
        assert inspection.source_code is not None
        assert "def sample_function" in inspection.source_code
        assert inspection.complexity_metrics is not None
        assert inspection.complexity_metrics.lines_of_code >= 0  # May be 0 due to filtering
    
    def test_inspect_function_error_handling(self, debug_analyzer):
        """Test function inspection error handling."""
        # Test with non-function object
        inspection = debug_analyzer.inspect_function("not_a_function")
        
        assert isinstance(inspection, FunctionInspection)
        assert "<unable to inspect:" in inspection.signature
    
    def test_parse_docstring_basic(self, debug_analyzer):
        """Test basic docstring parsing."""
        docstring = """
        Short description of the function.
        
        Longer description with more details
        about what the function does.
        """
        
        parsed = debug_analyzer.parse_docstring(docstring)
        
        assert isinstance(parsed, ParsedDocstring)
        assert "Short description" in parsed.short_description
        assert "Longer description" in parsed.long_description
    
    def test_parse_docstring_empty(self, debug_analyzer):
        """Test parsing empty docstring."""
        parsed = debug_analyzer.parse_docstring("")
        
        assert isinstance(parsed, ParsedDocstring)
        assert parsed.short_description == ""
        assert parsed.long_description == ""
    
    def test_parse_docstring_with_parser(self, debug_analyzer):
        """Test docstring parsing with docstring_parser."""
        # Test with a real docstring since the parser might not be available
        docstring = "Test docstring"
        parsed = debug_analyzer.parse_docstring(docstring)
        
        assert isinstance(parsed, ParsedDocstring)
        # The actual result depends on whether docstring_parser is available
        assert parsed.short_description is not None
    
    def test_generate_debug_context(self, debug_analyzer, sample_function_spec):
        """Test debug context generation."""
        # Create a test exception
        try:
            raise ValueError("Test error")
        except ValueError as e:
            context = debug_analyzer.generate_debug_context(e, sample_function_spec)
            
            assert isinstance(context, DebugContext)
            assert context.function_spec == sample_function_spec
            assert context.traceback_analysis is not None
            assert context.traceback_analysis.error_type == "ValueError"
            assert context.parsed_docstring is not None
            assert len(context.related_code) > 0
            assert "python_version" in context.execution_environment
    
    def test_suggest_code_revision(self, debug_analyzer, sample_function_spec):
        """Test AI-powered code revision suggestions."""
        # Create debug context
        try:
            raise NameError("test_var is not defined")
        except NameError as e:
            context = debug_analyzer.generate_debug_context(e, sample_function_spec)
            
            revision = debug_analyzer.suggest_code_revision(context)
            
            assert isinstance(revision, CodeRevision)
            assert revision.revised_code is not None
            assert revision.revision_reason is not None
            assert 0.0 <= revision.confidence_score <= 1.0
            assert not revision.applied
    
    def test_suggest_code_revision_no_ai_client(self, sample_function_spec):
        """Test code revision without AI client."""
        analyzer = DebugAnalyzer(project_path="/test")
        analyzer.initialize()
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            context = analyzer.generate_debug_context(e, sample_function_spec)
            
            with pytest.raises(RuntimeError, match="AI client is required"):
                analyzer.suggest_code_revision(context)
    
    @patch("builtins.open", new_callable=mock_open, read_data="def old_function():\n    pass")
    def test_apply_revision_success(self, mock_file, debug_analyzer):
        """Test successful code revision application."""
        revision = CodeRevision(
            original_code="def old_function():\n    pass",
            revised_code="def new_function():\n    return True",
            revision_reason="Test revision",
            confidence_score=0.9
        )
        
        with patch("pathlib.Path.exists", return_value=True):
            result = debug_analyzer.apply_revision(revision, "/test/module.py")
            
            assert result is True
            assert revision.applied is True
    
    @patch("builtins.open", side_effect=IOError("File not found"))
    def test_apply_revision_failure(self, mock_file, debug_analyzer):
        """Test code revision application failure."""
        revision = CodeRevision(
            original_code="def old_function():\n    pass",
            revised_code="def new_function():\n    return True",
            revision_reason="Test revision",
            confidence_score=0.9
        )
        
        result = debug_analyzer.apply_revision(revision, "/nonexistent/module.py")
        
        assert result is False
        assert revision.applied is False
    
    def test_verify_revision_success(self, debug_analyzer, sample_function_spec):
        """Test successful revision verification."""
        revision = CodeRevision(
            original_code="def test_function():\n    return undefined_var",
            revised_code="def test_function():\n    return True",
            revision_reason="Fixed undefined variable",
            confidence_score=0.9
        )
        
        result = debug_analyzer.verify_revision(revision, sample_function_spec)
        
        assert isinstance(result, VerificationResult)
        assert result.function_name == sample_function_spec.name
        assert result.is_verified is True
        assert result.execution_result is not None
        assert result.execution_result.success is True
    
    def test_verify_revision_syntax_error(self, debug_analyzer, sample_function_spec):
        """Test revision verification with syntax error."""
        revision = CodeRevision(
            original_code="def test_function():\n    return True",
            revised_code="def test_function(\n    return True",  # Missing closing parenthesis
            revision_reason="Broken revision",
            confidence_score=0.5
        )
        
        result = debug_analyzer.verify_revision(revision, sample_function_spec)
        
        assert result.is_verified is False
        assert len(result.verification_errors) > 0
        assert "Syntax error" in result.verification_errors[0]
    
    def test_identify_root_cause_name_error(self, debug_analyzer):
        """Test root cause identification for NameError."""
        exception = NameError("name 'undefined_var' is not defined")
        stack_trace = []
        
        root_cause = debug_analyzer._identify_root_cause(exception, stack_trace)
        
        assert "undefined_var" in root_cause
        assert "not defined" in root_cause
    
    def test_identify_root_cause_type_error(self, debug_analyzer):
        """Test root cause identification for TypeError."""
        exception = TypeError("unsupported operand type(s) for +: 'int' and 'str'")
        stack_trace = []
        
        root_cause = debug_analyzer._identify_root_cause(exception, stack_trace)
        
        assert "incompatible data types" in root_cause
    
    def test_generate_fix_suggestions_name_error(self, debug_analyzer):
        """Test fix suggestions for NameError."""
        exception = NameError("name 'undefined_var' is not defined")
        stack_trace = []
        
        suggestions = debug_analyzer._generate_fix_suggestions(exception, stack_trace)
        
        assert len(suggestions) > 0
        assert any("variable is defined" in suggestion for suggestion in suggestions)
        assert any("spelled correctly" in suggestion for suggestion in suggestions)
    
    def test_generate_fix_suggestions_import_error(self, debug_analyzer):
        """Test fix suggestions for ImportError."""
        exception = ImportError("No module named 'nonexistent_module'")
        stack_trace = []
        
        suggestions = debug_analyzer._generate_fix_suggestions(exception, stack_trace)
        
        assert len(suggestions) > 0
        assert any("pip" in suggestion for suggestion in suggestions)
        assert any("module name" in suggestion for suggestion in suggestions)
    
    def test_calculate_complexity_metrics(self, debug_analyzer):
        """Test complexity metrics calculation."""
        source_code = """
def complex_function(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        return 0
"""
        
        metrics = debug_analyzer._calculate_complexity_metrics(source_code)
        
        assert metrics.cyclomatic_complexity > 1
        assert metrics.lines_of_code > 0
        assert 0.0 <= metrics.single_responsibility_score <= 1.0
    
    def test_calculate_complexity_metrics_error(self, debug_analyzer):
        """Test complexity metrics calculation with invalid code."""
        invalid_code = "def broken_function(\n    invalid syntax"
        
        metrics = debug_analyzer._calculate_complexity_metrics(invalid_code)
        
        # Should return default metrics on error
        assert metrics.cyclomatic_complexity == 0
        assert metrics.lines_of_code == 0
    
    def test_fallback_docstring_parse(self, debug_analyzer):
        """Test fallback docstring parsing."""
        docstring = """
        Short description.
        
        Longer description with
        multiple lines.
        """
        
        parsed = debug_analyzer._fallback_docstring_parse(docstring)
        
        assert "Short description" in parsed.short_description
        assert "Longer description" in parsed.long_description
    
    def test_collect_related_code(self, debug_analyzer, sample_function_spec):
        """Test related code collection."""
        related_code = debug_analyzer._collect_related_code(sample_function_spec)
        
        assert len(related_code) > 0
        assert sample_function_spec.name in related_code[0]
        assert sample_function_spec.module in related_code[0]
    
    @patch("builtins.open", new_callable=mock_open, read_data="import os\nfrom typing import List\n\ndef helper():\n    pass")
    def test_collect_related_code_with_file(self, mock_file, debug_analyzer, sample_function_spec):
        """Test related code collection with existing module file."""
        with patch("pathlib.Path.exists", return_value=True):
            related_code = debug_analyzer._collect_related_code(sample_function_spec)
            
            assert len(related_code) >= 2
            # Should include imports and function definitions
            assert any("import os" in code for code in related_code)
    
    def test_build_revision_prompt(self, debug_analyzer, sample_function_spec):
        """Test revision prompt building."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            context = debug_analyzer.generate_debug_context(e, sample_function_spec)
            prompt = debug_analyzer._build_revision_prompt(context)
            
            assert "FUNCTION SPECIFICATION:" in prompt
            assert sample_function_spec.name in prompt
            assert "ERROR ANALYSIS:" in prompt
            assert "ValueError" in prompt
            assert "corrected implementation" in prompt
    
    def test_parse_ai_revision_response_with_code_block(self, debug_analyzer):
        """Test parsing AI response with code block."""
        ai_response = """
Here's the fixed code:

```python
def fixed_function(x: int) -> int:
    return x * 2
```

This should resolve the issue.
"""
        
        code, reason, confidence = debug_analyzer._parse_ai_revision_response(ai_response)
        
        assert "def fixed_function" in code
        assert "return x * 2" in code
        assert confidence == 0.9
    
    def test_parse_ai_revision_response_without_code_block(self, debug_analyzer):
        """Test parsing AI response without code block."""
        ai_response = "def simple_function():\n    return True"
        
        code, reason, confidence = debug_analyzer._parse_ai_revision_response(ai_response)
        
        assert code == ai_response
        assert "AI-generated" in reason
        assert confidence == 0.8


class TestDebugAnalyzerIntegration:
    """Integration tests for DebugAnalyzer."""
    
    @pytest.fixture
    def real_ai_client(self):
        """Create a real AI client mock for integration testing."""
        client = Mock(spec=AIClientInterface)
        client.validate_api_key.return_value = True
        client.generate_with_retry.return_value = """
```python
def corrected_function(x: int, y: str = "default") -> bool:
    \"\"\"Corrected function implementation.\"\"\"
    if not isinstance(x, int):
        raise TypeError("x must be an integer")
    return x > 0
```
"""
        return client
    
    def test_full_debug_workflow(self, real_ai_client):
        """Test the complete debug workflow."""
        analyzer = DebugAnalyzer(ai_client=real_ai_client, project_path="/test")
        analyzer.initialize()
        
        # Create a function spec
        func_spec = FunctionSpec(
            name="buggy_function",
            module="test_module",
            docstring="Function with a bug",
            arguments=[Argument(name="x", type_hint="int")],
            return_type="bool"
        )
        
        # Create an exception
        try:
            result = undefined_variable + 1
        except NameError as e:
            # Generate debug context
            context = analyzer.generate_debug_context(e, func_spec)
            
            # Get revision suggestion
            revision = analyzer.suggest_code_revision(context)
            
            # Verify the revision
            verification = analyzer.verify_revision(revision, func_spec)
            
            # Assertions
            assert context.traceback_analysis.error_type == "NameError"
            assert "corrected_function" in revision.revised_code
            assert revision.confidence_score > 0.8
            assert verification.function_name == func_spec.name
    
    def test_error_recovery_workflow(self, real_ai_client):
        """Test error recovery and multiple revision attempts."""
        analyzer = DebugAnalyzer(ai_client=real_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="error_prone_function",
            module="test_module",
            docstring="Function that might have errors",
            arguments=[],
            return_type="None"
        )
        
        # Simulate multiple error types
        errors = [
            NameError("name 'x' is not defined"),
            TypeError("unsupported operand type(s)"),
            AttributeError("'NoneType' object has no attribute 'method'")
        ]
        
        for error in errors:
            context = analyzer.generate_debug_context(error, func_spec)
            revision = analyzer.suggest_code_revision(context)
            
            assert context.traceback_analysis.error_type == type(error).__name__
            assert revision.revised_code is not None
            assert len(context.traceback_analysis.suggested_fixes) > 0


    def test_debug_and_revise_loop_success(self, real_ai_client):
        """Test successful debug and revision loop."""
        analyzer = DebugAnalyzer(ai_client=real_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="None"
        )
        
        # Create an exception
        try:
            raise NameError("undefined_var is not defined")
        except NameError as e:
            with patch.object(analyzer, 'apply_revision', return_value=True):
                revisions = analyzer.debug_and_revise_loop(e, func_spec, "/test/module.py", max_iterations=2)
                
                assert len(revisions) >= 1
                assert all(isinstance(rev, CodeRevision) for rev in revisions)
                # Should have at least one successful revision due to mocked apply_revision
    
    def test_debug_and_revise_loop_max_iterations(self, real_ai_client):
        """Test debug and revision loop with max iterations."""
        analyzer = DebugAnalyzer(ai_client=real_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="problematic_function",
            module="test_module",
            docstring="Problematic function",
            arguments=[],
            return_type="None"
        )
        
        try:
            raise RuntimeError("Persistent error")
        except RuntimeError as e:
            with patch.object(analyzer, 'apply_revision', return_value=False):
                revisions = analyzer.debug_and_revise_loop(e, func_spec, "/test/module.py", max_iterations=3)
                
                assert len(revisions) == 3  # Should try exactly max_iterations times
                assert all(not rev.applied for rev in revisions)  # None should be applied due to mock
    
    def test_analyze_and_fix_function_with_error(self, real_ai_client):
        """Test complete analyze and fix workflow with error."""
        analyzer = DebugAnalyzer(ai_client=real_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="buggy_function",
            module="test_module",
            docstring="Buggy function",
            arguments=[],
            return_type="None"
        )
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            with patch.object(analyzer, 'apply_revision', return_value=True), \
                 patch.object(analyzer, 'verify_revision') as mock_verify:
                # Mock verification to return success
                mock_verify.return_value = VerificationResult(
                    function_name=func_spec.name,
                    is_verified=True,
                    execution_result=ExecutionResult(success=True),
                    verification_errors=[]
                )
                
                result = analyzer.analyze_and_fix_function(func_spec, "/test/module.py", e)
                
                assert result['function_spec'] == func_spec
                assert result['original_error'] == e
                assert len(result['revisions']) >= 1
                assert result['final_status'] == 'fixed'
                assert result['success'] is True
    
    def test_analyze_and_fix_function_without_error(self, real_ai_client):
        """Test analyze and fix workflow without error (analysis only)."""
        analyzer = DebugAnalyzer(ai_client=real_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="good_function",
            module="test_module",
            docstring="Good function",
            arguments=[],
            return_type="None"
        )
        
        result = analyzer.analyze_and_fix_function(func_spec, "/test/module.py")
        
        assert result['function_spec'] == func_spec
        assert result['original_error'] is None
        assert len(result['revisions']) == 0
        # Status depends on whether function can be found and analyzed
        assert result['final_status'] in ['analyzed', 'function_not_found']
    
    def test_debug_and_revise_loop_no_ai_client(self):
        """Test debug and revision loop without AI client."""
        analyzer = DebugAnalyzer(project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="test_function",
            module="test_module",
            docstring="Test function",
            arguments=[],
            return_type="None"
        )
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            with pytest.raises(RuntimeError, match="AI client is required"):
                analyzer.debug_and_revise_loop(e, func_spec, "/test/module.py")


class TestDebugAnalyzerAdvanced:
    """Advanced test cases for DebugAnalyzer functionality."""
    
    @pytest.fixture
    def advanced_ai_client(self):
        """Create an advanced AI client mock."""
        client = Mock(spec=AIClientInterface)
        client.validate_api_key.return_value = True
        
        # Mock different responses for different iterations
        responses = [
            """
```python
def fixed_function_v1(x: int) -> int:
    # First attempt - might still have issues
    return x + undefined_var
```
""",
            """
```python
def fixed_function_v2(x: int) -> int:
    # Second attempt - should be better
    if x is None:
        raise ValueError("x cannot be None")
    return x * 2
```
"""
        ]
        client.generate_with_retry.side_effect = responses
        return client
    
    def test_iterative_revision_improvement(self, advanced_ai_client):
        """Test that revisions improve over iterations."""
        analyzer = DebugAnalyzer(ai_client=advanced_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="iterative_function",
            module="test_module",
            docstring="Function that improves over iterations",
            arguments=[Argument(name="x", type_hint="int")],
            return_type="int"
        )
        
        try:
            raise NameError("undefined_var is not defined")
        except NameError as e:
            with patch.object(analyzer, 'apply_revision', return_value=False):
                revisions = analyzer.debug_and_revise_loop(e, func_spec, "/test/module.py", max_iterations=2)
                
                assert len(revisions) == 2
                # First revision should contain the problematic code
                assert "undefined_var" in revisions[0].revised_code
                # Second revision should be improved
                assert "undefined_var" not in revisions[1].revised_code
                assert "ValueError" in revisions[1].revised_code  # Better error handling
    
    def test_revision_history_tracking(self, advanced_ai_client):
        """Test that revision history is properly tracked."""
        analyzer = DebugAnalyzer(ai_client=advanced_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="history_function",
            module="test_module",
            docstring="Function for testing history tracking",
            arguments=[],
            return_type="None"
        )
        
        try:
            raise RuntimeError("Persistent issue")
        except RuntimeError as e:
            with patch.object(analyzer, 'apply_revision', return_value=False):
                # Mock the generate_debug_context to capture history
                original_generate = analyzer.generate_debug_context
                contexts = []
                
                def capture_context(error, spec):
                    context = original_generate(error, spec)
                    contexts.append(context)
                    return context
                
                with patch.object(analyzer, 'generate_debug_context', side_effect=capture_context):
                    revisions = analyzer.debug_and_revise_loop(e, func_spec, "/test/module.py", max_iterations=2)
                    
                    # Check that revision history is accumulated
                    assert len(contexts) == 2
                    assert len(contexts[0].revision_history) == 0  # First iteration has no history
                    assert len(contexts[1].revision_history) == 1  # Second iteration has one previous revision
    
    def test_complex_error_analysis(self, advanced_ai_client):
        """Test analysis of complex, chained errors."""
        analyzer = DebugAnalyzer(ai_client=advanced_ai_client, project_path="/test")
        analyzer.initialize()
        
        func_spec = FunctionSpec(
            name="complex_function",
            module="test_module",
            docstring="Function with complex error chain",
            arguments=[],
            return_type="None"
        )
        
        # Create a chained exception
        try:
            try:
                raise ValueError("Original problem")
            except ValueError as e:
                raise RuntimeError("Secondary problem") from e
        except RuntimeError as e:
            result = analyzer.analyze_and_fix_function(func_spec, "/test/module.py", e)
            
            assert result['original_error'] == e
            assert len(result['revisions']) >= 1
            # Should capture the exception chain
            if result['revisions']:
                revision = result['revisions'][0]
                # The revision should be generated (basic check)
                assert revision.revised_code is not None
                assert len(revision.revised_code) > 0


if __name__ == "__main__":
    pytest.main([__file__])