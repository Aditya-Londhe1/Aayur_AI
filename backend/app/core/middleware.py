import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming requests and response time
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.4f}s "
            f"status={response.status_code}"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate-limiting middleware (basic implementation)
    """

    def __init__(self, app, max_requests: int = 100):
        super().__init__(app)
        self.max_requests = max_requests
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        self.request_counts[client_ip] = self.request_counts.get(client_ip, 0) + 1

        if self.request_counts[client_ip] > self.max_requests:
            return Response(
                content="Too many requests",
                status_code=429
            )

        return await call_next(request)
