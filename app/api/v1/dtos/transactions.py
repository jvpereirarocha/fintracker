from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.api.v1.dtos.pagination import Pagination
from app.domain.value_objects.currency import clean_brl_format_to_decimal


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


class PaginatedTransactions(Pagination[TransactionResponse]):
    items: list[TransactionResponse] = Field(alias="transactions")


class SaveTransactionRequestDTO(BaseModel):
    description: str
    amount: Decimal
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    registration_date: datetime = Field(alias="registrationDate")
    due_date: Optional[datetime] = Field(alias="dueDate", default=None)
    category: str = Field(alias="category")

    @classmethod
    def _validate_date_format(cls, date_reference: Optional[str]) -> Optional[datetime]:
        expected_format = "%d/%m/%Y"
        try:
            if not date_reference:
                return None
            converted_date_reference = datetime.strptime(date_reference, expected_format)
            return converted_date_reference
        except ValueError:
            raise ValueError(
                f"Formato incorreto para a data. Deve ter o formato DD/MM/YYYY. Exemplo: 13/11/2025"
            )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, amount: str) -> Decimal:
        return clean_brl_format_to_decimal(amount=amount)

    @field_validator("registration_date", mode="before")
    @classmethod
    def validate_registration_date(cls, registration_date: str) -> Optional[date]:
        return cls._validate_date_format(date_reference=registration_date)

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, due_date: str = "") -> Optional[date]:
        return cls._validate_date_format(date_reference=due_date)