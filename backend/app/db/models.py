"""
SQLAlchemy ORM models for database tables
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, LargeBinary, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String)
    folder_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    uploaded_files = relationship("UploadedFile", back_populates="user")
    access_logs = relationship("AccessLog", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String, index=True)
    content = Column(Text)
    markdown_source = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents", foreign_keys=[user_id])
    versions = relationship("DocumentVersion", back_populates="document")
    chat_history = relationship("ChatHistory", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    version_number = Column(Integer)
    content = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="versions")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True, index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    chat_metadata = Column(JSON, nullable=True)  # {request_id, retrieval_time, generation_time, tokens_used, citations}
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    document = relationship("Document", back_populates="chat_history")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    original_filename = Column(String)
    file_type = Column(String)  # pdf, txt, md
    file_path = Column(String, unique=True)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    indexed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="uploaded_files")
    rag_chunks = relationship("RAGChunk", back_populates="file")

class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), index=True)
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding_vector = Column(LargeBinary, nullable=True)  # Serialized numpy array
    chunk_metadata = Column(JSON)  # {file, page, section}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("UploadedFile", back_populates="rag_chunks")

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String)  # read, write, upload, delete, ai_request
    resource_type = Column(String)  # document, file, chat
    resource_id = Column(String, index=True)
    request_id = Column(String, unique=True, nullable=True)
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="access_logs")
