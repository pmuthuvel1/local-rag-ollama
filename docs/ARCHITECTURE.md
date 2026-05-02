# Architecture Overview: Loomin-Docs

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Browser                          │
│                    (Chrome/Firefox/Safari)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │   React Frontend (Port 3000)          │
         │   ├─ Google Docs UI                   │
         │   ├─ Rich Text Editor                 │
         │   ├─ AI Chat Side-Panel               │
         │   ├─ File Grid & Asset Manager        │
         │   └─ Token Visualization              │
         └────────┬────────────────────────────┬─┘
                  │                            │
                  │ HTTP + WebSocket           │ File Upload
                  │                            │
                  ▼                            ▼
    ┌──────────────────────────────────────────────────┐
    │     FastAPI Backend (Port 8000)                  │
    ├──────────────────────────────────────────────────┤
    │ API Layer:                                       │
    │  ├─ /api/documents/*       (CRUD)               │
    │  ├─ /api/ai/*              (Chat, Summarize)    │
    │  ├─ /api/rag/*             (Retrieval)          │
    │  └─ /api/files/*           (Asset Management)   │
    ├──────────────────────────────────────────────────┤
    │ Middleware:                                      │
    │  ├─ Authentication/Authorization                │
    │  ├─ PII Sanitization                            │
    │  ├─ Request Logging & Tracing                   │
    │  └─ CORS Handling                               │
    ├──────────────────────────────────────────────────┤
    │ Business Logic Layer:                            │
    │  ├─ Document Service                            │
    │  ├─ RAG Service (FAISS, Embeddings)             │
    │  ├─ LLM Service (Ollama Integration)            │
    │  ├─ File Service (Upload, Validation)           │
    │  └─ Chat Service (History, Context)             │
    └────┬───────────────┬────────────┬────────────┬──┘
         │               │            │            │
         │               │            │            │
    ┌────▼──┐      ┌─────▼──┐   ┌────▼───┐   ┌───▼────┐
    │SQLite │      │ FAISS  │   │Sentence│   │Ollama  │
    │ DB    │      │Vector  │   │ Trans- │   │Local   │
    │       │      │Store   │   │former  │   │Models  │
    │Users  │      │        │   │        │   │        │
    │Docs   │      │Chunks  │   │ Embed-│   │Llama 2/│
    │Chat   │      │&Scores │   │dings  │   │Mistral │
    │Logs   │      │        │   │       │   │        │
    └───────┘      └────────┘   └───────┘   └───────┘
         │               │            │            │
         └───────────────┼────────────┼────────────┘
                         │            │
                    ┌────▼────────────▼────┐
                    │ /mnt/uploads/        │
                    │ - PDF/MD/TXT files   │
                    │ - User Folders       │
                    │ - Output Artifacts   │
                    └──────────────────────┘
```

## Data Flow: Document Summarization with RAG

```
User selects text → "Summarize" button
                          ↓
              Frontend API POST /api/ai/summarize
                    {text: "...", doc_id: "..."}
                          ↓
              Backend: PII Sanitization Middleware
                    (Mask sensitive patterns)
                          ↓
                 RAG Service: retrieve()
                    ├─ Tokenize selected text
                    ├─ Generate embeddings
                    ├─ Query FAISS index
                    ├─ Retrieve top K chunks
                    └─ Return with citations
                          ↓
                LLM Service: generate()
              ├─ Build prompt with context
              ├─ Count tokens (input + retrieval)
              ├─ Call Ollama API
              ├─ Stream response
              └─ Track generation time
                          ↓
              Response JSON:
              {
                "summary": "...",
                "citations": [
                  {
                    "file": "doc.pdf",
                    "chunk_id": "0",
                    "text": "...",
                    "score": 0.87
                  }
                ],
                "metadata": {
                  "request_id": "uuid",
                  "retrieval_time_ms": 145,
                  "generation_time_ms": 1234,
                  "tokens_used": {
                    "input": 256,
                    "output": 128,
                    "total": 384,
                    "context_window": 4096,
                    "usage_percent": 9.4
                  }
                }
              }
                          ↓
            Frontend receives and auto-fills
            editor with summary + citations
```

## File Organization & User Isolation

```
/mnt/uploads/
├── user1/
│   ├── documents/
│   │   ├── doc1.md (1.0)
│   │   ├── doc1.md (2.0)
│   │   └── doc1.md (3.0)
│   ├── assets/
│   │   ├── research.pdf
│   │   ├── notes.txt
│   │   └── reference.md
│   └── .permissions (user1 read/write only)
├── user2/
│   ├── documents/
│   ├── assets/
│   └── .permissions (user2 read/write only)
└── shared/
    └── models/ (read-only model cache)
```

## Database Schema (SQLite)

### Tables

#### users
```sql
id (PK)
username (UNIQUE)
email
created_at
updated_at
folder_path
```

#### documents
```sql
id (PK)
user_id (FK)
title
content (LONGTEXT)
markdown_source
version
created_at
updated_at
last_modified_by
```

#### document_versions
```sql
id (PK)
document_id (FK)
version_number
content
created_by
created_at
```

#### chat_history
```sql
id (PK)
user_id (FK)
document_id (FK, nullable)
role (user|assistant)
content
metadata (JSON: {
  request_id: uuid,
  retrieval_time: ms,
  generation_time: ms,
  tokens_used: {...},
  citations: [...]
})
created_at
```

#### uploaded_files
```sql
id (PK)
user_id (FK)
original_filename
file_type (pdf|md|txt)
file_path
file_size
upload_date
indexed_at (nullable)
```

#### rag_chunks
```sql
id (PK)
file_id (FK)
chunk_index
content
embedding_vector (BLOB, serialized numpy)
metadata (JSON: {file, page, section})
created_at
```

#### access_logs
```sql
id (PK)
user_id (FK)
action (read|write|upload|delete|ai_request)
resource_type (document|file|chat)
resource_id
request_id
success (bool)
timestamp
details (JSON)
```

## RAG Pipeline (FAISS + Embeddings)

### 1. Indexing Phase (On File Upload)

```
PDF/MD/TXT File
    ↓
1. Text Extraction
   └─ PyPDF2, python-magic for format detection
    ↓
2. Chunking
   ├─ Chunk size: 512 tokens (~384 chars)
   ├─ Overlap: 50 tokens
   └─ Store metadata (file, page, section)
    ↓
3. Embedding
   ├─ Model: all-MiniLM-L6-v2 (384-dim)
   ├─ Batch size: 32
   └─ Output: Dense vectors
    ↓
4. FAISS Index Update
   ├─ Index type: IVF (Inverted File)
   ├─ Quantization: PQ (Product Quantization)
   └─ Persistence: Save to disk
    ↓
5. Database Insert
   └─ Store chunk + embedding + metadata
```

### 2. Retrieval Phase (On AI Query)

```
User Query / Selected Text
    ↓
1. Query Embedding
   └─ all-MiniLM-L6-v2(query_text) → 384-dim vector
    ↓
2. FAISS Search
   ├─ k=5 nearest neighbors
   └─ Max distance threshold: 0.3
    ↓
3. Chunk Retrieval
   ├─ Fetch full chunk content from DB
   ├─ Sort by similarity score
   └─ Add file/page metadata
    ↓
4. Context Assembly
   ├─ Combine top K chunks
   ├─ Max combined length: 2000 tokens
   └─ Rerank by relevance (optional)
    ↓
5. Citation Generation
   ├─ For each chunk: store file_id, chunk_id
   ├─ Make clickable in frontend
   └─ Return full chunk for citation display
```

## Ollama Integration

### Supported Models

```
Model          Size    VRAM    Speed   Quality
─────────────────────────────────────────────
Llama 2 7B     3.8GB   6GB    Fast    Good
Llama 2 13B    7GB     10GB   Medium  Better
Mistral 7B     3.8GB   6GB    Fast    Good
Neural Chat    4.1GB   6GB    Fast    Good
```

### Custom Modelfile (if needed)

```dockerfile
FROM llama2:latest

PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER stop "User:"
PARAMETER stop "Assistant:"

SYSTEM """
You are a helpful AI assistant integrated into a collaborative document editor.
- You have access to uploaded documents via RAG
- Be concise and actionable
- Always cite sources when referencing documents
- Do not hallucinate or make up information
"""
```

## Deployment Layers

### Development (Docker Compose - Local)

```yaml
version: '3.9'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  backend:
    build: ./backend
    ports: ["8000:8000"]
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
  db:
    volumes: ["/mnt/uploads:/mnt/uploads"]
```

### Production (RHEL 9 - Air-Gapped)

```
Bootstrap Package:
├── setup.sh (Main installation script)
├── docker-compose.yml
├── rhel9-rpms/ (Docker installation packages)
├── images/
│   ├── frontend.tar
│   ├── backend.tar
│   └── ollama.tar
├── models/ (Optional: Ollama GGUF files)
└── config/
    ├── .env.production
    └── nginx.conf (optional reverse proxy)
```

## Security Model

### 1. Authentication & Authorization
- Simple username/password for MVP
- JWT tokens for API calls
- User ID embedded in token

### 2. File Isolation
```
/mnt/uploads/user1/ → accessible by user1 only
/mnt/uploads/user2/ → accessible by user2 only
Enforced via:
  - Unix permissions: 700 (rwx------)
  - Backend checks user_id before access
  - SQLite role-based queries
```

### 3. PII Sanitization
```
Patterns detected:
- SSN: \d{3}-\d{2}-\d{4}
- Credit Card: \d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}
- API Keys: [a-zA-Z0-9_]{40,}
- Email: [^@]+@[^@]+\.[^@]+
- Phone: (\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}

Replacement: [REDACTED_TYPE]
```

### 4. Access Logging
```json
{
  "timestamp": "2026-05-02T10:30:45Z",
  "user_id": "user123",
  "action": "ai_request",
  "resource": "document:doc456",
  "request_id": "uuid-uuid-uuid",
  "success": true,
  "details": {
    "query_length": 150,
    "retrieval_count": 5,
    "generation_time_ms": 1234
  }
}
```

## Performance Metrics

### Latency Targets
- Document list: < 100ms
- Document open: < 200ms
- Text search: < 500ms
- RAG retrieval: 100-300ms (FAISS search + chunk fetch)
- LLM generation: 2-8s (depends on model size)
- Total AI response: 2.5-8.5s

### Throughput
- Single instance: ~10-20 concurrent users
- Horizontal scaling: Add more backend replicas

### Storage
- Vector index (FAISS): ~100MB per 50k chunks
- SQLite DB: ~10MB base + 1MB per 10k chat messages
- Documents: Depends on user content

## Error Handling & Resilience

### Backend Error Responses
```json
{
  "error": "rag_not_ready",
  "message": "FAISS index has not been built yet",
  "status": 503,
  "request_id": "uuid",
  "retry_after": 60
}
```

### Graceful Degradation
- If Ollama unavailable: Return "AI temporarily unavailable"
- If FAISS index missing: Rebuild automatically
- If file not found: Return 404 with user-friendly message

## Future Enhancements

1. **Real-time Collaboration**
   - Use WebSocket for multi-user editing
   - Operational Transformation (OT) or CRDT
   - Presence indicators

2. **Advanced RAG**
   - Hybrid search (semantic + BM25)
   - Re-ranking with cross-encoders
   - Query expansion

3. **Fine-tuning**
   - Train embeddings on domain-specific data
   - Fine-tune LLM on user documents

4. **Caching**
   - Redis for semantic cache
   - Embedding cache for repeated queries

5. **Analytics**
   - Usage dashboards
   - Performance profiling
   - Cost attribution per user

---

For deployment details, see [DEPLOYMENT.md](DEPLOYMENT.md).
