#!/usr/bin/env python3
"""
Simple test to check if the error handling module can be loaded.
"""

import importlib.util
import sys

def test_module_load():
    """Test loading the error handling module."""
    print("🧪 Testing module loading...")
    
    try:
        # Load the error handling module
        spec = importlib.util.spec_from_file_location(
            "error_handling", 
            "offers_check_marketplaces/error_handling.py"
        )
        error_handling = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(error_handling)
        
        print("Module loaded successfully")
        
        # Check what's available in the module
        print("\nAvailable attributes:")
        attrs = [attr for attr in dir(error_handling) if not attr.startswith('_')]
        for attr in sorted(attrs):
            obj = getattr(error_handling, attr)
            obj_type = type(obj).__name__
            print(f"  {attr}: {obj_type}")
        
        # Test if ErrorHandler class exists
        if hasattr(error_handling, 'ErrorHandler'):
            print("\nErrorHandler class found")
            handler = error_handling.ErrorHandler()
            print("ErrorHandler instance created successfully")
        else:
            print("\nErrorHandler class not found")
        
        # Test if error categories exist
        if hasattr(error_handling, 'ErrorCategory'):
            print("ErrorCategory enum found")
        else:
            print("ErrorCategory enum not found")
        
        # Test if decorators exist
        decorators = ['handle_errors', 'handle_marketplace_errors', 'handle_database_errors']
        for decorator in decorators:
            if hasattr(error_handling, decorator):
                print(f"{decorator} decorator found")
            else:
                print(f"{decorator} decorator not found")
        
    except Exception as e:
        print(f"Error loading module: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_module_load()