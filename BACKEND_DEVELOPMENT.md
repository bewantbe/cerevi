# Backend Development Guide

## Configuration

### Environment Variables
Create a `.env` file in the project root, see `.env.example` for reference.

### Data Setup (only need once)
```bash
# Setup data directory structure
./scripts/setup_data_links.sh

# Verify data is accessible
ls -la data/specimens/macaque_brain_rm009/
ls -la data/regions/
ls -la data/models/
```

Note that the `/share/data` and `/home/xyy` path in `docker-compose.yml` is necessary
because the data is link through symbolic links.

## Quick Start

### Docker development (recommended)

```bash
# Start backend in development mode with hot reload (no Redis dependency)
docker-compose -f docker-compose.yml -f docker-compose.dev-backend.yml up -d backend

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/api/specimens | python3 -m json.tool

# Full test
docker-compose exec backend python -m pytest tests/ -v -rs
# or
docker exec cerevi_backend_1 python -m pytest tests/ -v -rs

# View logs
docker-compose logs -f backend

# Check Redis memory usage
docker exec cerevi_redis_1 redis-cli info memory

# Monitor container resources
docker stats --no-stream cerevi_backend_1

# Enter the backend container
docker-compose exec backend /bin/sh       # about 0.74 s overhead
# or
docker exec -it cerevi_backend_1 /bin/sh  # about 0.15 s overhead

# Stop containers
docker-compose down

# Restart containers
docker-compose up --build -d
```

### Local Development

```bash
sudo apt-get update && sudo apt-get install -y \
    gcc g++ libhdf5-dev pkg-config curl python3-pip

python3 -m venv visor-env
source visor-env/bin/activate

# Setup environment
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Start Redis (required for caching)
redis-server

# Start the backend with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test the API
curl http://localhost:8000/health
```

### API endpoints

See the [API documentation](http://localhost:8000/docs) for details on available endpoints.
Need to run the backend server first.

### API Testing

With curl

```bash
# Health check
curl http://localhost:8000/health

# Get specimens
curl http://localhost:8000/api/specimens

# Get specimen details
curl http://localhost:8000/api/specimens/macaque_brain_rm009

# Get brain regions
curl http://localhost:8000/api/specimens/macaque_brain_rm009/regions

# Test with JSON data
curl -X POST http://localhost:8000/api/specimens/macaque_brain_rm009/pick-region \
  -H "Content-Type: application/json" \
  -d '{"x": 100, "y": 200, "z": 50, "view": "sagittal", "level": 3}'

# Test reading images
curl -o tmp/image_tile.jpg "http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/4/256/0/0"
```

With pytest

```bash
# Run all tests
cd backend
pytest tests/ -v

# Run specific test files
pytest tests/test_integration.py
pytest tests/test_api_endpoints.py

# Test Specific Class
docker-compose exec backend python -m pytest tests/test_api_endpoints.py::TestHealthEndpoint -v -rs

# Test Specific Method
docker-compose exec backend python -m pytest tests/test_api_endpoints.py::TestHealthEndpoint::test_health_check -v -rs
```

# Currently testing
```bash
cd backend
#curl -o tmp/image_tile.jpg "http://localhost:8000/api/specimens/macaque_brain_rm009/image/sagittal/0/0/0/0"
curl -o tmp/image_tile.jpg "http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/0/0/0/0"

docker-compose exec backend python dev_script/fetch_image_backend.py
docker-compose exec backend python dev_script/fetch_image_h5py.py
```

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration settings
│   ├── api/               # API endpoints
│   │   ├── __init__.py
│   │   ├── specimens.py   # Specimen-related endpoints
│   │   ├── tiles.py       # Image tile serving
│   │   ├── regions.py     # Brain region operations
│   │   └── metadata.py    # Metadata endpoints
│   ├── models/            # Pydantic data models
│   │   ├── __init__.py
│   │   ├── specimen.py    # Specimen models
│   │   └── region.py      # Region models
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── tile_service.py       # Image processing
│   │   └── imaris_handler.py     # HDF5/Imaris file handling
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── test_integration.py       # Integration tests
│   ├── test_api_endpoints.py     # API tests
│   └── run_tests.py       # Simple test runner
├── Dockerfile             # Production Docker image
├── requirements.txt       # Python dependencies
└── README.md             # Basic backend info
```

## Working with the Code

### Adding New API Endpoints

1. **Create endpoint in appropriate module** (`app/api/`):
   ```python
   # app/api/my_feature.py
   from fastapi import APIRouter, HTTPException
   from ..models.my_model import MyModel
   
   router = APIRouter()
   
   @router.get("/my-endpoint")
   async def get_my_data() -> MyModel:
       try:
           # Your logic here
           return MyModel(data="example")
       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))
   ```

2. **Register router in main.py**:
   ```python
   from .api import my_feature
   app.include_router(my_feature.router, prefix="/api", tags=["my-feature"])
   ```

### Working with Data Models

```python
# app/models/my_model.py
from pydantic import BaseModel, Field
from typing import Optional, List

class MyModel(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    optional_field: Optional[str] = None
    items: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "example-id",
                "name": "Example Name",
                "items": ["item1", "item2"]
            }
        }
```

### Configuration Management

```python
# Access configuration anywhere in the app
from app.config import settings

# Use configuration
data_path = settings.data_path
redis_url = settings.redis_url
debug_mode = settings.debug
```

### Error Handling

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@router.get("/example")
async def example_endpoint():
    try:
        # Your logic here
        result = some_operation()
        return result
    except FileNotFoundError:
        logger.error("Required file not found")
        raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Writing New Tests

```python
# tests/test_my_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_my_endpoint():
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data

@pytest.mark.asyncio
async def test_async_function():
    # Test async functions
    result = await my_async_function()
    assert result is not None
```
