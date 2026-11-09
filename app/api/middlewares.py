"""Request logging middleware: one JSON line per HTTP request.

    {"event": "request", "method": "GET", "route": "/api/v1/transactions/{id}", "status": 200,
     "duration_ms": 87, "request_id": "3f9c...", "error": null}

It is a pure ASGI middleware rather than `@app.middleware("http")` (BaseHTTPMiddleware): it
does not wrap the response body in a separate task and sees the exceptions as they propagate.

Privacy: the logs leave the cluster, so only the route *template* is logged (never the raw path
or the query string), and never headers or bodies. For 422s only the names of the failing fields
are logged (see `validation_exception_handler`), never their values.
"""

import json
import logging
import re
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.routing import Match
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.logging_config import REQUEST_LOGGER_NAME

logger = logging.getLogger(REQUEST_LOGGER_NAME)

REQUEST_ID_HEADER = "x-request-id"
# Prometheus scrapes /metrics every 10 s: logging it would only be noise
SKIPPED_PATHS = frozenset({"/metrics"})
# The incoming request id is client-controlled: accept only short, plain ids
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _route_template(scope: Scope) -> str:
    # FastAPI's APIRoute stores itself in scope["route"] when it matches
    route = scope.get("route")
    if route is not None:
        return str(route.path)
    # Plain Starlette routes (/openapi.json, /docs, /redoc) do not: look the match up here.
    # This runs only for those and for 404s, so the extra loop costs nothing on API routes.
    router = getattr(scope.get("app"), "router", None)
    for candidate in getattr(router, "routes", []):
        match, _ = candidate.matches(scope)
        if match == Match.FULL:
            return str(getattr(candidate, "path", "unmatched"))
    return "unmatched"


def _request_id_from(scope: Scope) -> str:
    incoming = Headers(scope=scope).get(REQUEST_ID_HEADER)
    if incoming and _VALID_REQUEST_ID.match(incoming):
        return incoming
    return uuid.uuid4().hex


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in SKIPPED_PATHS:
            await self.app(scope, receive, send)
            return

        request_id = _request_id_from(scope)
        # `request.state` reads and writes this dict: the handlers use it to get the request id
        # and to hand back the names of the fields that failed validation
        state = scope.setdefault("state", {})
        state["request_id"] = request_id

        status_code = 500
        response_started = False

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        error: str | None = None
        start = time.perf_counter()
        try:
            await self.app(scope, receive, send_with_request_id)
        except BaseException as exc:
            # Unhandled exceptions reach this point before the 500 handler builds the response
            # (it is registered on ServerErrorMiddleware, outside the user middlewares)
            error = type(exc).__name__
            if not response_started:
                status_code = 500
            raise
        finally:
            record: dict[str, object] = {
                "event": "request",
                "method": scope["method"],
                "route": _route_template(scope),
                "status": status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000),
                "request_id": request_id,
                "error": error,
            }
            if "validation_errors" in state:
                record["validation_errors"] = state["validation_errors"]
            logger.info(json.dumps(record))
