#!/bin/bash

# Function to display usage information
show_usage() {
    echo "Usage: $0 <command> [mode]"
    echo ""
    echo "Commands:"
    echo "  start [production]     Start containers (build if needed, warn if containers exist)"
    echo "  stop                   Stop all containers"
    echo "  rebuild [production]   Rebuild images with cache (stop containers first, don't auto-start)"
    echo "  rebuild-all [production] Force rebuild all images without cache (stop containers first, don't auto-start)"
    echo "  clean                  Remove unused Docker images"
    echo ""
    echo "Modes (for start/rebuild/rebuild-all):"
    echo "  (no argument)          Development environment with hot reloading"
    echo "  production             Production environment with optimized build"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start development environment"
    echo "  $0 start production   # Start production environment"
    echo "  $0 stop               # Stop all containers"
    echo "  $0 rebuild            # Rebuild development images with cache"
    echo "  $0 rebuild-all        # Force rebuild development images without cache"
    echo "  $0 clean              # Clean unused Docker images"
}

# Function to check if containers are running
check_running_containers() {
    local running_containers
    running_containers=$(docker-compose ps -q 2>/dev/null)
    if [ -n "$running_containers" ]; then
        return 0  # containers are running
    else
        return 1  # no containers running
    fi
}

# Function to check if images exist
check_images_exist() {
    local images
    images=$(docker images -q cerevi* 2>/dev/null)
    if [ -n "$images" ]; then
        return 0  # images exist
    else
        return 1  # no images found
    fi
}

# Function to determine compose files based on mode
get_compose_files() {
    local mode=$1
    if [ "$mode" = "production" ]; then
        echo "-f docker-compose.yml"
    else
        echo "-f docker-compose.yml -f docker-compose.dev-frontend.yml"
    fi
}

# Function to set environment variables based on mode
set_environment() {
    local mode=$1
    if [ "$mode" = "production" ]; then
        export DEBUG=false
        echo "PRODUCTION environment"
    else
        export DEBUG=true
        echo "DEVELOPMENT environment with hot reloading"
    fi
}

# Start command
cmd_start() {
    local mode=$1
    
    echo "Starting $(set_environment $mode)..."
    
    # Check if containers are already running
    if check_running_containers; then
        echo "WARNING: Containers are already running!"
        echo "Current running containers:"
        docker-compose ps
        echo ""
        read -p "Do you want to stop existing containers and continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        cmd_stop
    fi
    
    local compose_files=$(get_compose_files $mode)
    
    # Check if images exist
    if check_images_exist; then
        echo "Docker images found. Starting containers..."
        docker-compose $compose_files up -d
    else
        echo "Docker images not found. Building and starting containers..."
        docker-compose $compose_files up --build -d
    fi
    
    echo "Containers started successfully!"
    echo "Container status:"
    docker-compose ps
}

# Stop command
cmd_stop() {
    echo "Stopping existing containers..."
    
    # Stop both development and production configurations
    docker-compose down
    docker-compose -f docker-compose.yml -f docker-compose.dev-frontend.yml down
    
    echo "All containers stopped successfully!"
}

# Shared rebuild function
do_rebuild() {
    local mode=$1
    local use_cache=$2
    
    if [ "$use_cache" = "true" ]; then
        echo "Rebuilding images with cache for $(set_environment $mode)..."
    else
        echo "Force rebuilding all images for $(set_environment $mode)..."
    fi
    
    # Stop existing containers first
    if check_running_containers; then
        echo "Stopping existing containers before rebuild..."
        cmd_stop
    fi
    
    local compose_files=$(get_compose_files $mode)
    
    if [ "$use_cache" = "true" ]; then
        echo "Rebuilding images (using cache)..."
        docker-compose $compose_files build
    else
        echo "Force rebuilding all images (no cache)..."
        docker-compose $compose_files build --no-cache --force-rm
    fi
    
    echo "Images rebuilt successfully!"
    echo "Note: Containers were not started automatically. Use '$0 start' to start them."
}

# Rebuild command (with cache)
cmd_rebuild() {
    do_rebuild $1 true
}

# Rebuild-all command (no cache)
cmd_rebuild_all() {
    do_rebuild $1 false
}

# Clean command
cmd_clean() {
    echo "Cleaning up orphaned containers..."
    docker-compose down --remove-orphans
    docker-compose -f docker-compose.yml -f docker-compose.dev-frontend.yml down --remove-orphans
    
    #echo "Removing unused containers, networks, images, and volumes..."
    #docker system prune -a --volumes
    echo "Removing dangling containers, networks, images, and volumes..."
    docker system prune
    
    echo "Docker cleanup completed!"
    
    echo "Remaining Docker images:"
    docker images
}

# Main script logic
if [ $# -eq 0 ]; then
    echo "Error: No command specified."
    show_usage
    exit 1
fi

COMMAND=$1
MODE=$2

case $COMMAND in
    start)
        if [ -n "$MODE" ] && [ "$MODE" != "production" ]; then
            echo "Error: Invalid mode '$MODE'. Use 'production' or no argument for development."
            show_usage
            exit 1
        fi
        cmd_start $MODE
        ;;
    stop)
        if [ -n "$MODE" ]; then
            echo "Warning: 'stop' command doesn't use mode argument. Ignoring '$MODE'."
        fi
        cmd_stop
        ;;
    rebuild)
        if [ -n "$MODE" ] && [ "$MODE" != "production" ]; then
            echo "Error: Invalid mode '$MODE'. Use 'production' or no argument for development."
            show_usage
            exit 1
        fi
        cmd_rebuild $MODE
        ;;
    rebuild-all)
        if [ -n "$MODE" ] && [ "$MODE" != "production" ]; then
            echo "Error: Invalid mode '$MODE'. Use 'production' or no argument for development."
            show_usage
            exit 1
        fi
        cmd_rebuild_all $MODE
        ;;
    clean)
        if [ -n "$MODE" ]; then
            echo "Warning: 'clean' command doesn't use mode argument. Ignoring '$MODE'."
        fi
        cmd_clean
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'."
        show_usage
        exit 1
        ;;
esac
