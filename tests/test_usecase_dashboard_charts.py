import asyncio
from datetime import date
from decimal import Decimal

import pytest

from app.domain.exceptions.users import UserNotFoundException
from app.domain.value_objects.dashboard import CategoryAmount, MonthlyTotals
from app.usecases.dashboards.expenses_by_category import ExpensesByCategoryUseCase
from app.usecases.dashboards.monthly_summary import MonthlySummaryUseCase
from tests.fakes import FakeTransactionRepo, FakeUserRepo

# ---------------------------------------------------------------- monthly summary


def test_monthly_summary_always_returns_twelve_months_filling_gaps_with_zero() -> None:
    repo = FakeTransactionRepo(
        monthly_totals=[
            MonthlyTotals(month=3, income=Decimal("5000.00"), expense=Decimal("1200.50")),
            MonthlyTotals(month=11, income=Decimal("0"), expense=Decimal("300.00")),
        ]
    )
    use_case = MonthlySummaryUseCase(user_repo=FakeUserRepo(), transaction_repo=repo)

    result = asyncio.run(use_case.execute(username="me", year=2024))

    assert result.year == 2024
    assert [m.month for m in result.months] == list(range(1, 13))
    assert result.months[2] == MonthlyTotals(
        month=3, income=Decimal("5000.00"), expense=Decimal("1200.50")
    )
    assert result.months[10].expense == Decimal("300.00")
    assert result.months[0] == MonthlyTotals(month=1, income=Decimal(0), expense=Decimal(0))
    assert repo.calls == [{"user_id": 1, "year": 2024}]


def test_monthly_summary_defaults_to_current_year() -> None:
    use_case = MonthlySummaryUseCase(
        user_repo=FakeUserRepo(), transaction_repo=FakeTransactionRepo()
    )

    result = asyncio.run(use_case.execute(username="me"))

    assert result.year == date.today().year
    assert all(m.income == 0 and m.expense == 0 for m in result.months)


def test_monthly_summary_raises_when_user_does_not_exist() -> None:
    use_case = MonthlySummaryUseCase(
        user_repo=FakeUserRepo(user_id=None), transaction_repo=FakeTransactionRepo()
    )

    with pytest.raises(UserNotFoundException):
        asyncio.run(use_case.execute(username="ghost", year=2024))


# ---------------------------------------------------------- expenses by category


def test_expenses_by_category_queries_the_whole_month() -> None:
    repo = FakeTransactionRepo()
    use_case = ExpensesByCategoryUseCase(user_repo=FakeUserRepo(), transaction_repo=repo)

    asyncio.run(use_case.execute(username="me", month=2, year=2024))

    assert repo.calls == [
        {"user_id": 1, "start_date": date(2024, 2, 1), "end_date": date(2024, 2, 29)}
    ]


def test_expenses_by_category_computes_total_and_percentages_sorted_desc() -> None:
    repo = FakeTransactionRepo(
        category_amounts=[
            CategoryAmount(category="Saúde", amount=Decimal("100.00")),
            CategoryAmount(category="Cartão de crédito", amount=Decimal("300.00")),
            CategoryAmount(category="Essenciais", amount=Decimal("600.00")),
        ]
    )
    use_case = ExpensesByCategoryUseCase(user_repo=FakeUserRepo(), transaction_repo=repo)

    result = asyncio.run(use_case.execute(username="me", month=3, year=2025))

    assert (result.month, result.year) == (3, 2025)
    assert result.total == Decimal("1000.00")
    assert [(c.category, c.amount, c.percentage) for c in result.categories] == [
        ("Essenciais", Decimal("600.00"), Decimal("60.00")),
        ("Cartão de crédito", Decimal("300.00"), Decimal("30.00")),
        ("Saúde", Decimal("100.00"), Decimal("10.00")),
    ]


def test_expenses_by_category_percentages_always_sum_to_one_hundred() -> None:
    repo = FakeTransactionRepo(
        category_amounts=[
            CategoryAmount(category="A", amount=Decimal("1")),
            CategoryAmount(category="B", amount=Decimal("1")),
            CategoryAmount(category="C", amount=Decimal("1")),
        ]
    )
    use_case = ExpensesByCategoryUseCase(user_repo=FakeUserRepo(), transaction_repo=repo)

    result = asyncio.run(use_case.execute(username="me", month=3, year=2025))

    percentages = [c.percentage for c in result.categories]
    assert sum(percentages) == Decimal("100.00")
    assert sorted(percentages) == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]


def test_expenses_without_category_are_labeled_sem_categoria() -> None:
    repo = FakeTransactionRepo(
        category_amounts=[CategoryAmount(category=None, amount=Decimal("50.00"))]
    )
    use_case = ExpensesByCategoryUseCase(user_repo=FakeUserRepo(), transaction_repo=repo)

    result = asyncio.run(use_case.execute(username="me", month=3, year=2025))

    assert result.categories[0].category == "Sem categoria"
    assert result.categories[0].percentage == Decimal("100.00")


def test_expenses_by_category_empty_month_returns_no_categories_and_zero_total() -> None:
    use_case = ExpensesByCategoryUseCase(
        user_repo=FakeUserRepo(), transaction_repo=FakeTransactionRepo()
    )

    result = asyncio.run(use_case.execute(username="me", month=3, year=2025))

    assert result.total == Decimal(0)
    assert result.categories == []


def test_expenses_by_category_defaults_to_current_month_and_year() -> None:
    use_case = ExpensesByCategoryUseCase(
        user_repo=FakeUserRepo(), transaction_repo=FakeTransactionRepo()
    )

    result = asyncio.run(use_case.execute(username="me"))

    today = date.today()
    assert (result.month, result.year) == (today.month, today.year)


def test_expenses_by_category_raises_when_user_does_not_exist() -> None:
    use_case = ExpensesByCategoryUseCase(
        user_repo=FakeUserRepo(user_id=None), transaction_repo=FakeTransactionRepo()
    )

    with pytest.raises(UserNotFoundException):
        asyncio.run(use_case.execute(username="ghost", month=3, year=2025))
