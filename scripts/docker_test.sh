#!/bin/bash

# VISoR Platform Docker Test Management Script

set -e

BACKEND_CONTAINER="visor-backend-test"
REDIS_CONTAINER="redis-test"
BACKEND_IMAGE="visor-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if container exists
container_exists() {
    docker ps -a --format "table {{.Names}}" | grep -q "^$1$"
}

# Function to check if container is running
container_running() {
    docker ps --format "table {{.Names}}" | grep -q "^$1$"
}

# Start containers
start_containers() {
    log_info "Starting VISoR Platform test containers..."
    
    # Start Redis if not running
    if container_running "$REDIS_CONTAINER"; then
        log_warning "Redis container already running"
    else
        if container_exists "$REDIS_CONTAINER"; then
            log_info "Starting existing Redis container..."
            docker start "$REDIS_CONTAINER"
        else
            log_info "Creating and starting Redis container..."
            docker run -d --name "$REDIS_CONTAINER" redis:7-alpine
        fi
        log_success "Redis container started"
    fi
    
    # Start Backend if not running
    if container_running "$BACKEND_CONTAINER"; then
        log_warning "Backend container already running"
    else
        if container_exists "$BACKEND_CONTAINER"; then
            log_info "Starting existing backend container..."
            docker start "$BACKEND_CONTAINER"
        else
            log_info "Creating and starting backend container..."
            docker run -d --name "$BACKEND_CONTAINER" \
                --link "$REDIS_CONTAINER":redis \
                -e REDIS_URL=redis://redis:6379 \
                -e DATA_PATH=/app/data \
                -v "$(pwd)/data:/app/data:ro" \
                -p 8000:8000 \
                "$BACKEND_IMAGE"
        fi
        log_success "Backend container started"
    fi
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 5
    
    # Test health endpoint
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log_success "Backend is healthy and ready!"
        echo
        log_info "Testing API endpoints:"
        echo "🔗 Health: http://localhost:8000/health"
        echo "🔗 API Docs: http://localhost:8000/docs"
        echo "🔗 Specimens: http://localhost:8000/api/specimens"
    else
        log_error "Backend health check failed"
        show_logs
        exit 1
    fi
}

# Stop containers
stop_containers() {
    log_info "Stopping VISoR Platform test containers..."
    
    if container_running "$BACKEND_CONTAINER"; then
        docker stop "$BACKEND_CONTAINER"
        log_success "Backend container stopped"
    fi
    
    if container_running "$REDIS_CONTAINER"; then
        docker stop "$REDIS_CONTAINER"
        log_success "Redis container stopped"
    fi
}

# Remove containers
remove_containers() {
    log_info "Removing VISoR Platform test containers..."
    
    if container_exists "$BACKEND_CONTAINER"; then
        docker rm -f "$BACKEND_CONTAINER"
        log_success "Backend container removed"
    fi
    
    if container_exists "$REDIS_CONTAINER"; then
        docker rm -f "$REDIS_CONTAINER"
        log_success "Redis container removed"
    fi
}

# Show container status
show_status() {
    log_info "Container Status:"
    echo
    
    if container_running "$REDIS_CONTAINER"; then
        echo -e "  Redis:   ${GREEN}Running${NC}"
    elif container_exists "$REDIS_CONTAINER"; then
        echo -e "  Redis:   ${YELLOW}Stopped${NC}"
    else
        echo -e "  Redis:   ${RED}Not Created${NC}"
    fi
    
    if container_running "$BACKEND_CONTAINER"; then
        echo -e "  Backend: ${GREEN}Running${NC}"
    elif container_exists "$BACKEND_CONTAINER"; then
        echo -e "  Backend: ${YELLOW}Stopped${NC}"
    else
        echo -e "  Backend: ${RED}Not Created${NC}"
    fi
    
    echo
    
    if container_running "$BACKEND_CONTAINER"; then
        log_info "Testing backend health..."
        if curl -f -s http://localhost:8000/health > /dev/null; then
            echo -e "  Health:  ${GREEN}Healthy${NC}"
            echo
            log_info "Available endpoints:"
            echo "  🔗 Health: curl http://localhost:8000/health"
            echo "  🔗 Docs: http://localhost:8000/docs"
            echo "  🔗 Specimens: curl http://localhost:8000/api/specimens"
        else
            echo -e "  Health:  ${RED}Unhealthy${NC}"
        fi
    fi
}

# Show logs
show_logs() {
    log_info "Recent backend logs:"
    echo
    if container_exists "$BACKEND_CONTAINER"; then
        docker logs --tail 20 "$BACKEND_CONTAINER"
    else
        log_error "Backend container doesn't exist"
    fi
}

# Build backend image
build_backend() {
    log_info "Building backend Docker image..."
    docker build -t "$BACKEND_IMAGE" ./backend
    log_success "Backend image built successfully"
}

# Run API tests
test_api() {
    log_info "Running API tests..."
    
    if ! container_running "$BACKEND_CONTAINER"; then
        log_error "Backend container is not running. Use 'start' command first."
        exit 1
    fi
    
    echo
    log_info "Testing health endpoint..."
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    echo
    log_info "Testing specimens endpoint..."
    curl -s http://localhost:8000/api/specimens | python3 -m json.tool
    
    echo
    log_success "API tests completed successfully!"
}

# Show help
show_help() {
    echo "VISoR Platform Docker Test Management"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start    - Start Redis and Backend containers"
    echo "  stop     - Stop containers"
    echo "  restart  - Restart containers"
    echo "  remove   - Remove containers"
    echo "  status   - Show container status"
    echo "  logs     - Show backend logs"
    echo "  build    - Build backend Docker image"
    echo "  test     - Run API tests"
    echo "  help     - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start     # Start the platform"
    echo "  $0 test      # Test API endpoints"
    echo "  $0 logs      # Check logs"
    echo "  $0 remove    # Clean up containers"
}

# Main command handler
case "${1:-help}" in
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        stop_containers
        sleep 2
        start_containers
        ;;
    remove|clean)
        remove_containers
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        build_backend
        ;;
    test)
        test_api
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac
