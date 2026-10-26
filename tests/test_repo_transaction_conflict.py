from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.api.handlers import get_status_code_by_exception_type
from app.domain.entities.transactions import SaveTransaction
from app.domain.exceptions.base import ExceptionType
from app.domain.exceptions.transactions import TransactionAlreadyExistsException
from app.infra.repositories.transactions import AdapterTransactionRepo


def _new_expense() -> SaveTransaction:
    return SaveTransaction(
        description="Lanche",
        amount=Decimal("20.00"),
        type_of_transaction="expense",
        transaction_status="already_paid",
        registration_date=datetime(2026, 10, 26),
        due_date=datetime(2026, 10, 26),
        category="Alimentação",
    )


def test_save_raises_conflict_and_rolls_back_on_integrity_error():
    session = MagicMock()
    session.commit.side_effect = IntegrityError("INSERT ...", params=None, orig=Exception())
    repo = AdapterTransactionRepo(session=session)

    with pytest.raises(TransactionAlreadyExistsException) as exc_info:
        repo.save(new_transaction=_new_expense(), user_id=1, category_id=1)

    assert exc_info.value.type == ExceptionType.CONFLICT
    session.rollback.assert_called_once()
    session.refresh.assert_not_called()


def test_conflict_exception_type_maps_to_http_409():
    assert get_status_code_by_exception_type(exception_type=ExceptionType.CONFLICT) == 409
