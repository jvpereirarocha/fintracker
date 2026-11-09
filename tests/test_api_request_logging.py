import json
import logging
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.api.dependencies.base import get_current_user
from app.api.dependencies.dashboards import get_monthly_summary_use_case
from app.logging_config import REQUEST_LOGGER_NAME
from app.main import app
from app.usecases.dashboards.monthly_summary import MonthlySummaryUseCase
from tests.fakes import FakeTransactionRepo, FakeUserRepo

MONTHLY_ROUTE = "/api/v1/dashboards/monthly"


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[dict[str, Any]] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(json.loads(record.getMessage()))


def _logged_in_as_me(request: Request) -> SimpleNamespace:
    user = SimpleNamespace(sub="me")
    request.state.user = user
    return user


def _broken_use_case() -> MonthlySummaryUseCase:
    raise RuntimeError("database is gone")


@pytest.fixture
def request_logs() -> Iterator[list[dict[str, Any]]]:
    # The request logger does not propagate to the root logger, so caplog cannot see it
    handler = _ListHandler()
    logger = logging.getLogger(REQUEST_LOGGER_NAME)
    logger.addHandler(handler)
    yield handler.records
    logger.removeHandler(handler)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_current_user] = _logged_in_as_me
    app.dependency_overrides[get_monthly_summary_use_case] = lambda: MonthlySummaryUseCase(
        user_repo=FakeUserRepo(), transaction_repo=FakeTransactionRepo(monthly_totals=[])
    )
    # Return the 500 response like production does, instead of re-raising in the test
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


def test_logs_one_json_line_with_route_template_and_duration(
    client: TestClient, request_logs: list[dict[str, Any]]
) -> None:
    response = client.get(MONTHLY_ROUTE, params={"year": 2024})

    assert response.status_code == 200
    assert len(request_logs) == 1
    record = request_logs[0]
    assert record["event"] == "request"
    assert record["method"] == "GET"
    assert record["route"] == MONTHLY_ROUTE
    assert record["status"] == 200
    assert isinstance(record["duration_ms"], int)
    assert record["error"] is None
    assert "validation_errors" not in record


def test_echoes_incoming_request_id(client: TestClient, request_logs: list[dict[str, Any]]) -> None:
    response = client.get(
        MONTHLY_ROUTE, params={"year": 2024}, headers={"X-Request-ID": "bot-abc.123"}
    )

    assert response.headers["X-Request-ID"] == "bot-abc.123"
    assert request_logs[0]["request_id"] == "bot-abc.123"


def test_replaces_an_invalid_request_id_with_a_generated_one(
    client: TestClient, request_logs: list[dict[str, Any]]
) -> None:
    response = client.get(
        MONTHLY_ROUTE, params={"year": 2024}, headers={"X-Request-ID": "has spaces" + "x" * 80}
    )

    generated = response.headers["X-Request-ID"]
    assert len(generated) == 32
    assert request_logs[0]["request_id"] == generated


def test_unknown_path_is_logged_as_unmatched(
    client: TestClient, request_logs: list[dict[str, Any]]
) -> None:
    response = client.get("/api/v1/does-not-exist/42")

    assert response.status_code == 404
    assert request_logs[0]["route"] == "unmatched"
    assert request_logs[0]["status"] == 404


def test_unhandled_exception_is_logged_as_500_with_its_type(
    client: TestClient, request_logs: list[dict[str, Any]]
) -> None:
    app.dependency_overrides[get_monthly_summary_use_case] = _broken_use_case

    response = client.get(MONTHLY_ROUTE, params={"year": 2024})

    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected error occurred. Please try again later."}
    record = request_logs[0]
    assert record["status"] == 500
    assert record["error"] == "RuntimeError"
    assert record["route"] == MONTHLY_ROUTE
    # The 500 response is built outside the middleware: the handler adds the header itself
    assert response.headers["X-Request-ID"] == record["request_id"]


def test_validation_error_logs_field_names_but_not_values(
    client: TestClient, request_logs: list[dict[str, Any]]
) -> None:
    response = client.get(MONTHLY_ROUTE, params={"year": "secret-value"})

    assert response.status_code == 422
    record = request_logs[0]
    assert record["status"] == 422
    assert record["validation_errors"] == ["query.year"]
    assert "secret-value" not in json.dumps(record)


def test_metrics_endpoint_is_not_logged(
    client: TestClient, request_logs: list[dict[str, Any]]
) -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert request_logs == []


@pytest.mark.parametrize("path", ["/openapi.json", "/docs"])
def test_plain_starlette_routes_are_logged_with_their_path(
    client: TestClient, request_logs: list[dict[str, Any]], path: str
) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert request_logs[0]["route"] == path
