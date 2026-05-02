"""
Utility functions for PII sanitization, token counting, and other helpers
"""

import re
import tiktoken
from typing import Dict, Tuple

class PIISanitizer:
    """Utility class for PII detection and sanitization"""
    
    PATTERNS = {
        "ssn": (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
        "credit_card": (r"\b(?:\d{4}[\s-]?){3}\d{4}\b", "[REDACTED_CARD]"),
        "api_key": (r"(?i)(?:api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*([a-zA-Z0-9_\-]{40,})", "[REDACTED_API_KEY]"),
        "email": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
        "phone": (r"(?:\+1)?[\s.-]?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})", "[REDACTED_PHONE]"),
        "ip_address": (r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", "[REDACTED_IP]"),
    }
    
    @staticmethod
    def sanitize(text: str) -> Tuple[str, Dict[str, int]]:
        """
        Sanitize text by redacting PII patterns.
        Returns: (sanitized_text, detected_patterns_dict)
        """
        if not text:
            return text, {}
        
        sanitized = text
        detected = {}
        
        for pattern_name, (pattern, replacement) in PIISanitizer.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[pattern_name] = len(matches) if isinstance(matches[0], str) else len(matches)
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized, detected
    
    @staticmethod
    def detect(text: str) -> Dict[str, int]:
        """Detect PII patterns without sanitizing"""
        if not text:
            return {}
        
        detected = {}
        for pattern_name, (pattern, _) in PIISanitizer.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[pattern_name] = len(matches) if isinstance(matches[0], str) else len(matches)
        
        return detected


class TokenCounter:
    """Utility class for counting tokens"""
    
    def __init__(self, model: str = "cl100k_base"):
        """Initialize with encoding model"""
        try:
            self.encoding = tiktoken.get_encoding(model)
        except:
            # Fallback to basic token counting if tiktoken not available
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Simple fallback: estimate 1 token per 4 characters
            return len(text) // 4
    
    def estimate_context_usage(self, 
                              input_tokens: int, 
                              output_tokens: int, 
                              context_window: int = 4096) -> float:
        """Calculate percentage of context window used"""
        total = input_tokens + output_tokens
        return (total / context_window) * 100


class MetadataGenerator:
    """Generate metadata for API responses"""
    
    @staticmethod
    def create_token_metadata(input_tokens: int, output_tokens: int, context_window: int = 4096):
        """Create token metadata"""
        total = input_tokens + output_tokens
        usage_percent = (total / context_window) * 100
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total,
            "context_window_size": context_window,
            "usage_percent": min(100.0, round(usage_percent, 2))
        }
    
    @staticmethod
    def create_latency_metadata(retrieval_time_ms: float, generation_time_ms: float):
        """Create latency metadata"""
        return {
            "retrieval_time_ms": round(retrieval_time_ms, 2),
            "generation_time_ms": round(generation_time_ms, 2),
            "total_time_ms": round(retrieval_time_ms + generation_time_ms, 2)
        }
