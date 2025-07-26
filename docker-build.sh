#!/bin/bash

# Docker Build Script for E-commerce Chatbot
# This script builds both backend and frontend Docker images

set -e

echo "🐳 Building E-commerce Chatbot Docker Images..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running ✅"

# Build backend image
print_status "Building backend image..."
cd backend
if docker build -t ecommerce-chatbot-backend .; then
    print_status "Backend image built successfully ✅"
else
    print_error "Failed to build backend image ❌"
    exit 1
fi
cd ..

# Build frontend image
print_status "Building frontend image..."
cd frontend
if docker build -t ecommerce-chatbot-frontend .; then
    print_status "Frontend image built successfully ✅"
else
    print_error "Failed to build frontend image ❌"
    exit 1
fi
cd ..

print_status "All images built successfully! 🎉"

# Show built images
print_status "Built images:"
docker images | grep ecommerce-chatbot

echo ""
print_status "🚀 Quick Start Commands:"
echo "  Development: docker-compose up -d"
echo "  Production:  docker-compose -f docker-compose.prod.yml up -d"
echo ""
print_status "📱 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
