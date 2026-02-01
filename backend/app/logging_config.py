"""Logging configuration for the application."""

import logging
import sys
from typing import Any, Dict

from app.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.db_echo else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


# Request logging context
class RequestLoggingContext:
    """Context manager for request-scoped logging."""

    def __init__(self, request_id: str, extra: Dict[str, Any] = None):
        self.request_id = request_id
        self.extra = extra or {}

    def get_log_extra(self) -> Dict[str, Any]:
        """Get extra fields for logging."""
        return {"request_id": self.request_id, **self.extra}
