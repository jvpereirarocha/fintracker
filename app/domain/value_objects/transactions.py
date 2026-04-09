from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class TypeOfTransaction(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionStatus(StrEnum):
    RECEIVED = "received"
    NOT_PAID = "not_paid"
    ALREADY_PAID = "already_paid"


@dataclass(frozen=True)
class TransactionsFilter:
    username: str
    month: Optional[int]
    year: Optional[int]
    description: Optional[str]
    category: Optional[str]
    type_of_transaction: Optional[TypeOfTransaction]