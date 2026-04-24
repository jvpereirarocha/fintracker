from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Optional


class TypeOfTransaction(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionStatus(StrEnum):
    RECEIVED = "received"
    NOT_PAID = "not_paid"
    PAYING = "paying"
    ALREADY_PAID = "already_paid"


EXPENSE_STATUS_OF_TRANSACTIONS = ["paying", "already_paid", "not_paid"]
INCOME_STATUS_OF_TRANSACTIONS = ["received"]

STATUS_OF_TRANSACTION = Literal["paying", "already_paid", "not_paid", "received"]


@dataclass(frozen=True)
class TransactionsFilter:
    username: str
    month: Optional[int]
    year: Optional[int]
    description: Optional[str]
    category: Optional[str]
    type_of_transaction: Optional[TypeOfTransaction]
    status_of_transaction: Optional[TransactionStatus]