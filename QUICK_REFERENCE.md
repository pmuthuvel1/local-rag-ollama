# Quick Reference Guide

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Ollama | http://localhost:11434 | LLM inference engine |

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/documents | Create document |
| GET | /api/documents | List documents |
| POST | /api/ai/chat | Chat with AI |
| POST | /api/ai/summarize | Summarize text |
| POST | /api/ai/improve | Improve text |
| POST | /api/files/upload | Upload file for RAG |
| GET | /api/health | Check system status |

## Common Commands

### Docker Compose
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Rebuild
docker-compose build --no-cache
```

### Database
```bash
# Connect to SQLite
sqlite3 /app/data/loomin-docs.db

# Check tables
.tables

# Query documents
SELECT * FROM documents;
```

### Ollama
```bash
# List models
ollama list

# Pull model
ollama pull llama2

# Run model directly
ollama run llama2 "Hello!"
```

## File Locations

| Path | Purpose |
|------|---------|
| `/mnt/uploads/user{id}/` | User file storage |
| `/app/data/loomin-docs.db` | SQLite database |
| `/app/data/rag_index` | FAISS vector index |
| `/root/.ollama/models/` | Ollama model cache |

## Environment Variables

Key variables in `.env`:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
EMBEDDING_MODEL=all-MiniLM-L6-v2
DATABASE_URL=sqlite:///./loomin-docs.db
UPLOAD_DIR=/mnt/uploads
```

## Troubleshooting Checklist

- ☐ Docker daemon running: `systemctl status docker`
- ☐ Services running: `docker ps`
- ☐ Health check: `curl http://localhost:8000/api/health`
- ☐ Ollama connectivity: `curl http://localhost:11434/api/tags`
- ☐ Database exists: `ls -la /app/data/loomin-docs.db`
- ☐ Upload folder writable: `ls -ld /mnt/uploads`
- ☐ Logs clean: `docker-compose logs | grep ERROR`

## Common Tasks

### View Backend Logs
```bash
docker-compose logs -f backend
```

### Restart a Service
```bash
docker-compose restart backend
```

### Access Database
```bash
docker exec -it loomin-backend sqlite3 /app/data/loomin-docs.db
```

### Check Resource Usage
```bash
docker stats
```

### Reset Everything
```bash
docker-compose down
docker system prune -a
rm -rf /mnt/uploads/*
```

## Performance Tuning

### Increase Model Size
Update `OLLAMA_MODEL` to `llama2-13b` (requires 10GB+ VRAM)

### Reduce Memory Usage
Set `num_ctx=512` in Ollama parameters

### Speed Up Responses
Use `mistral` model instead of `llama2`

## Security Quick Tips

- Change default user credentials
- Enable HTTPS for production
- Restrict API access with firewall
- Enable SELinux policies
- Regular database backups

## Support

- **Docs**: See `/docs` folder
- **API**: http://localhost:8000/docs
- **Issues**: Check GitHub issues
- **Logs**: `docker-compose logs`

---

For detailed guides, see [DEPLOYMENT.md](docs/DEPLOYMENT.md) and [ARCHITECTURE.md](docs/ARCHITECTURE.md)
