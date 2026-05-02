"""
RAG pipeline endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import RetrieveRequest
from app.services.rag_service import RAGService
from app.services.file_service import FileService

router = APIRouter()

rag = RAGService()
file_service = FileService()

@router.post("/retrieve")
async def retrieve(request: RetrieveRequest):
    """Retrieve relevant chunks from RAG index"""
    try:
        chunks, retrieval_time = rag.retrieve(
            query=request.query,
            top_k=request.top_k,
            distance_threshold=0.3
        )
        
        return {
            "chunks": [c["text"] for c in chunks],
            "citations": [
                {
                    "file_id": c["file_id"],
                    "chunk_id": c["chunk_index"],
                    "score": c["similarity_score"]
                }
                for c in chunks
            ],
            "retrieval_time_ms": retrieval_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index-stats")
async def index_stats():
    """Get RAG index statistics"""
    try:
        stats = rag.get_index_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the FAISS index (maintenance operation)"""
    try:
        success = rag.rebuild_index()
        if success:
            return {"message": "Index rebuilt successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to rebuild index")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
