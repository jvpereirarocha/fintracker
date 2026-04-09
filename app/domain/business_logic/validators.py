from app.domain.value_objects.transactions import TransactionStatus, TypeOfTransaction


def status_validator(type_of_transaction, value):
    if (
        value
        and type_of_transaction == TypeOfTransaction.EXPENSE
        and value not in [TransactionStatus.NOT_PAID, TransactionStatus.ALREADY_PAID]
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
        raise ValueError(
            "A data de vencimento deve ser maior que a data de registro"
        )
    if (
        type_of_transaction
        and type_of_transaction == TypeOfTransaction.EXPENSE
        and not due_date
    ):
        raise ValueError("A data de vencimento deve ser informada para despesas")
    return value