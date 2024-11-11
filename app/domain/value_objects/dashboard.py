from decimal import Decimal

from app.domain.entities.transactions import TransactionEntity


class FormatDashboardValues:
    @classmethod
    def from_decimal_to_brl(cls, amount: Decimal) -> str:
        return TransactionEntity.format_to_currency(amount)