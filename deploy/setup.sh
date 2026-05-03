#!/bin/bash

# setup.sh - Bootstrap installation script for RHEL 9 (Air-Gapped)
# This script installs Docker and docker-compose from local RPMs

set -e

echo "=================================================="
echo "Loomin-Docs Bootstrap Setup for RHEL 9"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Detect RHEL version
RHEL_VERSION=$(rpm -q --queryformat '%{RELEASE}' centos-release 2>/dev/null || echo "unknown")
echo "✓ Detected RHEL/CentOS version: $RHEL_VERSION"

# =============================================================================
# 1. Install Docker from local RPMs
# =============================================================================
echo ""
echo "📦 Installing Docker Engine from local RPMs..."

RPM_DIR="./rhel9-rpms"
if [ ! -d "$RPM_DIR" ]; then
    echo "❌ RPM directory not found: $RPM_DIR"
    echo "   Make sure rhel9-rpms/ contains Docker RPMs"
    exit 1
fi

# Install containerd and runc first (dependencies)
rpm -ivh "$RPM_DIR"/containerd* 2>/dev/null || true
rpm -ivh "$RPM_DIR"/runc* 2>/dev/null || true

# Install Docker
rpm -ivh "$RPM_DIR"/docker-ce-*.rpm "$RPM_DIR"/docker-ce-cli-*.rpm 2>/dev/null || true

# Verify Docker installation
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ Docker installed: $DOCKER_VERSION"
else
    echo "❌ Docker installation failed"
    exit 1
fi

# =============================================================================
# 2. Install Docker Compose from local
# =============================================================================
echo ""
echo "📦 Installing Docker Compose..."

COMPOSE_BINARY="/usr/local/bin/docker-compose"
if [ -f "$RPM_DIR/docker-compose" ]; then
    cp "$RPM_DIR/docker-compose" "$COMPOSE_BINARY"
    chmod +x "$COMPOSE_BINARY"
    echo "✅ Docker Compose installed"
else
    echo "⚠️  Docker Compose binary not found in $RPM_DIR"
fi

# =============================================================================
# 3. Start Docker daemon
# =============================================================================
echo ""
echo "🚀 Starting Docker daemon..."

systemctl enable docker
systemctl start docker

if systemctl is-active --quiet docker; then
    echo "✅ Docker daemon is running"
else
    echo "⚠️  Failed to start Docker daemon"
fi

# =============================================================================
# 4. Create directory structure
# =============================================================================
echo ""
echo "📁 Creating directory structure..."

mkdir -p /mnt/uploads
mkdir -p /opt/loomin-docs

# Create user folders
for i in {1..10}; do
    mkdir -p "/mnt/uploads/user$i/documents"
    mkdir -p "/mnt/uploads/user$i/assets"
    chmod 700 "/mnt/uploads/user$i"
done

chmod 755 /mnt/uploads
echo "✅ Directory structure created at /mnt/uploads"

# =============================================================================
# 5. Load Docker images from tarballs
# =============================================================================
echo ""
echo "🐳 Loading Docker images..."

IMAGES_DIR="./images"
if [ -d "$IMAGES_DIR" ]; then
    for tar_file in "$IMAGES_DIR"/*.tar; do
        if [ -f "$tar_file" ]; then
            echo "  Loading: $(basename "$tar_file")"
            docker load -i "$tar_file"
        fi
    done
    echo "✅ Docker images loaded"
else
    echo "⚠️  No images directory found. Images will be built from Dockerfile"
fi

# =============================================================================
# 6. Pull or prepare Ollama model
# =============================================================================
echo ""
echo "🤖 Preparing Ollama model..."

MODELS_DIR="./models"
if [ -d "$MODELS_DIR" ] && [ "$(ls -A "$MODELS_DIR")" ]; then
    echo "  Found local models in $MODELS_DIR"
    mkdir -p /root/.ollama/models/blobs
    cp -v "$MODELS_DIR"/* /root/.ollama/models/blobs/ 2>/dev/null || true
    echo "✅ Models staged for Ollama"
else
    echo "⚠️  No models directory found"
    echo "   Ollama will download models on first run (requires internet)"
fi

# =============================================================================
# 7. Start services with docker-compose
# =============================================================================
echo ""
echo "🚀 Starting Loomin-Docs services..."

cd /opt/loomin-docs

if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check service health
    if docker ps | grep -q loomin-backend; then
        echo "✅ Backend service is running"
    else
        echo "❌ Backend service failed to start"
    fi
    
    if docker ps | grep -q loomin-frontend; then
        echo "✅ Frontend service is running"
    else
        echo "❌ Frontend service failed to start"
    fi
    
    if docker ps | grep -q loomin-ollama; then
        echo "✅ Ollama service is running"
    else
        echo "❌ Ollama service failed to start"
    fi
else
    echo "❌ docker-compose.yml not found in current directory"
    exit 1
fi

# =============================================================================
# 8. Final status
# =============================================================================
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Services should now be accessible at:"
echo "  📱 Frontend: http://localhost:3000"
echo "  🔌 Backend API: http://localhost:8000"
echo "  🤖 Ollama: http://localhost:11434"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop services: docker-compose down"
echo ""
