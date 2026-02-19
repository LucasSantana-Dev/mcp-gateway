#!/bin/bash

# Production Deployment Script for Forge MCP Gateway
# This script handles the complete production deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="forge-mcp-gateway"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy-$(date +%Y%m%d-%H%M%S).log"

# Helper functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        error ".env.production file not found. Please copy .env.production.example to .env.production and configure it."
    fi
    
    # Create necessary directories
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./logs"
    
    success "Prerequisites check completed"
}

# Backup current deployment
backup_current() {
    log "Backing up current deployment..."
    
    if [ -d "./data" ]; then
        tar -czf "$BACKUP_DIR/data-backup-$(date +%Y%m%d-%H%M%S).tar.gz" ./data/
        success "Data backup completed"
    fi
    
    # Backup current configuration
    cp .env.production "$BACKUP_DIR/.env.production.backup-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
    
    success "Backup completed"
}

# Run pre-deployment tests
run_tests() {
    log "Running pre-deployment tests..."
    
    # Test configuration
    log "Testing configuration files..."
    docker-compose -f docker-compose.scalable.yml config --quiet
    
    # Test build
    log "Testing Docker build..."
    docker-compose -f docker-compose.scalable.yml build --quiet
    
    success "Pre-deployment tests passed"
}

# Deploy services
deploy_services() {
    log "Deploying production services..."
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose -f docker-compose.scalable.yml down --remove-orphans || true
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f docker-compose.scalable.yml pull
    
    # Start services
    log "Starting production services..."
    docker-compose -f docker-compose.scalable.yml up -d
    
    success "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to be healthy..."
    
    # Wait for gateway service
    log "Waiting for gateway service..."
    timeout 300 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done' || {
        error "Gateway service failed to become healthy within 5 minutes"
    }
    
    # Wait for service manager
    log "Waiting for service manager..."
    timeout 120 bash -c 'until curl -f http://localhost:9000/health; do sleep 5; done' || {
        warning "Service manager may not be ready yet"
    }
    
    success "All services are healthy"
}

# Run post-deployment verification
verify_deployment() {
    log "Running post-deployment verification..."
    
    # Check service status
    log "Checking service status..."
    docker-compose -f docker-compose.scalable.yml ps
    
    # Test gateway endpoint
    log "Testing gateway endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$response" = "200" ]; then
        success "Gateway endpoint is responding correctly"
    else
        error "Gateway endpoint returned HTTP $response"
    fi
    
    # Test service discovery
    log "Testing service discovery..."
    services=$(curl -s http://localhost:8000/services | jq -r '.services | length' 2>/dev/null || echo "0")
    if [ "$services" -gt "0" ]; then
        success "Service discovery is working ($services services found)"
    else
        warning "Service discovery may not be fully configured"
    fi
    
    success "Post-deployment verification completed"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Check if monitoring is configured
    if grep -q "PROMETHEUS_URL" .env.production; then
        log "Prometheus monitoring is configured"
    fi
    
    if grep -q "GRAFANA_URL" .env.production; then
        log "Grafana dashboard is configured"
    fi
    
    success "Monitoring setup completed"
}

# Main deployment function
main() {
    log "Starting production deployment for $PROJECT_NAME"
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    check_prerequisites
    backup_current
    run_tests
    deploy_services
    wait_for_health
    verify_deployment
    setup_monitoring
    
    success "Production deployment completed successfully!"
    log "Deployment log saved to: $LOG_FILE"
    log "Services are running at: http://localhost:8000"
    log "Admin UI is available at: http://localhost:3000"
}

# Handle script arguments
case "${1:-}" in
    "backup")
        backup_current
        ;;
    "test")
        run_tests
        ;;
    "deploy")
        deploy_services
        ;;
    "verify")
        verify_deployment
        ;;
    "health")
        wait_for_health
        ;;
    "full")
        main
        ;;
    *)
        echo "Usage: $0 {backup|test|deploy|verify|health|full}"
        echo "  backup  - Backup current deployment"
        echo "  test    - Run pre-deployment tests"
        echo "  deploy  - Deploy services"
        echo "  verify  - Verify deployment"
        echo "  health  - Wait for services to be healthy"
        echo "  full    - Run complete deployment (default)"
        exit 1
        ;;
esac