"""
AI assistance endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import SummarizeRequest, ImproveRequest, ChatRequest, AIResponse
from app.services.ai_service import AIService
from app.services.ollama_service import OllamaService

router = APIRouter()

ai_service = AIService()
ollama = OllamaService()

@router.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        models = ollama.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize(
    user_id: int = Query(...),
    request: SummarizeRequest = None
):
    """Summarize text with RAG"""
    try:
        result = ai_service.summarize(
            text=request.text,
            document_id=request.document_id,
            max_length=request.max_length or 150
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Summarization failed"))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improve")
async def improve(
    user_id: int = Query(...),
    request: ImproveRequest = None
):
    """Improve selected text"""
    try:
        result = ai_service.improve(
            text=request.text,
            improvement_type=request.improvement_type or "enhance",
            document_id=request.document_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Improvement failed"))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(
    user_id: int = Query(...),
    request: ChatRequest = None
):
    """Chat with AI assistant"""
    try:
        result = ai_service.chat(
            message=request.message,
            document_id=request.document_id,
            conversation_history=request.conversation_history,
            use_rag=request.use_rag
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Chat failed"))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
