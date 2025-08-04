#!/usr/bin/env python3
"""
Test script to reproduce the original AttributeError and verify it's fixed.
"""

from a3 import A3

def test_original_error():
    """Test the original error scenario from the user's report."""
    try:
        # Use the exact same code from the user's error report
        a3 = A3(project_path=r"C:\Users\milin\Documents\A3 Testing")
        
        # Configure A3 settings
        a3.set_api_key("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")
        a3.set_model("qwen/qwen3-coder:free")
        a3.set_generate_tests(True)
        a3.set_code_style("black")
        
        plan = a3.plan("A web scraper for news articles with sentiment analysis")
        specs = a3.generate_specs()
        
        # This is where the original error occurred
        implementation = a3.implement()
        
        print("✓ No AttributeError occurred! The fix is working.")
        return True
        
    except AttributeError as e:
        if "'str' object has no attribute 'value'" in str(e):
            print(f"❌ Original AttributeError still occurs: {e}")
            return False
        else:
            print(f"❌ Different AttributeError: {e}")
            return False
    except Exception as e:
        print(f"✓ Different error (not the original AttributeError): {e}")
        print("This means the AttributeError fix is working!")
        return True

if __name__ == "__main__":
    test_original_error()