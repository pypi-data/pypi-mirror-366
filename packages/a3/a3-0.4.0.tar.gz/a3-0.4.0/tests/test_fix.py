#!/usr/bin/env python3
"""
Test script to verify the A3 fix for the current_phase.value AttributeError.
"""

from a3 import A3

def test_a3_fix():
    """Test that A3 can handle the implementation phase without AttributeError."""
    try:
        # Initialize A3 with a test project
        import tempfile
        import os
        test_dir = os.path.join(tempfile.gettempdir(), "a3_test_fix")
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
        os.makedirs(test_dir, exist_ok=True)
        a3 = A3(project_path=test_dir)
        
        # Configure A3 settings
        a3.set_api_key("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")
        a3.set_model("qwen/qwen3-coder:free")
        a3.set_generate_tests(True)
        a3.set_code_style("black")
        
        # Test the workflow
        print("Testing A3 workflow...")
        
        plan = a3.plan("A simple calculator with basic arithmetic operations")
        print("✓ Planning completed successfully")
        
        specs = a3.generate_specs()
        print("✓ Specification generation completed successfully")
        
        implementation = a3.implement()
        print("✓ Implementation completed successfully")
        
        integration = a3.integrate()
        print("✓ Integration completed successfully")
        
        print("\n🎉 All tests passed! The fix is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_a3_fix()