# Development Guide

## Hot Reloading Frontend in Docker

This project supports hot reloading for the frontend when running in Docker containers for development purposes.

### Quick Start

1. **Start development environment with hot reloading:**
   ```bash
   ./scripts/dev.sh
   ```

2. **Or manually with docker-compose:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```

### Container and Image Management

**What the `dev.sh` script does:**

✅ **Stops all existing containers** (both production and development)
✅ **Cleans up orphaned containers** 
✅ **Forces recreation** of containers with `--force-recreate`
✅ **Rebuilds images** with `--build` flag
✅ **Creates new development image** using `Dockerfile.dev`

**Image behavior:**
- Creates a **new development image** tagged as `cerevi_frontend` (development version)
- **Does NOT remove** existing production images by default (for safety)
- Use `--build` flag to rebuild if you've made changes to Dockerfile.dev or package.json

**For complete cleanup** (if you want to remove all images and start fresh):
```bash
# Stop containers
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Remove project images
docker rmi cerevi_frontend cerevi-frontend 2>/dev/null || true

# Start fresh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build --force-recreate
```

3. **Access the application:**
   - **Frontend (with hot reloading): http://localhost:3001** ← Use this for development
   - Backend API: http://localhost:8000
   - ⚠️ **Note**: http://localhost:3000 will show `ERR_EMPTY_RESPONSE` in development mode (this is expected)

### What's Different in Development Mode

**Production vs Development:**
- **Production**: Builds static files and serves via nginx on port 80
- **Development**: Runs Vite dev server with hot module replacement (HMR) on port 5173

**Development Configuration:**
- Uses `Dockerfile.dev` instead of production `Dockerfile`
- Runs `npm run dev` instead of building static files
- Maps port 3001 to Vite's dev server (port 5173 inside container)
- Enables file watching with polling for Docker compatibility
- Supports Vue DevTools and HMR

**Why port 3000 doesn't work in development:**
When using the development override, Docker Compose merges configurations:
- `docker-compose.yml` maps `3000:80` (for nginx)
- `docker-compose.dev.yml` overrides to use `Dockerfile.dev` (runs Vite, not nginx)
- Result: Port 3000 tries to connect to nginx on port 80, but only Vite is running on port 5173
- Solution: Use port 3001 which correctly maps to the Vite dev server

### Development Files

- `docker-compose.dev.yml` - Development override configuration
- `frontend/Dockerfile.dev` - Development Docker image
- `scripts/dev.sh` - Convenience script to start dev environment
- `frontend/vite.config.ts` - Updated with Docker-compatible dev server settings

### Hot Reloading Features

✅ **Instant file change detection**
✅ **Vue component hot replacement**
✅ **CSS hot reloading**
✅ **Vue DevTools support**
✅ **Automatic browser refresh**

### Troubleshooting

**If hot reloading isn't working:**

1. Ensure you're using the development docker-compose files
2. Check that volumes are properly mounted (`./frontend:/app`)
3. Verify Vite dev server is running (check container logs)
4. Make sure ports aren't conflicting with other services

**View container logs:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs frontend
```

**Rebuild containers if needed:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build --force-recreate
```

### Production Deployment

For production, continue using the regular docker-compose:
```bash
docker-compose up --build
```

This will use the production Dockerfile that builds static files and serves them via nginx.
