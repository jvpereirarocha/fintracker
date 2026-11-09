import calendar
from collections.abc import Sequence
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import case, extract, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.abstractions.repositories import AbstractTransactionRepository
from app.domain.entities.transactions import SaveTransaction, TransactionEntity
from app.domain.exceptions.transactions import TransactionAlreadyExistsException
from app.domain.value_objects.dashboard import CategoryAmount, DashboardValues, MonthlyTotals
from app.domain.value_objects.transactions import (
    TransactionsFilter,
    TransactionsOrder,
    TypeOfTransaction,
)
from app.infra.database.orm_category import Category
from app.infra.database.orm_transaction import Transaction


class AdapterTransactionRepo(AbstractTransactionRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def _get_transaction_by_id(self, transaction_id: int) -> Transaction:
        """
        It doesn't check if the transaction exists

        We must handle it in the use case level

        :param transaction_id: int
        :return: Transaction
        """
        query = select(Transaction).where(Transaction.transaction_id == transaction_id)
        result = self.session.execute(statement=query)
        transaction_dao = result.scalar_one()
        return transaction_dao

    def _commit(self) -> None:
        """
        Commits the session, translating unique constraint violations
        (description_expense_due_date_idx) into a domain exception
        """
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise TransactionAlreadyExistsException(
                message="Já existe uma despesa com essa descrição e data de vencimento"
            ) from exc

    def exists(self, transaction_id: int) -> bool:
        query = select(Transaction).where(Transaction.transaction_id == transaction_id)
        result = self.session.execute(statement=query)
        return bool(result.scalar_one_or_none())

    def fetch_one(self, transaction_id: int) -> TransactionEntity:
        transaction = self._get_transaction_by_id(transaction_id=transaction_id)
        return TransactionEntity(
            transaction_id=transaction.transaction_id,
            description=transaction.description,
            amount=transaction.amount,
            type_of_transaction=transaction.type_of_transaction,  # type: ignore
            transaction_status=transaction.status,  # type: ignore
            registration_date=transaction.registration_date,
            due_date=transaction.due_date,
            user_id=transaction.user_id,
            category_id=transaction.category_id,
        )

    def fetch_all(
        self,
        user_id: int,
        filters: TransactionsFilter,
        page: int,
        page_size: int,
    ) -> tuple[list[TransactionEntity], int]:
        query = select(Transaction).where(Transaction.user_id == user_id)
        if filters.month and filters.year:
            last_day = calendar.monthrange(filters.year, filters.month)[1]
            query = query.where(
                Transaction.registration_date >= date(filters.year, filters.month, 1)
            ).where(Transaction.registration_date <= date(filters.year, filters.month, last_day))
        elif filters.year:
            query = query.where(Transaction.registration_date >= date(filters.year, 1, 1)).where(
                Transaction.registration_date <= date(filters.year, 12, 31)
            )
        elif filters.month:
            query = query.where(extract("month", Transaction.registration_date) == filters.month)

        if filters.description:
            query = query.where(Transaction.description.ilike(f"%{filters.description}%"))
        if filters.type_of_transaction and filters.type_of_transaction == TypeOfTransaction.INCOME:
            query = query.where(Transaction.type_of_transaction == TypeOfTransaction.INCOME.value)
        elif (
            filters.type_of_transaction and filters.type_of_transaction == TypeOfTransaction.EXPENSE
        ):
            query = query.where(Transaction.type_of_transaction == TypeOfTransaction.EXPENSE.value)

        if filters.category:
            query = query.join(Category, Transaction.category_id == Category.category_id).where(
                func.lower(Category.name) == filters.category.lower()
            )

        if filters.status_of_transaction:
            query = query.where(Transaction.status == filters.status_of_transaction)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.session.execute(statement=count_query)
        total_count = total_result.scalar() or 0

        offset = (page - 1) * page_size
        # transaction_id breaks ties, otherwise rows sharing a date could repeat or be skipped
        # across pages
        if filters.order_by == TransactionsOrder.ID:
            query = query.order_by(Transaction.transaction_id.desc())
        else:
            query = query.order_by(
                Transaction.registration_date.desc(), Transaction.transaction_id.desc()
            )
        query = query.limit(page_size).offset(offset)

        result = self.session.execute(statement=query)
        transactions: Sequence[Transaction] = result.scalars().all()
        transaction_entities = [
            TransactionEntity(
                transaction_id=transaction.transaction_id,
                description=transaction.description,
                amount=transaction.amount,
                type_of_transaction=transaction.type_of_transaction,  # type: ignore
                transaction_status=transaction.status,
                registration_date=transaction.registration_date,
                due_date=transaction.due_date,
                user_id=transaction.user_id,
                category_id=transaction.category_id,
            )
            for transaction in transactions
        ]
        return transaction_entities, total_count

    def update(
        self,
        transaction_id: int,
        edit_transaction: SaveTransaction,
        category_id: int,
    ) -> TransactionEntity:
        transaction_dao = self._get_transaction_by_id(transaction_id=transaction_id)
        transaction_dao.description = edit_transaction.description
        transaction_dao.amount = edit_transaction.amount
        transaction_dao.type_of_transaction = edit_transaction.type_of_transaction  # type: ignore
        transaction_dao.status = edit_transaction.transaction_status  # type: ignore
        transaction_dao.registration_date = edit_transaction.registration_date
        transaction_dao.due_date = edit_transaction.due_date  # type: ignore
        transaction_dao.category_id = category_id

        self._commit()
        self.session.refresh(transaction_dao)
        return TransactionEntity(
            transaction_id=transaction_dao.transaction_id,
            description=transaction_dao.description,
            amount=transaction_dao.amount,
            type_of_transaction=transaction_dao.type_of_transaction,  # type: ignore
            transaction_status=transaction_dao.status,  # type: ignore
            registration_date=transaction_dao.registration_date,
            due_date=transaction_dao.due_date,  # type: ignore
            user_id=transaction_dao.user_id,
            category_id=transaction_dao.category_id,
        )

    def save(
        self, new_transaction: SaveTransaction, user_id: int, category_id: int
    ) -> TransactionEntity:
        transaction_dao = Transaction(
            description=new_transaction.description,
            amount=new_transaction.amount,
            type_of_transaction=new_transaction.type_of_transaction,  # type: ignore
            registration_date=new_transaction.registration_date,
            status=new_transaction.transaction_status,  # type: ignore
            due_date=new_transaction.due_date,  # type: ignore
            user_id=user_id,
            category_id=category_id,
        )
        self.session.add(transaction_dao)
        self._commit()
        self.session.refresh(transaction_dao)

        return TransactionEntity(
            transaction_id=transaction_dao.transaction_id,
            description=transaction_dao.description,
            amount=transaction_dao.amount,
            type_of_transaction=transaction_dao.type_of_transaction,  # type: ignore
            transaction_status=transaction_dao.status,  # type: ignore
            registration_date=transaction_dao.registration_date,
            due_date=transaction_dao.due_date,  # type: ignore
            user_id=transaction_dao.user_id,
            category_id=transaction_dao.category_id,
        )

    def delete(self, transaction_id: int) -> None:
        transaction = self._get_transaction_by_id(transaction_id=transaction_id)
        self.session.delete(transaction)
        self.session.commit()
        return None

    def get_sum_of_transactions_by_interval(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> DashboardValues:
        result = self.session.execute(
            select(
                func.sum(
                    case(
                        (
                            Transaction.type_of_transaction == "expense",
                            Transaction.amount,
                        )  # type: ignore
                    )
                ).label("total_expense"),
                func.sum(
                    case(
                        (
                            Transaction.type_of_transaction == "income",
                            Transaction.amount,
                        )  # type: ignore
                    )
                ).label("total_income"),
            ).where(
                (Transaction.user_id == user_id)
                & (Transaction.registration_date >= start_date)
                & (Transaction.registration_date <= end_date)
            )
        ).first()

        total_expense: Decimal = (
            result.total_expense if result and result.total_expense else Decimal(0)
        )
        total_income: Decimal = (
            result.total_income if result and result.total_income else Decimal(0)
        )

        return DashboardValues(
            total_expense=total_expense,
            total_income=total_income,
        )

    @staticmethod
    def _to_cents(value: Decimal | float | None) -> Decimal:
        """Float column sums carry binary noise (1200.4999...), so round them to cents"""
        return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def get_monthly_totals_by_year(self, user_id: int, year: int) -> list[MonthlyTotals]:
        """Totals of the months that have transactions; months without any are left out"""
        month = extract("month", Transaction.registration_date)
        statement = (
            select(
                month.label("month"),
                func.sum(
                    case(
                        (
                            Transaction.type_of_transaction == TypeOfTransaction.INCOME.value,
                            Transaction.amount,
                        )
                    )
                ).label("total_income"),
                func.sum(
                    case(
                        (
                            Transaction.type_of_transaction == TypeOfTransaction.EXPENSE.value,
                            Transaction.amount,
                        )
                    )
                ).label("total_expense"),
            )
            .where(
                (Transaction.user_id == user_id)
                & (Transaction.registration_date >= date(year, 1, 1))
                & (Transaction.registration_date <= date(year, 12, 31))
            )
            .group_by(month)
        )
        return [
            MonthlyTotals(
                month=int(row.month),
                income=self._to_cents(row.total_income),
                expense=self._to_cents(row.total_expense),
            )
            for row in self.session.execute(statement).all()
        ]

    def get_expenses_by_category(
        self, user_id: int, start_date: date, end_date: date
    ) -> list[CategoryAmount]:
        """Expense totals per category; uncategorized expenses come with category None"""
        statement = (
            select(Category.name.label("category"), func.sum(Transaction.amount).label("total"))
            .select_from(Transaction)
            .outerjoin(Category, Transaction.category_id == Category.category_id)
            .where(
                (Transaction.user_id == user_id)
                & (Transaction.type_of_transaction == TypeOfTransaction.EXPENSE.value)
                & (Transaction.registration_date >= start_date)
                & (Transaction.registration_date <= end_date)
            )
            .group_by(Transaction.category_id, Category.name)
        )
        return [
            CategoryAmount(category=row.category, amount=self._to_cents(row.total))
            for row in self.session.execute(statement).all()
        ]
