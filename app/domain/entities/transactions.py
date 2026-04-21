from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import locale
import re
from typing import Optional

from app.domain.value_objects.transactions import TypeOfTransaction, TransactionStatus


@dataclass()
class TransactionEntity:
    transaction_id: int
    description: str
    amount: Decimal
    type_of_transaction: TypeOfTransaction
    transaction_status: TransactionStatus
    registration_date: date
    due_date: Optional[date]
    user_id: int
    category_id: int


@dataclass(frozen=True)
class SaveTransaction:
    description: str
    amount: Decimal
    type_of_transaction: str
    transaction_status: str
    registration_date: datetime
    due_date: Optional[datetime]
    category: str

    def __post_init__(self):
        if self.type_of_transaction == TypeOfTransaction.EXPENSE.value and not self.due_date:
            raise ValueError("Due date is required for expense transactions")


