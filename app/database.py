from datetime import datetime
from decimal import Decimal
from enum import Enum
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    registry,
    Mapped,
    mapped_column,
    sessionmaker,
    relationship
)
from app.config import Settings


mapped_registry = registry()


@mapped_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, onupdate=func.now())

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")

    __table_args__ = (
        Index('user_email_pass_idx', 'username', 'email', 'password'),
        Index('email_pass_idx', 'email', 'password'),
        Index('user_pass_idx', 'username', 'password'),
        Index('user_created_at_idx', 'username', 'created_at'),
        Index('email_created_at_idx', 'email', 'created_at'),
        Index('user_updated_at_idx', 'username', 'updated_at'),
        Index('email_updated_at_idx', 'email', 'updated_at'),
    )


class TypeTransaction(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@mapped_registry.mapped_as_dataclass
class Transaction:
    __tablename__ = 'transactions'
    
    transaction_id: Mapped[int] = mapped_column(init=False, primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Float(asdecimal=True), nullable=False)
    type_of_transaction: Mapped[TypeTransaction] = mapped_column(
        String(20)
    )
    registration_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    user: Mapped["User"] = relationship(back_populates="transactions")

    __table_args__ = (
        Index('desc_amount_idx', 'description', 'amount'),
        Index('desc_amount_userid_idx', 'description', 'amount', 'user_id'),
        Index('amount_type_of_transaction_idx', 'amount', 'type_of_transaction'),
        Index('type_of_transaction_date_idx', 'type_of_transaction', 'registration_date'),
    )


engine = sqlalchemy.create_engine(
    url=Settings().DATABASE_URL
)

Session = sessionmaker(engine)
