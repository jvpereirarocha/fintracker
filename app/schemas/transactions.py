from decimal import Decimal
import locale
from typing import Literal

from pydantic import BaseModel, Field
from app.config import Settings
from datetime import date, datetime


class TransactionResponse(BaseModel):
    description: str
    value: str = Field(alias="amount", default="")
    date: str = Field(alias="registration_date", default="")

    @classmethod
    def format_to_currency(cls, amount: Decimal) -> str:
        locale.setlocale(locale.LC_ALL, "pt_BR.utf-8")
        currency_format = locale.currency(val=amount)
        return currency_format

    @classmethod
    def format_date(cls, date_reference: datetime | date) -> str:
        return datetime.strftime(date_reference, format="%d/%m/%Y")


class PaginatedTransactions(BaseModel):
    total_of_pages: int = Field("totalOfPages")
    items_per_page: int = Field("itemsPerPage")
    page: int | None
    prev: int | None
    next_page: int | None = Field(alias="next")
    items: list[TransactionResponse]


class PersistTransaction(BaseModel):
    description: str
    amount: Decimal
    type_of_transaction: Literal["income", "expense"]
    registration_date: date = Field(alias="registrationDate")


class NonRequiredPersistTransaction(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    type_of_transaction: Literal["income", "expense"] | None = None
    registration_date: date | None = Field(alias="registrationDate", default=None)


class DeletedTransaction(BaseModel):
    message: str
