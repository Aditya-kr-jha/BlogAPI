import time
from typing import Callable, Dict

import jwt
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import ALGORITHM, SECRET_KEY


# 1. Request Timing Middleware
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


# 2. Request Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path}"
        )
        response = await call_next(request)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status: {response.status_code}")
        return response


# 3. Rate Limiting Middleware
class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_records: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next: Callable):
        # Simple in-memory rate limiting by IP
        client_ip = request.client.host
        current_time = time.time()

        # Initialize or clean expired timestamps
        if client_ip not in self.request_records:
            self.request_records[client_ip] = []

        self.request_records[client_ip] = [
            timestamp
            for timestamp in self.request_records[client_ip]
            if current_time - timestamp < self.window_seconds
        ]

        # Check rate limit
        if len(self.request_records[client_ip]) >= self.max_requests:
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Add current request timestamp
        self.request_records[client_ip].append(current_time)

        # Process request
        return await call_next(request)


# 4. JWT Verification Middleware (alternative approach to dependencies)
class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths=None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/token",
            "/register",
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip middleware for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Check for authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return Response(
                content="Not authenticated",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.replace("Bearer ", "")

        try:
            # Verify the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            # Add the user information to the request state for handlers to use
            request.state.username = payload.get("sub")
        except jwt.PyJWTError:
            return Response(
                content="Invalid token",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Process request
        return await call_next(request)
