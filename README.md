# VISoR Platform - Volumetric Imaging with Synchronized on-the-fly-scan and Readout

A modern web application for high-throughput, high-quality brain mapping visualization at micrometer resolution.

## Features

- **Multi-view Brain Visualization**: Synchronized sagittal, coronal, and horizontal views
- **3D Brain Shell Rendering**: Interactive 3D visualization using Three.js
- **Multi-resolution Images**: Efficient tile-based rendering with OpenSeadragon
- **Region Analysis**: Hierarchical brain region browsing and clicking
- **Multi-channel Support**: Channel selection and image enhancement controls
- **Multi-language**: English and Chinese support

## Architecture

- **Frontend**: Vue.js 3 + TypeScript + Pinia + OpenSeadragon + Three.js
- **Backend**: FastAPI + Python + h5py + Redis caching
- **Data**: HDF5 (.ims) files with multi-resolution pyramids
- **Infrastructure**: Docker Compose + Nginx

## Quick Start

### Full Platform (Docker - Recommended)
```bash
# Clone and setup
git clone <repository>
cd cerevi

# Setup data links (first time only)
./scripts/setup_data_links.sh

# Start all services
docker-compose up --build

# Access the application
open http://localhost:3000    # Frontend
open http://localhost:8000    # Backend API
```

### Development Mode
```bash
# Frontend development (with hot reload)
./scripts/dev.sh

# Backend development (local)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# View API documentation
open http://localhost:8000/docs
```

## Status

### ✅ Backend: Production Ready
- Complete API implementation with all endpoints working
- Docker containerization with health monitoring
- 275GB multi-resolution image processing pipeline
- 241 brain regions with hierarchical structure
- Redis caching and performance optimization

### 🚧 Frontend: In Development
- Vue.js 3 application with TypeScript
- OpenSeadragon integration for image viewing
- Three.js for 3D brain visualization
- Multi-language support (English/Chinese)

## Documentation

- **[Backend Development Guide](BACKEND_DEVELOPMENT.md)** - Complete backend development instructions
- **[Frontend Development Guide](DEVELOPMENT.md)** - Frontend and full-stack development
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when running)

## Data Structure

- **Images**: Multi-resolution 3D arrays in HDF5 (.ims) format
- **Atlas**: Brain region masks with hierarchical structure
- **Models**: 3D brain shell models in .obj format
- **Metadata**: Image dimensions, channels, coordinate systems

## Testing

```bash
# Test backend
./scripts/docker_test.sh start && ./scripts/docker_test.sh test

# Test frontend
cd frontend && npm test

# Full platform test
./scripts/test_platform.sh
```
