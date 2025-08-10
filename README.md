# Cerevi - Viewer for the 3D Brain Atlas

A modern web application for high-throughput, high-quality brain image and atlas visualization at micrometer resolution and centimeter scale.

It is part of VISoR([Volumetric Imaging with Synchronized on-the-fly-scan and Readout](https://academic.oup.com/nsr/article/6/5/982/5475673)) Platform.

## Features

- **Multi-view Brain Visualization**: Synchronized sagittal, coronal, and horizontal views
- **Multi-resolution Images**: Efficient tile-based rendering
- **Multi-channel Support**: Channel selection and image enhancement controls
- **3D Brain Shell Rendering**: Interactive 3D visualizatiion
- **Region Analysis**: Hierarchical brain region browsing
- **Multi-language**: English and Chinese support

## Architecture

- **Frontend**: Vue.js 3 + TypeScript + Pinia + OpenSeadragon + Three.js
- **Backend**: FastAPI + Python + h5py + Redis caching
- **Data**: HDF5 (.ims) or Zarr files with multi-resolution pyramids
- **Infrastructure**: Docker Compose + Nginx

## Quick Start

### Code and data setup

```bash
# Clone and setup
git clone <repository>
cd cerevi

# Setup data links (first time only),
# You need to modify it to point to your data directory
./scripts/setup_data_links.sh

# check .env file
cat .env
```

### Production mode

```bash
# Start all services
docker-compose up --build
# or
#docker-compose build          # rerun when code changes
#docker-compose up             # ctrl + C to stop

# Access the application
open http://localhost:3000    # Frontend
open http://localhost:8000    # Backend API
```

### Development Mode (Docker)

With hot reload of source code

```bash
# Start development with hot reload and no Redis dependency
docker-compose -f docker-compose.yml -f docker-compose.dev-frontend.yml -f docker-compose.dev-backend.yml up --build

#Or start development through
#./scripts/app_services.sh start

# Access the application
open http://localhost:3001    # Frontend, note the 3001
open http://localhost:8000    # Backend API
# View API documentation
open http://localhost:8000/docs
# simple tests
curl http://localhost:8000/health
curl http://localhost:8000/api/specimens | python3 -m json.tool

# Modify the code in the repository directory
# The frontend and backend will automatically reload when you save changes

# one needs a full rebuild when switching between production and development mode
docker-compose $extra_yml_files build --no-cache --force-rm
# or
docker-compose $extra_yml_files up --build --force-recreate
```

### Development Mode (Local)

Read the `frontend/Dockerfile`, `backend/Dockerfile`.

### Network Issues

If you can't access Docker Hub, try:

```bash
export http_proxy=<your_proxy>
export https_proxy=<your_proxy>
docker-compose up --build
```

If the rebuild is slow due to slow download, try look at repo url:
```bash
# Check the Dockerfile for pip source
cat backend/Dockerfile | grep pip
# Check the Dockerfile for apt source
cat backend/Dockerfile | grep apt
```

### Clean up

```bash
# Stop all services
docker-compose down
# Remove all containers, networks, and volumes
docker system prune -a --volumes
# or just remove dangling images (recommended)
docker system prune
```

## Status

## Documentation

- **[Backend Development Guide](BACKEND_DEVELOPMENT.md)** - Complete backend development instructions
- **[Frontend Development Guide](DEVELOPMENT.md)** - Frontend and full-stack development
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when running)

## Data File

### Directory Structure
```
data/
├── specimens/              # Specimen-specific data
│   └── macaque_brain_rm009/
│       ├── image.ims       # Multi-resolution image data (HDF5)
│       └── atlas.ims       # Brain region masks (HDF5)
├── models/                 # 3D brain shell models
│   └── macaque_brain_rm009/
│       └── brain_shell.obj # 3D brain surface model
└── regions/                # Brain region definitions
    ├── macaque_brain_regions.json   # Hierarchical region structure
    └── macaque_brain_regions.xlsx   # Source atlas data
```

### File Formats

#### Images (`specimens/{specimen_id}/image.ims`)
- **Format**: HDF5 (.ims) with multi-resolution pyramids
- **Structure**: Multiple resolution levels (e.g. 0-7) with decreasing resolution
- **Organization**: `/DataSet/ResolutionLevel {N}/TimePoint 0/Channel {N}/Data`
- **Channels**: e.g. 4 channels (405nm, 488nm, 561nm, 640nm)
- **Data Type**: e.g. 16-bit integer arrays
- **Coordinate System**: Right-handed (z, y, x) order

#### Atlas (`specimens/{specimen_id}/atlas.ims`)
- **Format**: HDF5 (.ims) matching image structure
- **Content**: Brain region masks with integer labels
- **Values**: Region IDs corresponding to hierarchical brain atlas
- **Resolution**: Same pyramid structure as image data

#### 3D Models (`models/{specimen_id}/brain_shell.obj`)
- **Format**: Wavefront OBJ files
- **Content**: 3D brain surface mesh
- **Scale**: e.g. 10 μm units matching image resolution
- **Coordinate System**: Aligned with image coordinate system

#### Brain Regions (`regions/macaque_brain_regions.json`)
- **Format**: JSON with hierarchical structure
- **Content**: e.g. 241 brain regions with 4-level hierarchy
- **Structure**: 
  - `regions[]`: Array of region definitions
  - `hierarchy{}`: Nested anatomical organization
  - `region_lookup{}`: ID-based region access
- **Metadata**: Coordinate system, conversion date, region count

### Metadata and Configuration

These settings can be configured in `backend/app/config.py`:

- **Coordinate System**: Right-handed with z_y_x axes order (`coordinate_system`, `axes_order`)
- **Resolution**: e.g. 10 μm per pixel at level 0 (`image_resolution_um`)
- **Tile Size**: e.g. 512×512 pixels for efficient streaming (`default_tile_size`)
- **Supported Views**: Sagittal, coronal, horizontal (defined in view types)
- **Channel Mapping**: Configurable wavelength assignments (`default_channels`)
- **Resolution Levels**: Maximum pyramid levels (`max_resolution_level`)
- **Model Scale**: 3D model units in micrometers (`mesh_scale_factor`)
- **Cache Settings**: TTL for tiles, metadata, and regions (`cache_ttl_*`)

## Testing

```bash
# Test backend
./scripts/docker_test.sh start && ./scripts/docker_test.sh test

# test backend functionality in docker
docker-compose up -d --force-recreate backend
docker exec cerevi_backend_1 python -m pytest tests/ -v -rs

# Test frontend
docker-compose up -d --force-recreate frontend
cd frontend && npm test

# Full platform test
./scripts/test_platform.sh
```
