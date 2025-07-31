#!/usr/bin/env python3
"""
Complete example demonstrating full integration of API key authentication with agent server.
This example shows global authentication, middleware integration, and comprehensive testing.
"""

from bssagent.infrastructure.server import Server, AgentServer
from bssagent.auth.authentication_with_key import AuthenticationWithKey
from bssagent.auth.api_key_management import APIKeyManagement
from bssagent.security.data_privacy_manager import DataPrivacyMiddleware
from bssagent.core.base_agent import BaseAgent
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import json
import uuid

class TestAgent(BaseAgent):
    """Simple test agent for demonstration."""
    
    def __init__(self):
        super().__init__(name="test_agent", description="A test agent with authentication")
    
    def define_graph(self):
        """Define the agent graph."""
        pass

def create_global_auth_middleware():
    """Create a global authentication middleware that applies to all endpoints."""
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp
    from fastapi import Request, Response
    from starlette.status import HTTP_401_UNAUTHORIZED
    
    class GlobalAuthMiddleware(BaseHTTPMiddleware):
        def __init__(self, app: ASGIApp, exclude_paths: list = None):
            super().__init__(app)
            self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/public"]
            self.key_manager = APIKeyManagement()
        
        async def dispatch(self, request: Request, call_next):
            # Skip authentication for excluded paths
            if any(request.url.path.startswith(path) for path in self.exclude_paths):
                return await call_next(request)
            
            # Check for API key
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                # Also support Authorization header
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("ApiKey "):
                    api_key = auth_header.split(" ")[1]
            
            if not api_key:
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"error": "Missing API key"},
                    headers={"WWW-Authenticate": "ApiKey"}
                )
            
            # Validate API key
            user_id = self.key_manager.validate_api_key(api_key)
            if not user_id:
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid or revoked API key"},
                    headers={"WWW-Authenticate": "ApiKey"}
                )
            
            # Add user_id to request state for use in endpoints
            request.state.user_id = user_id
            
            return await call_next(request)
    
    return GlobalAuthMiddleware

def complete_auth_example():
    """Complete example with global authentication and agent integration."""
    print("=== Complete API Key Authentication Example ===")
    
    # Create agent
    agent = TestAgent()
    
    # Create server with agent
    server = AgentServer(agent_instance=agent, title="Complete Auth Agent Server")
    
    # Add global authentication middleware
    GlobalAuthMiddleware = create_global_auth_middleware()
    server.add_custom_middleware(GlobalAuthMiddleware)
    
    # Add data privacy middleware
    server.add_custom_middleware(DataPrivacyMiddleware)
    
    # Create API key manager
    key_manager = APIKeyManagement()
    
    # Generate test API keys
    user_id = "demo_user_123"
    api_key = key_manager.generate_api_key(user_id)
    print(f"Generated API key for user {user_id}: {api_key[:20]}...")
    
    # Public endpoints (no authentication required)
    async def public_info():
        return {
            "message": "Welcome to the Complete Auth Agent Server",
            "version": "1.0.0",
            "features": [
                "Global API key authentication",
                "Agent integration",
                "Data privacy monitoring",
                "Session management"
            ]
        }
    
    async def health_check():
        return {
            "status": "healthy",
            "service": "Complete Auth Agent Server",
            "agent": agent.get_name(),
            "authentication": "enabled"
        }
    
    # Protected endpoints (authentication handled by middleware)
    async def agent_chat(request: Request):
        """Chat with the agent (requires authentication)."""
        try:
            data = await request.json()
            message = data.get("message", "Hello")
            user_id = request.state.user_id  # Set by middleware
            
            # Get or create user session
            session = agent.get_or_create_user_session(user_id)
            
            # Create initial state
            initial_state = {
                "messages": [{"role": "user", "content": message}],
                "should_continue": False,
                "user_id": user_id
            }
            
            # Run agent
            result = agent.invoke(initial_state, session["thread"])
            
            return {
                "message": "Agent response",
                "user_id": user_id,
                "session_id": session["thread_id"],
                "response": result
            }
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Agent error: {str(e)}"}
            )
    
    async def user_sessions(request: Request):
        """Get user sessions (requires authentication)."""
        user_id = request.state.user_id
        try:
            session = agent.get_user_session(user_id)
            return {
                "message": "User session retrieved",
                "user_id": user_id,
                "session": {
                    "thread_id": session["thread_id"],
                    "created_at": session["created_at"],
                    "is_active": session["is_active"]
                }
            }
        except ValueError:
            return {
                "message": "No active session found",
                "user_id": user_id,
                "session": None
            }
    
    async def create_session(request: Request):
        """Create a new session (requires authentication)."""
        user_id = request.state.user_id
        try:
            session = agent.create_user_session(user_id)
            return {
                "message": "New session created",
                "user_id": user_id,
                "session": {
                    "thread_id": session["thread_id"],
                    "created_at": session["created_at"]
                }
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to create session: {str(e)}"}
            )
    
    async def delete_session(request: Request):
        """Delete user session (requires authentication)."""
        user_id = request.state.user_id
        try:
            agent.deactivate_session(user_id)
            return {
                "message": "Session deleted successfully",
                "user_id": user_id
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to delete session: {str(e)}"}
            )
    
    # Admin endpoints (require admin authentication)
    admin_auth = AuthenticationWithKey(header_name="X-Admin-Key")
    
    async def admin_stats(admin_id: str = Depends(admin_auth)):
        """Get admin statistics."""
        try:
            sessions = agent.list_active_sessions()
            return {
                "message": "Admin statistics",
                "admin_id": admin_id,
                "stats": {
                    "total_sessions": len(sessions),
                    "active_sessions": len([s for s in sessions if s.get("is_active", True)]),
                    "agent_name": agent.get_name()
                }
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to get stats: {str(e)}"}
            )
    
    # Add endpoints
    server.add_endpoint("/public", "GET", public_info, tags=["public"])
    server.add_endpoint("/health", "GET", health_check, tags=["health"])
    server.add_endpoint("/agent/chat", "POST", agent_chat, tags=["agent"])
    server.add_endpoint("/user/sessions", "GET", user_sessions, tags=["user"])
    server.add_endpoint("/user/sessions", "POST", create_session, tags=["user"])
    server.add_endpoint("/user/sessions", "DELETE", delete_session, tags=["user"])
    server.add_endpoint("/admin/stats", "GET", admin_stats, tags=["admin"])
    
    print("✓ Added endpoints:")
    print("  Public endpoints (no auth):")
    print("    - GET /public")
    print("    - GET /health")
    print("  Protected endpoints (require X-API-Key):")
    print("    - POST /agent/chat")
    print("    - GET /user/sessions")
    print("    - POST /user/sessions")
    print("    - DELETE /user/sessions")
    print("  Admin endpoints (require X-Admin-Key):")
    print("    - GET /admin/stats")
    print("  Agent endpoints (inherited):")
    print("    - GET /sessions")
    print("    - DELETE /sessions/{user_id}")
    
    return server, api_key

def run_comprehensive_tests(server, api_key):
    """Run comprehensive tests to verify the authentication system."""
    print("\n" + "="*60)
    print("COMPREHENSIVE TESTING GUIDE:")
    print("="*60)
    
    print("\n1. TEST PUBLIC ENDPOINTS (No authentication required):")
    print("   curl -X GET http://localhost:8000/public")
    print("   curl -X GET http://localhost:8000/health")
    
    print("\n2. TEST PROTECTED ENDPOINTS (Require X-API-Key):")
    print("   # Chat with agent")
    print(f"   curl -X POST http://localhost:8000/agent/chat \\")
    print(f"     -H 'X-API-Key: {api_key}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"message\": \"Hello, agent!\"}}'")
    
    print("\n   # Get user sessions")
    print(f"   curl -X GET http://localhost:8000/user/sessions \\")
    print(f"     -H 'X-API-Key: {api_key}'")
    
    print("\n   # Create new session")
    print(f"   curl -X POST http://localhost:8000/user/sessions \\")
    print(f"     -H 'X-API-Key: {api_key}'")
    
    print("\n   # Delete session")
    print(f"   curl -X DELETE http://localhost:8000/user/sessions \\")
    print(f"     -H 'X-API-Key: {api_key}'")
    
    print("\n3. TEST WITHOUT API KEY (Should fail with 401):")
    print("   curl -X POST http://localhost:8000/agent/chat \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Hello\"}'")
    
    print("\n4. TEST WITH INVALID API KEY (Should fail with 401):")
    print("   curl -X POST http://localhost:8000/agent/chat \\")
    print("     -H 'X-API-Key: invalid_key' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Hello\"}'")
    
    print("\n5. TEST AUTHORIZATION HEADER FORMAT:")
    print(f"   curl -X GET http://localhost:8000/user/sessions \\")
    print(f"     -H 'Authorization: ApiKey {api_key}'")
    
    print("\n6. TEST AGENT ENDPOINTS (Inherited from AgentServer):")
    print("   curl -X GET http://localhost:8000/sessions \\")
    print(f"     -H 'X-API-Key: {api_key}'")
    
    print("\n7. TEST DATA PRIVACY MONITORING:")
    print("   # Send request with sensitive data (check server logs)")
    print(f"   curl -X POST http://localhost:8000/agent/chat \\")
    print(f"     -H 'X-API-Key: {api_key}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"message\": \"My email is john.doe@example.com and phone is 555-123-4567\"}}'")

if __name__ == "__main__":
    server, api_key = complete_auth_example()
    
    # Run comprehensive tests
    run_comprehensive_tests(server, api_key)
    
    print("\n" + "="*60)
    print("FEATURES DEMONSTRATED:")
    print("✓ Global API key authentication middleware")
    print("✓ Data privacy monitoring middleware")
    print("✓ Agent integration with authentication")
    print("✓ Session management with user isolation")
    print("✓ Multiple authentication levels (user/admin)")
    print("✓ Comprehensive error handling")
    print("✓ Flexible header support (X-API-Key and Authorization)")
    
    print("\nTo start the server:")
    print("server.run(host='0.0.0.0', port=8000)")
    
    # Uncomment to run the server
    # server.run(host="0.0.0.0", port=8000) 