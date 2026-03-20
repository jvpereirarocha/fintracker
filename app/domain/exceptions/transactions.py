from app.domain.exceptions.base import BaseDomainException, ExceptionType


class TransactionNotFoundException(BaseDomainException):
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(
            message=message,
            name="TransactionNotFound",
            type=ExceptionType.NOT_FOUND
        )