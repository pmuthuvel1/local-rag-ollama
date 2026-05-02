"""
Ollama integration service for LLM inference
"""

import os
import requests
import time
import logging
from typing import List, Dict, Optional, Tuple
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with local Ollama instance"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.timeout = 300  # 5 minutes for generation
        self._health_checked = False
    
    def check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self._health_checked = response.status_code == 200
            return self._health_checked
        except (ConnectionError, Timeout):
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            self._health_checked = False
            return False
    
    def list_models(self) -> List[Dict]:
        """List available models in Ollama"""
        try:
            if not self.check_health():
                return []
            
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    models.append({
                        "name": model["name"],
                        "size": model.get("size", 0) / (1024**3),  # Convert to GB
                        "modified_at": model.get("modified_at")
                    })
                return models
            return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {str(e)}")
            return []
    
    def generate(self, 
                prompt: str, 
                model: Optional[str] = None,
                stream: bool = False,
                temperature: float = 0.7) -> Tuple[str, float]:
        """
        Generate text using Ollama
        Returns: (generated_text, generation_time_ms)
        """
        model = model or self.default_model
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": stream,
                    "temperature": temperature,
                },
                timeout=self.timeout,
                stream=stream
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code}")
            
            if stream:
                # For streaming, collect all responses
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
            else:
                data = response.json()
                full_response = data.get("response", "")
            
            generation_time = (time.time() - start_time) * 1000  # Convert to ms
            
            logger.info(f"Generated {len(full_response)} chars in {generation_time:.0f}ms")
            return full_response, generation_time
            
        except Exception as e:
            logger.error(f"Error generating with Ollama: {str(e)}")
            raise
    
    def embedding(self, text: str, model: Optional[str] = None) -> Optional[List[float]]:
        """
        Generate embedding for text using Ollama
        Returns: embedding vector or None if error
        """
        model = model or self.default_model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("embedding")
            else:
                logger.error(f"Ollama embedding error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error generating embedding with Ollama: {str(e)}")
            return None
