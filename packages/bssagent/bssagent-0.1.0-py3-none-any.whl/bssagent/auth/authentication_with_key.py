from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED
from bssagent.auth.api_key_management import APIKeyManagement

class AuthenticationWithKey:
    """
    FastAPI dependency for API key authentication. Checks for a valid API key in the request headers.
    Usage (as dependency):
        from bssagent.auth.authentication_with_key import AuthenticationWithKey
        auth = AuthenticationWithKey()
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(auth)):
            ...
    """
    def __init__(self, header_name: str = "X-API-Key"):
        self.header_name = header_name
        self.key_manager = APIKeyManagement()

    async def __call__(self, request: Request) -> str:
        api_key = request.headers.get(self.header_name)
        if not api_key:
            # Also support Authorization: ApiKey <key>
            auth_header = request.headers.get("Authorization")
            if auth_header:
                scheme, param = get_authorization_scheme_param(auth_header)
                if scheme.lower() == "apikey":
                    api_key = param
        if not api_key:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Missing API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        user_id = self.key_manager.validate_api_key(api_key)
        if not user_id:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        return user_id 