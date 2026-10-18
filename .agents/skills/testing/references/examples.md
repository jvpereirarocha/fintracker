# Exemplos de testes

Padrões validados contra o código atual (pytest 9, anyio 4.4, FastAPI 0.111).

## `tests/conftest.py`

```python
import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

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
```

Imports de `app.*` ficam dentro da fixture: garantem que as env vars já existem quando `Settings()` roda.

## `tests/fakes.py`

Versão real no repositório (inclui `FakeTransactionRepo`, `make_transaction`, `make_filters`). Trecho:

```python
from app.domain.abstractions.repositories import AbstractCategoryRepository, AbstractUserRepository
from app.domain.entities.categories import CategoryEntity, SaveCategory


class FakeUserRepo(AbstractUserRepository):
    def __init__(self, users: dict[str, int] | None = None) -> None:
        self.users = users or {}

    def get_user_id_by_username(self, username: str) -> int:
        return self.users.get(username, 0)


class FakeCategoryRepo(AbstractCategoryRepository):
    def __init__(self) -> None:
        self.items: dict[int, CategoryEntity] = {}

    def get_category_id_by_name(self, name: str) -> int:
        return next(
            (cid for cid, c in self.items.items() if c.name.lower() == name.lower()), 0
        )

    def get_category_by_id(self, category_id: int) -> CategoryEntity | None:
        return self.items.get(category_id)

    def save(self, new_category: SaveCategory) -> CategoryEntity:
        category_id = len(self.items) + 1
        entity = CategoryEntity(
            category_id=category_id, name=new_category.name, description=new_category.description
        )
        self.items[category_id] = entity
        return entity
```

## Use case — `tests/test_usecase_create_category.py`

```python
import pytest

from app.domain.entities.categories import SaveCategory
from app.domain.exceptions.categories import CategoryAlreadyExistsException
from app.usecases.categories.persist_category import CreateCategoryUseCase
from tests.fakes import FakeCategoryRepo


@pytest.mark.anyio
async def test_create_category_returns_saved_entity() -> None:
    repo = FakeCategoryRepo()
    use_case = CreateCategoryUseCase(category_repo=repo)

    result = await use_case.execute(new_category=SaveCategory(name="Food", description="Meals"))

    assert result.category_id == 1
    assert result.name == "Food"


@pytest.mark.anyio
async def test_create_category_raises_when_name_already_exists_case_insensitive() -> None:
    repo = FakeCategoryRepo()
    use_case = CreateCategoryUseCase(category_repo=repo)
    await use_case.execute(new_category=SaveCategory(name="Food", description="Meals"))

    with pytest.raises(CategoryAlreadyExistsException):
        await use_case.execute(new_category=SaveCategory(name="food", description="Other"))
```

Padrão de autorização (vale para todo use case que recebe `username`):

```python
@pytest.mark.anyio
async def test_list_transactions_raises_when_user_not_found() -> None:
    use_case = ListTransactionsUseCase(
        user_repo=FakeUserRepo(), transaction_repo=FakeTransactionRepo()
    )

    with pytest.raises(UserNotFoundException):
        await use_case.execute(filters=make_filters(username="ghost"), page=1, page_size=10)
```

## API — `tests/test_api_categories.py`

```python
from fastapi.testclient import TestClient

from app.api.dependencies.categories import get_create_category_use_case
from app.main import app
from app.usecases.categories.persist_category import CreateCategoryUseCase
from tests.fakes import FakeCategoryRepo


def test_post_category_returns_201_with_camel_case_body(client: TestClient) -> None:
    repo = FakeCategoryRepo()
    app.dependency_overrides[get_create_category_use_case] = lambda: CreateCategoryUseCase(
        category_repo=repo
    )

    response = client.post("/api/v1/categories/", json={"name": "Food", "description": "x"})

    assert response.status_code == 201
    assert response.json() == {"categoryId": 1, "name": "Food", "description": "x"}


def test_post_duplicated_category_returns_400_with_detail(client: TestClient) -> None:
    repo = FakeCategoryRepo()
    app.dependency_overrides[get_create_category_use_case] = lambda: CreateCategoryUseCase(
        category_repo=repo
    )
    client.post("/api/v1/categories/", json={"name": "Food", "description": "x"})

    response = client.post("/api/v1/categories/", json={"name": "Food", "description": "x"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Category Food already exists"}


def test_get_categories_without_token_returns_401() -> None:
    response = TestClient(app).get("/api/v1/categories/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authorization header is missing"}
```

Payload de transação usa o contrato do frontend: `"amount": "R$ 1.000,00"`, `"registrationDate": "13/11/2025"`, `"typeOfTransaction": "expense"`, `"status": "not_paid"`, `"dueDate"` obrigatório para despesa.

## Domínio — `tests/test_domain_conversor.py`

```python
from decimal import Decimal

import pytest

from app.domain.business_logic.conversor import (
    clean_brl_format_to_decimal,
    format_decimal_to_brl_format,
)
from app.domain.exceptions.transactions import InvalidFormatCurrencyException


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("R$ 1.000,00", Decimal("1000.00")),
        ("R$ 0,50", Decimal("0.50")),
        ("R$1.234.567,89", Decimal("1234567.89")),
    ],
)
def test_clean_brl_format_to_decimal(raw: str, expected: Decimal) -> None:
    assert clean_brl_format_to_decimal(amount=raw) == expected


@pytest.mark.parametrize("raw", ["1000", "R$ 1000,00", "R$ 1.000.00", ""])
def test_clean_brl_format_to_decimal_rejects_invalid_format(raw: str) -> None:
    with pytest.raises(InvalidFormatCurrencyException):
        clean_brl_format_to_decimal(amount=raw)


def test_format_decimal_to_brl_format() -> None:
    assert format_decimal_to_brl_format(amount=Decimal("1234.5")) == "R$ 1.234,50"
```
