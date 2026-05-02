"""
Document CRUD endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document, User
from app.models.schemas import Document as DocumentSchema, DocumentCreate, DocumentUpdate
from datetime import datetime
import uuid

router = APIRouter()

@router.get("")
async def list_documents(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List user's documents"""
    try:
        documents = db.query(Document).filter(
            Document.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return {
            "total": len(documents),
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "version": d.version,
                    "created_at": d.created_at,
                    "updated_at": d.updated_at
                }
                for d in documents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_document(
    user_id: int = Query(...),
    doc: DocumentCreate = None,
    db: Session = Depends(get_db)
):
    """Create new document"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_doc = Document(
            user_id=user_id,
            title=doc.title,
            content=doc.content,
            markdown_source=doc.markdown_source,
            version=1
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        return {
            "id": db_doc.id,
            "title": db_doc.title,
            "version": db_doc.version,
            "created_at": db_doc.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doc_id}")
async def get_document(
    user_id: int = Query(...),
    doc_id: int = None,
    db: Session = Depends(get_db)
):
    """Get document by ID"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "markdown_source": document.markdown_source,
            "version": document.version,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{doc_id}")
async def update_document(
    user_id: int = Query(...),
    doc_id: int = None,
    doc_update: DocumentUpdate = None,
    db: Session = Depends(get_db)
):
    """Update document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc_update.title:
            document.title = doc_update.title
        if doc_update.content:
            document.content = doc_update.content
            document.version += 1
        if doc_update.markdown_source:
            document.markdown_source = doc_update.markdown_source
        
        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
        
        return {
            "id": document.id,
            "title": document.title,
            "version": document.version,
            "updated_at": document.updated_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
async def delete_document(
    user_id: int = Query(...),
    doc_id: int = None,
    db: Session = Depends(get_db)
):
    """Delete document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
