"""
FastAPI application entry point for Loomin-Docs backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from app.middleware.logging import LoggingMiddleware
from app.middleware.pii_sanitizer import PIISanitizationMiddleware
from app.api import documents, ai, rag, files, health
from app.db.database import init_db

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Loomin-Docs API",
    description="Collaborative editor with local RAG-AI",
    version="0.1.0"
)

# Add middleware (order matters)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "['http://localhost:3000']").replace("'", '"'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PIISanitizationMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    print("🚀 Starting Loomin-Docs backend...")
    init_db()
    print("✅ Database initialized")
    print("✅ Ready to serve requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Loomin-Docs backend...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Loomin-Docs API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
