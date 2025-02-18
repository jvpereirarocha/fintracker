from datetime import datetime
from decimal import Decimal
from enum import Enum
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    registry,
    Mapped,
    mapped_column,
    sessionmaker,
    relationship,
    validates,
)
from sqlalchemy.sql.sqltypes import LargeBinary
from app.config import Settings


mapped_registry = registry()


@mapped_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(60))
    password_salt: Mapped[bytes] = mapped_column(LargeBinary(29))
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")

    __table_args__ = (
        Index(
            "user_email_pass_idx", "username", "email", "password_hash", "password_salt"
        ),
        Index("email_pass_idx", "email", "password_hash", "password_salt"),
        Index("user_pass_idx", "username", "password_hash", "password_salt"),
        Index("user_created_at_idx", "username", "created_at"),
        Index("email_created_at_idx", "email", "created_at"),
        Index("user_updated_at_idx", "username", "updated_at"),
        Index("email_updated_at_idx", "email", "updated_at"),
    )


class TypeTransaction(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@mapped_registry.mapped_as_dataclass
class Transaction:
    __tablename__ = "transactions"

    transaction_id: Mapped[int] = mapped_column(init=False, primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Float(asdecimal=True), nullable=False)
    type_of_transaction: Mapped[TypeTransaction] = mapped_column(String(20))
    registration_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    due_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.category_id"), nullable=True)

    user: Mapped["User"] = relationship(back_populates="transactions")

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
    )


@mapped_registry.mapped_as_dataclass
class Category:
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    __table_args__ = (
        Index("category_id_name_idx", "category_id", "name"),
        Index("category_id_description_idx", "category_id", "description"),
        Index("category_id_created_at_idx", "category_id", "created_at"),
        Index("category_id_updated_at_idx", "category_id", "updated_at"),
        Index("name_description_idx", "name", "description"),
        Index("category_id_name_description_idx", "category_id", "name", "description"),
        Index(
            "category_id_name_description_created_at_idx",
            "category_id",
            "name",
            "description",
            "created_at",
        ),
        Index(
            "category_id_name_description_created_at_updated_at_idx",
            "category_id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ),
    )


engine = sqlalchemy.create_engine(url=Settings().DATABASE_URL)  # type: ignore

Session = sessionmaker(engine)
