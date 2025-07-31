import re
import logging
from typing import Dict, Any, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class DataPrivacyManager:
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'api_key': r'\b[A-Za-z0-9]{32,}\b'
    }
    
    def detect_sensitive_data(self, text: str) -> Dict[str, list]:
        findings = {}
        for data_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[data_type] = matches
        return findings
    
    def mask_sensitive_data(self, text: str) -> str:
        for data_type, pattern in self.PII_PATTERNS.items():
            if data_type == 'email':
                text = re.sub(pattern, '[EMAIL_MASKED]', text)
            elif data_type == 'phone':
                text = re.sub(pattern, '[PHONE_MASKED]', text)
            elif data_type == 'api_key':
                text = re.sub(pattern, '[API_KEY_MASKED]', text)
            else:
                text = re.sub(pattern, f'[{data_type.upper()}_MASKED]', text)
        return text

    async def privacy_middleware(self, request: Request, call_next):
        # Log sensitive data detection for monitoring
        if request.method == "POST":
            body = await request.body()
            if body:
                text_content = body.decode('utf-8')
                sensitive_findings = self.detect_sensitive_data(text_content)
                if sensitive_findings:
                    # Log security event
                    print(f"Sensitive data detected: {list(sensitive_findings.keys())}")
        
        response = await call_next(request)
        return response


class DataPrivacyMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for detecting and logging sensitive data in requests.
    Can be used with Server.add_custom_middleware() method.
    
    Usage Examples:
    
    1. Basic usage with default settings:
        from bssagent.infrastructure.server import Server
        from bssagent.security.data_privacy_manager import DataPrivacyMiddleware
        
        server = Server()
        server.create_app()
        server.add_custom_middleware(DataPrivacyMiddleware)
    
    2. With custom configuration:
        from bssagent.security.data_privacy_manager import DataPrivacyMiddlewareFactory
        
        # Create middleware with custom settings
        CustomPrivacyMiddleware = DataPrivacyMiddlewareFactory.create(
            enable_logging=True,
            enable_masking=True,
            log_level="INFO"
        )
        
        server.add_custom_middleware(CustomPrivacyMiddleware)
    
    3. Direct instantiation (not recommended for add_custom_middleware):
        middleware = DataPrivacyMiddleware(
            app=server.app,
            enable_logging=True,
            enable_masking=False,
            log_level="WARNING"
        )
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        enable_logging: bool = True,
        enable_masking: bool = False,
        log_level: str = "WARNING"
    ):
        super().__init__(app)
        self.enable_logging = enable_logging
        self.enable_masking = enable_masking
        self.privacy_manager = DataPrivacyManager()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and detect sensitive data."""
        
        # Only process POST requests with body content
        if request.method == "POST" and request.headers.get("content-type", "").startswith("application/json"):
            try:
                # Read the request body
                body = await request.body()
                if body:
                    text_content = body.decode('utf-8')
                    
                    # Detect sensitive data
                    sensitive_findings = self.privacy_manager.detect_sensitive_data(text_content)
                    
                    if sensitive_findings and self.enable_logging:
                        # Log security event
                        self.logger.warning(
                            f"Sensitive data detected in request to {request.url.path}: "
                            f"{list(sensitive_findings.keys())}"
                        )
                    
                    # Optionally mask sensitive data in logs
                    if self.enable_masking and sensitive_findings:
                        masked_content = self.privacy_manager.mask_sensitive_data(text_content)
                        self.logger.info(f"Request body (masked): {masked_content}")
                    
            except Exception as e:
                self.logger.error(f"Error processing request body for privacy check: {e}")
        
        # Continue with the request
        response = await call_next(request)
        return response


class DataPrivacyMiddlewareFactory:
    """
    Factory class to create DataPrivacyMiddleware instances with different configurations.
    Useful for creating middleware instances that can be passed to add_custom_middleware.
    
    Usage Example:
        from bssagent.security.data_privacy_manager import DataPrivacyMiddlewareFactory
        from bssagent.infrastructure.server import Server
        
        # Create a custom middleware class
        CustomPrivacyMiddleware = DataPrivacyMiddlewareFactory.create(
            enable_logging=True,
            enable_masking=True,
            log_level="INFO"
        )
        
        # Use with server
        server = Server()
        server.create_app()
        server.add_custom_middleware(CustomPrivacyMiddleware)
    """
    
    @staticmethod
    def create(
        enable_logging: bool = True,
        enable_masking: bool = False,
        log_level: str = "WARNING"
    ) -> type:
        """
        Create a middleware class with the specified configuration.
        
        Args:
            enable_logging: Whether to log detected sensitive data
            enable_masking: Whether to mask sensitive data in logs
            log_level: Logging level for privacy events
            
        Returns:
            A middleware class that can be used with add_custom_middleware
        """
        class ConfiguredDataPrivacyMiddleware(DataPrivacyMiddleware):
            def __init__(self, app: ASGIApp):
                super().__init__(
                    app=app,
                    enable_logging=enable_logging,
                    enable_masking=enable_masking,
                    log_level=log_level
                )
        
        return ConfiguredDataPrivacyMiddleware
