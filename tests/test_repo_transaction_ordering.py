from unittest.mock import MagicMock

import pytest

from app.domain.value_objects.transactions import TransactionsFilter, TransactionsOrder
from app.infra.repositories.transactions import AdapterTransactionRepo


def _listing_order_by(order_by: TransactionsOrder) -> str:
    """Runs fetch_all against a fake session and returns the ORDER BY of the listing query"""
    session = MagicMock()
    session.execute.return_value.scalar.return_value = 0
    session.execute.return_value.scalars.return_value.all.return_value = []
    filters = TransactionsFilter(
        username="me",
        month=None,
        year=None,
        description=None,
        category=None,
        type_of_transaction=None,
        status_of_transaction=None,
        order_by=order_by,
    )

    AdapterTransactionRepo(session=session).fetch_all(
        user_id=1, filters=filters, page=1, page_size=10
    )

    listing_query = session.execute.call_args_list[-1].kwargs["statement"]
    sql = str(listing_query.compile())
    return sql.split("ORDER BY", 1)[1].split("LIMIT", 1)[0].strip()


@pytest.mark.parametrize(
    "order_by, expected",
    [
        (
            TransactionsOrder.REGISTRATION_DATE,
            "transactions.registration_date DESC, transactions.transaction_id DESC",
        ),
        (TransactionsOrder.ID, "transactions.transaction_id DESC"),
    ],
)
def test_fetch_all_orders_newest_first_with_id_as_tiebreaker(order_by, expected):
    assert _listing_order_by(order_by) == expected


def test_filter_defaults_to_registration_date_order():
    filters = TransactionsFilter(
        username="me",
        month=None,
        year=None,
        description=None,
        category=None,
        type_of_transaction=None,
        status_of_transaction=None,
    )

    assert filters.order_by == TransactionsOrder.REGISTRATION_DATE
