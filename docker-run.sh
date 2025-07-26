#!/bin/bash

# Simple Docker Run Script for E-commerce Chatbot
# Quick commands to build and run the application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build Docker images"
    echo "  dev       Run in development mode"
    echo "  prod      Run in production mode"
    echo "  stop      Stop all containers"
    echo "  clean     Stop and remove containers"
    echo "  logs      Show container logs"
    echo ""
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

case "${1:-}" in
    "build")
        check_docker
        print_status "🔨 Building Docker images..."
        ./docker-build.sh
        ;;
    "dev")
        check_docker
        print_status "🚀 Starting development environment..."
        docker-compose up -d
        print_status "✅ Application started!"
        echo ""
        echo "📱 Access your application:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        ;;
    "prod")
        check_docker
        print_status "🚀 Starting production environment..."
        docker-compose -f docker-compose.prod.yml up -d
        print_status "✅ Production application started!"
        echo ""
        echo "📱 Access your application:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000"
        ;;
    "stop")
        print_status "🛑 Stopping containers..."
        docker-compose down
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        print_status "✅ Containers stopped!"
        ;;
    "clean")
        print_status "🧹 Cleaning up containers and volumes..."
        docker-compose down -v
        docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
        print_status "✅ Cleanup complete!"
        ;;
    "logs")
        print_status "📋 Showing container logs..."
        docker-compose logs -f
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
