from app.domain.exceptions.base import BaseDomainException, ExceptionType


class TransactionNotFoundException(BaseDomainException):
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(
            message=message,
            name="TransactionNotFound",
            type=ExceptionType.NOT_FOUND
        )


class TransactionAlreadyExistsException(BaseDomainException):
    def __init__(self, message: str = "Transaction already exists"):
        super().__init__(
            message=message,
            name="TransactionAlreadyExists",
            type=ExceptionType.BAD_REQUEST
        )