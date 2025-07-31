#!/usr/bin/env python3
"""
Advanced example demonstrating comprehensive API key authentication.
This example shows multiple protected endpoints, different auth levels, and API key management.
"""

from bssagent.infrastructure.server import Server
from bssagent.auth.authentication_with_key import AuthenticationWithKey
from bssagent.auth.api_key_management import APIKeyManagement
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
import json

def advanced_auth_example():
    """Advanced example with multiple protected endpoints and key management."""
    print("=== Advanced API Key Authentication Example ===")
    
    # Create server
    server = Server(title="Advanced Auth Server")
    server.create_app()
    
    # Create authentication dependencies
    auth = AuthenticationWithKey()
    admin_auth = AuthenticationWithKey(header_name="X-Admin-Key")
    
    # Create API key manager
    key_manager = APIKeyManagement()
    
    # Generate test API keys
    user_id = "user_123"
    admin_id = "admin_456"
    user_key = key_manager.generate_api_key(user_id)
    admin_key = key_manager.generate_api_key(admin_id)
    
    print(f"Generated user API key: {user_key[:20]}...")
    print(f"Generated admin API key: {admin_key[:20]}...")
    
    # Public endpoints (no authentication)
    async def health_check():
        return {"status": "healthy", "service": "Advanced Auth Server"}
    
    async def public_info():
        return {
            "message": "Public information",
            "endpoints": ["/health", "/public", "/user/data", "/admin/users", "/admin/keys"]
        }
    
    # User-level protected endpoints
    async def user_data(user_id: str = Depends(auth)):
        return {
            "message": "User data accessed successfully",
            "user_id": user_id,
            "data": {
                "profile": {"name": "John Doe", "email": "john@example.com"},
                "preferences": {"theme": "dark", "language": "en"}
            }
        }
    
    async def user_profile(user_id: str = Depends(auth)):
        return {
            "message": "User profile accessed",
            "user_id": user_id,
            "profile": {
                "id": user_id,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    # Admin-level protected endpoints
    async def admin_users(admin_id: str = Depends(admin_auth)):
        return {
            "message": "Admin access granted",
            "admin_id": admin_id,
            "users": [
                {"id": "user_123", "name": "John Doe", "status": "active"},
                {"id": "user_456", "name": "Jane Smith", "status": "inactive"}
            ]
        }
    
    async def admin_keys(admin_id: str = Depends(admin_auth)):
        return {
            "message": "API keys management",
            "admin_id": admin_id,
            "keys": [
                {"user_id": "user_123", "key_preview": user_key[:20] + "..."},
                {"user_id": "admin_456", "key_preview": admin_key[:20] + "..."}
            ]
        }
    
    # API key management endpoints (admin only)
    async def create_api_key(request, admin_id: str = Depends(admin_auth)):
        try:
            data = await request.json()
            new_user_id = data.get("user_id")
            if not new_user_id:
                raise HTTPException(status_code=400, detail="user_id is required")
            
            new_key = key_manager.generate_api_key(new_user_id)
            return {
                "message": "API key created successfully",
                "user_id": new_user_id,
                "api_key": new_key
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to create API key: {str(e)}"}
            )
    
    async def revoke_api_key(request, admin_id: str = Depends(admin_auth)):
        try:
            data = await request.json()
            api_key = data.get("api_key")
            if not api_key:
                raise HTTPException(status_code=400, detail="api_key is required")
            
            success = key_manager.revoke_api_key(api_key)
            if success:
                return {"message": "API key revoked successfully"}
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to revoke API key"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to revoke API key: {str(e)}"}
            )
    
    # Add endpoints
    server.add_endpoint("/health", "GET", health_check, tags=["health"])
    server.add_endpoint("/public", "GET", public_info, tags=["public"])
    server.add_endpoint("/user/data", "GET", user_data, tags=["user"])
    server.add_endpoint("/user/profile", "GET", user_profile, tags=["user"])
    server.add_endpoint("/admin/users", "GET", admin_users, tags=["admin"])
    server.add_endpoint("/admin/keys", "GET", admin_keys, tags=["admin"])
    server.add_endpoint("/admin/keys/create", "POST", create_api_key, tags=["admin"])
    server.add_endpoint("/admin/keys/revoke", "POST", revoke_api_key, tags=["admin"])
    
    print("✓ Added endpoints:")
    print("  Public endpoints:")
    print("    - GET /health")
    print("    - GET /public")
    print("  User endpoints (require X-API-Key):")
    print("    - GET /user/data")
    print("    - GET /user/profile")
    print("  Admin endpoints (require X-Admin-Key):")
    print("    - GET /admin/users")
    print("    - GET /admin/keys")
    print("    - POST /admin/keys/create")
    print("    - POST /admin/keys/revoke")
    
    return server, user_key, admin_key

if __name__ == "__main__":
    server, user_key, admin_key = advanced_auth_example()
    
    print("\n" + "="*60)
    print("TESTING INSTRUCTIONS:")
    print("1. Start the server: server.run()")
    print("\n2. Test public endpoints:")
    print("   GET /health")
    print("   GET /public")
    print("\n3. Test user endpoints (use X-API-Key header):")
    print(f"   GET /user/data")
    print(f"   GET /user/profile")
    print(f"   Headers: X-API-Key: {user_key}")
    print("\n4. Test admin endpoints (use X-Admin-Key header):")
    print(f"   GET /admin/users")
    print(f"   GET /admin/keys")
    print(f"   Headers: X-Admin-Key: {admin_key}")
    print("\n5. Test API key management:")
    print(f"   POST /admin/keys/create")
    print(f"   Body: {{'user_id': 'new_user_789'}}")
    print(f"   POST /admin/keys/revoke")
    print(f"   Body: {{'api_key': '{user_key}'}}")
    
    # Uncomment to run the server
    # server.run(host="0.0.0.0", port=8000) 