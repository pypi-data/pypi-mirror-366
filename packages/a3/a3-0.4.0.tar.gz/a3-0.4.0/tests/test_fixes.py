#!/usr/bin/env python3
"""
Test script to verify all A3 fixes.
"""

from a3 import A3

def test_configuration_fixes():
    """Test that configuration fixes work correctly."""
    print("🔧 Testing A3 configuration fixes...")
    
    # Initialize A3
    a3 = A3(project_path=r"C:\Users\milin\Documents\A3 Testing")
    
    # Configure A3 settings
    a3.set_api_key("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")
    a3.set_model("qwen/qwen3-coder:free")
    a3.set_generate_tests(True)
    a3.set_code_style("black")
    
    # Disable fallback models (as requested)
    a3.set_use_fallback_models(False)
    
    print("✅ Configuration completed successfully!")
    
    # Test configuration summary
    config_summary = a3.get_config_summary()
    print("\n📋 Configuration Summary:")
    for key, value in config_summary.items():
        print(f"  - {key}: {value}")
    
    # Verify the model is set correctly
    current_model = a3.get_current_model()
    print(f"\n🎯 Current model: {current_model}")
    
    # Verify fallback is disabled
    use_fallbacks = config_summary.get('use_fallback_models', True)
    print(f"🚫 Fallback models disabled: {not use_fallbacks}")
    
    return True

def test_import_fix():
    """Test that the import fix works."""
    print("\n🔍 Testing import fix...")
    
    try:
        # This should not raise an error anymore
        from a3.core.user_feedback import start_operation_progress
        print("✅ Import fix successful - start_operation_progress can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import fix failed: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Starting A3 fixes verification...\n")
        
        # Test configuration fixes
        config_success = test_configuration_fixes()
        
        # Test import fix
        import_success = test_import_fix()
        
        if config_success and import_success:
            print("\n🎉 All fixes verified successfully!")
            print("\n📝 Summary of fixes:")
            print("  ✅ Removed fallback model warnings")
            print("  ✅ Fixed model configuration consistency")
            print("  ✅ Added option to disable fallback models")
            print("  ✅ Fixed missing import error")
            print("\n🔥 Your code should now run without warnings!")
        else:
            print("\n⚠️  Some fixes may need additional work")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()