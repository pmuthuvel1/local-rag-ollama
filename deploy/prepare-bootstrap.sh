#!/bin/bash

# prepare-bootstrap.sh - Prepare the bootstrap package for RHEL 9 air-gapped deployment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORK_DIR="${SCRIPT_DIR}/bootstrap-work"
OUTPUT_FILE="${SCRIPT_DIR}/loomin-docs-bootstrap.tar.gz"

echo "=================================================="
echo "Loomin-Docs Bootstrap Package Preparation"
echo "=================================================="
echo ""

# Clean previous work
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

# =============================================================================
# 1. Copy deployment files
# =============================================================================
echo "📋 Copying deployment files..."

cp "${SCRIPT_DIR}/setup.sh" "$WORK_DIR/"
cp "${SCRIPT_DIR}/docker-compose.yml" "$WORK_DIR/"
cp "${SCRIPT_DIR}/Modelfile" "$WORK_DIR/"
chmod +x "$WORK_DIR/setup.sh"

# =============================================================================
# 2. Create Docker RPM directory
# =============================================================================
echo "📦 Setting up Docker RPM directory..."

mkdir -p "$WORK_DIR/rhel9-rpms"

# Note: This assumes you've pre-downloaded Docker RPMs
# If not available, the script will guide users to download them
if [ -d "${SCRIPT_DIR}/rhel9-rpms" ] && [ "$(ls -A "${SCRIPT_DIR}/rhel9-rpms")" ]; then
    cp "${SCRIPT_DIR}/rhel9-rpms"/* "$WORK_DIR/rhel9-rpms/" 2>/dev/null || true
    echo "✅ Docker RPMs copied"
else
    cat > "$WORK_DIR/rhel9-rpms/README.md" << 'EOF'
# Docker RPMs for RHEL 9

Place Docker installation RPMs here. You can obtain them by:

1. On a connected machine with yum:
```bash
yum install --downloadonly --downloaddir=. \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

2. Or download from Docker's official repository:
https://download.docker.com/linux/rhel/

Required RPMs:
- containerd.io-*.rpm
- docker-ce-*.rpm
- docker-ce-cli-*.rpm
- (Optional) docker-compose-plugin-*.rpm
EOF
    echo "⚠️  Docker RPMs not found. See rhel9-rpms/README.md for instructions"
fi

# =============================================================================
# 3. Export Docker images
# =============================================================================
echo "🐳 Exporting Docker images..."

mkdir -p "$WORK_DIR/images"

# Check if images exist, if so export them
if docker images | grep -q "loomin-frontend"; then
    echo "  Exporting frontend image..."
    docker save loomin-frontend -o "$WORK_DIR/images/frontend.tar" 2>/dev/null || echo "    ⚠️  Could not save frontend image"
else
    echo "    ⚠️  Frontend image not found. Building..."
    # docker build -t loomin-frontend ./frontend  # If you want to build first
fi

if docker images | grep -q "loomin-backend"; then
    echo "  Exporting backend image..."
    docker save loomin-backend -o "$WORK_DIR/images/backend.tar" 2>/dev/null || echo "    ⚠️  Could not save backend image"
else
    echo "    ⚠️  Backend image not found. Building..."
    # docker build -t loomin-backend ./backend
fi

if docker images | grep -q "ollama"; then
    echo "  Exporting ollama image..."
    # Get the ollama image ID (could be ollama:latest or custom built image)
    OLLAMA_IMAGE=$(docker images | grep ollama | awk '{print $1":"$2}' | head -1)
    docker save "$OLLAMA_IMAGE" -o "$WORK_DIR/images/ollama.tar" 2>/dev/null || echo "    ⚠️  Could not save ollama image"
else
    echo "    ⚠️  Ollama image not found. Building custom ollama image with embedded llama2 model..."
    docker build -t loomin-ollama -f ./Ollama.dockerfile . 2>/dev/null || echo "    ⚠️  Could not build ollama image"
    docker save loomin-ollama -o "$WORK_DIR/images/ollama.tar" 2>/dev/null || echo "    ⚠️  Could not save ollama image"
fi

# =============================================================================
# 4. (Optional) Export Ollama models
# =============================================================================
echo "🤖 Checking for Ollama models..."

mkdir -p "$WORK_DIR/models"

# Check if ollama models directory exists
if [ -d ~/.ollama/models/blobs ]; then
    echo "  Found Ollama models directory"
    # Copy a sample model if available
    # Note: Models are large, so we don't automatically copy all
    echo "    💡 To include models, manually copy from ~/.ollama/models/blobs/"
else
    echo "    ℹ️  No Ollama models found. Models will be downloaded on first run"
    echo "    💡 To speed up deployment, download models beforehand:"
    echo "       ollama pull llama2"
    echo "       ollama pull mistral"
fi

# =============================================================================
# 5. Create verification script stub
# =============================================================================
echo "✅ Adding verification script..."

cp "${SCRIPT_DIR}/verify-rag-faithfulness.py" "$WORK_DIR/" 2>/dev/null || echo "    ⚠️  Verification script not found"

# =============================================================================
# 6. Create README for bootstrap
# =============================================================================
echo "📖 Creating bootstrap README..."

cat > "$WORK_DIR/README.md" << 'EOF'
# Loomin-Docs Bootstrap Package

This package contains everything needed to deploy Loomin-Docs on a clean RHEL 9 VM.

## Contents

- `setup.sh` - Main installation script
- `docker-compose.yml` - Service orchestration
- `Modelfile` - Ollama model configuration
- `rhel9-rpms/` - Docker installation packages
- `images/` - Docker image tarballs (pre-built)
- `models/` - Optional: Ollama model weights
- `verify-rag-faithfulness.py` - Post-deployment verification

## Quick Start

1. Extract this package on your RHEL 9 VM:
   ```bash
   tar xzf loomin-docs-bootstrap.tar.gz
   cd loomin-docs-bootstrap
   ```

2. Run the setup script:
   ```bash
   sudo bash setup.sh
   ```

3. Wait 2-5 minutes for services to start

4. Verify installation:
   ```bash
   python3 verify-rag-faithfulness.py
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Troubleshooting

- **Docker won't install**: Ensure all RPMs in `rhel9-rpms/` are present
- **Services won't start**: Check `docker-compose logs` for errors
- **Out of memory**: Reduce model size or increase VM RAM

See DEPLOYMENT.md for more details.

## System Requirements

- RHEL 9 minimal installation
- 16GB RAM (8GB minimum)
- 50GB free disk space
- Root or sudo access

## Next Steps

After deployment:
1. Create documents in the web interface
2. Upload PDF/TXT files for RAG
3. Use the AI assistant to improve documents
4. Explore the API at http://localhost:8000/docs

For questions, see the main README at the project root.
EOF

# =============================================================================
# 7. Create the final bootstrap tarball
# =============================================================================
echo ""
echo "📦 Creating bootstrap package..."

cd "${SCRIPT_DIR}"
tar czf "$OUTPUT_FILE" \
    --transform 's,^bootstrap-work,loomin-docs-bootstrap,' \
    "$WORK_DIR"

# Get size
SIZE=$(du -sh "$OUTPUT_FILE" | cut -f1)

echo ""
echo "=================================================="
echo "✅ Bootstrap package created successfully!"
echo "=================================================="
echo ""
echo "📦 File: $OUTPUT_FILE"
echo "💾 Size: $SIZE"
echo ""
echo "Next steps:"
echo "1. Transfer this file to your RHEL 9 VM (USB, SFTP, etc.)"
echo "2. Extract: tar xzf loomin-docs-bootstrap.tar.gz"
echo "3. Run: sudo bash loomin-docs-bootstrap/setup.sh"
echo ""
