import os
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

API_KEY_HEADER = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API keys for all protected endpoints."""

    # Endpoints that don't require authentication
    PUBLIC_ENDPOINTS = {"/health", "/docs", "/redoc", "/openapi.json"}

    def __init__(self, app):
        super().__init__(app)
        # Load valid API keys from environment variable
        # Format: KEY1,KEY2,KEY3 or single key
        api_keys_env = os.getenv("API_KEYS", "")
        self.valid_api_keys = set(
            key.strip() for key in api_keys_env.split(",") if key.strip()
        )

        if not self.valid_api_keys:
            raise ValueError(
                "No API keys configured. Set API_KEYS environment variable."
            )

    async def dispatch(self, request: Request, call_next):
        # Allow public endpoints without authentication
        if request.url.path in self.PUBLIC_ENDPOINTS:
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get(API_KEY_HEADER)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key. Include X-API-Key header.",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Validate API key
        if api_key not in self.valid_api_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )

        # API key is valid, proceed with request
        response = await call_next(request)
        return response
