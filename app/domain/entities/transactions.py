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
