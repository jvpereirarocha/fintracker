from datetime import date, datetime
from decimal import Decimal
import locale
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TransactionResponse(BaseModel):
    transaction_id: int = Field(alias="id")
    description: str
    value: Decimal = Field(alias="amount", default="")
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    registration_date: date = Field(alias="registrationDate", default="")
    due_date: date = Field(alias="dueDate", default="")
    category_id: Optional[int] = Field(alias="categoryId", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    @field_serializer("value")
    def serialize_value(cls, amount: Decimal) -> str:
        locale.setlocale(locale.LC_ALL, "pt_BR.utf-8")
        currency_format = locale.currency(val=amount)
        return currency_format

    @classmethod
    @field_serializer("registration_date")
    def serialize_registration_date(cls, date_reference: datetime | date) -> str:
        return datetime.strftime(date_reference, format="%d/%m/%Y")

    @classmethod
    @field_serializer("due_date")
    def serialize_due_date(cls, date_reference: datetime | date | None = None) -> str:
        if date_reference:
            return datetime.strftime(date_reference, format="%d/%m/%Y")
        return ""


class PaginatedTransactions(BaseModel):
    total_of_pages: int = Field(alias="totalOfPages")
    items_per_page: int = Field(alias="itemsPerPage")
    page: int | None
    prev: int | None
    next_page: int | None = Field(alias="next")
    items: list[TransactionResponse]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )