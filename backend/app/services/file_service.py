"""
File upload and processing service
"""

import os
import shutil
import logging
from typing import Optional, List
from pathlib import Path
import PyPDF2

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling file uploads and processing"""
    
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "/mnt/uploads")
        self.max_upload_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
        self.allowed_types = os.getenv("ALLOWED_FILE_TYPES", "pdf,txt,md").split(",")
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def get_user_folder(self, user_id: int) -> str:
        """Get or create user's isolated folder"""
        user_folder = os.path.join(self.upload_dir, f"user{user_id}")
        os.makedirs(user_folder, exist_ok=True)
        os.makedirs(os.path.join(user_folder, "documents"), exist_ok=True)
        os.makedirs(os.path.join(user_folder, "assets"), exist_ok=True)
        
        # Set permissions (700 = rwx------)
        os.chmod(user_folder, 0o700)
        
        return user_folder
    
    def validate_upload(self, filename: str, file_size: int) -> tuple[bool, str]:
        """Validate uploaded file"""
        # Check file size
        if file_size > self.max_upload_size_mb * 1024 * 1024:
            return False, f"File too large. Max: {self.max_upload_size_mb}MB"
        
        # Check file type
        file_ext = Path(filename).suffix.lstrip(".").lower()
        if file_ext not in self.allowed_types:
            return False, f"File type not allowed. Allowed: {','.join(self.allowed_types)}"
        
        return True, "OK"
    
    def save_upload(self, user_id: int, filename: str, file_content: bytes) -> Optional[str]:
        """Save uploaded file to user's folder"""
        user_folder = self.get_user_folder(user_id)
        file_path = os.path.join(user_folder, "assets", filename)
        
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"Saved file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return None
    
    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            text = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return None
    
    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """Extract text from various file types"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == ".pdf":
                return self.extract_text_from_pdf(file_path)
            elif file_ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap size in tokens (approximate)
        
        Returns:
            List of text chunks
        """
        # Rough token approximation: 1 token ≈ 4 characters
        char_size = chunk_size * 4
        char_overlap = overlap * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + char_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            
            start = end - char_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def delete_file(self, user_id: int, file_path: str) -> bool:
        """Delete uploaded file"""
        user_folder = self.get_user_folder(user_id)
        
        # Security check: ensure file is in user's folder
        if not file_path.startswith(user_folder):
            logger.error(f"Attempted to delete file outside user folder: {file_path}")
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
