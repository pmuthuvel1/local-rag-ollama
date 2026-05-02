"""
File upload and asset management endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import os
from app.db.database import get_db
from app.db.models import UploadedFile
from app.services.file_service import FileService
from app.services.rag_service import RAGService
from datetime import datetime

router = APIRouter()

file_service = FileService()
rag = RAGService()

@router.post("/upload")
async def upload_file(
    user_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload file for RAG indexing"""
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        valid, message = file_service.validate_upload(file.filename, len(content))
        if not valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Save file
        file_path = file_service.save_upload(user_id, file.filename, content)
        if not file_path:
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        # Extract text
        text = file_service.extract_text_from_file(file_path)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from file")
        
        # Chunk and index
        chunks = file_service.chunk_text(text)
        chunk_dicts = [
            {
                "text": chunk,
                "file_id": user_id,  # Use user_id as file identifier for now
                "chunk_index": i,
                "metadata": {"file": file.filename}
            }
            for i, chunk in enumerate(chunks)
        ]
        
        if not rag.add_chunks(chunk_dicts):
            raise HTTPException(status_code=500, detail="Failed to index file")
        
        # Save to database
        db_file = UploadedFile(
            user_id=user_id,
            original_filename=file.filename,
            file_type=Path(file.filename).suffix.lstrip(".").lower(),
            file_path=file_path,
            file_size=len(content),
            indexed_at=datetime.utcnow()
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return {
            "id": db_file.id,
            "filename": db_file.original_filename,
            "file_type": db_file.file_type,
            "file_size": db_file.file_size,
            "chunks_indexed": len(chunks),
            "upload_date": db_file.upload_date
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def list_files(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """List uploaded files for user"""
    try:
        files = db.query(UploadedFile).filter(
            UploadedFile.user_id == user_id
        ).all()
        
        return {
            "files": [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "file_type": f.file_type,
                    "file_size": f.file_size,
                    "upload_date": f.upload_date,
                    "indexed_at": f.indexed_at
                }
                for f in files
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(
    user_id: int = Query(...),
    file_id: int = None,
    db: Session = Depends(get_db)
):
    """Delete uploaded file"""
    try:
        db_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user_id
        ).first()
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete physical file
        if os.path.exists(db_file.file_path):
            os.remove(db_file.file_path)
        
        # Delete from database
        db.delete(db_file)
        db.commit()
        
        return {"message": "File deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
