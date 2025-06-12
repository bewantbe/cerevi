#!/bin/bash

# Check for production mode argument
if [ "$1" = "production" ]; then
    echo "Starting PRODUCTION environment..."
    MODE="production"
    COMPOSE_FILES="-f docker-compose.yml"
    BUILD_MESSAGE="Building and starting production containers..."
elif [ "$1" = "" ]; then
    echo "Starting DEVELOPMENT environment with hot reloading..."
    MODE="development"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
    BUILD_MESSAGE="Building and starting development containers..."
else
    echo "Usage: $0 [production]"
    echo ""
    echo "Arguments:"
    echo "  (no argument)  Start development environment with hot reloading"
    echo "  production     Start production environment with optimized build"
    exit 1
fi

# Stop any existing containers (both production and development)
echo "Stopping existing containers..."
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Remove existing images to ensure clean build (optional - uncomment if needed)
# echo "Removing existing frontend images..."
# docker rmi cerevi_frontend 2>/dev/null || true
# docker rmi cerevi-frontend 2>/dev/null || true

# Clean up any orphaned containers
echo "Cleaning up orphaned containers..."
docker-compose $COMPOSE_FILES down --remove-orphans

# Start the appropriate environment with fresh build
echo "$BUILD_MESSAGE"
docker-compose $COMPOSE_FILES up --build --force-recreate

echo "$MODE environment stopped."
