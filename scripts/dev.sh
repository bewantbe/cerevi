#!/bin/bash

# Development script for hot reloading frontend
echo "Starting development environment with hot reloading..."

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
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down --remove-orphans

# Start development environment with fresh build
echo "Building and starting development containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build --force-recreate

echo "Development environment stopped."
