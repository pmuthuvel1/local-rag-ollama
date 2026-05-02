"""
AI/Chat service for document manipulation and conversations
"""

import logging
import time
import uuid
from typing import List, Dict, Optional, Tuple
from app.services.ollama_service import OllamaService
from app.services.rag_service import RAGService
from app.utils.helpers import PIISanitizer, TokenCounter, MetadataGenerator

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered document assistance"""
    
    def __init__(self):
        self.ollama = OllamaService()
        self.rag = RAGService()
        self.pii_sanitizer = PIISanitizer()
        self.token_counter = TokenCounter()
        self.context_window = 4096  # Default for Llama2
    
    def summarize(self, 
                  text: str,
                  document_id: Optional[int] = None,
                  max_length: int = 150,
                  model: Optional[str] = None) -> Dict:
        """
        Summarize text using RAG and LLM
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Sanitize input
            sanitized_text, pii_detected = self.pii_sanitizer.sanitize(text)
            
            if pii_detected:
                logger.warning(f"PII detected in summarization request: {pii_detected}")
            
            # Retrieve context if document provided
            retrieved_chunks = []
            retrieval_time_ms = 0
            citations = []
            
            if document_id:
                retrieved_chunks, retrieval_time_ms = self.rag.retrieve(sanitized_text, top_k=3)
                citations = self._format_citations(retrieved_chunks)
            
            # Build prompt
            context = "\n".join([c["text"] for c in retrieved_chunks[:3]]) if retrieved_chunks else ""
            prompt = self._build_summarization_prompt(sanitized_text, context, max_length)
            
            # Count input tokens
            input_tokens = self.token_counter.count_tokens(prompt)
            
            # Generate summary
            start_gen = time.time()
            summary, generation_time_ms = self.ollama.generate(prompt, model=model)
            
            # Count output tokens
            output_tokens = self.token_counter.count_tokens(summary)
            
            # Prepare response
            token_metadata = MetadataGenerator.create_token_metadata(input_tokens, output_tokens, self.context_window)
            latency_metadata = MetadataGenerator.create_latency_metadata(retrieval_time_ms, generation_time_ms)
            
            return {
                "success": True,
                "response": summary.strip(),
                "citations": citations,
                "request_id": request_id,
                "tokens": token_metadata,
                "latency": latency_metadata,
                "model_used": model or self.ollama.default_model
            }
        
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
    
    def improve(self,
               text: str,
               improvement_type: str = "enhance",
               document_id: Optional[int] = None,
               model: Optional[str] = None) -> Dict:
        """
        Improve text using LLM
        improvement_type: 'enhance', 'simplify', or 'expand'
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Sanitize input
            sanitized_text, pii_detected = self.pii_sanitizer.sanitize(text)
            
            if pii_detected:
                logger.warning(f"PII detected in improve request: {pii_detected}")
            
            # Retrieve context
            retrieved_chunks = []
            retrieval_time_ms = 0
            citations = []
            
            if document_id:
                retrieved_chunks, retrieval_time_ms = self.rag.retrieve(sanitized_text, top_k=3)
                citations = self._format_citations(retrieved_chunks)
            
            # Build prompt
            context = "\n".join([c["text"] for c in retrieved_chunks[:3]]) if retrieved_chunks else ""
            prompt = self._build_improvement_prompt(sanitized_text, context, improvement_type)
            
            # Count input tokens
            input_tokens = self.token_counter.count_tokens(prompt)
            
            # Generate improvement
            start_gen = time.time()
            improved_text, generation_time_ms = self.ollama.generate(prompt, model=model)
            
            # Count output tokens
            output_tokens = self.token_counter.count_tokens(improved_text)
            
            # Prepare response
            token_metadata = MetadataGenerator.create_token_metadata(input_tokens, output_tokens, self.context_window)
            latency_metadata = MetadataGenerator.create_latency_metadata(retrieval_time_ms, generation_time_ms)
            
            return {
                "success": True,
                "response": improved_text.strip(),
                "citations": citations,
                "request_id": request_id,
                "tokens": token_metadata,
                "latency": latency_metadata,
                "model_used": model or self.ollama.default_model
            }
        
        except Exception as e:
            logger.error(f"Error in text improvement: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
    
    def chat(self,
            message: str,
            document_id: Optional[int] = None,
            conversation_history: Optional[List[Dict]] = None,
            use_rag: bool = True,
            model: Optional[str] = None) -> Dict:
        """
        Chat with AI assistant with optional RAG context
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Sanitize input
            sanitized_message, pii_detected = self.pii_sanitizer.sanitize(message)
            
            if pii_detected:
                logger.warning(f"PII detected in chat: {pii_detected}")
            
            # Retrieve context if RAG enabled
            retrieved_chunks = []
            retrieval_time_ms = 0
            citations = []
            
            if use_rag:
                retrieved_chunks, retrieval_time_ms = self.rag.retrieve(sanitized_message, top_k=5)
                citations = self._format_citations(retrieved_chunks)
            
            # Build prompt with conversation history
            context = "\n".join([c["text"] for c in retrieved_chunks[:5]]) if retrieved_chunks else ""
            prompt = self._build_chat_prompt(
                sanitized_message,
                context,
                conversation_history or []
            )
            
            # Count input tokens
            input_tokens = self.token_counter.count_tokens(prompt)
            
            # Generate response
            start_gen = time.time()
            response, generation_time_ms = self.ollama.generate(prompt, model=model)
            
            # Count output tokens
            output_tokens = self.token_counter.count_tokens(response)
            
            # Prepare response
            token_metadata = MetadataGenerator.create_token_metadata(input_tokens, output_tokens, self.context_window)
            latency_metadata = MetadataGenerator.create_latency_metadata(retrieval_time_ms, generation_time_ms)
            
            return {
                "success": True,
                "response": response.strip(),
                "citations": citations,
                "request_id": request_id,
                "tokens": token_metadata,
                "latency": latency_metadata,
                "model_used": model or self.ollama.default_model
            }
        
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
    
    def _build_summarization_prompt(self, text: str, context: str, max_length: int) -> str:
        """Build prompt for summarization"""
        prompt = f"""You are a helpful document summarization assistant.

Summarize the following text in {max_length} words or less. Be concise and capture the main points.

Text to summarize:
{text}
"""
        if context:
            prompt += f"\nRelated context:\n{context}"
        
        return prompt
    
    def _build_improvement_prompt(self, text: str, context: str, improvement_type: str) -> str:
        """Build prompt for text improvement"""
        instructions = {
            "enhance": "Make the text more professional and engaging",
            "simplify": "Simplify the text to be easier to understand",
            "expand": "Expand the text with more details and examples"
        }
        
        instruction = instructions.get(improvement_type, "Improve the text")
        
        prompt = f"""You are a writing assistant. {instruction}.

Original text:
{text}

Improved text:"""
        
        if context:
            prompt += f"\nYou can use this related context:\n{context}"
        
        return prompt
    
    def _build_chat_prompt(self, message: str, context: str, history: List[Dict]) -> str:
        """Build prompt for chat"""
        prompt = "You are a helpful AI assistant integrated into a document editor.\n"
        
        # Add conversation history
        if history:
            prompt += "\nConversation history:\n"
            for msg in history[-5:]:  # Last 5 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
        
        # Add context if available
        if context:
            prompt += f"\nRelevant document content:\n{context}\n"
        
        prompt += f"\nUser: {message}\nAssistant:"
        
        return prompt
    
    def _format_citations(self, chunks: List[Dict]) -> List[Dict]:
        """Format chunks as citations"""
        return [
            {
                "file_id": chunk["file_id"],
                "chunk_id": chunk["chunk_index"],
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "score": chunk["similarity_score"]
            }
            for chunk in chunks
        ]
