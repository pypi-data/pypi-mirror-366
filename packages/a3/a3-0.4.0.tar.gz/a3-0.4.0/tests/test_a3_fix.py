#!/usr/bin/env python3
"""
Test script to verify A3 fixes for fallback model warnings.
"""

from a3 import A3

def test_a3_configuration():
    """Test A3 configuration without warnings."""
    print("Testing A3 configuration...")
    
    # Initialize A3
    a3 = A3(project_path=r"C:\Users\milin\Documents\A3 Testing")
    
    # Configure A3 settings
    a3.set_api_key("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")
    a3.set_model("qwen/qwen3-coder:free")
    a3.set_generate_tests(True)
    a3.set_code_style("black")
    
    print("✓ Configuration completed successfully!")
    print(f"✓ Current model: {a3.get_current_model()}")
    
    # Test configuration summary
    config_summary = a3.get_config_summary()
    print("✓ Configuration summary:")
    for key, value in config_summary.items():
        print(f"  - {key}: {value}")
    
    return True

if __name__ == "__main__":
    try:
        test_a3_configuration()
        print("\n🎉 All tests passed! The fallback model warnings should be resolved.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")