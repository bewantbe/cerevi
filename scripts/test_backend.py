#!/usr/bin/env python3
"""
Test script for VISoR Platform backend

DEPRECATED: This script has been moved to backend/tests/
Please use the new test structure:
- backend/tests/test_integration.py - Integration tests (converted from this script)
- backend/tests/test_api_endpoints.py - API endpoint tests (placeholders)
- backend/tests/run_tests.py - Simple test runner

To run tests:
- cd backend/tests && python run_tests.py
- Or with pytest: cd backend && pytest tests/
"""

import sys
import os

print("""==================================================================
⚠️  DEPRECATION NOTICE
==================================================================
This test script has been moved to backend/tests/ for better organization.
Please use the new test structure:

    New location: backend/tests/test_integration.py
    Test runner:  backend/tests/run_tests.py

To run tests:
    cd backend/tests && python run_tests.py
    Or with pytest: cd backend && pytest tests/

Running original tests for backward compatibility...
==================================================================
""")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_imports():
    """Test that all backend modules can be imported"""
    print("Testing backend imports...")
    
    try:
        from app.config import settings
        print("✓ Configuration loaded successfully")
        print(f"  - App name: {settings.app_name}")
        print(f"  - Data path: {settings.data_path}")
        print(f"  - Default tile size: {settings.default_tile_size}")
        
        from app.models.specimen import SpecimenMetadata, ViewType
        print("✓ Specimen models imported")
        
        from app.models.region import Region, RegionHierarchy
        print("✓ Region models imported")
        
        from app.services.imaris_handler import ImarisHandler
        print("✓ Imaris handler imported")
        
        from app.services.tile_service import TileService
        print("✓ Tile service imported")
        
        from app.main import app
        print("✓ FastAPI app imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_data_access():
    """Test access to data files"""
    print("\nTesting data access...")
    
    try:
        from app.config import settings
        
        # Check if data directories exist
        print(f"Data path exists: {settings.data_path.exists()}")
        print(f"Specimens path exists: {settings.specimens_path.exists()}")
        print(f"Models path exists: {settings.models_path.exists()}")
        print(f"Regions path exists: {settings.regions_path.exists()}")
        
        # Check specimen data
        specimen_id = "macaque_brain_rm009"
        image_path = settings.get_image_path(specimen_id)
        atlas_path = settings.get_atlas_path(specimen_id)
        model_path = settings.get_model_path(specimen_id)
        regions_file = settings.get_regions_file()
        
        print(f"\nSpecimen: {specimen_id}")
        print(f"  Image file exists: {image_path.exists()} ({image_path})")
        print(f"  Atlas file exists: {atlas_path.exists()} ({atlas_path})")
        print(f"  Model file exists: {model_path.exists()} ({model_path})")
        print(f"  Regions file exists: {regions_file.exists()} ({regions_file})")
        
        return True
        
    except Exception as e:
        print(f"✗ Data access test failed: {e}")
        return False

def test_region_loading():
    """Test loading region hierarchy"""
    print("\nTesting region loading...")
    
    try:
        import json
        from app.config import settings
        
        regions_file = settings.get_regions_file()
        if regions_file.exists():
            with open(regions_file, 'r') as f:
                data = json.load(f)
            
            print(f"✓ Regions loaded: {data['metadata']['total_regions']} regions")
            print(f"  Source: {data['metadata']['source']}")
            print(f"  Conversion date: {data['metadata']['conversion_date']}")
            
            # Show some sample regions
            sample_regions = data['regions'][:5]
            print("  Sample regions:")
            for region in sample_regions:
                print(f"    - {region['name']} ({region['abbreviation']})")
            
            return True
        else:
            print("✗ Regions file not found")
            return False
            
    except Exception as e:
        print(f"✗ Region loading failed: {e}")
        return False

def test_image_metadata():
    """Test image metadata extraction"""
    print("\nTesting image metadata extraction...")
    
    try:
        from app.config import settings
        from app.services.imaris_handler import ImarisHandler
        
        specimen_id = "macaque_brain_rm009"
        image_path = settings.get_image_path(specimen_id)
        
        if image_path.exists():
            with ImarisHandler(image_path) as handler:
                metadata = handler.get_metadata()
                
                print(f"✓ Image metadata extracted")
                print(f"  File size: {metadata['file_size'] / 1024 / 1024:.1f} MB")
                print(f"  Resolution levels: {metadata['resolution_levels']}")
                print(f"  Channels: {metadata['channels']}")
                print(f"  Data type: {metadata['data_type']}")
                
                # Show shapes for each level
                print("  Shapes by level:")
                for level, shape in metadata['shapes'].items():
                    print(f"    Level {level}: {shape}")
                
                return True
        else:
            print("✗ Image file not found")
            return False
            
    except Exception as e:
        print(f"✗ Image metadata test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("VISoR Platform Backend Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_data_access,
        test_region_loading,
        test_image_metadata
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
