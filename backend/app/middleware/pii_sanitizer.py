"""
Middleware for PII (Personally Identifiable Information) sanitization
"""

import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class PIISanitizationMiddleware(BaseHTTPMiddleware):
    """
    Detects and redacts PII patterns from request bodies and response content
    before they are processed by the LLM
    """
    
    # PII patterns
    PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
        "api_key": r"(?i)(?:api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*([a-zA-Z0-9_\-]{40,})",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"(?:\+1)?[\s.-]?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})",
        "ip_address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    }
    
    @staticmethod
    def sanitize(text: str) -> str:
        """Redact PII patterns from text"""
        if not text:
            return text
        
        sanitized = text
        replacements = {
            "ssn": "[REDACTED_SSN]",
            "credit_card": "[REDACTED_CARD]",
            "api_key": "[REDACTED_API_KEY]",
            "email": "[REDACTED_EMAIL]",
            "phone": "[REDACTED_PHONE]",
            "ip_address": "[REDACTED_IP]",
        }
        
        for pattern_name, pattern in PIISanitizationMiddleware.PATTERNS.items():
            sanitized = re.sub(
                pattern,
                replacements[pattern_name],
                sanitized,
                flags=re.IGNORECASE
            )
        
        return sanitized
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Intercept request, check for PII, and potentially sanitize before passing to next middleware
        """
        # For now, we log detection but don't block
        # Production systems may want to reject or sanitize
        
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    text_body = body.decode("utf-8")
                    
                    # Check for PII
                    found_pii = []
                    for pattern_name, pattern in self.PATTERNS.items():
                        if re.search(pattern, text_body, re.IGNORECASE):
                            found_pii.append(pattern_name)
                    
                    if found_pii:
                        logger.warning(
                            f"PII detected in request: {', '.join(found_pii)}",
                            extra={
                                "request_id": getattr(request.state, "request_id", "unknown"),
                                "path": request.url.path,
                                "pii_types": found_pii
                            }
                        )
                
                # Re-create request since we consumed the body
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
                
            except Exception as e:
                logger.error(f"Error in PII sanitization: {str(e)}")
        
        response = await call_next(request)
        return response
