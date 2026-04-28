from app.domain.value_objects.transactions import TransactionStatus, TypeOfTransaction


def get_expense_available_status() -> list[TransactionStatus]:
    expense_status = [
        status
        for status in TransactionStatus.__members__.values()
        if status != TransactionStatus.RECEIVED
    ]
    return expense_status


def status_validator(type_of_transaction, value):
    if (
        value
        and type_of_transaction == TypeOfTransaction.EXPENSE
        and value not in get_expense_available_status()
    ):
        raise ValueError("O status não é válido para despesas")

    elif (
        value
        and type_of_transaction == TypeOfTransaction.INCOME
        and value != TransactionStatus.RECEIVED
    ):
        raise ValueError("O status não é válido para receitas")

    return value


def due_date_validator(registration_date, type_of_transaction, due_date, value):
    if value and value < registration_date:
        raise ValueError("A data de vencimento deve ser maior que a data de registro")
    if type_of_transaction and type_of_transaction == TypeOfTransaction.EXPENSE and not value:
        raise ValueError("A data de vencimento deve ser informada para despesas")
    return value
