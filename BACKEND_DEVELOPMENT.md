# VISoR Platform Backend Development Guide

A comprehensive guide for developing the VISoR Platform backend - a high-performance FastAPI application for brain imaging visualization.

## 🚀 Quick Start

### Option 1: Local Development (Recommended)
```bash
# Setup environment
cd backend
pip install -r requirements.txt

# Start Redis (required for caching)
redis-server

# Start the backend with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Interactive API documentation
```

### Option 2: Docker Development
```bash
# Start backend with Redis using Docker
./scripts/docker_test.sh start

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/api/specimens

# View logs
./scripts/docker_test.sh logs

# Stop containers
./scripts/docker_test.sh stop
```

### Option 3: Backend Development without Redis
```bash
# For backend development when Redis is not needed or available
docker-compose -f docker-compose.yml -f docker-compose.dev-backend-no-redis.yml up backend frontend

# This configuration:
# ✅ Disables Redis dependency for backend
# ✅ Enables debug mode  
# ✅ Useful for testing without cache layer
# ✅ Simplifies development setup

# Test the API (Redis-related features will be disabled)
curl http://localhost:8000/health
curl http://localhost:8000/api/specimens
```

## 📋 Prerequisites

### System Requirements
- **Python 3.11+** (recommended: 3.11.6)
- **Redis 7+** (for caching)
- **Git** (for version control)
- **Docker & Docker Compose** (optional, for containerized development)

### System Dependencies (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y \
    gcc g++ libhdf5-dev pkg-config curl python3-pip

# macOS (with Homebrew)
brew install hdf5 pkg-config redis

# Fedora/RHEL
sudo dnf install gcc gcc-c++ hdf5-devel pkgconfig curl python3-pip
```

### Python Environment Setup
```bash
# Create virtual environment (recommended)
python3 -m venv visor-env
source visor-env/bin/activate  # Linux/macOS
# visor-env\Scripts\activate   # Windows

# Install dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

## 🏗️ Project Structure

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

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Application settings
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Data paths
DATA_PATH=./data
SPECIMENS_PATH=./data/specimens
MODELS_PATH=./data/models
REGIONS_PATH=./data/regions

# Redis settings
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# CORS settings (for frontend development)
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:5173"]
```

### Data Setup
```bash
# Setup data directory structure
./scripts/setup_data_links.sh

# Verify data is accessible
ls -la data/specimens/macaque_brain_rm009/
ls -la data/regions/
ls -la data/models/
```

## 💻 Development Workflow

### Running the Backend Locally

1. **Start Redis** (required for caching):
   ```bash
   # Option 1: Local Redis
   redis-server
   
   # Option 2: Docker Redis
   docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
   ```

2. **Start the FastAPI server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify it's working**:
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Browse API documentation
   open http://localhost:8000/docs
   ```

### Development Features

- **Hot Reload**: Code changes automatically reload the server
- **Interactive Docs**: Auto-generated API documentation at `/docs`
- **Health Monitoring**: Built-in health check endpoint
- **Comprehensive Logging**: Structured logging with configurable levels
- **CORS Support**: Pre-configured for frontend development

## 🔧 Working with the Code

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

## 🧪 Testing

### Running Tests

```bash
# Option 1: Using pytest (recommended)
cd backend
pytest tests/ -v

# Option 2: Using simple test runner
cd backend/tests
python run_tests.py

# Option 3: Run specific test files
pytest tests/test_integration.py
pytest tests/test_api_endpoints.py
```

### Test Categories

- **Integration Tests** (`test_integration.py`): Test component integration
- **API Tests** (`test_api_endpoints.py`): Test REST API endpoints
- **Unit Tests**: Test individual functions and classes

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

### API Testing with curl

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
```

## 🐳 Docker Development

### Using Docker for Development

```bash
# Build and start all services
./scripts/docker_test.sh start

# Check container status
./scripts/docker_test.sh status

# View backend logs
./scripts/docker_test.sh logs

# Run API tests
./scripts/docker_test.sh test

# Stop all containers
./scripts/docker_test.sh stop

# Clean up containers
./scripts/docker_test.sh remove
```

### Docker Development Features

- **Consistent Environment**: Same environment across all developers
- **Redis Integration**: Automatically configured Redis caching
- **Data Volume Mounting**: Access to large datasets
- **Health Monitoring**: Automatic health checks
- **Easy Reset**: Quick container recreation

### Docker Compose Services

```yaml
# docker-compose.yml (relevant backend parts)
backend:
  build: ./backend
  ports:
    - "8000:8000"
  environment:
    - REDIS_URL=redis://redis:6379
    - DATA_PATH=/app/data
  volumes:
    - ./backend:/app
    - ./data:/app/data:ro
  depends_on:
    - redis

redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

## 🔍 Debugging and Logging

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use logging in your code
logger.info("Processing request")
logger.warning("Unusual condition detected")
logger.error("Error occurred", exc_info=True)
```

### Debug Mode Features

```bash
# Enable debug mode
export DEBUG=true

# Start with debug logging
uvicorn app.main:app --reload --log-level debug
```

Debug mode enables:
- Detailed error messages
- Interactive API documentation
- Verbose logging
- Hot reload on code changes

### Common Debugging Scenarios

```bash
# Check if Redis is accessible
redis-cli ping

# Verify data paths exist
ls -la data/specimens/macaque_brain_rm009/

# Test specific API endpoint
curl -v http://localhost:8000/api/specimens

# Check container logs
docker logs visor-backend-test

# Monitor resource usage
docker stats visor-backend-test
```

## 🚀 Performance Optimization

### Caching Strategy

The backend uses Redis for caching:
- **Tile Cache**: Image tiles cached for 1 hour
- **Metadata Cache**: Specimen metadata cached for 24 hours
- **Region Cache**: Brain region data cached for 24 hours

### Memory Management

```python
# Efficient data loading
with h5py.File(image_path, 'r') as f:
    # Load only required data chunks
    tile_data = f['DataSet'][z, y:y+512, x:x+512]

# Use generators for large datasets
def process_large_dataset():
    for chunk in dataset_chunks:
        yield process_chunk(chunk)
```

### Performance Monitoring

```bash
# Monitor API response times
curl -w "Time: %{time_total}s\n" http://localhost:8000/api/specimens

# Check Redis memory usage
redis-cli info memory

# Monitor container resources
docker stats --no-stream visor-backend-test
```

## 📚 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/api/specimens` | GET | List all specimens |
| `/api/specimens/{id}` | GET | Get specimen details |
| `/api/specimens/{id}/image/{view}/{level}/{z}/{x}/{y}` | GET | Get image tile |
| `/api/specimens/{id}/atlas/{view}/{level}/{z}/{x}/{y}` | GET | Get atlas mask |
| `/api/specimens/{id}/regions` | GET | Get brain regions |
| `/api/specimens/{id}/pick-region` | POST | Identify region by coordinates |
| `/api/specimens/{id}/metadata` | GET | Get complete metadata |

### Response Formats

All API responses use JSON format with consistent error handling:

```json
// Success response
{
  "id": "macaque_brain_rm009",
  "name": "Macaque Brain RM009",
  "status": "available"
}

// Error response
{
  "detail": "Specimen not found",
  "status_code": 404
}
```

## 🛠️ Troubleshooting

### Common Issues

**1. Redis Connection Failed**
```bash
# Check if Redis is running
redis-cli ping
# Expected: PONG

# Start Redis if not running
redis-server
# or with Docker:
docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
```

**2. Data Path Not Found**
```bash
# Verify data directory exists
ls -la data/specimens/macaque_brain_rm009/

# Setup data links if missing
./scripts/setup_data_links.sh
```

**3. Import Errors**
```bash
# Verify Python environment
python -c "import fastapi, h5py, redis; print('Dependencies OK')"

# Reinstall dependencies if needed
pip install -r requirements.txt --force-reinstall
```

**4. Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process or use different port
uvicorn app.main:app --reload --port 8001
```

**5. Docker Container Issues**
```bash
# Check container status
docker ps -a

# View container logs
docker logs visor-backend-test

# Rebuild containers
docker-compose down && docker-compose up --build
```

### Performance Issues

**Slow API Responses:**
- Check Redis cache hit rates
- Monitor data file access patterns
- Verify network connectivity
- Review query optimization

**High Memory Usage:**
- Monitor HDF5 file access patterns
- Check for memory leaks in processing
- Optimize data loading strategies

### Getting Help

1. **Check Logs**: Always start with application logs
2. **API Documentation**: Visit `/docs` for interactive testing
3. **Test Scripts**: Use `./scripts/docker_test.sh test` for validation
4. **Container Inspection**: Use `docker logs` and `docker stats`

## 🚀 Production Deployment

### Environment Preparation

```bash
# Production environment variables
export DEBUG=false
export LOG_LEVEL=WARNING
export REDIS_URL=redis://production-redis:6379
export DATA_PATH=/data/visor
```

### Docker Production Build

```bash
# Build production image
docker build -t visor-backend:latest ./backend

# Run production container
docker run -d \
  --name visor-backend-prod \
  -p 8000:8000 \
  -e DEBUG=false \
  -e REDIS_URL=redis://redis:6379 \
  -v /data/visor:/app/data:ro \
  visor-backend:latest
```

### Health Monitoring

The backend includes comprehensive health checks:
- **Health Endpoint**: `/health` returns service status
- **Docker Health Check**: Automatic container health monitoring
- **Redis Connectivity**: Verifies cache availability
- **Data Access**: Confirms data path accessibility

### Security Considerations

- **Read-only Data Mounts**: Data volumes mounted as read-only
- **Environment Isolation**: Use environment variables for secrets
- **CORS Configuration**: Restrict origins in production
- **Container Security**: Run with non-root user in production

## 📈 Next Steps

### Advanced Development Topics

- **Custom Middleware**: Add request/response processing
- **Database Integration**: Connect to PostgreSQL/MongoDB
- **Authentication**: Add JWT-based authentication
- **Rate Limiting**: Implement API rate limiting
- **Monitoring**: Add Prometheus metrics
- **Documentation**: Generate OpenAPI specifications

### Contributing to the Backend

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Write tests**: Add tests for new functionality
4. **Follow code style**: Use `black` and `isort` for formatting
5. **Update documentation**: Keep this guide up to date
6. **Submit pull request**: Include clear description of changes

---

## 📞 Support

For questions or issues with backend development:

1. **Check this guide** for common solutions
2. **Review test results** with `./scripts/docker_test.sh test`
3. **Check application logs** for error details
4. **Consult API documentation** at `/docs`
5. **Create an issue** in the project repository

---

*This guide covers VISoR Platform Backend v1.0.0. For frontend development, see [DEVELOPMENT.md](DEVELOPMENT.md).*
