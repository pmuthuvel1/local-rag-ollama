# Loomin-Docs API Reference

## Base URL
- **Local Development**: `http://localhost:8000`
- **Production**: `http://<server-ip>:8000`

All endpoints return JSON responses with consistent error handling.

---

## Health & Status

### Health Check
**GET** `/api/health`

Check system health and service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-02T10:30:45Z",
  "services": {
    "ollama": {
      "status": "running",
      "models": 2,
      "default_model": "llama2"
    },
    "rag": {
      "status": "ready",
      "total_vectors": 1250,
      "total_chunks": 250
    }
  }
}
```

### Get Metrics
**GET** `/api/health/metrics`

Get system performance metrics.

**Response:**
```json
{
  "timestamp": "2026-05-02T10:30:45Z",
  "rag": {...},
  "available_models": ["llama2", "mistral"]
}
```

---

## Documents

### List Documents
**GET** `/api/documents?user_id=1&skip=0&limit=100`

List all documents for a user.

**Parameters:**
- `user_id` (required): User ID
- `skip`: Number of documents to skip (default: 0)
- `limit`: Maximum documents to return (default: 100)

**Response:**
```json
{
  "total": 3,
  "documents": [
    {
      "id": 1,
      "title": "My Document",
      "version": 2,
      "created_at": "2026-05-01T10:00:00Z",
      "updated_at": "2026-05-02T10:30:00Z"
    }
  ]
}
```

### Create Document
**POST** `/api/documents?user_id=1`

Create a new document.

**Body:**
```json
{
  "title": "New Document",
  "content": "Initial content",
  "markdown_source": "Optional markdown"
}
```

**Response:**
```json
{
  "id": 5,
  "title": "New Document",
  "version": 1,
  "created_at": "2026-05-02T10:30:45Z"
}
```

### Get Document
**GET** `/api/documents/{doc_id}?user_id=1`

Get full document content.

**Response:**
```json
{
  "id": 1,
  "title": "My Document",
  "content": "Full content here...",
  "markdown_source": "...",
  "version": 2,
  "created_at": "2026-05-01T10:00:00Z",
  "updated_at": "2026-05-02T10:30:00Z"
}
```

### Update Document
**PUT** `/api/documents/{doc_id}?user_id=1`

Update document content or title.

**Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "markdown_source": "Updated markdown"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Updated Title",
  "version": 3,
  "updated_at": "2026-05-02T10:35:00Z"
}
```

### Delete Document
**DELETE** `/api/documents/{doc_id}?user_id=1`

Delete a document.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

## AI Assistance

### List Models
**GET** `/api/ai/models`

List available Ollama models.

**Response:**
```json
{
  "models": [
    {
      "name": "llama2",
      "size_gb": 3.8
    },
    {
      "name": "mistral",
      "size_gb": 3.8
    }
  ]
}
```

### Summarize Text
**POST** `/api/ai/summarize?user_id=1`

Summarize selected text with RAG context.

**Body:**
```json
{
  "text": "Long text to summarize...",
  "document_id": 1,
  "max_length": 150
}
```

**Response:**
```json
{
  "response": "Concise summary here...",
  "citations": [
    {
      "file_id": 5,
      "chunk_id": 10,
      "text": "Relevant passage...",
      "score": 0.87
    }
  ],
  "request_id": "uuid-uuid-uuid",
  "tokens": {
    "input_tokens": 256,
    "output_tokens": 45,
    "total_tokens": 301,
    "context_window_size": 4096,
    "usage_percent": 7.35
  },
  "latency": {
    "retrieval_time_ms": 145.2,
    "generation_time_ms": 1234.5,
    "total_time_ms": 1379.7
  },
  "model_used": "llama2"
}
```

### Improve Text
**POST** `/api/ai/improve?user_id=1`

Improve selected text (enhance, simplify, or expand).

**Body:**
```json
{
  "text": "Text to improve...",
  "improvement_type": "enhance",
  "document_id": 1
}
```

**Response:** Same as Summarize

### Chat with AI
**POST** `/api/ai/chat?user_id=1`

Have a conversation with the AI assistant.

**Body:**
```json
{
  "message": "What is the main topic?",
  "document_id": 1,
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant",
      "content": "Previous response"
    }
  ],
  "use_rag": true
}
```

**Response:** Same as Summarize

---

## RAG Pipeline

### Retrieve Chunks
**POST** `/api/rag/retrieve`

Retrieve relevant document chunks for a query.

**Body:**
```json
{
  "query": "What is the main topic?",
  "top_k": 5,
  "max_context_tokens": 2000
}
```

**Response:**
```json
{
  "chunks": [
    "First relevant chunk...",
    "Second relevant chunk..."
  ],
  "citations": [
    {
      "file_id": 5,
      "chunk_id": 0,
      "score": 0.92
    }
  ],
  "retrieval_time_ms": 145.2
}
```

### Get Index Statistics
**GET** `/api/rag/index-stats`

Get current RAG index status.

**Response:**
```json
{
  "status": "ready",
  "total_vectors": 1250,
  "total_chunks": 250,
  "index_type": "IndexIVFFlat",
  "embedding_dimension": 384
}
```

### Rebuild Index
**POST** `/api/rag/rebuild-index`

Rebuild the FAISS index (maintenance operation).

**Response:**
```json
{
  "message": "Index rebuilt successfully"
}
```

---

## File Management

### Upload File
**POST** `/api/files/upload?user_id=1`

Upload a PDF, TXT, or MD file for RAG indexing.

**Request:**
```
Content-Type: multipart/form-data

Form data:
- file: <binary file content>
```

**Response:**
```json
{
  "id": 15,
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 245000,
  "chunks_indexed": 50,
  "upload_date": "2026-05-02T10:30:45Z"
}
```

### List Files
**GET** `/api/files?user_id=1`

List all uploaded files for user.

**Response:**
```json
{
  "files": [
    {
      "id": 15,
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 245000,
      "upload_date": "2026-05-02T10:30:45Z",
      "indexed_at": "2026-05-02T10:31:00Z"
    }
  ]
}
```

### Delete File
**DELETE** `/api/files/{file_id}?user_id=1`

Delete an uploaded file.

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error description",
  "status": 400,
  "request_id": "uuid-uuid-uuid"
}
```

### Common Status Codes
- `200 OK` - Successful request
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - RAG not ready or Ollama offline

---

## Rate Limiting

Current implementation has no rate limiting. For production, consider adding:
- Per-user request limits
- Token usage quotas
- Concurrent request limits

---

## Authentication

Current implementation uses simple `user_id` parameter. For production, upgrade to:
- JWT tokens
- OAuth 2.0
- API keys

---

## WebSocket Support (Future)

For real-time collaboration:
- `WS /api/documents/{doc_id}/subscribe`
- `WS /api/ai/chat/stream`

---

## Examples

### cURL Examples

**Create a document:**
```bash
curl -X POST http://localhost:8000/api/documents \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "title": "My Document",
    "content": "Hello World"
  }'
```

**Get health status:**
```bash
curl http://localhost:8000/api/health
```

**Upload a file:**
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "user_id=1" \
  -F "file=@myfile.pdf"
```

### Python Examples

```python
import requests

# Initialize client
api = "http://localhost:8000/api"

# Create document
response = requests.post(
    f"{api}/documents",
    params={"user_id": 1},
    json={"title": "Test", "content": "Content"}
)
doc = response.json()

# Summarize text
response = requests.post(
    f"{api}/ai/summarize",
    params={"user_id": 1},
    json={
        "text": "Long text here...",
        "document_id": doc["id"]
    }
)
summary = response.json()
print(f"Summary: {summary['response']}")
print(f"Tokens used: {summary['tokens']['usage_percent']:.1f}%")
```

### JavaScript/TypeScript Examples

```typescript
// See frontend/src/services/api.ts for full implementation

const api = "http://localhost:8000/api";

// Summarize
const response = await fetch(`${api}/ai/summarize?user_id=1`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "Long text...",
    max_length: 150
  })
});

const data = await response.json();
console.log(`Token usage: ${data.tokens.usage_percent}%`);
```

---

For more examples and integration guides, see [ARCHITECTURE.md](ARCHITECTURE.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
