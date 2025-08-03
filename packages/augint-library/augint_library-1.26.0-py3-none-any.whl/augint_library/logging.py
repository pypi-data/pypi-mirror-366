"""Simple logging configuration for augint-library.

This module provides structured logging using only the Python standard library.
It's designed to work everywhere Python works, with optional JSON formatting
for compatibility with log aggregation systems like CloudWatch Logs Insights.

For AWS integration, consuming applications should use AWS Powertools Logger
which will enhance these standard logs with trace IDs and Lambda context.

Example:
    >>> from augint_library.logging import setup_logging
    >>> logger = setup_logging("my-service")
    >>> logger.info("Hello world", extra={"user_id": 123})

    >>> # With JSON formatting for production
    >>> logger = setup_logging("my-service", json_format=True)
    >>> logger.info("Processing started", extra={"batch_size": 100})
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """Simple JSON formatter using only standard library.

    Formats log records as JSON with consistent field names for
    structured logging systems. Handles exceptions gracefully.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string.

        Args:
            record: Python logging record to format.

        Returns:
            JSON string representation of the log record.
        """
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the log call
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_logging(
    service_name: str,
    level: str = "INFO",
    json_format: bool = False,
    handler: Optional[logging.Handler] = None,
) -> logging.Logger:
    """Configure structured logging for the service.

    Creates a logger with consistent formatting that works well with
    both local development and production log aggregation systems.

    Args:
        service_name: Name of the service/component for log identification.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: Whether to use JSON formatting for structured logs.
        handler: Optional custom handler (defaults to StreamHandler to stdout).

    Returns:
        Configured logger instance ready for use.

    Example:
        >>> # Basic usage for development
        >>> logger = setup_logging("user-service")
        >>> logger.info("User created", extra={"user_id": 123})

        >>> # JSON format for production
        >>> logger = setup_logging("user-service", json_format=True)
        >>> logger.error("Validation failed", extra={"errors": ["email required"]})
    """
    logger = logging.getLogger(service_name)

    # Clear any existing handlers to avoid duplication
    logger.handlers.clear()

    # Create handler (default to stdout for container/Lambda compatibility)
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on preference
    formatter: logging.Formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent log messages from being handled by root logger
    logger.propagate = False

    return logger
