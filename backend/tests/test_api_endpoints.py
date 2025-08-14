"""
API endpoint tests for VISoR Platform backend

Tests for the REST API endpoints defined in the FastAPI application.
Based on the API specification from BACKEND_COMPLETE.md
"""

import sys
import os
import pytest
import numpy as np
from PIL import Image
import io
from fastapi.testclient import TestClient

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    from app.main import app
    return TestClient(app)

class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test GET /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "data_path_exists" in data

class TestSpecimenEndpoints:
    """Tests for specimen-related endpoints"""
    
    def test_list_specimens(self, client):
        """Test GET /api/specimens"""
        response = client.get("/api/specimens")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check specimen structure
        specimen = data[0]
        assert "id" in specimen
        assert "name" in specimen
        assert "species" in specimen
        assert "description" in specimen
        assert "has_image" in specimen
        assert "has_atlas" in specimen
        assert "has_model" in specimen
        assert "channels" in specimen
        assert "resolution_um" in specimen
        assert "coordinate_system" in specimen
        assert "axes_order" in specimen
    
    def test_get_specimen_details(self, client):
        """Test GET /api/specimens/{id}"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["id"] == specimen_id
        assert "name" in data
        assert "species" in data
        assert "description" in data
        assert "has_image" in data
        assert "has_atlas" in data
        assert "has_model" in data
        assert "channels" in data
        assert "resolution_um" in data
        assert "coordinate_system" in data
        assert "axes_order" in data
    
    def test_get_specimen_config(self, client):
        """Test GET /api/specimens/{id}/config"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["id"] == specimen_id
        assert "name" in data
        assert "species" in data
        assert "description" in data
        assert "has_image" in data
        assert "has_atlas" in data
        assert "has_model" in data
        assert "channels" in data
        assert "resolution_um" in data
        assert "coordinate_system" in data
        assert "axes_order" in data
    
    def test_get_specimen_model(self, client):
        """Test GET /api/specimens/{id}/model"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/model")
        
        # This might return 404 if model file doesn't exist in test environment
        if response.status_code == 200:
            data = response.json()
            assert "model_path" in data
            assert isinstance(data["model_path"], str)
        elif response.status_code == 404:
            # Model file not found - this is a warning in test environment
            data = response.json()
            assert "detail" in data
            pytest.skip(f"Model file not found for specimen {specimen_id}: {data['detail']}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_invalid_specimen(self, client):
        """Test GET /api/specimens/{id} with invalid ID"""
        response = client.get("/api/specimens/invalid_specimen_id")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

class TestMetadataEndpoints:
    """Tests for metadata endpoints"""
    
    def test_get_complete_metadata(self, client):
        """Test GET /api/specimens/{id}/metadata"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/metadata")
        assert response.status_code == 200
        
        data = response.json()
        assert "specimen" in data
        assert "image" in data
        assert "atlas" in data
        assert "model" in data
        
        # Check specimen metadata
        specimen = data["specimen"]
        assert "id" in specimen
        assert specimen["id"] == specimen_id
        assert "name" in specimen
        assert "species" in specimen
        assert "description" in specimen
    
    def test_get_image_info(self, client):
        """Test GET /api/specimens/{id}/image-info"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/image-info")
        
        # This might return 404 if image file doesn't exist in test environment
        if response.status_code == 200:
            data = response.json()
            assert "specimen_id" in data
            assert data["specimen_id"] == specimen_id
            assert "dimensions" in data
            assert "channels" in data
            assert "resolution_levels" in data
            assert "tile_size" in data
            assert "pixel_size_um" in data
            assert "data_type" in data
            assert "file_size" in data
        elif response.status_code == 404:
            # Image file not found - this is a warning in test environment
            data = response.json()
            assert "detail" in data
            pytest.skip(f"Image file not found for specimen {specimen_id}: {data['detail']}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_atlas_info(self, client):
        """Test GET /api/specimens/{id}/atlas-info"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/atlas-info")
        
        # This might return 404 if atlas file doesn't exist in test environment
        if response.status_code == 200:
            data = response.json()
            assert "specimen_id" in data
            assert data["specimen_id"] == specimen_id
            assert "dimensions" in data
            assert "resolution_levels" in data
            assert "tile_size" in data
            assert "pixel_size_um" in data
            assert "data_type" in data
            assert "file_size" in data
            assert "total_regions" in data
        elif response.status_code == 404:
            # Atlas file not found - this is a warning in test environment
            data = response.json()
            assert "detail" in data
            pytest.skip(f"Atlas file not found for specimen {specimen_id}: {data['detail']}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_model_info(self, client):
        """Test GET /api/specimens/{id}/model-info"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/model-info")
        
        # This might return 404 if model file doesn't exist in test environment
        if response.status_code == 200:
            data = response.json()
            assert "specimen_id" in data
            assert data["specimen_id"] == specimen_id
            assert "file_path" in data
            assert "scale_factor" in data
            assert "vertex_count" in data
            assert "face_count" in data
            assert "file_size" in data
        elif response.status_code == 404:
            # Model file not found - this is a warning in test environment
            data = response.json()
            assert "detail" in data
            pytest.skip(f"Model file not found for specimen {specimen_id}: {data['detail']}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_config_info(self, client):
        """Test GET /api/specimens/{id}/config-info"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/config-info")
        assert response.status_code == 200
        
        data = response.json()
        assert "specimen_id" in data
        assert data["specimen_id"] == specimen_id
        assert "suggested_tile_size" in data
        assert "max_resolution_level" in data
        assert "supported_views" in data
        assert "coordinate_system" in data
        assert "axes_order" in data
        assert "capabilities" in data
        assert "channels" in data
        assert "resolution_um" in data
        
        # Check capabilities structure
        capabilities = data["capabilities"]
        assert "has_image" in capabilities
        assert "has_atlas" in capabilities
        assert "has_model" in capabilities
        assert "multi_channel" in capabilities
        assert "multi_resolution" in capabilities
        assert "region_picking" in capabilities
        
        # Check supported views
        supported_views = data["supported_views"]
        assert "sagittal" in supported_views
        assert "coronal" in supported_views
        assert "horizontal" in supported_views
    
    def test_get_metadata_invalid_specimen(self, client):
        """Test metadata endpoints with invalid specimen ID"""
        response = client.get("/api/specimens/invalid_specimen_id/metadata")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

class TestImageEndpoints:
    """Tests for image tile endpoints with critical pixel statistics validation"""
    
    @pytest.mark.parametrize("test_case", [
        {
            "name": "coronal_level4",
            "view": "coronal", "level": 4, "z": 256, "y": 0, "x": 0, "channel": 0,
            "expected_mean": 39.27, "expected_std": 39.47, "expected_size_range": (15000, 20000),
            "expected_shape_approx": (384, 448)  # Non-square due to data bounds
        },
        {
            "name": "sagittal_level4", 
            "view": "sagittal", "level": 4, "z": 0, "y": 0, "x": 224, "channel": 0,
            "expected_mean": 11.79, "expected_std": 20.88, "expected_size_range": (13000, 18000),
            "expected_shape_approx": (384, 512)
        },
        {
            "name": "horizontal_level4",
            "view": "horizontal", "level": 4, "z": 0, "y": 192, "x": 0, "channel": 0,
            "expected_mean": 13.52, "expected_std": 17.57, "expected_size_range": (14000, 19000),
            "expected_shape_approx": (512, 448)
        },
        {
            "name": "coronal_level0_highres",
            "view": "coronal", "level": 0, "z": 3200, "y": 3200, "x": 3200, "channel": 0,
            "expected_mean": None, "expected_std": None, "expected_size_range": (10000, 50000),
            "expected_shape_approx": (512, 512)  # Full tile size for high-res
        }
    ])
    def test_image_api_with_critical_statistics(self, client, test_case):
        """Test image API with expected pixel statistics and dimensions from dev script"""
        specimen_id = "macaque_brain_RM009"
        
        # Build API endpoint URL
        url = (f"/api/specimens/{specimen_id}/image/{test_case['view']}/"
               f"{test_case['level']}/{test_case['z']}/{test_case['y']}/{test_case['x']}")
        if test_case['channel'] != 0:
            url += f"?channel={test_case['channel']}"
        
        response = client.get(url)
        
        # Skip if image file not available in test environment
        if response.status_code == 404:
            data = response.json()
            pytest.skip(f"Image file not found for {test_case['name']}: {data['detail']}")
        
        # Verify successful response
        assert response.status_code == 200, f"Failed for test case: {test_case['name']}"
        
        # Verify response headers
        assert response.headers["content-type"] == "image/jpeg"
        assert "Cache-Control" in response.headers
        assert "X-Tile-Info" in response.headers
        
        # Verify JPEG format
        assert len(response.content) > 0
        assert response.content[:2] == b'\xff\xd8', "Not a valid JPEG file"
        
        # Verify image size is in expected range
        size_min, size_max = test_case['expected_size_range']
        actual_size = len(response.content)
        assert size_min <= actual_size <= size_max, \
            f"Image size {actual_size} not in expected range [{size_min}, {size_max}] for {test_case['name']}"
        
        # Decode JPEG and validate pixel statistics
        try:
            image = Image.open(io.BytesIO(response.content))
            pixels = np.array(image)
            
            # Validate image dimensions
            expected_height, expected_width = test_case['expected_shape_approx']
            actual_height, actual_width = pixels.shape
            
            # Require exact dimension match
            assert actual_height == expected_height, \
                f"Height mismatch for {test_case['name']}: expected {expected_height}, got {actual_height}"
            assert actual_width == expected_width, \
                f"Width mismatch for {test_case['name']}: expected {expected_width}, got {actual_width}"
            
            # Validate pixel range (proper normalization)
            assert pixels.min() >= 0, f"Pixel values below 0 for {test_case['name']}"
            assert pixels.max() <= 255, f"Pixel values above 255 for {test_case['name']}"
            assert pixels.dtype == np.uint8, f"Wrong pixel data type for {test_case['name']}"
            
            # Validate pixel statistics (if expected values provided)
            if test_case['expected_mean'] is not None:
                actual_mean = np.mean(pixels)
                expected_mean = test_case['expected_mean']
                tolerance = 0.01 * expected_mean  # ±1% tolerance
                
                assert abs(actual_mean - expected_mean) <= tolerance, \
                    f"Mean mismatch for {test_case['name']}: expected {expected_mean:.2f} ±{tolerance:.2f}, got {actual_mean:.2f}"
            
            if test_case['expected_std'] is not None:
                actual_std = np.std(pixels)
                expected_std = test_case['expected_std']
                tolerance = 0.01 * expected_std  # ±1% tolerance
                
                assert abs(actual_std - expected_std) <= tolerance, \
                    f"Std mismatch for {test_case['name']}: expected {expected_std:.2f} ±{tolerance:.2f}, got {actual_std:.2f}"
            
            # Ensure image is not blank (has some variation)
            assert np.std(pixels) > 1.0, f"Image appears blank for {test_case['name']}"
            
        except Exception as e:
            pytest.fail(f"Failed to decode or validate image for {test_case['name']}: {e}")
    
    def test_get_image_tile_invalid_specimen(self, client):
        """Test image tile with invalid specimen ID"""
        response = client.get("/api/specimens/invalid_specimen_id/image/sagittal/0/0/0/0")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_image_tile_invalid_parameters(self, client):
        """Test image tile with invalid parameters"""
        specimen_id = "macaque_brain_RM009"
        
        # Test invalid view
        response = client.get(f"/api/specimens/{specimen_id}/image/invalid_view/0/0/0/0")
        assert response.status_code == 422  # Validation error
        
        # Test invalid level (negative)
        response = client.get(f"/api/specimens/{specimen_id}/image/sagittal/-1/0/0/0")
        assert response.status_code == 422
        
        # Test invalid level (too high)
        response = client.get(f"/api/specimens/{specimen_id}/image/sagittal/10/0/0/0")
        assert response.status_code == 422
        
        # Test invalid coordinates (negative)
        response = client.get(f"/api/specimens/{specimen_id}/image/sagittal/0/0/-1/0")
        assert response.status_code == 422
        
        response = client.get(f"/api/specimens/{specimen_id}/image/sagittal/0/0/0/-1")
        assert response.status_code == 422
    
    def test_get_atlas_tile(self, client):
        """Test GET /api/specimens/{id}/atlas/{view}/{level}/{z}/{x}/{y}"""
        specimen_id = "macaque_brain_RM009"
        view = "sagittal"
        level = 0
        z, x, y = 0, 0, 0
        
        response = client.get(f"/api/specimens/{specimen_id}/atlas/{view}/{level}/{z}/{x}/{y}")
        
        # Check if atlas file exists - if not, should return 404
        if response.status_code == 200:
            # Verify response headers
            assert response.headers["content-type"] == "image/png"
            assert "Cache-Control" in response.headers
            assert "public" in response.headers["Cache-Control"]
            assert "max-age" in response.headers["Cache-Control"]
            assert "X-Atlas-Info" in response.headers
            
            # Verify response content
            assert len(response.content) > 0
            # Check for PNG magic bytes (89 50 4E 47 0D 0A 1A 0A)
            assert response.content[:8] == b'\x89PNG\r\n\x1a\n'
            
        elif response.status_code == 404:
            # Atlas file not found is acceptable in test environment
            data = response.json()
            assert "detail" in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_atlas_tile_with_parameters(self, client):
        """Test atlas tile with various parameters"""
        specimen_id = "macaque_brain_RM009"
        
        # Test different views
        for view in ["sagittal", "coronal", "horizontal"]:
            response = client.get(f"/api/specimens/{specimen_id}/atlas/{view}/0/0/0/0")
            assert response.status_code in [200, 404]  # 404 acceptable if file missing
            
            if response.status_code == 200:
                assert response.headers["content-type"] == "image/png"
        
        # Test with tile_size parameter
        response = client.get(f"/api/specimens/{specimen_id}/atlas/sagittal/0/0/0/0?tile_size=256")
        assert response.status_code in [200, 404]
    
    def test_get_atlas_tile_invalid_specimen(self, client):
        """Test atlas tile with invalid specimen ID"""
        response = client.get("/api/specimens/invalid_specimen_id/atlas/sagittal/0/0/0/0")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_atlas_tile_invalid_parameters(self, client):
        """Test atlas tile with invalid parameters"""
        specimen_id = "macaque_brain_RM009"
        
        # Test invalid view
        response = client.get(f"/api/specimens/{specimen_id}/atlas/invalid_view/0/0/0/0")
        assert response.status_code == 422  # Validation error
        
        # Test invalid level (negative)
        response = client.get(f"/api/specimens/{specimen_id}/atlas/sagittal/-1/0/0/0")
        assert response.status_code == 422
        
        # Test invalid level (too high)
        response = client.get(f"/api/specimens/{specimen_id}/atlas/sagittal/10/0/0/0")
        assert response.status_code == 422
    
    def test_get_tile_grid_info(self, client):
        """Test GET /api/specimens/{id}/tile-grid/{view}/{level}"""
        specimen_id = "macaque_brain_RM009"
        view = "sagittal"
        level = 0
        
        response = client.get(f"/api/specimens/{specimen_id}/tile-grid/{view}/{level}")
        
        # Check if image file exists - if not, should return 404
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            assert "view" in data
            assert "level" in data
            assert "tile_size" in data
            assert "tiles_x" in data
            assert "tiles_y" in data
            assert "image_shape" in data
            assert "total_tiles" in data
            
            # Verify data types and values
            assert data["view"] == view
            assert data["level"] == level
            assert isinstance(data["tile_size"], int)
            assert isinstance(data["tiles_x"], int)
            assert isinstance(data["tiles_y"], int)
            assert isinstance(data["image_shape"], (list, tuple))
            assert isinstance(data["total_tiles"], int)
            
            # Verify reasonable values
            assert data["tile_size"] > 0
            assert data["tiles_x"] > 0
            assert data["tiles_y"] > 0
            assert data["total_tiles"] == data["tiles_x"] * data["tiles_y"]
            
        elif response.status_code == 404:
            # Image file not found is acceptable in test environment
            data = response.json()
            assert "detail" in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_tile_grid_info_all_views(self, client):
        """Test tile grid info for all views"""
        specimen_id = "macaque_brain_RM009"
        
        for view in ["sagittal", "coronal", "horizontal"]:
            response = client.get(f"/api/specimens/{specimen_id}/tile-grid/{view}/0")
            assert response.status_code in [200, 404]  # 404 acceptable if file missing
            
            if response.status_code == 200:
                data = response.json()
                assert data["view"] == view
                assert data["level"] == 0
    
    def test_get_tile_grid_info_invalid_specimen(self, client):
        """Test tile grid info with invalid specimen ID"""
        response = client.get("/api/specimens/invalid_specimen_id/tile-grid/sagittal/0")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_tile_grid_info_invalid_parameters(self, client):
        """Test tile grid info with invalid parameters"""
        specimen_id = "macaque_brain_RM009"
        
        # Test invalid view
        response = client.get(f"/api/specimens/{specimen_id}/tile-grid/invalid_view/0")
        assert response.status_code == 422  # Validation error
        
        # Test invalid level (negative)
        response = client.get(f"/api/specimens/{specimen_id}/tile-grid/sagittal/-1")
        assert response.status_code == 422
        
        # Test invalid level (too high)
        response = client.get(f"/api/specimens/{specimen_id}/tile-grid/sagittal/10")
        assert response.status_code == 422

class TestRegionEndpoints:
    """Tests for brain region endpoints"""
    
    def test_get_regions(self, client):
        """Test GET /api/specimens/{id}/regions"""
        specimen_id = "macaque_brain_RM009"
        response = client.get(f"/api/specimens/{specimen_id}/regions")
        
        # Check if regions data is available
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            assert "regions" in data
            assert "total_count" in data
            assert "filtered_count" in data
            assert "statistics" in data
            
            # Verify regions list
            regions = data["regions"]
            assert isinstance(regions, list)
            assert len(regions) > 0
            
            # Verify first region structure
            region = regions[0]
            required_fields = ["id", "name", "abbreviation", "level1", "level2", "level3", "level4", "value"]
            for field in required_fields:
                assert field in region, f"Required field '{field}' missing from region"
            
            # Verify field types
            assert isinstance(region["id"], int)
            assert isinstance(region["name"], str)
            assert isinstance(region["abbreviation"], str)
            assert isinstance(region["value"], int)
            assert isinstance(region["level1"], str)
            assert isinstance(region["level2"], str)
            assert isinstance(region["level3"], str)
            assert isinstance(region["level4"], str)
            
            # Verify counts
            assert isinstance(data["total_count"], int)
            assert isinstance(data["filtered_count"], int)
            assert data["total_count"] > 0
            assert data["filtered_count"] > 0
            
            # Verify statistics
            stats = data["statistics"]
            assert "total_regions" in stats
            assert "regions_by_level" in stats
            assert "hierarchy_depth" in stats
            assert isinstance(stats["total_regions"], int)
            assert isinstance(stats["regions_by_level"], dict)
            assert isinstance(stats["hierarchy_depth"], int)
            
        elif response.status_code == 500:
            # Regions file might not be available in test environment
            data = response.json()
            assert "detail" in data
            pytest.skip(f"Regions data not available: {data['detail']}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_regions_with_filters(self, client):
        """Test GET /api/specimens/{id}/regions with query parameters"""
        specimen_id = "macaque_brain_RM009"
        
        # Test with level filter
        response = client.get(f"/api/specimens/{specimen_id}/regions?level=1")
        if response.status_code == 200:
            data = response.json()
            assert "regions" in data
            assert isinstance(data["regions"], list)
            
            # Verify level filtering if regions exist
            if len(data["regions"]) > 0:
                # All regions should have distinct level1 values
                level1_values = [r["level1"] for r in data["regions"]]
                assert len(set(level1_values)) == len(level1_values), "Level 1 regions should be unique"
        
        # Test with search filter
        response = client.get(f"/api/specimens/{specimen_id}/regions?search=cortex")
        if response.status_code == 200:
            data = response.json()
            assert "regions" in data
            assert isinstance(data["regions"], list)
            
            # Verify search filtering if regions exist
            if len(data["regions"]) > 0:
                # At least one region should contain "cortex" in name
                has_cortex = any("cortex" in r["name"].lower() for r in data["regions"])
                assert has_cortex, "Search results should contain regions with 'cortex' in name"
        
        # Test with max_results filter
        response = client.get(f"/api/specimens/{specimen_id}/regions?max_results=10")
        if response.status_code == 200:
            data = response.json()
            assert "regions" in data
            assert len(data["regions"]) <= 10, "Should not return more than max_results"
    
    def test_get_regions_invalid_specimen(self, client):
        """Test GET /api/specimens/{id}/regions with invalid specimen ID"""
        response = client.get("/api/specimens/invalid_specimen_id/regions")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_pick_region(self, client):
        """Test POST /api/specimens/{id}/pick-region"""
        specimen_id = "macaque_brain_RM009"
        coordinates = {
            "view": "sagittal",
            "x": 100,
            "y": 100,
            "z": 100,
            "level": 0
        }
        
        response = client.post(f"/api/specimens/{specimen_id}/pick-region", json=coordinates)
        
        # Check if region picking is available
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            assert "specimen_id" in data
            assert "coordinate" in data
            assert "region_value" in data
            assert "confidence" in data
            
            # Verify specimen_id matches
            assert data["specimen_id"] == specimen_id
            
            # Verify coordinate structure
            coord = data["coordinate"]
            assert "x" in coord
            assert "y" in coord
            assert "z" in coord
            assert coord["x"] == coordinates["x"]
            assert coord["y"] == coordinates["y"]
            assert coord["z"] == coordinates["z"]
            
            # Verify data types
            assert isinstance(data["region_value"], int)
            assert isinstance(data["confidence"], float)
            assert 0.0 <= data["confidence"] <= 1.0
            
            # If region is found, verify its structure
            if "region" in data and data["region"] is not None:
                region = data["region"]
                required_fields = ["id", "name", "abbreviation", "level1", "level2", "level3", "level4", "value"]
                for field in required_fields:
                    assert field in region, f"Required field '{field}' missing from region"
                assert data["confidence"] == 1.0, "Confidence should be 1.0 when region is found"
            else:
                # If no region found, confidence should be 0.0
                assert data["confidence"] == 0.0, "Confidence should be 0.0 when no region is found"
                
        elif response.status_code == 500:
            # Region picking might not be available in test environment
            data = response.json()
            assert "detail" in data
            pytest.skip(f"Region picking not available: {data['detail']}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_pick_region_different_views(self, client):
        """Test region picking with different view types"""
        specimen_id = "macaque_brain_RM009"
        
        views = ["sagittal", "coronal", "horizontal"]
        for view in views:
            coordinates = {
                "view": view,
                "x": 50,
                "y": 50,
                "z": 50,
                "level": 0
            }
            
            response = client.post(f"/api/specimens/{specimen_id}/pick-region", json=coordinates)
            
            if response.status_code == 200:
                data = response.json()
                assert data["specimen_id"] == specimen_id
                assert data["coordinate"]["x"] == coordinates["x"]
                assert data["coordinate"]["y"] == coordinates["y"]
                assert data["coordinate"]["z"] == coordinates["z"]
            elif response.status_code == 500:
                # Skip if region picking not available
                pytest.skip(f"Region picking not available for view {view}")
            else:
                pytest.fail(f"Unexpected status code for view {view}: {response.status_code}")
    
    def test_pick_region_invalid_specimen(self, client):
        """Test POST /api/specimens/{id}/pick-region with invalid specimen ID"""
        coordinates = {
            "view": "sagittal",
            "x": 100,
            "y": 100,
            "z": 100,
            "level": 0
        }
        
        response = client.post("/api/specimens/invalid_specimen_id/pick-region", json=coordinates)
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_pick_region_invalid_coordinates(self, client):
        """Test region picking with invalid coordinates"""
        specimen_id = "macaque_brain_RM009"
        
        # Test with invalid view
        invalid_coordinates = {
            "view": "invalid_view",
            "x": 100,
            "y": 100,
            "z": 100,
            "level": 0
        }
        
        response = client.post(f"/api/specimens/{specimen_id}/pick-region", json=invalid_coordinates)
        assert response.status_code == 422  # Validation error
        
        # Test with missing required fields
        incomplete_coordinates = {
            "view": "sagittal",
            "x": 100,
            "y": 100
            # Missing z and level
        }
        
        response = client.post(f"/api/specimens/{specimen_id}/pick-region", json=incomplete_coordinates)
        assert response.status_code == 422  # Validation error
        
        # Test with negative coordinates
        negative_coordinates = {
            "view": "sagittal",
            "x": -1,
            "y": 100,
            "z": 100,
            "level": 0
        }
        
        response = client.post(f"/api/specimens/{specimen_id}/pick-region", json=negative_coordinates)
        assert response.status_code == 422  # Validation error

class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_invalid_specimen_id_specimens(self, client):
        """Test API response for invalid specimen ID in specimens endpoints"""
        invalid_id = "invalid_specimen_id"
        
        # Test various endpoints with invalid specimen ID
        endpoints = [
            f"/api/specimens/{invalid_id}",
            f"/api/specimens/{invalid_id}/config",
            f"/api/specimens/{invalid_id}/model",
            f"/api/specimens/{invalid_id}/metadata",
            f"/api/specimens/{invalid_id}/image-info",
            f"/api/specimens/{invalid_id}/atlas-info",
            f"/api/specimens/{invalid_id}/model-info",
            f"/api/specimens/{invalid_id}/config-info"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 404, f"Expected 404 for {endpoint}"
            
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()
    
    def test_invalid_paths(self, client):
        """Test API response for invalid paths"""
        invalid_paths = [
            "/api/nonexistent",
            "/api/specimens/macaque_brain_RM009/nonexistent",
            "/api/invalid/path"
        ]
        
        for path in invalid_paths:
            response = client.get(path)
            assert response.status_code == 404, f"Expected 404 for {path}"
    
    def test_method_not_allowed(self, client):
        """Test API response for invalid HTTP methods"""
        # Test POST on GET-only endpoints
        get_only_endpoints = [
            "/api/specimens",
            "/api/specimens/macaque_brain_RM009",
            "/api/specimens/macaque_brain_RM009/config",
            "/api/specimens/macaque_brain_RM009/metadata"
        ]
        
        for endpoint in get_only_endpoints:
            response = client.post(endpoint)
            assert response.status_code == 405, f"Expected 405 for POST to {endpoint}"

class TestRootEndpoints:
    """Tests for root and utility endpoints"""
    
    def test_root_endpoint(self, client):
        """Test GET / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "VISoR Platform API" in data["message"]
    
    def test_api_documentation_available(self, client):
        """Test that API documentation is accessible"""
        # Check if docs endpoint exists (may be disabled in production)
        response = client.get("/docs")
        
        # In debug mode, docs should be available
        # In production mode, docs might be disabled
        if response.status_code == 200:
            # Docs are available
            assert "text/html" in response.headers.get("content-type", "")
        elif response.status_code == 404:
            # Docs are disabled (acceptable in production)
            pass
        else:
            pytest.fail(f"Unexpected status code for /docs: {response.status_code}")
    
    def test_api_openapi_spec(self, client):
        """Test that OpenAPI specification is available"""
        response = client.get("/openapi.json")
        
        # OpenAPI spec should be available even if docs are disabled
        if response.status_code == 200:
            data = response.json()
            assert "openapi" in data
            assert "info" in data
            assert "paths" in data
            
            # Check basic API info
            info = data["info"]
            assert "title" in info
            assert "version" in info
            assert "VISoR Platform API" in info["title"]
        elif response.status_code == 404:
            # OpenAPI spec might be disabled in production
            pass
        else:
            pytest.fail(f"Unexpected status code for /openapi.json: {response.status_code}")

class TestSpecimenEndpointsCoverage:
    """Additional coverage tests for specimen endpoints"""
    
    def test_specimen_list_structure(self, client):
        """Test that specimen list returns expected structure"""
        response = client.get("/api/specimens")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Test with known specimen
        specimen = next((s for s in data if s["id"] == "macaque_brain_RM009"), None)
        assert specimen is not None, "Expected specimen 'macaque_brain_RM009' not found"
        
        # Test required fields
        required_fields = ["id", "name", "species", "description", "has_image", "has_atlas", "has_model"]
        for field in required_fields:
            assert field in specimen, f"Required field '{field}' missing from specimen"
        
        # Test field types
        assert isinstance(specimen["id"], str)
        assert isinstance(specimen["name"], str)
        assert isinstance(specimen["species"], str)
        assert isinstance(specimen["description"], str)
        assert isinstance(specimen["has_image"], bool)
        assert isinstance(specimen["has_atlas"], bool)
        assert isinstance(specimen["has_model"], bool)
    
    def test_specimen_details_consistency(self, client):
        """Test that specimen details are consistent with list"""
        # Get specimen from list
        list_response = client.get("/api/specimens")
        specimens = list_response.json()
        specimen_from_list = specimens[0]
        
        # Get same specimen details
        specimen_id = specimen_from_list["id"]
        detail_response = client.get(f"/api/specimens/{specimen_id}")
        specimen_from_detail = detail_response.json()
        
        # Compare key fields
        key_fields = ["id", "name", "species", "description", "has_image", "has_atlas", "has_model"]
        for field in key_fields:
            assert specimen_from_list[field] == specimen_from_detail[field], \
                f"Field '{field}' differs between list and detail endpoints"
