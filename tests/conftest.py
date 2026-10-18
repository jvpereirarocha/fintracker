import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# Settings() is instantiated at import time (app/infra/database/session.py, app/infra/auth/token.py),
# so these must exist before any app.infra / app.main import. Env vars take precedence over .env.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("TOKEN_TYPE", "bearer")
os.environ.setdefault("GH_TOKEN", "test")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.api.dependencies.base import get_current_user
    from app.domain.value_objects.auth import JWTPayload
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: JWTPayload(sub="john", exp=9999999999)
    yield TestClient(app)
    app.dependency_overrides.clear()
