#!/usr/bin/env python3
"""
Comprehensive test for the enhanced function-level dependency system.

This test verifies that all components of the enhanced dependency system
work together correctly in the A3 pipeline.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the a3 package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from a3 import A3, EnhancedDependencyGraph, FunctionDependency, DependencyType
from a3.core.models import Module, FunctionSpec, Argument, ImplementationStatus
from a3.managers.dependency import DependencyAnalyzer


def test_enhanced_dependency_models():
    """Test the enhanced dependency models."""
    print("🧪 Testing Enhanced Dependency Models...")
    
    # Test FunctionDependency creation
    dep = FunctionDependency(
        from_function="module_a.function_1",
        to_function="module_b.function_2",
        dependency_type=DependencyType.DIRECT_CALL,
        confidence=0.9,
        line_number=42,
        context="Direct function call"
    )
    
    assert dep.from_function == "module_a.function_1"
    assert dep.to_function == "module_b.function_2"
    assert dep.dependency_type == DependencyType.DIRECT_CALL
    assert dep.confidence == 0.9
    
    # Test EnhancedDependencyGraph
    graph = EnhancedDependencyGraph()
    
    # Add functions
    graph.add_function("function_1", "module_a")
    graph.add_function("function_2", "module_b")
    graph.add_function("function_3", "module_a")
    
    assert len(graph.function_nodes) == 3
    assert "module_a.function_1" in graph.function_nodes
    assert "module_b.function_2" in graph.function_nodes
    
    # Add dependency
    graph.add_function_dependency(dep)
    
    assert len(graph.function_dependencies) == 1
    assert len(graph.module_edges) == 1  # Cross-module dependency should create module edge
    
    # Test implementation order
    order = graph.get_function_implementation_order()
    assert len(order) == 3
    
    # function_2 should come before function_1 (dependency order)
    func1_index = order.index("module_a.function_1")
    func2_index = order.index("module_b.function_2")
    assert func2_index < func1_index, "Dependencies should be implemented first"
    
    print("✅ Enhanced dependency models working correctly")


def test_dependency_analyzer_enhancements():
    """Test the enhanced dependency analyzer."""
    print("\n🔍 Testing Enhanced Dependency Analyzer...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test modules
        modules = []
        
        # Module A with functions that depend on Module B
        module_a = Module(
            name="module_a",
            description="Module A with dependencies",
            file_path="module_a.py",
            dependencies=["module_b"],
            functions=[
                FunctionSpec(
                    name="process_data",
                    module="module_a",
                    docstring="Process data using validate_input from module_b",
                    arguments=[Argument("data", "Dict", None, "Input data")],
                    return_type="Dict",
                    implementation_status=ImplementationStatus.NOT_STARTED
                ),
                FunctionSpec(
                    name="save_results",
                    module="module_a",
                    docstring="Save results calls process_data",
                    arguments=[Argument("results", "Dict", None, "Results to save")],
                    return_type="None",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        modules.append(module_a)
        
        # Module B with utility functions
        module_b = Module(
            name="module_b",
            description="Utility module",
            file_path="module_b.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="validate_input",
                    module="module_b",
                    docstring="Validate input data",
                    arguments=[Argument("data", "Dict", None, "Data to validate")],
                    return_type="bool",
                    implementation_status=ImplementationStatus.NOT_STARTED
                ),
                FunctionSpec(
                    name="format_output",
                    module="module_b",
                    docstring="Format output data",
                    arguments=[Argument("data", "Any", None, "Data to format")],
                    return_type="str",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        modules.append(module_b)
        
        # Test dependency analyzer
        analyzer = DependencyAnalyzer(temp_dir)
        
        # Build enhanced dependency graph
        enhanced_graph = analyzer.build_enhanced_dependency_graph(modules)
        
        # Verify the graph (allow for some extra nodes from type analysis)
        assert len(enhanced_graph.function_nodes) >= 4, f"Expected at least 4 function nodes, got {len(enhanced_graph.function_nodes)}"
        assert len(enhanced_graph.module_nodes) >= 2, f"Expected at least 2 module nodes, got {len(enhanced_graph.module_nodes)}"
        
        # Verify that our expected functions are present
        expected_functions = [
            "module_a.process_data", "module_a.save_results",
            "module_b.validate_input", "module_b.format_output"
        ]
        for func in expected_functions:
            assert func in enhanced_graph.function_nodes, f"Expected function {func} not found in graph"
        
        # Check function implementation order
        impl_order = enhanced_graph.get_function_implementation_order()
        assert len(impl_order) >= 4
        
        # Test parallel groups
        parallel_groups = enhanced_graph.get_parallel_implementation_groups()
        assert len(parallel_groups) >= 1, "Should have at least one parallel group"
        
        # Test complexity analysis
        complexity = enhanced_graph.analyze_dependency_complexity()
        assert complexity['total_functions'] >= 4
        assert complexity['has_cycles'] == False
        
        print("✅ Enhanced dependency analyzer working correctly")


def test_integration_with_a3():
    """Test integration with the main A3 API."""
    print("\n🚀 Testing Integration with A3 API...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        # Initialize A3
        a3 = A3(str(project_path))
        a3._api_key = "test_key"  # Mock API key for testing
        
        # Create a simple project plan manually for testing
        from a3.core.models import ProjectPlan, DependencyGraph
        
        modules = []
        
        # Create test modules
        module_utils = Module(
            name="utils",
            description="Utility functions",
            file_path="utils.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="log_message",
                    module="utils",
                    docstring="Log a message",
                    arguments=[Argument("message", "str", None, "Message to log")],
                    return_type="None",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        modules.append(module_utils)
        
        module_processor = Module(
            name="processor",
            description="Data processor",
            file_path="processor.py",
            dependencies=["utils"],
            functions=[
                FunctionSpec(
                    name="process_data",
                    module="processor",
                    docstring="Process data uses log_message",
                    arguments=[Argument("data", "Dict", None, "Data to process")],
                    return_type="Dict",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        modules.append(module_processor)
        
        # Create dependency graph
        dep_graph = DependencyGraph(
            nodes=["utils", "processor"],
            edges=[("processor", "utils")]
        )
        
        # Create enhanced dependency graph
        analyzer = DependencyAnalyzer(str(project_path))
        enhanced_graph = analyzer.build_enhanced_dependency_graph(modules)
        
        # Create project plan
        plan = ProjectPlan(
            objective="Test project with enhanced dependencies",
            modules=modules,
            dependency_graph=dep_graph,
            enhanced_dependency_graph=enhanced_graph,
            estimated_functions=2
        )
        
        # Save the plan
        a3._state_manager.save_project_plan(plan)
        
        # Test enhanced dependency methods
        try:
            # Test analyze_dependencies
            analysis = a3.analyze_dependencies()
            assert 'enhanced_dependency_graph' in analysis
            assert 'function_implementation_order' in analysis
            assert 'complexity_analysis' in analysis
            
            # Test get_enhanced_dependency_graph
            retrieved_graph = a3.get_enhanced_dependency_graph()
            assert len(retrieved_graph.function_nodes) >= 2
            assert len(retrieved_graph.module_nodes) >= 2
            
            # Test implementation strategy
            strategy = a3.get_implementation_strategy()
            assert 'parallel_implementation_groups' in strategy
            assert 'critical_path' in strategy
            
            print("✅ A3 API integration working correctly")
            
        except Exception as e:
            print(f"❌ A3 API integration failed: {e}")
            raise


def main():
    """Run all enhanced dependency tests."""
    print("🔗 Enhanced Function-Level Dependency System Tests")
    print("=" * 60)
    
    try:
        test_enhanced_dependency_models()
        test_dependency_analyzer_enhancements()
        test_integration_with_a3()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Enhanced dependency system is working correctly.")
        print("=" * 60)
        
        print("\n📊 Summary of Enhanced Features:")
        print("• Function-level dependency tracking ✅")
        print("• Optimal implementation ordering ✅")
        print("• Parallel implementation groups ✅")
        print("• Critical path analysis ✅")
        print("• Dependency complexity metrics ✅")
        print("• Integration with A3 API ✅")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())