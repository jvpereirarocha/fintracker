"""Logging setup for the application loggers (`app.*`).

uvicorn configures only its own loggers, so without this the `app.*` records fall back to
Python's "last resort" handler: WARNING and above only, with no timestamp or level.

Two outputs, both on stdout (collected by Fluent Bit in the cluster):
- `app.*`: plain text, "2026-01-01 10:00:00,123 [ERROR] app.api.handlers: ...". The timestamp
  prefix is what the Fluent Bit multiline parser uses to start a record, so tracebacks stay
  attached to their log line.
- `app.request`: one JSON object per line, written as-is by the request logging middleware.
"""

import logging.config
from typing import Any

REQUEST_LOGGER_NAME = "app.request"

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    # Keep the uvicorn, sqlalchemy and alembic loggers as they are
    "disable_existing_loggers": False,
    "formatters": {
        "text": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "raw": {"format": "%(message)s"},
    },
    "handlers": {
        "text_stdout": {
            "class": "logging.StreamHandler",
            "formatter": "text",
            "stream": "ext://sys.stdout",
        },
        "raw_stdout": {
            "class": "logging.StreamHandler",
            "formatter": "raw",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {"level": "INFO", "handlers": ["text_stdout"], "propagate": False},
        REQUEST_LOGGER_NAME: {"level": "INFO", "handlers": ["raw_stdout"], "propagate": False},
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
