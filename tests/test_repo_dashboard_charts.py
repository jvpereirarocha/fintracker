from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.domain.value_objects.dashboard import CategoryAmount, MonthlyTotals
from app.infra.repositories.transactions import AdapterTransactionRepo


def _session_returning(rows: list[SimpleNamespace]) -> MagicMock:
    session = MagicMock()
    session.execute.return_value.all.return_value = rows
    return session


def _executed_sql(session: MagicMock) -> str:
    statement = session.execute.call_args.args[0]
    return str(statement.compile(compile_kwargs={"literal_binds": True}))


# ------------------------------------------------------------ monthly totals


def test_monthly_totals_groups_the_users_year_by_month() -> None:
    session = _session_returning([])

    AdapterTransactionRepo(session=session).get_monthly_totals_by_year(user_id=7, year=2024)

    sql = _executed_sql(session)
    assert "transactions.user_id = 7" in sql
    assert "transactions.registration_date >= '2024-01-01'" in sql
    assert "transactions.registration_date <= '2024-12-31'" in sql
    assert "GROUP BY EXTRACT(month FROM transactions.registration_date)" in sql


def test_monthly_totals_maps_rows_rounding_float_sums_to_cents() -> None:
    session = _session_returning(
        [
            SimpleNamespace(month=Decimal("3"), total_income=5000.0, total_expense=1200.4999999),
            SimpleNamespace(month=Decimal("11"), total_income=None, total_expense=300.0),
        ]
    )

    result = AdapterTransactionRepo(session=session).get_monthly_totals_by_year(
        user_id=7, year=2024
    )

    assert result == [
        MonthlyTotals(month=3, income=Decimal("5000.00"), expense=Decimal("1200.50")),
        MonthlyTotals(month=11, income=Decimal("0.00"), expense=Decimal("300.00")),
    ]


# ------------------------------------------------------- expenses by category


def test_expenses_by_category_sums_only_expenses_of_the_interval_keeping_uncategorized() -> None:
    session = _session_returning([])

    AdapterTransactionRepo(session=session).get_expenses_by_category(
        user_id=7, start_date=date(2025, 3, 1), end_date=date(2025, 3, 31)
    )

    sql = _executed_sql(session)
    assert "LEFT OUTER JOIN category" in sql
    assert "transactions.type_of_transaction = 'expense'" in sql
    assert "transactions.user_id = 7" in sql
    assert "transactions.registration_date >= '2025-03-01'" in sql
    assert "transactions.registration_date <= '2025-03-31'" in sql
    assert "GROUP BY transactions.category_id, category.name" in sql


def test_expenses_by_category_maps_rows_with_null_category_as_none() -> None:
    session = _session_returning(
        [
            SimpleNamespace(category="Saúde", total=100.0),
            SimpleNamespace(category=None, total=49.999999),
        ]
    )

    result = AdapterTransactionRepo(session=session).get_expenses_by_category(
        user_id=7, start_date=date(2025, 3, 1), end_date=date(2025, 3, 31)
    )

    assert result == [
        CategoryAmount(category="Saúde", amount=Decimal("100.00")),
        CategoryAmount(category=None, amount=Decimal("50.00")),
    ]
