# VISoR Platform Backend Tests

This directory contains the test suite for the VISoR Platform backend, organized following Python testing best practices.

## Test Structure

```
backend/tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_integration.py         # Integration tests (core functionality)
├── test_api_endpoints.py       # API endpoint tests (placeholders)
├── run_tests.py               # Simple test runner (no pytest required)
└── README.md                  # This file
```

## Running Tests

### Option 1: Using the Simple Test Runner (Recommended for Development)

```bash
# From the backend/tests directory
cd backend/tests
python run_tests.py

# Run specific test types
python run_tests.py integration   # Only integration tests
python run_tests.py api           # Only API tests  
python run_tests.py all           # All tests (default)
```

### Option 2: Using pytest (Recommended for CI/CD)

```bash
# From the backend directory
cd backend
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test files
pytest tests/test_integration.py
pytest tests/test_api_endpoints.py

# Run specific test classes or methods
pytest tests/test_integration.py::TestBackendIntegration::test_imports
```

### Option 3: Legacy Script (Deprecated)

The original test script is still available for backward compatibility:

```bash
# From the project root
python scripts/test_backend.py
```

**Note**: This will show a deprecation notice and recommend using the new test structure.

## Test Categories

### Integration Tests (`test_integration.py`)

Tests the integration between different backend components:

- **`test_imports()`** - Verifies all backend modules can be imported
- **`test_data_access()`** - Tests data file and directory access
- **`test_region_loading()`** - Tests JSON region data loading
- **`test_image_metadata_extraction()`** - Tests Imaris/HDF5 file handling

### API Endpoint Tests (`test_api_endpoints.py`)

Tests for REST API endpoints (currently placeholders):

- **Health endpoints** - `/health` status checks
- **Specimen endpoints** - CRUD operations for specimens
- **Image endpoints** - Image tile serving
- **Region endpoints** - Brain region operations
- **Error handling** - Invalid inputs and edge cases

## Test Configuration

### Fixtures (`conftest.py`)

- `backend_path` - Path to the backend directory
- `data_path` - Path to the data directory
- `client` - FastAPI test client (for API tests)

### Environment Setup

Tests automatically handle Python path configuration to import backend modules. No additional setup is required.

## Implementation Status

### ✅ Completed
- Integration test conversion from original script
- Pytest-compatible structure
- Simple test runner for development
- Backward compatibility with original script

### 🚧 In Progress
- API endpoint test implementations
- Test fixtures for data setup
- Performance and load tests

### 📋 Planned
- Unit tests for individual components
- Mock data for isolated testing
- CI/CD integration tests
- Coverage reporting

## Adding New Tests

### For Integration Tests

Add new test methods to `TestBackendIntegration` class in `test_integration.py`:

```python
def test_new_functionality(self):
    """Test description"""
    # Import required modules
    from app.some_module import SomeClass
    
    # Test implementation
    assert SomeClass is not None
    # Add more assertions...
```

### For API Tests

Uncomment and implement placeholder tests in `test_api_endpoints.py`:

```python
def test_some_endpoint(self, client):
    """Test some API endpoint"""
    response = client.get("/api/some-endpoint")
    assert response.status_code == 200
    data = response.json()
    # Add assertions for response data...
```

### For New Test Categories

Create new test files following the naming convention `test_*.py`:

```python
# backend/tests/test_new_category.py
import pytest

class TestNewCategory:
    def test_something(self):
        assert True
```

## Troubleshooting

### Import Errors

If you encounter import errors:

1. Ensure you're running tests from the correct directory
2. Check that the backend modules are available
3. Verify the Python path configuration in `conftest.py`

### Data Access Issues

If data access tests fail:

1. Check that data directories exist
2. Verify file permissions
3. Ensure data files are in the expected locations

### Pytest Not Found

If pytest is not available:

1. Use the simple test runner: `python run_tests.py`
2. Or install pytest: `pip install pytest`
3. Check `requirements.txt` for the correct pytest version

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Assertions**: Use descriptive assertion messages
3. **Setup/Teardown**: Use pytest fixtures for common setup
4. **Documentation**: Document test purpose and expected behavior
5. **Coverage**: Aim for comprehensive test coverage

## Migration Notes

This test structure was created by migrating from `scripts/test_backend.py`. Key changes:

- Converted from custom test runner to pytest format
- Replaced print statements with proper assertions
- Added proper test organization and documentation
- Maintained all original test functionality
- Added support for both pytest and simple test runner

For questions or issues with the test suite, refer to the project documentation or create an issue in the project repository.
