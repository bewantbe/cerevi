#!/usr/bin/env python3
"""
Test runner for VISoR Platform backend tests

This script provides a simple way to run tests without requiring pytest installation
in the development environment. It can run individual test modules or all tests.
"""

import sys
import os
import importlib.util

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_integration_tests():
    """Run integration tests without pytest"""
    print("="*50)
    print("VISoR Platform Backend Integration Tests")
    print("="*50)
    
    try:
        # Import the test module
        from test_integration import TestBackendIntegration
        
        # Create test instance
        test_instance = TestBackendIntegration()
        
        # List of test methods to run
        test_methods = [
            ('test_imports', 'Testing module imports'),
            ('test_data_access', 'Testing data access'),
            ('test_region_loading', 'Testing region loading'),
            ('test_image_metadata_extraction', 'Testing image metadata extraction')
        ]
        
        passed = 0
        total = len(test_methods)
        
        for method_name, description in test_methods:
            print(f"\n{description}...")
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"✓ {method_name} passed")
                passed += 1
            except Exception as e:
                print(f"✗ {method_name} failed: {e}")
        
        print("\n" + "="*50)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            return 1
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def run_api_tests():
    """Run API tests (currently just placeholders)"""
    print("\n" + "="*50)
    print("VISoR Platform Backend API Tests")
    print("="*50)
    print("API tests are currently placeholders and will be skipped.")
    print("To implement API tests, uncomment the test code in test_api_endpoints.py")
    return 0

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'integration':
            return run_integration_tests()
        elif test_type == 'api':
            return run_api_tests()
        elif test_type == 'all':
            result1 = run_integration_tests()
            result2 = run_api_tests()
            return max(result1, result2)
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [integration|api|all]")
            return 1
    else:
        # Run all tests by default
        result1 = run_integration_tests()
        result2 = run_api_tests()
        return max(result1, result2)

if __name__ == "__main__":
    sys.exit(main())
