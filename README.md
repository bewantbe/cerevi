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

```bash
# Clone and setup
git clone <repository>
cd cerevi

# Setup data links (first time only)
./scripts/setup_data_links.sh

# Start backend services (Docker)
./scripts/docker_test.sh start

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/specimens

# View API documentation
open http://localhost:8000/docs
```

## ✅ Backend Status: PRODUCTION READY!

The VISoR Platform backend is **fully functional** with:

- ✅ **Complete API Implementation**: All endpoints working
- ✅ **Docker Containerization**: Production-ready containers
- ✅ **Data Processing**: 275GB multi-resolution image pipeline
- ✅ **Brain Region Analysis**: 241 regions with hierarchical structure
- ✅ **Multi-view Support**: Sagittal, coronal, horizontal projections
- ✅ **Performance Optimization**: Redis caching and health monitoring

**Test Results**: See [DOCKER_TEST_RESULTS.md](DOCKER_TEST_RESULTS.md) for complete validation.

## Development

```bash
# Frontend development
cd frontend
npm install
npm run dev

# Backend development  
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Convert region data
python scripts/convert_regions.py
```

## Data Structure

- Images: Multi-resolution 3D arrays in .ims format
- Atlas: Region masks with hierarchical structure
- Models: 3D brain shell models in .obj format
- Metadata: Image dimensions, channels, coordinate systems

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.
