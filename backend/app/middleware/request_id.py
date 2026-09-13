import re
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.request_context import request_id_context

# Safe characters: letters, digits, _, -, ., and :
# Max 128 characters
# Not empty
# No newlines or control characters
SAFE_REQUEST_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.:]{1,128}$")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", "").strip()
        
        if not req_id or not SAFE_REQUEST_ID_REGEX.match(req_id):
            req_id = str(uuid.uuid4())
            
        token = request_id_context.set(req_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_context.reset(token)
