from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import locale
import re

from app.domain.value_objects.transactions import TypeOfTransaction


@dataclass()
class TransactionEntity:
    transaction_id: int
    description: str
    amount: Decimal
    type_of_transaction: TypeOfTransaction
    registration_date: date
    user_id: int

    @classmethod
    def brl_to_decimal(cls, brl_string: str) -> Decimal:
        # Remove the "R$" symbol and any spaces, then replace the comma with a dot
        sanitized_str = re.sub(r"[^\d,]", "", brl_string).replace(",", ".")
        return Decimal(sanitized_str)

    @classmethod
    def format_to_currency(cls, amount: Decimal) -> str:
        locale.setlocale(locale.LC_ALL, "pt_BR.utf-8")
        currency_format = locale.currency(val=amount)
        return currency_format

    @classmethod
    def date_to_string(cls, date_reference: date | None = None) -> str:
        if date_reference:
            return datetime.strftime(date_reference, format="%d/%m/%Y")
        return ""
