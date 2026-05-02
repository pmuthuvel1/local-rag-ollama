"""
RAG (Retrieval-Augmented Generation) service using FAISS and embeddings
"""

import os
import time
import json
import pickle
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)

class RAGService:
    """Service for RAG pipeline using FAISS"""
    
    def __init__(self):
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.index_path = os.getenv("FAISS_INDEX_PATH", "/app/data/rag_index")
        self.chunk_metadata_path = os.path.join(os.path.dirname(self.index_path), "chunk_metadata.pkl")
        
        # Initialize embedding model
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Embedding model loaded. Dimension: {self.embedding_model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            self.embedding_model = None
        
        self.index = None
        self.chunk_metadata = []
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index from disk if it exists"""
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            if os.path.exists(self.chunk_metadata_path):
                with open(self.chunk_metadata_path, 'rb') as f:
                    self.chunk_metadata = pickle.load(f)
                logger.info(f"Loaded {len(self.chunk_metadata)} chunk metadata")
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            
            with open(self.chunk_metadata_path, 'wb') as f:
                pickle.dump(self.chunk_metadata, f)
            
            logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
    
    def _ensure_index(self):
        """Ensure FAISS index is initialized"""
        if self.index is None and self.embedding_model:
            dim = self.embedding_model.get_sentence_embedding_dimension()
            # Use IVF index with PQ quantization
            quantizer = faiss.IndexFlatL2(dim)
            self.index = faiss.IndexIVFFlat(quantizer, dim, 100)
            self.index.train(np.random.random((1000, dim)).astype('float32'))
    
    def add_chunks(self, chunks: List[Dict]) -> bool:
        """
        Add text chunks to the FAISS index
        
        Args:
            chunks: List of dicts with keys: text, file_id, chunk_index, metadata
        
        Returns:
            Success bool
        """
        if not self.embedding_model:
            logger.error("Embedding model not loaded")
            return False
        
        try:
            self._ensure_index()
            
            # Extract texts
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_model.encode(texts, batch_size=32, convert_to_tensor=False)
            embeddings = embeddings.astype('float32')
            
            # Add to index
            self.index.add(embeddings)
            
            # Store metadata
            for i, chunk in enumerate(chunks):
                self.chunk_metadata.append({
                    "file_id": chunk["file_id"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "metadata": chunk.get("metadata", {})
                })
            
            # Save to disk
            self._save_index()
            logger.info(f"Added {len(chunks)} chunks to index. Total vectors: {self.index.ntotal}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks: {str(e)}")
            return False
    
    def retrieve(self, query: str, top_k: int = 5, distance_threshold: float = 0.3) -> Tuple[List[Dict], float]:
        """
        Retrieve top-k similar chunks for a query
        
        Returns:
            (chunks, retrieval_time_ms)
        """
        if not self.embedding_model or self.index is None:
            logger.warning("RAG not ready")
            return [], 0
        
        try:
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False).astype('float32')
            
            # Search
            distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Collect results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= len(self.chunk_metadata):  # Invalid index
                    continue
                
                distance = distances[0][i]
                # FAISS returns L2 distance, convert to similarity
                similarity = 1 / (1 + distance)
                
                if similarity < distance_threshold:
                    continue
                
                metadata = self.chunk_metadata[idx]
                results.append({
                    "file_id": metadata["file_id"],
                    "chunk_index": metadata["chunk_index"],
                    "text": metadata["text"],
                    "similarity_score": float(similarity),
                    "metadata": metadata["metadata"]
                })
            
            retrieval_time = (time.time() - start_time) * 1000  # Convert to ms
            return results, retrieval_time
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return [], 0
    
    def rebuild_index(self) -> bool:
        """Rebuild the entire index (for maintenance)"""
        try:
            logger.info("Rebuilding FAISS index...")
            self.index = None
            self.chunk_metadata = []
            
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.chunk_metadata_path):
                os.remove(self.chunk_metadata_path)
            
            logger.info("Index rebuilt successfully")
            return True
        except Exception as e:
            logger.error(f"Error rebuilding index: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the current index"""
        if self.index is None:
            return {
                "status": "not_ready",
                "total_vectors": 0,
                "total_chunks": 0
            }
        
        return {
            "status": "ready",
            "total_vectors": self.index.ntotal,
            "total_chunks": len(self.chunk_metadata),
            "index_type": type(self.index).__name__,
            "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension() if self.embedding_model else 0
        }
