from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import locale
import re
from typing import Optional

from app.domain.value_objects.transactions import TypeOfTransaction


@dataclass()
class TransactionEntity:
    transaction_id: int
    description: str
    amount: Decimal
    type_of_transaction: TypeOfTransaction
    registration_date: date
    due_date: Optional[date]
    user_id: int
    category_id: int


@dataclass(frozen=True)
class NewTransaction:
    description: str
    amount: Decimal
    type_of_transaction: str
    registration_date: datetime
    due_date: Optional[datetime]
    category: str


@dataclass(frozen=True)
class PatchTransaction:
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    type_of_transaction: Optional[str] = None
    registration_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    category: Optional[str] = None

