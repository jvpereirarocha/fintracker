from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from app.domain.value_objects.transactions import TransactionStatus, TypeOfTransaction


@dataclass()
class TransactionEntity:
    transaction_id: int
    description: str
    amount: Decimal
    type_of_transaction: TypeOfTransaction
    transaction_status: TransactionStatus
    registration_date: date
    due_date: date | None
    user_id: int
    category_id: int


@dataclass(frozen=True)
class SaveTransaction:
    description: str
    amount: Decimal
    type_of_transaction: str
    transaction_status: str
    registration_date: datetime
    due_date: datetime | None
    category: str

    def __post_init__(self):
        if self.type_of_transaction == TypeOfTransaction.EXPENSE.value and not self.due_date:
            raise ValueError("Due date is required for expense transactions")
