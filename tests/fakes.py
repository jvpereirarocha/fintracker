from datetime import date
from decimal import Decimal

from app.domain.abstractions.repositories import (
    AbstractCategoryRepository,
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.entities.categories import CategoryEntity, SaveCategory
from app.domain.entities.transactions import SaveTransaction, TransactionEntity
from app.domain.value_objects.transactions import (
    TransactionsFilter,
    TransactionStatus,
    TypeOfTransaction,
)


class FakeUserRepo(AbstractUserRepository):
    def __init__(self, users: dict[str, int] | None = None) -> None:
        self.users = users or {}

    def get_user_id_by_username(self, username: str) -> int:
        return self.users.get(username, 0)


class FakeCategoryRepo(AbstractCategoryRepository):
    def __init__(self) -> None:
        self.items: dict[int, CategoryEntity] = {}

    def get_category_id_by_name(self, name: str) -> int:
        return next((cid for cid, c in self.items.items() if c.name.lower() == name.lower()), 0)

    def get_category_by_id(self, category_id: int) -> CategoryEntity | None:
        return self.items.get(category_id)

    def save(self, new_category: SaveCategory) -> CategoryEntity:
        category_id = len(self.items) + 1
        entity = CategoryEntity(
            category_id=category_id, name=new_category.name, description=new_category.description
        )
        self.items[category_id] = entity
        return entity


class FakeTransactionRepo(AbstractTransactionRepository):
    def __init__(self, transactions: list[TransactionEntity] | None = None) -> None:
        self.items: dict[int, TransactionEntity] = {t.transaction_id: t for t in transactions or []}
        self.last_filters: TransactionsFilter | None = None

    def exists(self, transaction_id: int) -> bool:
        return transaction_id in self.items

    def fetch_one(self, transaction_id: int) -> TransactionEntity:
        return self.items[transaction_id]

    def fetch_all(
        self, user_id: int, filters: TransactionsFilter, page: int, page_size: int
    ) -> tuple[list[TransactionEntity], int]:
        self.last_filters = filters
        user_items = sorted(
            (t for t in self.items.values() if t.user_id == user_id),
            key=lambda t: t.registration_date,
            reverse=True,
        )
        offset = (page - 1) * page_size
        return user_items[offset : offset + page_size], len(user_items)

    def save(
        self, new_transaction: SaveTransaction, user_id: int, category_id: int
    ) -> TransactionEntity:
        transaction_id = len(self.items) + 1
        entity = TransactionEntity(
            transaction_id=transaction_id,
            description=new_transaction.description,
            amount=new_transaction.amount,
            type_of_transaction=TypeOfTransaction(new_transaction.type_of_transaction),
            transaction_status=TransactionStatus(new_transaction.transaction_status),
            registration_date=new_transaction.registration_date.date(),
            due_date=new_transaction.due_date.date() if new_transaction.due_date else None,
            user_id=user_id,
            category_id=category_id,
        )
        self.items[transaction_id] = entity
        return entity


def make_transaction(
    transaction_id: int = 1,
    user_id: int = 1,
    registration_date: date = date(2025, 11, 13),
    type_of_transaction: TypeOfTransaction = TypeOfTransaction.INCOME,
    transaction_status: TransactionStatus = TransactionStatus.RECEIVED,
    amount: Decimal = Decimal("100.00"),
    description: str = "Salary",
    category_id: int = 1,
) -> TransactionEntity:
    return TransactionEntity(
        transaction_id=transaction_id,
        description=description,
        amount=amount,
        type_of_transaction=type_of_transaction,
        transaction_status=transaction_status,
        registration_date=registration_date,
        due_date=None,
        user_id=user_id,
        category_id=category_id,
    )


def make_filters(username: str = "john", **overrides: object) -> TransactionsFilter:
    values: dict[str, object] = {
        "month": None,
        "year": None,
        "description": None,
        "category": None,
        "type_of_transaction": None,
        "status_of_transaction": None,
    }
    values.update(overrides)
    return TransactionsFilter(username=username, **values)  # type: ignore[arg-type]
