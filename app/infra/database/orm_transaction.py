from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, Float, ForeignKey, Index, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    validates,
)

from app.infra.database.base import mapped_registry as base_mapped_registry


class TypeTransaction(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@base_mapped_registry.mapped_as_dataclass
class Transaction:
    __tablename__ = "transactions"

    transaction_id: Mapped[int] = mapped_column(init=False, primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Float(asdecimal=True), nullable=False)
    type_of_transaction: Mapped[TypeTransaction] = mapped_column(String(20))
    registration_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    due_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.category_id"), nullable=True
    )

    @validates("due_date")
    def validate_due_date(self, key, value):
        if value and value < self.registration_date:
            raise ValueError(
                "A data de vencimento deve ser maior que a data de registro"
            )
        if (
            self.type_of_transaction
            and self.type_of_transaction == TypeTransaction.EXPENSE
            and not self.due_date
        ):
            raise ValueError("A data de vencimento deve ser informada para despesas")
        return value

    __table_args__ = (
        Index("desc_amount_idx", "description", "amount"),
        Index("desc_amount_userid_idx", "description", "amount", "user_id"),
        Index("amount_type_of_transaction_idx", "amount", "type_of_transaction"),
        Index(
            "type_of_transaction_date_idx", "type_of_transaction", "registration_date"
        ),
        Index(
            "description_expense_due_date_idx",
            "description",
            "type_of_transaction",
            "due_date",
            postgresql_where=(
                type_of_transaction == TypeTransaction.EXPENSE.value
                and due_date != None
            ),
            unique=True,
        ),
        Index(
            "description_amount_type_category_idx",
            "description",
            "amount",
            "type_of_transaction",
            "category_id",
            postgresql_where=(category_id != None),
        ),
    )
