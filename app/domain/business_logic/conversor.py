import re
from datetime import date, datetime
from decimal import Decimal

from app.domain.exceptions.transactions import (
    DueDateNotProvidedException,
    InvalidFormatCurrencyException,
    InvalidFormatDateException,
    InvalidTransactionStatusException,
)
from app.domain.value_objects.transactions import (
    EXPENSE_STATUS_OF_TRANSACTIONS,
    INCOME_STATUS_OF_TRANSACTIONS,
)

REGEX_BRL_FORMAT = re.compile(r"^R\$\s?\d{1,3}(\.\d{3})*,\d{2}$")


def format_date_to_brazilian_date_text_format(date_reference: date) -> str:
    brazilian_date_format = "%d/%m/%Y"
    return date_reference.strftime(brazilian_date_format)


def format_decimal_to_brl_format(amount: Decimal) -> str:
    formatted = f"{amount:,.2f}"
    return f"R$ {formatted.replace(',', 'v').replace('.', ',').replace('v', '.')}"


def clean_brl_format_to_decimal(amount: str) -> Decimal:
    if not REGEX_BRL_FORMAT.match(amount):
        raise InvalidFormatCurrencyException(
            message="Formato incorreto para o valor. Deve ter o formato R$ 1.000,00"
        )

    clean_value = re.sub(r"[R$\s.]", "", amount).replace(",", ".")
    return Decimal(clean_value)


def validate_date_format(date_reference: str) -> datetime | None:
    expected_format = "%d/%m/%Y"
    try:
        if not date_reference:
            return None
        converted_date_reference = datetime.strptime(date_reference, expected_format)
        return converted_date_reference
    except ValueError:
        raise InvalidFormatDateException(
            message="Formato incorreto para a data. Deve ter o formato DD/MM/YYYY. Exemplo: 13/11/2025"
        )


def validate_transaction_status_by_type_of_transaction(
    type_of_transaction: str, transaction_status: str
) -> None:
    if type_of_transaction == "income" and transaction_status not in INCOME_STATUS_OF_TRANSACTIONS:
        raise InvalidTransactionStatusException(message="O status não é válido para receitas")
    elif (
        type_of_transaction == "expense"
        and transaction_status not in EXPENSE_STATUS_OF_TRANSACTIONS
    ):
        raise InvalidTransactionStatusException(message="O status não é válido para despesas")

    return None


def validate_if_due_date_was_provided_for_expense(
    type_of_transaction: str,
    due_date: datetime | None = None,
) -> None:
    if type_of_transaction == "expense" and due_date is None:
        raise DueDateNotProvidedException(
            message="A data de vencimento deve ser informada para despesas"
        )

    return None
