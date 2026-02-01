"""Middleware for the FastAPI application."""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # Add request ID to request state
        request.state.request_id = request_id

        # Log incoming request
        logger.info(
            f"[{request_id}] --> {request.method} {request.url.path}"
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] <-- {request.method} {request.url.path} | "
                f"ERROR | {process_time:.3f}s | {str(e)}"
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"[{request_id}] <-- {request.method} {request.url.path} | "
            f"{response.status_code} | {process_time:.3f}s"
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
