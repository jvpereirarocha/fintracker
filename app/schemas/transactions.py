from decimal import Decimal
import locale
from pydantic import BaseModel, Field
from app.config import Settings
from datetime import date, datetime


class TransactionResponse(BaseModel):
    description: str
    value: str = Field(alias="amount", default="")
    date: str = Field(alias="registration_date", default="")

    @classmethod
    def format_to_currency(cls, amount: Decimal) -> str:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
        currency_format = locale.currency(val=amount)
        return currency_format
    
    @classmethod
    def format_date(cls, date_reference: datetime) -> str:
        return datetime.strftime(date_reference, format="%d/%m/%Y")
    


class PaginatedTransactions(BaseModel):
    page: int | None
    prev: int | None
    next_page: int | None = Field(alias="next")
    items: list[TransactionResponse]