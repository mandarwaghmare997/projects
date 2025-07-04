#!/bin/bash

# Qryti Learn Deployment Script
# Automated deployment for production environment

set -e  # Exit on any error

echo "🚀 Starting Qryti Learn Deployment"
echo "=================================="

# Configuration
PROJECT_NAME="qryti-learn"
BACKEND_IMAGE="qryti-learn-backend"
FRONTEND_IMAGE="qryti-learn-frontend"
NETWORK_NAME="qryti-learn-network"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create environment file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        log_info "Creating .env file..."
        cat > .env << EOF
# Qryti Learn Environment Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
FLASK_ENV=production
DATABASE_URL=sqlite:///src/database/app.db
CORS_ORIGINS=https://qryti.com,https://www.qryti.com,http://localhost:3000
EOF
        log_success "Environment file created"
    else
        log_info "Environment file already exists"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build backend
    log_info "Building backend image..."
    docker build -t $BACKEND_IMAGE ./backend
    log_success "Backend image built successfully"
    
    # Build frontend
    log_info "Building frontend image..."
    docker build -t $FRONTEND_IMAGE ./frontend
    log_success "Frontend image built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose down --remove-orphans || true
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    log_success "Services deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    # Wait for services to start
    sleep 10
    
    # Check backend health
    log_info "Checking backend health..."
    for i in {1..30}; do
        if curl -f http://localhost:5000/health &> /dev/null; then
            log_success "Backend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Backend health check failed"
            exit 1
        fi
        sleep 2
    done
    
    # Check frontend health
    log_info "Checking frontend health..."
    for i in {1..30}; do
        if curl -f http://localhost/health &> /dev/null; then
            log_success "Frontend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Frontend health check failed"
            exit 1
        fi
        sleep 2
    done
}

# Show deployment status
show_status() {
    echo ""
    echo "🎉 Deployment Completed Successfully!"
    echo "====================================="
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost"
    echo "   Backend API: http://localhost:5000"
    echo "   Health Check: http://localhost:5000/health"
    echo ""
    echo "📋 Useful Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   Update services: ./deploy.sh"
    echo ""
    echo "🔧 Configuration:"
    echo "   Environment: .env"
    echo "   Docker Compose: docker-compose.yml"
    echo ""
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Deployment failed. Cleaning up..."
        docker-compose down --remove-orphans || true
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main deployment process
main() {
    echo "Starting deployment at $(date)"
    
    check_prerequisites
    create_env_file
    build_images
    deploy_services
    health_check
    show_status
    
    log_success "Qryti Learn deployed successfully!"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping Qryti Learn services..."
        docker-compose down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting Qryti Learn services..."
        docker-compose restart
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        log_warning "Cleaning up all containers and images..."
        docker-compose down --remove-orphans --volumes
        docker rmi $BACKEND_IMAGE $FRONTEND_IMAGE 2>/dev/null || true
        log_success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  clean    - Clean up containers and images"
        exit 1
        ;;
esac

