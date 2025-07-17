"""
API endpoint tests for VISoR Platform backend

Tests for the REST API endpoints defined in the FastAPI application.
Based on the API specification from BACKEND_COMPLETE.md
"""

import sys
import os
import pytest
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
        specimen_id = "macaque_brain_rm009"
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
        specimen_id = "macaque_brain_rm009"
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
        specimen_id = "macaque_brain_rm009"
        response = client.get(f"/api/specimens/{specimen_id}/model")
        
        # This might return 404 if model file doesn't exist in test environment
        if response.status_code == 200:
            data = response.json()
            assert "model_path" in data
            assert isinstance(data["model_path"], str)
        elif response.status_code == 404:
            # Model file not found is acceptable in test environment
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()
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
        specimen_id = "macaque_brain_rm009"
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
        specimen_id = "macaque_brain_rm009"
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
            # Image file not found is acceptable in test environment
            data = response.json()
            assert "detail" in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_atlas_info(self, client):
        """Test GET /api/specimens/{id}/atlas-info"""
        specimen_id = "macaque_brain_rm009"
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
            # Atlas file not found is acceptable in test environment
            data = response.json()
            assert "detail" in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_model_info(self, client):
        """Test GET /api/specimens/{id}/model-info"""
        specimen_id = "macaque_brain_rm009"
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
            # Model file not found is acceptable in test environment
            data = response.json()
            assert "detail" in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_config_info(self, client):
        """Test GET /api/specimens/{id}/config-info"""
        specimen_id = "macaque_brain_rm009"
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
    """Tests for image tile endpoints"""
    
    def test_get_image_tile(self, client):
        """Test GET /api/specimens/{id}/image/{view}/{level}/{z}/{x}/{y}"""
        # TODO: Implement test
        pytest.skip("API endpoint test not yet implemented")
        
        # specimen_id = "macaque_brain_rm009"
        # view = "sagittal"
        # level = 0
        # z, x, y = 0, 0, 0
        # response = client.get(f"/api/specimens/{specimen_id}/image/{view}/{level}/{z}/{x}/{y}")
        # assert response.status_code == 200
        # assert response.headers["content-type"].startswith("image/")
    
    def test_get_atlas_tile(self, client):
        """Test GET /api/specimens/{id}/atlas/{view}/{level}/{z}/{x}/{y}"""
        # TODO: Implement test
        pytest.skip("API endpoint test not yet implemented")

class TestRegionEndpoints:
    """Tests for brain region endpoints"""
    
    def test_get_regions(self, client):
        """Test GET /api/specimens/{id}/regions"""
        # TODO: Implement test
        pytest.skip("API endpoint test not yet implemented")
        
        # specimen_id = "macaque_brain_rm009"
        # response = client.get(f"/api/specimens/{specimen_id}/regions")
        # assert response.status_code == 200
        # data = response.json()
        # assert isinstance(data, list)
        # assert len(data) > 0
    
    def test_pick_region(self, client):
        """Test POST /api/specimens/{id}/pick-region"""
        # TODO: Implement test
        pytest.skip("API endpoint test not yet implemented")
        
        # specimen_id = "macaque_brain_rm009"
        # coordinates = {"x": 100, "y": 100, "z": 100, "view": "sagittal"}
        # response = client.post(f"/api/specimens/{specimen_id}/pick-region", json=coordinates)
        # assert response.status_code == 200

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
            "/api/specimens/macaque_brain_rm009/nonexistent",
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
            "/api/specimens/macaque_brain_rm009",
            "/api/specimens/macaque_brain_rm009/config",
            "/api/specimens/macaque_brain_rm009/metadata"
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
        specimen = next((s for s in data if s["id"] == "macaque_brain_rm009"), None)
        assert specimen is not None, "Expected specimen 'macaque_brain_rm009' not found"
        
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
