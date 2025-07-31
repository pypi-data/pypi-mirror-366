from typing import Any, Optional, Callable
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
import uvicorn
import logging

from bssagent.core import BaseAgent
from bssagent.security import get_limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


class Server:
    """Manages FastAPI server creation and configuration for agent applications."""
    
    def __init__(
        self,
        title: str = "BSS Agent Server",
        description: str = "A server for managing BSS Agent applications",
        version: str = "1.0.0",
        host: str = "0.0.0.0",
        port: int = 8000,
        enable_cors: bool = True,
        cors_origins: Optional[list] = None,
        log_level: str = "info"
    ):
        self.title = title
        self.description = description
        self.version = version
        self.host = host
        self.port = port
        self.enable_cors = enable_cors
        self.cors_origins = cors_origins or ["*"]
        self.log_level = log_level
        self.app = None
        self.endpoints = {}
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        self.logger = logging.getLogger(__name__)
    
    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        self.app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version
        )
        
        # Add CORS middleware if enabled
        if self.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Add global exception handler
        self.app.add_exception_handler(Exception, self._global_exception_handler)
        
        self.logger.info(f"FastAPI app created: {self.title} v{self.version}")
        return self.app
    
    def add_endpoint(
        self,
        path: str,
        method: str = "POST",
        handler: Optional[Callable] = None,
        response_model: Optional[Any] = None,
        tags: Optional[list] = None
    ):
        """Add an endpoint to the FastAPI app."""
        if not self.app:
            raise RuntimeError("App not created. Call create_app() first.")
        
        if handler is None:
            raise ValueError("Handler function is required")
        
        method = method.upper()
        
        if method == "GET":
            self.app.get(path, response_model=response_model, tags=tags or [])(handler)
        elif method == "POST":
            self.app.post(path, response_model=response_model, tags=tags or [])(handler)
        elif method == "PUT":
            self.app.put(path, response_model=response_model, tags=tags or [])(handler)
        elif method == "DELETE":
            self.app.delete(path, response_model=response_model, tags=tags or [])(handler)
        elif method == "PATCH":
            self.app.patch(path, response_model=response_model, tags=tags or [])(handler)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        self.endpoints[path] = {
            "method": method,
            "handler": handler,
            "tags": tags or []
        }
        
        self.logger.info(f"Added endpoint: {method} {path}")
    
    def add_agent_endpoints(self, agent_instance: Any):
        """Add standard agent endpoints to the server."""
        if not self.app:
            raise RuntimeError("App not created. Call create_app() first.")
        
        # Add session management endpoints
        async def list_sessions_endpoint():
            try:
                sessions = agent_instance.list_active_sessions()
                return {"sessions": sessions}
            except Exception as e:
                self.logger.error(f"Error listing sessions: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )
        
        async def delete_session_endpoint(user_id: str):
            try:
                agent_instance.deactivate_session(user_id)
                return {"message": f"Session for user {user_id} deleted"}
            except Exception as e:
                self.logger.error(f"Error deleting session: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )
        
        # Register endpoints
        self.add_endpoint("/sessions", "GET", list_sessions_endpoint, tags=["sessions"])
        self.add_endpoint("/sessions/{user_id}", "DELETE", delete_session_endpoint, tags=["sessions"])
        
        self.logger.info("Added standard agent endpoints")

    async def _global_exception_handler(self, request: Request, exc: Exception):
        """Global exception handler for the FastAPI app."""
        self.logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)}
        )
    
    def add_health_check(self):
        """Add a health check endpoint."""
        async def health_check():
            return {
                "status": "healthy",
                "service": self.title,
                "version": self.version,
                "endpoints": len(self.endpoints)
            }
        
        self.add_endpoint("/health", "GET", health_check, tags=["health"])
    
    def add_metrics_endpoint(self):
        """Add a metrics endpoint for monitoring."""
        async def metrics():
            return {
                "service": self.title,
                "version": self.version,
                "endpoints": self.endpoints,
                "session_count": getattr(self, 'session_count', 0)
            }
        
        self.add_endpoint("/metrics", "GET", metrics, tags=["monitoring"])
    
    def run(self, **kwargs):
        """Run the FastAPI server."""
        if not self.app:
            self.create_app()
        
        # Override default settings with provided kwargs
        host = kwargs.get("host", self.host)
        port = kwargs.get("port", self.port)
        log_level = kwargs.get("log_level", self.log_level)
        
        self.logger.info(f"Starting server on {host}:{port}")
        
        # Ensure app is not None before running
        if self.app is None:
            raise RuntimeError("Failed to create FastAPI app")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=log_level
        )
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance."""
        if not self.app:
            self.create_app()
        
        # Ensure app is not None before returning
        if self.app is None:
            raise RuntimeError("Failed to create FastAPI app")
        
        return self.app
    
    def add_custom_middleware(self, middleware_class: Any, **kwargs):
        """Add custom middleware to the FastAPI app."""
        if not self.app:
            raise RuntimeError("App not created. Call create_app() first.")
        
        self.app.add_middleware(middleware_class, **kwargs)
        self.logger.info(f"Added custom middleware: {middleware_class.__name__}")

    def add_limiter(self):
        """Add a limiter to the FastAPI app."""
        if not self.app:
            raise RuntimeError("App not created. Call create_app() first.")
        self.limiter: Limiter = get_limiter()
        self.app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

class AgentServer(Server):
    """Specialized server class for agent applications."""
    
    def __init__(self, agent_instance: BaseAgent, use_rate_limiter: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.agent_instance = agent_instance
        self.use_rate_limiter = use_rate_limiter
        self.create_app()
    
    def create_app(self) -> FastAPI:
        """Create app and add agent-specific endpoints."""
        app = super().create_app()
        if self.use_rate_limiter:
            self.add_limiter()
        self.add_health_check()
        self.add_metrics_endpoint()
        return app
