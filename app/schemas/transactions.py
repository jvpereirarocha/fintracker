from decimal import Decimal
import locale
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime

from app.domain.value_objects.currency import REGEX_BRL_FORMAT


class TransactionResponse(BaseModel):
    transaction_id: int = Field(alias="id")
    description: str
    value: str = Field(alias="amount", default="")
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    registration_date: str = Field(alias="registrationDate", default="")
    due_date: str = Field(alias="dueDate", default="")
    category_id: Optional[int] = Field(alias="categoryId", default=None)

    @classmethod
    def format_to_currency(cls, amount: Decimal) -> str:
        locale.setlocale(locale.LC_ALL, "pt_BR.utf-8")
        currency_format = locale.currency(val=amount)
        return currency_format

    @classmethod
    def format_registration_date(cls, date_reference: datetime | date) -> str:
        return datetime.strftime(date_reference, format="%d/%m/%Y")

    @classmethod
    def format_due_date(cls, date_reference: datetime | date | None = None) -> str:
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


class PersistTransaction(BaseModel):
    description: str
    amount: str
    type_of_transaction: Literal["income", "expense"] = Field(alias="typeOfTransaction")
    registration_date: str = Field(alias="registrationDate")
    due_date: str = Field(alias="dueDate", default="")
    category: str = Field(alias="category")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, amount: str) -> str:
        if not REGEX_BRL_FORMAT.match(amount):
            raise ValueError(
                "Formato incorreto para o valor. Deve ter o formato R$ 1.000,00"
            )

        return amount

    @field_validator("registration_date")
    @classmethod
    def validate_registration_date(cls, registration_date: str) -> str:
        expected_format = "%d/%m/%Y"
        try:
            datetime.strptime(registration_date, expected_format)
            return registration_date
        except ValueError:
            raise ValueError(
                f"Formato incorreto para a data. Deve ter o formato DD/MM/YYYY. Exemplo: 10/11/2024"
            )

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, due_date: str = "") -> str:
        expected_format = "%d/%m/%Y"
        try:
            if due_date:
                datetime.strptime(due_date, expected_format)
            return due_date
        except ValueError:
            raise ValueError(
                f"Formato incorreto para a data. Deve ter o formato DD/MM/YYYY. Exemplo: 10/11/2024"
            )


class NonRequiredPersistTransaction(BaseModel):
    description: str | None = None
    amount: str | None = None
    type_of_transaction: Literal["income", "expense"] | None = Field(
        alias="typeOfTransaction", default=None
    )
    registration_date: str | None = Field(alias="registrationDate", default=None)
    due_date: str | None = Field(alias="dueDate", default=None)
    category: str | None = Field(alias="category", default=None)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, amount: str) -> str:
        if amount and not REGEX_BRL_FORMAT.match(amount):
            raise ValueError(
                "Formato incorreto para o valor. Deve ter o formato R$ 1.000,00"
            )

        return amount

    @field_validator("registration_date")
    @classmethod
    def validate_registration_date(cls, registration_date: str) -> str:
        expected_format = "%d/%m/%Y"
        if registration_date:
            try:
                datetime.strptime(registration_date, expected_format)
                return registration_date
            except ValueError:
                raise ValueError(
                    f"Formato incorreto para a data. Deve ter o formato DD/MM/YYYY. Exemplo: 10/11/2024"
                )

        return registration_date

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, due_date: str = "") -> str:
        expected_format = "%d/%m/%Y"
        try:
            if due_date:
                datetime.strptime(due_date, expected_format)
            return due_date
        except ValueError:
            raise ValueError(
                f"Formato incorreto para a data. Deve ter o formato DD/MM/YYYY. Exemplo: 10/11/2024"
            )
