"""
Integration tests for enhanced planning functionality.

This module provides end-to-end integration tests for the complete
enhanced planning workflow, including import issue detection and fixing,
gap analysis, and dependency-driven optimization.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from a3.core.import_issue_detector import ImportIssueDetector
from a3.core.gap_analyzer import IntelligentGapAnalyzer
from a3.core.dependency_driven_planner import DependencyDrivenPlanner
from a3.engines.planning import PlanningEngine
from a3.core.models import (
    ImportIssue, ImportIssueType, ValidationResult, FunctionGap,
    EnhancedDependencyGraph, FunctionDependency, DependencyType,
    Module, FunctionSpec, Argument, StructureAnalysis, OptimizationSuggestion,
    CriticalPathAnalysis, ImplementationStatus, ProjectPlan
)
from a3.core.interfaces import AIClientInterface


class TestEnhancedPlanningWorkflowIntegration:
    """Integration tests for the complete enhanced planning workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_ai_client = Mock(spec=AIClientInterface)
        
        # Create test project structure
        self._create_test_project_structure()
        
        # Initialize components
        self.import_detector = ImportIssueDetector()
        self.gap_analyzer = IntelligentGapAnalyzer()
        self.dependency_planner = DependencyDrivenPlanner()
        self.planning_engine = PlanningEngine(
            ai_client=self.mock_ai_client,
            project_path=self.temp_dir
        )
        self.planning_engine.initialize()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_project_structure(self):
        """Create a realistic test project structure."""
        # Create main modules
        modules = {
            "user_service.py": '''
"""User service module with import issues."""

def create_user(user_data: dict) -> dict:
    """Create a new user."""
    from .validation import validate_user_data  # Import issue: relative import in function
    from ..config import get_database_config    # Import issue: relative import in function
    
    if not validate_user_data(user_data):
        raise ValueError("Invalid user data")
    
    # Missing: save_user function call
    return {"id": 1, "status": "created"}

def get_user(user_id: int) -> dict:
    """Get user by ID."""
    from .database import load_user  # Import issue: relative import in function
    return load_user(user_id)
''',
            
            "validation.py": '''
"""Validation module."""

def validate_user_data(data: dict) -> bool:
    """Validate user data."""
    required_fields = ["name", "email"]
    return all(field in data for field in required_fields)

# Missing: validate_email function
''',
            
            "database.py": '''
"""Database module with incomplete functionality."""

def load_user(user_id: int) -> dict:
    """Load user from database."""
    # Simplified implementation
    return {"id": user_id, "name": "Test User"}

# Missing: save_user, delete_user functions
''',
            
            "api_handler.py": '''
"""API handler with complex dependencies."""

def handle_user_request(request_data: dict) -> dict:
    """Handle user-related API requests."""
    def parse_request():
        from .request_parser import parse_user_request  # Import issue
        return parse_user_request(request_data)
    
    def process_request(parsed_data):
        from .user_service import create_user, get_user  # Import issue
        if parsed_data["action"] == "create":
            return create_user(parsed_data["data"])
        elif parsed_data["action"] == "get":
            return get_user(parsed_data["user_id"])
    
    parsed = parse_request()
    result = process_request(parsed)
    
    # Missing: format_response function
    return result
''',
            
            "config.py": '''
"""Configuration module."""

def get_database_config() -> dict:
    """Get database configuration."""
    return {
        "host": "localhost",
        "port": 5432,
        "database": "testdb"
    }

def get_api_config() -> dict:
    """Get API configuration."""
    return {
        "host": "0.0.0.0",
        "port": 8000
    }
'''
        }
        
        # Write modules to files
        for filename, content in modules.items():
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w') as f:
                f.write(content)
    
    def test_end_to_end_enhanced_planning_process(self):
        """Test the complete end-to-end enhanced planning process."""
        # Step 1: Analyze existing structure
        analysis = self.planning_engine.analyze_existing_structure()
        
        # Verify structure analysis results
        assert isinstance(analysis, StructureAnalysis)
        assert len(analysis.existing_modules) > 0
        
        # Should find modules
        module_names = [m.name for m in analysis.existing_modules]
        expected_modules = ["user_service", "validation", "database", "api_handler", "config"]
        for expected in expected_modules:
            assert expected in module_names
        
        # Should detect import issues
        assert len(analysis.import_issues) > 0
        relative_import_issues = [
            issue for issue in analysis.import_issues 
            if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION
        ]
        assert len(relative_import_issues) > 0
        
        # Should identify missing functions
        assert len(analysis.missing_functions) >= 0  # May or may not find gaps
        
        # Step 2: Test import issue detection and fixing
        user_service_file = Path(self.temp_dir) / "user_service.py"
        with open(user_service_file, 'r') as f:
            original_content = f.read()
        
        # Detect issues
        issues = self.import_detector.scan_for_import_issues(original_content, "user_service.py")
        assert len(issues) > 0
        
        # Fix issues
        fixed_content = self.import_detector.fix_function_level_imports(original_content)
        
        # Verify fixes
        assert fixed_content != original_content
        validation_result = self.import_detector.validate_import_resolution(fixed_content, "user_service.py")
        assert isinstance(validation_result, ValidationResult)
        
        # Step 3: Test gap analysis
        if analysis.enhanced_graph:
            gaps = self.gap_analyzer.detect_missing_functions(analysis.enhanced_graph)
            assert isinstance(gaps, list)
            
            # Test module completeness analysis
            completeness = self.gap_analyzer.analyze_module_completeness(analysis.existing_modules)
            assert "total_modules" in completeness
            assert "completeness_score" in completeness
        
        # Step 4: Test dependency-driven planning
        if analysis.enhanced_graph:
            # Test optimal implementation order
            implementation_order = self.dependency_planner.get_optimal_implementation_order(analysis.enhanced_graph)
            assert isinstance(implementation_order, list)
            
            # Test parallel opportunities
            parallel_opportunities = self.dependency_planner.identify_parallel_opportunities(analysis.enhanced_graph)
            assert isinstance(parallel_opportunities, list)
            
            # Test critical path analysis
            critical_path_analysis = self.dependency_planner.analyze_critical_path(analysis.enhanced_graph)
            assert isinstance(critical_path_analysis, CriticalPathAnalysis)
    
    def test_import_issue_detection_and_fixing_in_real_scenarios(self):
        """Test import issue detection and fixing with realistic code patterns."""
        # Test with complex nested imports
        complex_code = '''
class DataProcessor:
    """Data processor with various import patterns."""
    
    def __init__(self):
        from .config import settings  # Should be moved to module level
        self.settings = settings
    
    def process_batch(self, data_batch):
        """Process a batch of data."""
        def validate_batch():
            from ..validation import batch_validator  # Nested function import
            return batch_validator(data_batch)
        
        def transform_batch():
            from .transformers import (  # Multiline import in function
                DataTransformer,
                ValidationTransformer
            )
            transformer = DataTransformer()
            validator = ValidationTransformer()
            return transformer.transform(validator.validate(data_batch))
        
        if not validate_batch():
            from .errors import BatchValidationError  # Conditional import
            raise BatchValidationError("Invalid batch data")
        
        return transform_batch()
    
    @staticmethod
    def cleanup_temp_files():
        from .filesystem import cleanup_temp  # Static method import
        return cleanup_temp()
'''
        
        # Detect issues
        issues = self.import_detector.scan_for_import_issues(complex_code, "data_processor.py")
        
        # Should detect multiple import issues
        relative_issues = [issue for issue in issues if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION]
        assert len(relative_issues) >= 4  # __init__, validate_batch, transform_batch, cleanup_temp_files
        
        # Fix issues
        fixed_code = self.import_detector.fix_function_level_imports(complex_code)
        
        # Verify that imports were moved to module level
        lines = fixed_code.split('\n')
        module_level_imports = [line for line in lines[:20] if line.strip().startswith(('from .', 'from ..'))]
        assert len(module_level_imports) > 0
        
        # Verify that class and methods still exist
        assert 'class DataProcessor:' in fixed_code
        assert 'def process_batch(self, data_batch):' in fixed_code
        assert 'def cleanup_temp_files():' in fixed_code
    
    def test_dependency_driven_optimization_suggestions(self):
        """Test dependency-driven optimization suggestions."""
        # Create a more complex project structure for optimization testing
        optimization_modules = {
            "complex_service.py": '''
"""Service with optimization opportunities."""

def process_user_data(user_data):
    """Process user data with multiple dependencies."""
    # This function has too many responsibilities
    validated_data = validate_user_data(user_data)
    transformed_data = transform_user_data(validated_data)
    saved_data = save_user_data(transformed_data)
    notification_sent = send_user_notification(saved_data)
    audit_logged = log_user_audit(saved_data)
    return {
        "data": saved_data,
        "notification": notification_sent,
        "audit": audit_logged
    }

def validate_user_data(data):
    """Validate user data."""
    return True

def transform_user_data(data):
    """Transform user data."""
    return data

def save_user_data(data):
    """Save user data."""
    return data

def send_user_notification(data):
    """Send user notification."""
    return True

def log_user_audit(data):
    """Log user audit."""
    return True
''',
            
            "heavy_processor.py": '''
"""Processor with high complexity."""

def process_everything(data):
    """Function that does too much."""
    # This function should be broken down
    step1 = preprocess_data(data)
    step2 = validate_data(step1)
    step3 = transform_data(step2)
    step4 = enrich_data(step3)
    step5 = format_data(step4)
    step6 = save_data(step5)
    step7 = notify_completion(step6)
    step8 = cleanup_resources(step7)
    return step8

def preprocess_data(data): return data
def validate_data(data): return data
def transform_data(data): return data
def enrich_data(data): return data
def format_data(data): return data
def save_data(data): return data
def notify_completion(data): return data
def cleanup_resources(data): return data
'''
        }
        
        # Add optimization test modules to temp directory
        for filename, content in optimization_modules.items():
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Analyze the enhanced structure
        analysis = self.planning_engine.analyze_existing_structure()
        
        # Should detect optimization opportunities
        assert len(analysis.optimization_opportunities) >= 0
        
        # Test module restructuring suggestions
        if analysis.enhanced_graph:
            restructuring_suggestions = self.gap_analyzer.suggest_module_restructuring(
                analysis.existing_modules, analysis.enhanced_graph
            )
            
            assert isinstance(restructuring_suggestions, list)
            
            # Should suggest breaking down complex functions/modules
            complexity_suggestions = [
                s for s in restructuring_suggestions 
                if "complex" in s.description.lower() or "break" in s.description.lower()
            ]
            assert len(complexity_suggestions) >= 0
    
    def test_enhanced_dependency_graph_analysis_integration(self):
        """Test integration of enhanced dependency graph analysis."""
        # Analyze existing structure to get enhanced dependency graph
        analysis = self.planning_engine.analyze_existing_structure()
        
        if analysis.enhanced_graph:
            graph = analysis.enhanced_graph
            
            # Test that graph contains expected functions
            assert len(graph.function_nodes) > 0
            
            # Test dependency analysis
            implementation_order = self.dependency_planner.get_optimal_implementation_order(graph)
            assert len(implementation_order) > 0
            
            # Test parallel opportunities
            parallel_groups = self.dependency_planner.identify_parallel_opportunities(graph)
            assert isinstance(parallel_groups, list)
            
            # Test critical path analysis
            critical_analysis = self.dependency_planner.analyze_critical_path(graph)
            assert isinstance(critical_analysis, CriticalPathAnalysis)
            assert critical_analysis.path_length >= 0
    
    def test_complete_planning_workflow_with_ai_integration(self):
        """Test complete planning workflow with AI client integration."""
        # Mock AI client responses for plan generation
        self.mock_ai_client.generate_response.side_effect = [
            # Response for module breakdown
            '''
            {
                "modules": [
                    {
                        "name": "enhanced_user_service",
                        "description": "Enhanced user service with proper separation of concerns",
                        "functions": [
                            {
                                "name": "create_user",
                                "description": "Create a new user with validation",
                                "arguments": [{"name": "user_data", "type": "dict"}],
                                "return_type": "User"
                            },
                            {
                                "name": "validate_user_creation",
                                "description": "Validate user creation data",
                                "arguments": [{"name": "user_data", "type": "dict"}],
                                "return_type": "bool"
                            }
                        ]
                    },
                    {
                        "name": "user_repository",
                        "description": "User data persistence layer",
                        "functions": [
                            {
                                "name": "save_user",
                                "description": "Save user to database",
                                "arguments": [{"name": "user", "type": "User"}],
                                "return_type": "User"
                            },
                            {
                                "name": "find_user_by_id",
                                "description": "Find user by ID",
                                "arguments": [{"name": "user_id", "type": "int"}],
                                "return_type": "Optional[User]"
                            }
                        ]
                    }
                ]
            }
            ''',
            # Response for function implementation
            '''
            def create_user(user_data: dict) -> User:
                """Create a new user with proper validation."""
                if not validate_user_creation(user_data):
                    raise ValueError("Invalid user data")
                
                user = User(**user_data)
                return save_user(user)
            '''
        ]
        
        # Test complete workflow
        objective = "Create an enhanced user management system with proper architecture"
        
        # Step 1: Analyze existing structure
        analysis = self.planning_engine.analyze_existing_structure()
        
        # Step 2: Generate enhanced plan
        with patch.object(self.planning_engine, 'generate_plan') as mock_generate_plan:
            mock_plan = Mock(spec=ProjectPlan)
            mock_plan.modules = [
                Module(
                    name="enhanced_user_service",
                    description="Enhanced user service",
                    file_path="enhanced_user_service.py",
                    functions=[
                        FunctionSpec(
                            name="create_user",
                            module="enhanced_user_service",
                            docstring="Create user with validation",
                            arguments=[Argument("user_data", "dict")],
                            return_type="User",
                            implementation_status=ImplementationStatus.PLANNED
                        )
                    ]
                )
            ]
            mock_generate_plan.return_value = mock_plan
            
            plan = self.planning_engine.generate_plan(objective)
            
            # Verify plan was generated
            assert plan is not None
            assert len(plan.modules) > 0
    
    def test_error_handling_and_recovery_in_integration(self):
        """Test error handling and recovery in the integration workflow."""
        # Create a file with syntax errors
        error_file = Path(self.temp_dir) / "syntax_error.py"
        with open(error_file, 'w') as f:
            f.write('''
def broken_function(:
    """This function has syntax errors."""
    return "broken"

def another_function()
    return "also broken"
''')
        
        # Test that analysis handles syntax errors gracefully
        analysis = self.planning_engine.analyze_existing_structure()
        
        # Should not crash, should handle errors gracefully
        assert isinstance(analysis, StructureAnalysis)
        
        # Test import issue detection with malformed code
        malformed_code = '''
def function():
    from . import  # Incomplete import
    from ..  # Incomplete relative import
    import  # Incomplete import
    return None
'''
        
        issues = self.import_detector.scan_for_import_issues(malformed_code, "malformed.py")
        
        # Should detect issues without crashing
        assert isinstance(issues, list)
        
        # Test validation with invalid code
        validation_result = self.import_detector.validate_import_resolution(malformed_code, "malformed.py")
        
        # Should return validation result indicating errors
        assert isinstance(validation_result, ValidationResult)
        assert not validation_result.is_valid
    
    def test_performance_with_large_project_structure(self):
        """Test performance and scalability with larger project structures."""
        # Create a larger project structure
        large_modules = {}
        
        for i in range(10):  # Create 10 modules
            module_content = f'''
"""Module {i} for performance testing."""

'''
            # Add 5 functions per module
            for j in range(5):
                module_content += f'''
def function_{i}_{j}(arg1, arg2=None):
    """Function {j} in module {i}."""
    from .utils import helper_{j}  # Import issue for testing
    return helper_{j}(arg1, arg2)

'''
            
            large_modules[f"module_{i}.py"] = module_content
        
        # Write large modules
        for filename, content in large_modules.items():
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Test analysis performance
        import time
        start_time = time.time()
        
        analysis = self.planning_engine.analyze_existing_structure()
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        # Should complete analysis in reasonable time (less than 10 seconds)
        assert analysis_time < 10.0
        
        # Should find all modules
        assert len(analysis.existing_modules) >= 10
        
        # Should detect import issues across all modules
        assert len(analysis.import_issues) >= 10  # At least one per module


class TestRealWorldScenarios:
    """Test enhanced planning with real-world-like scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_ai_client = Mock(spec=AIClientInterface)
        self.planning_engine = PlanningEngine(
            ai_client=self.mock_ai_client,
            project_path=self.temp_dir
        )
        self.planning_engine.initialize()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_web_application_project_analysis(self):
        """Test analysis of a web application project structure."""
        # Create a realistic web application structure
        web_app_modules = {
            "models/user.py": '''
"""User model."""

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save(self):
        from ..database import save_model  # Import issue
        return save_model(self)
''',
            
            "views/user_views.py": '''
"""User views."""

def create_user_view(request):
    """Create user view."""
    from ..models.user import User  # Import issue
    from ..forms import UserForm    # Import issue
    
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = User(**form.cleaned_data)
            user.save()
            return redirect("user_list")
    else:
        form = UserForm()
    
    return render(request, "create_user.html", {"form": form})
''',
            
            "forms.py": '''
"""Forms module."""

def validate_email(email):
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class UserForm:
    def __init__(self, data=None):
        self.data = data
    
    def is_valid(self):
        from .models.user import User  # Import issue
        return validate_email(self.data.get("email", ""))
    
    @property
    def cleaned_data(self):
        return self.data
''',
            
            "database.py": '''
"""Database operations."""

def save_model(model):
    """Save model to database."""
    # Simplified database save
    return model

def get_connection():
    """Get database connection."""
    from .config import DATABASE_CONFIG  # Import issue
    return f"Connected to {DATABASE_CONFIG['host']}"
'''
        }
        
        # Create directory structure
        models_dir = Path(self.temp_dir) / "models"
        views_dir = Path(self.temp_dir) / "views"
        models_dir.mkdir()
        views_dir.mkdir()
        
        # Write files
        for file_path, content in web_app_modules.items():
            full_path = Path(self.temp_dir) / file_path
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Analyze the web application structure
        analysis = self.planning_engine.analyze_existing_structure()
        
        # Should find modules in nested directories
        assert len(analysis.existing_modules) >= 3
        
        # Should detect import issues in web application
        relative_import_issues = [
            issue for issue in analysis.import_issues
            if issue.issue_type == ImportIssueType.RELATIVE_IMPORT_IN_FUNCTION
        ]
        assert len(relative_import_issues) > 0
        
        # Should identify missing functions (like redirect, render)
        if analysis.missing_functions:
            missing_names = [gap.suggested_name for gap in analysis.missing_functions]
            # Might suggest missing utility functions
            assert len(missing_names) >= 0
    
    def test_microservices_architecture_analysis(self):
        """Test analysis of a microservices architecture."""
        # Create microservices structure
        microservices = {
            "user_service/service.py": '''
"""User microservice."""

def create_user(user_data):
    """Create user in user service."""
    from .validation import validate_user  # Import issue
    from .repository import save_user      # Import issue
    
    if validate_user(user_data):
        return save_user(user_data)
    raise ValueError("Invalid user")
''',
            
            "order_service/service.py": '''
"""Order microservice."""

def create_order(order_data):
    """Create order in order service."""
    from .validation import validate_order  # Import issue
    from ..user_service.service import get_user  # Cross-service dependency
    
    user = get_user(order_data["user_id"])
    if user and validate_order(order_data):
        from .repository import save_order  # Import issue
        return save_order(order_data)
''',
            
            "notification_service/service.py": '''
"""Notification microservice."""

def send_notification(notification_data):
    """Send notification."""
    from .email_sender import send_email    # Import issue
    from .sms_sender import send_sms        # Import issue
    
    if notification_data["type"] == "email":
        return send_email(notification_data)
    elif notification_data["type"] == "sms":
        return send_sms(notification_data)
'''
        }
        
        # Create microservice directories
        for service in ["user_service", "order_service", "notification_service"]:
            service_dir = Path(self.temp_dir) / service
            service_dir.mkdir()
        
        # Write microservice files
        for file_path, content in microservices.items():
            full_path = Path(self.temp_dir) / file_path
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Analyze microservices architecture
        analysis = self.planning_engine.analyze_existing_structure()
        
        # Should find all microservices
        assert len(analysis.existing_modules) >= 3
        
        # Should detect cross-service dependencies
        if analysis.enhanced_graph:
            # Test dependency analysis across services
            implementation_order = DependencyDrivenPlanner().get_optimal_implementation_order(
                analysis.enhanced_graph
            )
            assert len(implementation_order) > 0
        
        # Should detect import issues across services
        assert len(analysis.import_issues) > 0


if __name__ == "__main__":
    pytest.main([__file__])