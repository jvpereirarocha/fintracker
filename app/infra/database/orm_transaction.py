from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, Float, ForeignKey, Index, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    validates,
)

from app.domain.business_logic.validators import due_date_validator, status_validator
from app.domain.value_objects.transactions import TransactionStatus, TypeOfTransaction
from app.infra.database.base import mapped_registry as base_mapped_registry



@base_mapped_registry.mapped_as_dataclass
class Transaction:
    __tablename__ = "transactions"

    transaction_id: Mapped[int] = mapped_column(init=False, primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Float(asdecimal=True), nullable=False)
    type_of_transaction: Mapped[TypeOfTransaction] = mapped_column(String(20))
    status: Mapped[TransactionStatus] = mapped_column(String(20), default=TransactionStatus.ALREADY_PAID)
    registration_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    due_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.category_id"), nullable=True
    )

    @validates("due_date")
    def validate_due_date(self, key, value):
        return due_date_validator(
            registration_date=self.registration_date,
            type_of_transaction=self.type_of_transaction,
            due_date=self.due_date,
            value=value
        )
    
    @validates("status")
    def validate_status(self, key, value):
        return status_validator(
            type_of_transaction=self.type_of_transaction,

            value=value
        )

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
                type_of_transaction == TypeOfTransaction.EXPENSE.value
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
