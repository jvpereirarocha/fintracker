from datetime import date

import pytest

from app.domain.exceptions.transactions import TransactionNotFoundException
from app.domain.exceptions.users import UserNotFoundException
from app.usecases.transactions.list_transactions import (
    GetOneTransactionUseCase,
    ListTransactionsUseCase,
)
from tests.fakes import FakeTransactionRepo, FakeUserRepo, make_filters, make_transaction


@pytest.mark.anyio
async def test_list_transactions_raises_when_user_not_found() -> None:
    use_case = ListTransactionsUseCase(
        user_repo=FakeUserRepo(), transaction_repo=FakeTransactionRepo()
    )

    with pytest.raises(UserNotFoundException):
        await use_case.execute(filters=make_filters(username="ghost"), page=1, page_size=10)


@pytest.mark.anyio
async def test_list_transactions_returns_only_current_user_transactions() -> None:
    transaction_repo = FakeTransactionRepo(
        [
            make_transaction(transaction_id=1, user_id=1),
            make_transaction(transaction_id=2, user_id=2),
        ]
    )
    use_case = ListTransactionsUseCase(
        user_repo=FakeUserRepo({"john": 1}), transaction_repo=transaction_repo
    )

    result = await use_case.execute(filters=make_filters(username="john"), page=1, page_size=10)

    assert [t.transaction_id for t in result.items] == [1]
    assert result.total_count == 1


@pytest.mark.anyio
async def test_list_transactions_builds_pagination_metadata() -> None:
    transaction_repo = FakeTransactionRepo(
        [
            make_transaction(transaction_id=1, registration_date=date(2025, 1, 1)),
            make_transaction(transaction_id=2, registration_date=date(2025, 2, 1)),
            make_transaction(transaction_id=3, registration_date=date(2025, 3, 1)),
        ]
    )
    use_case = ListTransactionsUseCase(
        user_repo=FakeUserRepo({"john": 1}), transaction_repo=transaction_repo
    )

    result = await use_case.execute(filters=make_filters(), page=2, page_size=2)

    assert [t.transaction_id for t in result.items] == [1]
    assert result.total_count == 3
    assert result.total_of_pages == 2
    assert result.prev == 1
    assert result.next_page is None


@pytest.mark.anyio
async def test_list_transactions_forwards_filters_to_repository() -> None:
    transaction_repo = FakeTransactionRepo()
    use_case = ListTransactionsUseCase(
        user_repo=FakeUserRepo({"john": 1}), transaction_repo=transaction_repo
    )
    filters = make_filters(month=11, year=2025, description="mercado")

    await use_case.execute(filters=filters, page=1, page_size=10)

    assert transaction_repo.last_filters == filters


@pytest.mark.anyio
async def test_get_one_transaction_raises_when_transaction_not_found() -> None:
    use_case = GetOneTransactionUseCase(
        user_repo=FakeUserRepo({"john": 1}), transaction_repo=FakeTransactionRepo()
    )

    with pytest.raises(TransactionNotFoundException):
        await use_case.execute(transaction_id=99, username="john")


@pytest.mark.anyio
async def test_get_one_transaction_returns_entity() -> None:
    transaction = make_transaction(transaction_id=7)
    use_case = GetOneTransactionUseCase(
        user_repo=FakeUserRepo({"john": 1}),
        transaction_repo=FakeTransactionRepo([transaction]),
    )

    result = await use_case.execute(transaction_id=7, username="john")

    assert result == transaction
