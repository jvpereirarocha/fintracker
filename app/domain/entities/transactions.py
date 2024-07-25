from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal, Self


class TypeTransaction(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class TransactionEntity:
    transaction_id: int = field(init=False)
    description: str
    amount: Decimal
    type_of_transaction: TypeTransaction
    registration_date: datetime
    user_id: int

    def _validate_amount(value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("O valor não pode ser menor que zero")
        
        return value


    @classmethod
    def new_transaction(
        cls,
        description: str,
        amount: Decimal,
        type_of_transaction: Literal["income", "expense"],
        user_id: int
    ) -> Self:
        
        return cls(
            description=description,
            amount=cls._validate_amount(value=amount),
            type_of_transaction=type_of_transaction,
            registration_date=datetime.now(),
            user_id=user_id
        )