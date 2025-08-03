"""
Unit tests for enhanced dependency planning data models.

Tests the new data models: StructureAnalysis, FunctionGap, ImportIssue, 
ImportIssueType, and OptimizationSuggestion.
"""

import pytest
from datetime import datetime
from a3.core.models import (
    StructureAnalysis, FunctionGap, ImportIssue, ImportIssueType,
    OptimizationSuggestion, Module, FunctionSpec, EnhancedDependencyGraph,
    ValidationError
)


class TestImportIssueType:
    """Test the ImportIssueType enum."""
    
    def test_enum_values(self):
        """Test that all expected enum values exist."""
        assert ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION.value == "relative_import_in_function"
        assert ImportIssueType.INCORRECT_INDENTATION.value == "incorrect_indentation"
        assert ImportIssueType.UNRESOLVABLE_RELATIVE_IMPORT.value == "unresolvable_relative_import"
        assert ImportIssueType.CIRCULAR_IMPORT_RISK.value == "circular_import_risk"


class TestImportIssue:
    """Test the ImportIssue data model."""
    
    def test_valid_import_issue(self):
        """Test creating a valid import issue."""
        issue = ImportIssue(
            file_path="src/module.py",
            line_number=10,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from .utils import helper",
            suggested_fix="from src.utils import helper",
            context="Inside function definition"
        )
        
        assert issue.file_path == "src/module.py"
        assert issue.line_number == 10
        assert issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION
        assert issue.problematic_import == "from .utils import helper"
        assert issue.suggested_fix == "from src.utils import helper"
        assert issue.context == "Inside function definition"
    
    def test_import_issue_validation_success(self):
        """Test that valid import issue passes validation."""
        issue = ImportIssue(
            file_path="test.py",
            line_number=5,
            issue_type=ImportIssueType.INCORRECT_INDENTATION,
            problematic_import="import os",
            suggested_fix="    import os"
        )
        
        # Should not raise any exception
        issue.validate()
    
    def test_empty_file_path_validation(self):
        """Test validation fails for empty file path."""
        issue = ImportIssue(
            file_path="",
            line_number=1,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from . import test",
            suggested_fix="from module import test"
        )
        
        with pytest.raises(ValidationError, match="Import issue file path cannot be empty"):
            issue.validate()
    
    def test_invalid_line_number_validation(self):
        """Test validation fails for invalid line number."""
        issue = ImportIssue(
            file_path="test.py",
            line_number=0,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from . import test",
            suggested_fix="from module import test"
        )
        
        with pytest.raises(ValidationError, match="Line number must be positive"):
            issue.validate()
    
    def test_empty_problematic_import_validation(self):
        """Test validation fails for empty problematic import."""
        issue = ImportIssue(
            file_path="test.py",
            line_number=1,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="",
            suggested_fix="from module import test"
        )
        
        with pytest.raises(ValidationError, match="Problematic import cannot be empty"):
            issue.validate()
    
    def test_empty_suggested_fix_validation(self):
        """Test validation fails for empty suggested fix."""
        issue = ImportIssue(
            file_path="test.py",
            line_number=1,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from . import test",
            suggested_fix=""
        )
        
        with pytest.raises(ValidationError, match="Suggested fix cannot be empty"):
            issue.validate()


class TestFunctionGap:
    """Test the FunctionGap data model."""
    
    def test_valid_function_gap(self):
        """Test creating a valid function gap."""
        gap = FunctionGap(
            suggested_name="calculate_total",
            suggested_module="math_utils",
            reason="Needed for sum calculations",
            confidence=0.85,
            dependencies=["math_utils.add_numbers"],
            dependents=["reporting.generate_report"]
        )
        
        assert gap.suggested_name == "calculate_total"
        assert gap.suggested_module == "math_utils"
        assert gap.reason == "Needed for sum calculations"
        assert gap.confidence == 0.85
        assert gap.dependencies == ["math_utils.add_numbers"]
        assert gap.dependents == ["reporting.generate_report"]
    
    def test_function_gap_validation_success(self):
        """Test that valid function gap passes validation."""
        gap = FunctionGap(
            suggested_name="valid_function",
            suggested_module="valid.module",
            reason="Valid reason",
            confidence=0.5
        )
        
        # Should not raise any exception
        gap.validate()
    
    def test_empty_suggested_name_validation(self):
        """Test validation fails for empty suggested name."""
        gap = FunctionGap(
            suggested_name="",
            suggested_module="module",
            reason="reason",
            confidence=0.5
        )
        
        with pytest.raises(ValidationError, match="Function gap suggested name cannot be empty"):
            gap.validate()
    
    def test_invalid_function_name_validation(self):
        """Test validation fails for invalid function name."""
        gap = FunctionGap(
            suggested_name="123invalid",
            suggested_module="module",
            reason="reason",
            confidence=0.5
        )
        
        with pytest.raises(ValidationError, match="Invalid function name"):
            gap.validate()
    
    def test_empty_suggested_module_validation(self):
        """Test validation fails for empty suggested module."""
        gap = FunctionGap(
            suggested_name="function",
            suggested_module="",
            reason="reason",
            confidence=0.5
        )
        
        with pytest.raises(ValidationError, match="Function gap suggested module cannot be empty"):
            gap.validate()
    
    def test_invalid_module_name_validation(self):
        """Test validation fails for invalid module name."""
        gap = FunctionGap(
            suggested_name="function",
            suggested_module="123invalid",
            reason="reason",
            confidence=0.5
        )
        
        with pytest.raises(ValidationError, match="Invalid module name"):
            gap.validate()
    
    def test_empty_reason_validation(self):
        """Test validation fails for empty reason."""
        gap = FunctionGap(
            suggested_name="function",
            suggested_module="module",
            reason="",
            confidence=0.5
        )
        
        with pytest.raises(ValidationError, match="Function gap reason cannot be empty"):
            gap.validate()
    
    def test_invalid_confidence_validation(self):
        """Test validation fails for invalid confidence values."""
        # Test confidence > 1.0
        gap1 = FunctionGap(
            suggested_name="function",
            suggested_module="module",
            reason="reason",
            confidence=1.5
        )
        
        with pytest.raises(ValidationError, match="Function gap confidence must be between 0.0 and 1.0"):
            gap1.validate()
        
        # Test confidence < 0.0
        gap2 = FunctionGap(
            suggested_name="function",
            suggested_module="module",
            reason="reason",
            confidence=-0.1
        )
        
        with pytest.raises(ValidationError, match="Function gap confidence must be between 0.0 and 1.0"):
            gap2.validate()
    
    def test_invalid_dependency_format_validation(self):
        """Test validation fails for invalid dependency format."""
        gap = FunctionGap(
            suggested_name="function",
            suggested_module="module",
            reason="reason",
            confidence=0.5,
            dependencies=["invalid_format"]
        )
        
        with pytest.raises(ValidationError, match="Invalid dependency function format"):
            gap.validate()
    
    def test_empty_dependency_validation(self):
        """Test validation fails for empty dependency."""
        gap = FunctionGap(
            suggested_name="function",
            suggested_module="module",
            reason="reason",
            confidence=0.5,
            dependencies=[""]
        )
        
        with pytest.raises(ValidationError, match="Dependency function name cannot be empty"):
            gap.validate()


class TestOptimizationSuggestion:
    """Test the OptimizationSuggestion data model."""
    
    def test_valid_optimization_suggestion(self):
        """Test creating a valid optimization suggestion."""
        suggestion = OptimizationSuggestion(
            suggestion_type="refactor",
            description="Split large function into smaller ones",
            affected_modules=["utils", "helpers"],
            affected_functions=["utils.large_function"],
            priority="high",
            estimated_effort="medium"
        )
        
        assert suggestion.suggestion_type == "refactor"
        assert suggestion.description == "Split large function into smaller ones"
        assert suggestion.affected_modules == ["utils", "helpers"]
        assert suggestion.affected_functions == ["utils.large_function"]
        assert suggestion.priority == "high"
        assert suggestion.estimated_effort == "medium"
    
    def test_optimization_suggestion_defaults(self):
        """Test default values for optimization suggestion."""
        suggestion = OptimizationSuggestion(
            suggestion_type="refactor",
            description="Test description"
        )
        
        assert suggestion.affected_modules == []
        assert suggestion.affected_functions == []
        assert suggestion.priority == "medium"
        assert suggestion.estimated_effort == "unknown"
    
    def test_optimization_suggestion_validation_success(self):
        """Test that valid optimization suggestion passes validation."""
        suggestion = OptimizationSuggestion(
            suggestion_type="valid_type",
            description="Valid description",
            priority="low",
            estimated_effort="small"
        )
        
        # Should not raise any exception
        suggestion.validate()
    
    def test_empty_suggestion_type_validation(self):
        """Test validation fails for empty suggestion type."""
        suggestion = OptimizationSuggestion(
            suggestion_type="",
            description="description"
        )
        
        with pytest.raises(ValidationError, match="Optimization suggestion type cannot be empty"):
            suggestion.validate()
    
    def test_empty_description_validation(self):
        """Test validation fails for empty description."""
        suggestion = OptimizationSuggestion(
            suggestion_type="type",
            description=""
        )
        
        with pytest.raises(ValidationError, match="Optimization suggestion description cannot be empty"):
            suggestion.validate()
    
    def test_invalid_priority_validation(self):
        """Test validation fails for invalid priority."""
        suggestion = OptimizationSuggestion(
            suggestion_type="type",
            description="description",
            priority="invalid"
        )
        
        with pytest.raises(ValidationError, match="Priority must be one of"):
            suggestion.validate()
    
    def test_invalid_estimated_effort_validation(self):
        """Test validation fails for invalid estimated effort."""
        suggestion = OptimizationSuggestion(
            suggestion_type="type",
            description="description",
            estimated_effort="invalid"
        )
        
        with pytest.raises(ValidationError, match="Estimated effort must be one of"):
            suggestion.validate()


class TestStructureAnalysis:
    """Test the StructureAnalysis data model."""
    
    def test_valid_structure_analysis(self):
        """Test creating a valid structure analysis."""
        # Create test modules
        module1 = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py"
        )
        
        # Create test function gap
        gap = FunctionGap(
            suggested_name="test_function",
            suggested_module="test_module",
            reason="Test reason",
            confidence=0.8
        )
        
        # Create test import issue
        issue = ImportIssue(
            file_path="test.py",
            line_number=1,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from . import test",
            suggested_fix="from module import test"
        )
        
        # Create test optimization suggestion
        suggestion = OptimizationSuggestion(
            suggestion_type="refactor",
            description="Test suggestion"
        )
        
        analysis = StructureAnalysis(
            existing_modules=[module1],
            complexity_metrics={"total_functions": 5},
            missing_functions=[gap],
            import_issues=[issue],
            optimization_opportunities=[suggestion]
        )
        
        assert len(analysis.existing_modules) == 1
        assert analysis.complexity_metrics["total_functions"] == 5
        assert len(analysis.missing_functions) == 1
        assert len(analysis.import_issues) == 1
        assert len(analysis.optimization_opportunities) == 1
        assert isinstance(analysis.analysis_timestamp, datetime)
    
    def test_structure_analysis_defaults(self):
        """Test default values for structure analysis."""
        analysis = StructureAnalysis()
        
        assert analysis.existing_modules == []
        assert analysis.enhanced_graph is None
        assert analysis.complexity_metrics == {}
        assert analysis.missing_functions == []
        assert analysis.import_issues == []
        assert analysis.optimization_opportunities == []
        assert isinstance(analysis.analysis_timestamp, datetime)
    
    def test_structure_analysis_validation_success(self):
        """Test that valid structure analysis passes validation."""
        module = Module(
            name="valid_module",
            description="Valid module",
            file_path="valid_module.py"
        )
        
        analysis = StructureAnalysis(
            existing_modules=[module],
            complexity_metrics={"test": "value"}
        )
        
        # Should not raise any exception
        analysis.validate()
    
    def test_duplicate_module_validation(self):
        """Test validation fails for duplicate module names."""
        module1 = Module(
            name="duplicate",
            description="First module",
            file_path="duplicate1.py"
        )
        module2 = Module(
            name="duplicate",
            description="Second module",
            file_path="duplicate2.py"
        )
        
        analysis = StructureAnalysis(existing_modules=[module1, module2])
        
        with pytest.raises(ValidationError, match="Duplicate module name"):
            analysis.validate()
    
    def test_duplicate_function_gap_validation(self):
        """Test validation fails for duplicate function gaps."""
        gap1 = FunctionGap(
            suggested_name="duplicate",
            suggested_module="module",
            reason="First gap",
            confidence=0.5
        )
        gap2 = FunctionGap(
            suggested_name="duplicate",
            suggested_module="module",
            reason="Second gap",
            confidence=0.7
        )
        
        analysis = StructureAnalysis(missing_functions=[gap1, gap2])
        
        with pytest.raises(ValidationError, match="Duplicate function gap"):
            analysis.validate()
    
    def test_invalid_complexity_metrics_validation(self):
        """Test validation fails for invalid complexity metrics."""
        analysis = StructureAnalysis(complexity_metrics="not_a_dict")
        
        with pytest.raises(ValidationError, match="Complexity metrics must be a dictionary"):
            analysis.validate()
    
    def test_get_total_functions(self):
        """Test getting total functions count."""
        func1 = FunctionSpec(
            name="func1",
            module="module1",
            docstring="Function 1"
        )
        func2 = FunctionSpec(
            name="func2",
            module="module1",
            docstring="Function 2"
        )
        func3 = FunctionSpec(
            name="func3",
            module="module2",
            docstring="Function 3"
        )
        
        module1 = Module(
            name="module1",
            description="Module 1",
            file_path="module1.py",
            functions=[func1, func2]
        )
        module2 = Module(
            name="module2",
            description="Module 2",
            file_path="module2.py",
            functions=[func3]
        )
        
        analysis = StructureAnalysis(existing_modules=[module1, module2])
        
        assert analysis.get_total_functions() == 3
    
    def test_get_modules_with_issues(self):
        """Test getting modules with import issues."""
        issue1 = ImportIssue(
            file_path="src/module1.py",
            line_number=1,
            issue_type=ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION,
            problematic_import="from . import test",
            suggested_fix="from module import test"
        )
        issue2 = ImportIssue(
            file_path="module2.py",
            line_number=5,
            issue_type=ImportIssueType.INCORRECT_INDENTATION,
            problematic_import="import os",
            suggested_fix="    import os"
        )
        
        analysis = StructureAnalysis(import_issues=[issue1, issue2])
        modules_with_issues = analysis.get_modules_with_issues()
        
        assert "module1" in modules_with_issues
        assert "module2" in modules_with_issues
        assert len(modules_with_issues) == 2
    
    def test_get_high_priority_gaps(self):
        """Test getting high priority function gaps."""
        gap1 = FunctionGap(
            suggested_name="high_confidence",
            suggested_module="module",
            reason="High confidence gap",
            confidence=0.9
        )
        gap2 = FunctionGap(
            suggested_name="low_confidence",
            suggested_module="module",
            reason="Low confidence gap",
            confidence=0.3
        )
        gap3 = FunctionGap(
            suggested_name="medium_confidence",
            suggested_module="module",
            reason="Medium confidence gap",
            confidence=0.7
        )
        
        analysis = StructureAnalysis(missing_functions=[gap1, gap2, gap3])
        high_priority = analysis.get_high_priority_gaps()
        
        assert len(high_priority) == 2
        assert gap1 in high_priority
        assert gap3 in high_priority
        assert gap2 not in high_priority
    
    def test_get_critical_optimization_suggestions(self):
        """Test getting critical optimization suggestions."""
        suggestion1 = OptimizationSuggestion(
            suggestion_type="refactor",
            description="High priority suggestion",
            priority="high"
        )
        suggestion2 = OptimizationSuggestion(
            suggestion_type="optimize",
            description="Medium priority suggestion",
            priority="medium"
        )
        suggestion3 = OptimizationSuggestion(
            suggestion_type="cleanup",
            description="Another high priority suggestion",
            priority="high"
        )
        
        analysis = StructureAnalysis(
            optimization_opportunities=[suggestion1, suggestion2, suggestion3]
        )
        critical_suggestions = analysis.get_critical_optimization_suggestions()
        
        assert len(critical_suggestions) == 2
        assert suggestion1 in critical_suggestions
        assert suggestion3 in critical_suggestions
        assert suggestion2 not in critical_suggestions


if __name__ == "__main__":
    pytest.main([__file__])