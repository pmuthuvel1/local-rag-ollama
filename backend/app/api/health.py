"""
Health check and monitoring endpoints
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from app.services.ollama_service import OllamaService
from app.services.rag_service import RAGService

router = APIRouter()

ollama = OllamaService()
rag = RAGService()

@router.get("")
async def health_check():
    """
    Health check endpoint
    """
    ollama_health = ollama.check_health()
    rag_stats = rag.get_index_stats()
    
    # Determine overall status
    status = "healthy"
    if not ollama_health:
        status = "degraded"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ollama": {
                "status": "running" if ollama_health else "offline",
                "models": len(ollama.list_models()) if ollama_health else 0,
                "default_model": ollama.default_model
            },
            "rag": {
                "status": "ready" if rag_stats["status"] == "ready" else "not_ready",
                "total_vectors": rag_stats.get("total_vectors", 0),
                "total_chunks": rag_stats.get("total_chunks", 0),
                "embedding_dimension": rag_stats.get("embedding_dimension", 0)
            }
        }
    }

@router.get("/metrics")
async def metrics():
    """
    Get performance metrics
    """
    rag_stats = rag.get_index_stats()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "rag": rag_stats,
        "available_models": [m["name"] for m in ollama.list_models()]
    }
