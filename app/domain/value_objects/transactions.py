from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class TypeOfTransaction(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass(frozen=True)
class TransactionsFilter:
    username: str
    month: Optional[int]
    year: Optional[int]
    description: Optional[str]
    category: Optional[str]
    type_of_transaction: Optional[TypeOfTransaction]