from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add conservative security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Only add HSTS if the request is actually served over HTTPS.
        # This checks both direct HTTPS and forwarded HTTPS (from a reverse proxy).
        scheme = request.url.scheme
        forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
        if scheme == "https" or forwarded_proto == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
        return response
