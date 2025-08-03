#!/usr/bin/env python3
"""
Test the original user code to ensure it works without errors.
"""

from a3 import A3

# Your original code with the fix
a3 = A3(project_path=r"C:\Users\milin\Documents\A3 Testing")

# Configure A3 settings
a3.set_api_key("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")
a3.set_model("qwen/qwen3-coder:free")
a3.set_generate_tests(True)
a3.set_code_style("black")

# Disable fallback models as requested
a3.set_use_fallback_models(False)

print("✅ Configuration completed successfully!")
print(f"📋 Current model: {a3.get_current_model()}")
print(f"🚫 Fallback models: {'Disabled' if not a3.get_config_summary()['use_fallback_models'] else 'Enabled'}")

print("\n🚀 Ready to run your project generation!")
print("You can now run:")
print('plan = a3.plan("A web scraper for news articles with sentiment analysis")')
print("specs = a3.generate_specs()")
print("implementation = a3.implement()")
print("integration = a3.integrate()")
print('print("Project created successfully!")')