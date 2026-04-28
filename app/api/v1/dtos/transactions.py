from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.api.v1.dtos.pagination import Pagination
from app.domain.business_logic.conversor import (
    clean_brl_format_to_decimal,
    format_date_to_brazilian_date_text_format,
    format_decimal_to_brl_format,
    validate_date_format,
    validate_if_due_date_was_provided_for_expense,
    validate_transaction_status_by_type_of_transaction,
)
from app.domain.value_objects.transactions import STATUS_OF_TRANSACTION


class TransactionResponse(BaseModel):
    transaction_id: int = Field(alias="id")
    description: str
    value: Decimal = Field(alias="amount", default="")
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    transaction_status: STATUS_OF_TRANSACTION = Field(alias="status")
    registration_date: date = Field(alias="registrationDate")
    due_date: date | None = Field(alias="dueDate", default=None)
    category_id: int | None = Field(alias="categoryId", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_serializer("value")
    def serialize_value(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)

    @field_serializer("registration_date")
    def serialize_registration_date(self, date_reference: date) -> str:
        return format_date_to_brazilian_date_text_format(date_reference=date_reference)

    @field_serializer("due_date")
    def serialize_due_date(self, date_reference: date | None) -> str:
        if date_reference:
            return format_date_to_brazilian_date_text_format(date_reference=date_reference)

        return ""


class PaginatedTransactions(Pagination[TransactionResponse]):
    items: list[TransactionResponse] = Field(alias="transactions")


class SaveTransactionRequestDTO(BaseModel):
    description: str
    amount: Decimal
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    registration_date: datetime = Field(alias="registrationDate")
    due_date: datetime | None = Field(alias="dueDate", default=None)
    category: str = Field(alias="category")
    transaction_status: STATUS_OF_TRANSACTION = Field(alias="status")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, amount: str) -> Decimal:
        return clean_brl_format_to_decimal(amount=amount)

    @field_validator("registration_date", mode="before")
    @classmethod
    def validate_registration_date(cls, registration_date: str) -> date | None:
        return validate_date_format(date_reference=registration_date)

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, due_date: str = "") -> date | None:
        return validate_date_format(date_reference=due_date)

    @model_validator(mode="after")
    def validate_transaction_status(self) -> "SaveTransactionRequestDTO":
        validate_transaction_status_by_type_of_transaction(
            type_of_transaction=self.type_of_transaction, transaction_status=self.transaction_status
        )
        validate_if_due_date_was_provided_for_expense(
            type_of_transaction=self.type_of_transaction,
            due_date=self.due_date,
        )

        return self
