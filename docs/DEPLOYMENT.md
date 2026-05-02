# Loomin-Docs Deployment Guide

## Pre-Deployment Requirements

### For Development (Local Machine)
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Node.js 18+
- Python 3.11+
- 8GB RAM minimum
- 20GB free disk space

### For Production (RHEL 9 Air-Gapped VM)
- RHEL 9 minimal installation
- 16GB RAM minimum
- 50GB free disk space
- USB/external media for package transfer (if truly air-gapped)

## Local Development Setup

### 1. Clone and Install Dependencies

```bash
cd frontend
npm install

cd ../backend
pip install -r requirements.txt
```

### 2. Start Services

**Terminal 1: Backend**
```bash
cd backend
export DATABASE_URL=sqlite:///./loomin-docs.db
export OLLAMA_BASE_URL=http://localhost:11434
export EMBEDDING_MODEL=all-MiniLM-L6-v2

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

**Terminal 3: Ollama** (if not already running)
```bash
ollama serve
```

### 3. Pull a Model

```bash
ollama pull llama2  # or mistral for faster inference
```

### 4. Access the Application

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434

## Docker Compose Setup (Local)

```bash
docker-compose -f deploy/docker-compose.yml up -d
```

Services will be available at the same URLs above.

## Air-Gapped RHEL 9 Deployment

### Phase 1: Prepare Bootstrap Package (On Connected Machine)

```bash
cd deploy

# Create necessary directories
mkdir -p rhel9-rpms
mkdir -p images
mkdir -p models

# Download Docker RPMs for RHEL 9
# Visit: https://docs.docker.com/engine/install/rhel/
# Or use your package manager to download:
yum install --downloadonly --downloaddir=rhel9-rpms \
  docker-ce \
  docker-ce-cli \
  docker-compose-plugin \
  containerd.io

# Export Docker images
docker save loomin-frontend -o images/frontend.tar
docker save loomin-backend -o images/backend.tar
docker save ollama/ollama -o images/ollama.tar

# (Optional) Download Ollama models locally
ollama pull llama2
# Models are typically stored in ~/.ollama/models/
# Copy to models/ directory

# Create bootstrap tarball
tar czf loomin-docs-bootstrap.tar.gz \
  setup.sh \
  docker-compose.yml \
  Modelfile \
  rhel9-rpms/ \
  images/ \
  models/

echo "✅ Bootstrap package created: loomin-docs-bootstrap.tar.gz"
```

### Phase 2: Transfer to RHEL 9 VM

Transfer via:
- USB drive
- SFTP if network available
- Physical media

```bash
# On RHEL 9 VM
tar xzf loomin-docs-bootstrap.tar.gz
cd loomin-docs-bootstrap
```

### Phase 3: Run Installation Script

```bash
sudo bash setup.sh
```

This script will:
1. ✅ Install Docker from local RPMs
2. ✅ Install docker-compose
3. ✅ Create user folders at /mnt/uploads
4. ✅ Load Docker images from .tar files
5. ✅ Start services with docker-compose

### Phase 4: Verify Installation

```bash
# Check Docker is running
docker ps

# Check services
docker-compose logs -f

# Run verification tests
python3 verify-rag-faithfulness.py --api-base http://localhost:8000/api
```

Expected output:
```
✅ All tests passed! System is ready.
```

## Post-Deployment Configuration

### 1. Add Users

The system comes with a default user (ID: 1). To add more users, use the API:

```bash
curl -X POST http://localhost:8000/api/documents \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "title": "Welcome Document",
    "content": "Hello User 2!"
  }'
```

### 2. Upload Sample Files

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "user_id=1" \
  -F "file=@sample.pdf"
```

### 3. Monitor System

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama

# Check resource usage
docker stats

# Access database
sqlite3 /app/data/loomin-docs.db ".tables"
```

## Scaling Considerations

### Single Instance Limits
- ~10-20 concurrent users
- Context window: 2048-4096 tokens
- Model: Llama2 7B (~4GB VRAM)

### To Scale:
1. **Horizontal**: Run multiple backend instances with load balancer
2. **Vertical**: Upgrade to larger model (Llama2 13B with 10GB+ VRAM)
3. **Cache**: Add Redis for embedding caching

### For Production:
```yaml
# docker-compose.yml additions
services:
  redis:
    image: redis:alpine
    ports: ["6379:6379"]
  
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

## Troubleshooting

### Issue: Services won't start

```bash
# Check Docker daemon
systemctl status docker

# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Out of memory

```bash
# Reduce model size
# In .env, change OLLAMA_MODEL to "mistral" or "neural-chat"

# Or limit container memory in docker-compose.yml
services:
  backend:
    mem_limit: 4g
  ollama:
    mem_limit: 6g
```

### Issue: Slow response times

```bash
# Check FAISS index size
sqlite3 /app/data/loomin-docs.db \
  "SELECT COUNT(*) FROM rag_chunks;"

# If too many chunks, rebuild with larger chunk size
curl -X POST http://localhost:8000/api/rag/rebuild-index
```

### Issue: Files not persisting

Check volume mounts:
```bash
docker inspect loomin-backend | grep Mounts -A 10
```

Ensure `/mnt/uploads` has proper permissions:
```bash
sudo chown -R 1000:1000 /mnt/uploads
sudo chmod 755 /mnt/uploads
```

## Backup & Restore

### Backup

```bash
# Backup database
docker cp loomin-backend:/app/data/loomin-docs.db ./backup/

# Backup FAISS index
docker cp loomin-backend:/app/data/rag_index ./backup/

# Backup uploads
sudo cp -r /mnt/uploads ./backup/uploads
```

### Restore

```bash
docker cp ./backup/loomin-docs.db loomin-backend:/app/data/
docker cp ./backup/rag_index loomin-backend:/app/data/
```

## Security Hardening

### 1. Change Default User
```bash
# Add new user to database
sqlite3 /app/data/loomin-docs.db \
  "INSERT INTO users (username, email, folder_path) \
   VALUES ('admin', 'admin@local', '/mnt/uploads/user99');"
```

### 2. Enable HTTPS (with reverse proxy)

```bash
# Create nginx configuration
# See deploy/nginx.conf
```

### 3. Set Resource Limits

```yaml
# docker-compose.yml
services:
  backend:
    mem_limit: 4g
    cpus: 2
```

## Monitoring & Maintenance

### Daily Checks

```bash
# Service health
curl http://localhost:8000/api/health

# Logs
docker-compose logs --since 24h
```

### Weekly Maintenance

```bash
# Restart services
docker-compose restart

# Prune unused images/volumes
docker system prune -a --volumes
```

### Monthly Checks

```bash
# Database integrity
sqlite3 /app/data/loomin-docs.db "PRAGMA integrity_check;"

# FAISS index status
curl http://localhost:8000/api/rag/index-stats
```

## Uninstallation

```bash
docker-compose down
docker system prune -a --volumes
rm -rf /mnt/uploads /opt/loomin-docs
```

---

For support, see the main [README.md](../README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
