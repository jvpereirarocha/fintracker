from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TransactionResponse(BaseModel):
    transaction_id: int = Field(alias="id")
    description: str
    value: Decimal = Field(alias="amount", default="")
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    registration_date: date = Field(alias="registrationDate")
    due_date: Optional[date] = Field(alias="dueDate", default=None)
    category_id: Optional[int] = Field(alias="categoryId", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def format_date(self, date_reference: date) -> str:
        brazilian_date_format = "%d/%m/%Y"
        return date_reference.strftime(brazilian_date_format)

    @field_serializer("value")
    def serialize_value(self, amount: Decimal) -> str:
        formatted = f"{amount:,.2f}"
        return f"R$ {formatted.replace(',', 'v').replace('.', ',').replace('v', '.')}"

    @field_serializer("registration_date")
    def serialize_registration_date(self, date_reference: date) -> str:
        return self.format_date(date_reference=date_reference)

    @field_serializer("due_date")
    def serialize_due_date(self, date_reference: date | None) -> str:
        if date_reference:
            return self.format_date(date_reference=date_reference)
        
        return ""


class PaginatedTransactions(BaseModel):
    items: list[TransactionResponse] = Field(alias="transactions")
    page: int
    total_count: int = Field(alias="totalItems")
    total_of_pages: int = Field(alias="totalOfPages")
    items_per_page: int = Field(alias="itemsPerPage")
    prev: int | None
    next_page: int | None = Field(alias="next")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )