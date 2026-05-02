# Loomin-Docs: Air-Gapped Collaborative Editor with Local RAG-AI

A complete, self-contained collaborative text editing system with an integrated AI assistant powered by local LLMs via Ollama, designed for deployment on an air-gapped RHEL 9 system.

## Project Overview

**Loomin-Docs** delivers:
- **Google Docs-style collaborative editor** with private user folders
- **Local RAG pipeline** using FAISS + local embeddings for context-aware AI assistance
- **Ollama integration** for offline LLM inference
- **Zero internet connectivity** bootstrap package for RHEL 9 deployment
- **Security-first design** with PII sanitization, access logging, and file isolation

### Key Features

#### Frontend (React)
- 🎨 Google Docs UI with file grid and private folders
- ✏️ Rich text editor with Markdown support
- 🤖 AI side-panel for contextual editing, summarization, and improvements
- 📊 Token visualization (real-time context window usage)
- 🔄 Model selector to toggle between Ollama models
- 📁 Asset management for PDF/MD/TXT uploads

#### Backend (Python)
- 🔍 FAISS-based RAG with local embeddings (all-MiniLM-L6-v2)
- 💾 SQLite persistence for documents, chat history, user folders
- 🔐 User folder isolation and permission handling
- 📋 Citation tracking with clickable references
- 🚨 PII sanitization middleware
- ⏱️ Latency tracking and metadata in every response

#### Deployment (Docker)
- 🐳 Docker Compose orchestration
- 🔧 One-click RHEL 9 setup with `setup.sh`
- 📦 Pre-configured bootstrap package with offline Docker images
- ⚙️ Model weights sideloading strategy

## Project Structure

```
loomin-docs/
├── frontend/                    # React TypeScript application
│   ├── public/
│   ├── src/
│   │   ├── components/          # UI components
│   │   ├── pages/               # Page layouts
│   │   ├── services/            # API clients
│   │   ├── hooks/               # React hooks
│   │   ├── types/               # TypeScript types
│   │   ├── utils/               # Utilities
│   │   └── App.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── backend/                     # Python FastAPI application
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   ├── services/            # Business logic (RAG, LLM, etc.)
│   │   ├── models/              # Pydantic models
│   │   ├── db/                  # Database and ORM
│   │   ├── utils/               # Utilities (PII, logging, etc.)
│   │   ├── middleware/          # FastAPI middleware
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── deploy/                      # Deployment and bootstrap
│   ├── docker-compose.yml       # Docker Compose orchestration
│   ├── setup.sh                 # RHEL 9 installation script
│   ├── Modelfile                # Custom Ollama Modelfile
│   ├── rhel9-rpms/              # Docker RPMs for offline install
│   └── bootstrap/               # Bootstrap package contents
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   ├── DEPLOYMENT.md            # Deployment instructions
│   ├── API.md                   # Backend API documentation
│   ├── RAG_PIPELINE.md          # RAG implementation details
│   └── VERIFICATION.md          # Testing & verification
└── README.md                    # This file
```

## Quick Start

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (RHEL 9)
- Node.js 18+ (for development only)
- Python 3.11+ (for development only)

### Development Setup (Local)

1. **Clone and setup**:
```bash
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
```

2. **Run services**:
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Ollama
ollama serve
```

3. **Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Deployment (Air-Gapped RHEL 9)

1. **Prepare bootstrap package**:
```bash
cd deploy && bash prepare-bootstrap.sh
```

2. **Transfer to RHEL 9 VM** (air-gapped):
```bash
# Copy bootstrap package to target VM via physical media or other secure means
tar -xzf loomin-docs-bootstrap.tar.gz
cd loomin-docs-bootstrap
```

3. **Run setup script**:
```bash
sudo bash setup.sh
docker-compose up -d
```

4. **Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Architecture Overview

```
User Browser
    ↓
React Frontend (Port 3000)
    ↓
FastAPI Backend (Port 8000)
    ├─→ FAISS Vector Store (Local)
    ├─→ SQLite Database (Local)
    ├─→ File Upload Handler (/mnt/uploads/)
    └─→ Ollama LLM Engine (Port 11434)
         ↓
    Local Model Inference
```

For detailed architecture, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## API Overview

### Document Endpoints
- `GET /api/documents` - List user documents
- `POST /api/documents` - Create new document
- `GET /api/documents/{id}` - Get document content
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

### RAG & AI Endpoints
- `POST /api/ai/summarize` - Summarize document with RAG
- `POST /api/ai/improve` - Improve selected text
- `POST /api/ai/chat` - Chat with AI assistant
- `GET /api/ai/models` - List available Ollama models
- `POST /api/rag/retrieve` - Retrieve relevant chunks

### File Management
- `POST /api/files/upload` - Upload PDF/MD/TXT for RAG
- `GET /api/files` - List uploaded files
- `DELETE /api/files/{id}` - Delete uploaded file

### Monitoring
- `GET /api/health` - System health
- `GET /api/metrics` - Performance metrics

For full API documentation, see [API.md](docs/API.md).

## Key Technologies

### Frontend
- **React 18** + TypeScript
- **Tailwind CSS** - Styling
- **Monaco Editor** or **Slate.js** - Rich text editing
- **TanStack Query** - Data fetching
- **Socket.io** - Real-time updates (optional)

### Backend
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM
- **FAISS** - Vector similarity search
- **Sentence-Transformers** - Local embeddings
- **Ollama SDK** - LLM interface
- **Uvicorn** - ASGI server

### DevOps
- **Docker & Docker Compose** - Containerization
- **SQLite** - Local database
- **Redis** (optional) - Caching layer

## Security & Privacy Features

1. **User Folder Isolation**
   - Each user has isolated `/mnt/uploads/user/{user_id}` directory
   - File permissions prevent cross-user access

2. **PII Sanitization**
   - Pattern-based detection (SSN, API keys, credit cards, etc.)
   - Automatic masking before LLM queries
   - Configurable patterns via environment

3. **Access Logging**
   - All file access logged locally
   - All AI requests tracked with request IDs
   - Audit trail in SQLite database

4. **No External Network**
   - 100% offline operation
   - All models, embeddings, and data local
   - No telemetry or external calls

## Testing & Verification

Run the RAG faithfulness verification:
```bash
python scripts/verify-rag-faithfulness.py
```

Run integration tests:
```bash
pytest backend/tests/
```

See [VERIFICATION.md](docs/VERIFICATION.md) for detailed testing procedures.

## Performance Characteristics

- **Token Visualization**: Real-time context window usage %
- **Latency Tracking**: Each response includes retrieval and generation times
- **Throughput**: Single instance handles ~10-20 concurrent users
- **Model Size**: Ollama defaults to Llama2 7B (~4GB) but supports flexible sizing

## Troubleshooting

### Backend Connection Refused
```bash
# Ensure Ollama is running
ollama serve
```

### FAISS Index Empty
```bash
# Re-index documents
curl -X POST http://localhost:8000/api/rag/rebuild-index
```

### Out of Memory
- Reduce model size: Use Mistral 7B instead of Llama2 13B
- Reduce chunk size: Adjust CHUNK_SIZE in backend config
- Enable pagination: Limit retrieved chunks per query

## Contributing

1. Create feature branches
2. Follow TypeScript/Python style guides
3. Add tests for new features
4. Update documentation

## License

MIT License - See LICENSE file

## Support

For issues, see [ARCHITECTURE.md](docs/ARCHITECTURE.md) or create an issue in the repository.

---

**Status**: Early Development Phase  
**Last Updated**: May 2, 2026
