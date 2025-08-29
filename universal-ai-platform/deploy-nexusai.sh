#!/bin/bash

# NexusAI - Deployment Script
# Supports both local and Docker Hub deployment

set -e

echo "🚀 NexusAI - AI Agent Platform Deployment"
echo "========================================"

# Configuration
IMAGE_NAME="nexusai"
DOCKER_USERNAME="bitsinfo"
VERSION=${1:-"latest"}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Check if .env file exists
check_env_file() {
    if [[ ! -f ".env" ]]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_info "Please edit .env file with your API keys before proceeding"
            read -p "Press Enter when you've configured .env file..."
        else
            print_error ".env.example not found. Please create .env file manually"
            exit 1
        fi
    fi
    print_status ".env file found"
}

# Build Docker image
build_image() {
    print_info "Building NexusAI Docker image..."
    docker build -t ${IMAGE_NAME}:${VERSION} .
    print_status "NexusAI Docker image built successfully"
}

# Tag for Docker Hub
tag_for_hub() {
    print_info "Tagging NexusAI image for Docker Hub..."
    docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
    docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
    print_status "NexusAI images tagged for Docker Hub"
}

# Push to Docker Hub
push_to_hub() {
    print_info "Pushing NexusAI to Docker Hub..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
    print_status "NexusAI images pushed to Docker Hub successfully"
    print_info "🐳 Available at: docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
}

# Deploy locally
deploy_local() {
    print_info "Starting NexusAI local deployment with docker-compose..."
    docker-compose up -d
    print_status "NexusAI local deployment started"
    
    # Wait for services to be ready
    print_info "Waiting for NexusAI services to be ready..."
    sleep 15
    
    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "✅ NexusAI is running!"
        echo ""
        print_info "🌐 NexusAI API Gateway: http://localhost:8000"
        print_info "📋 Health Check: http://localhost:8000/health"
        print_info "🔍 Check logs: docker-compose logs -f"
        print_info "🛑 Stop: docker-compose down"
        echo ""
        print_info "🧪 Test the demos:"
        print_info "   • Language Learning: python demos/language_learning/app.py"
        print_info "   • Emergency Services: python demos/emergency_services/app.py"
    else
        print_warning "NexusAI may still be starting up. Check logs with: docker-compose logs"
    fi
}

# Stop local deployment
stop_local() {
    print_info "Stopping NexusAI local deployment..."
    docker-compose down
    print_status "NexusAI local deployment stopped"
}

# Show deployment options
show_options() {
    echo ""
    echo "🎯 NexusAI Deployment Options:"
    echo "1) Build and deploy locally"
    echo "2) Build, push to Docker Hub, and deploy locally"
    echo "3) Build and push to Docker Hub only"
    echo "4) Deploy existing image locally"
    echo "5) Stop local deployment"
    echo "6) Exit"
    echo ""
}

# Main menu
main() {
    check_env_file
    
    show_options
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            print_info "🏠 Local deployment selected"
            build_image
            deploy_local
            ;;
        2)
            print_info "🐳 Build, push, and deploy locally selected"
            build_image
            tag_for_hub
            push_to_hub
            deploy_local
            ;;
        3)
            print_info "☁️  Build and push to Docker Hub only"
            build_image
            tag_for_hub
            push_to_hub
            ;;
        4)
            print_info "🚀 Deploy existing image locally"
            deploy_local
            ;;
        5)
            print_info "🛑 Stop local deployment"
            stop_local
            ;;
        6)
            print_info "👋 Exiting NexusAI deployment..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            main
            ;;
    esac
}

# Run main function
main
