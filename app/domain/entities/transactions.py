import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal, Self


class TypeTransaction(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass()
class TransactionEntity:
    transaction_id: int = field(init=False)
    description: str
    amount: Decimal
    type_of_transaction: TypeTransaction
    registration_date: datetime
    user_id: int

    @classmethod
    def validate_amount(cls, amount: Decimal) -> Decimal:
        if amount < 0:
            raise ValueError("O valor não pode ser menor que zero")

        return amount

    @classmethod
    def new_transaction(
        cls,
        description: str,
        amount: Decimal,
        type_of_transaction: Literal["income", "expense"],
        user_id: int,
    ) -> Self:

        return cls(
            description=description,
            amount=cls.validate_amount(amount=amount),
            type_of_transaction=(
                TypeTransaction.EXPENSE
                if type_of_transaction == "expense"
                else TypeTransaction.INCOME
            ),
            registration_date=datetime.now(),
            user_id=user_id,
        )

    @classmethod
    def brl_to_decimal(cls, brl_string: str) -> Decimal:
        # Remove the "R$" symbol and any spaces, then replace the comma with a dot
        sanitized_str = re.sub(r"[^\d,]", "", brl_string).replace(",", ".")
        return Decimal(sanitized_str)

    @classmethod
    def string_date_to_datetime(cls, string_date: str) -> datetime:
        return datetime.strptime(string_date, "%d/%m/%Y")
