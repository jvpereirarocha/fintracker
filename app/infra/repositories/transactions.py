from datetime import date
from decimal import Decimal
from typing import Sequence, Literal

from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy import select, extract, func, case

from app.database import Category, Transaction
from app.domain.abstractions.repositories import AbstractTransactionRepository
from app.domain.entities.transactions import SaveTransaction, TransactionEntity
from app.domain.value_objects.dashboard import DashboardValues
from app.domain.value_objects.transactions import TransactionsFilter, TypeOfTransaction


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
        query = (
            select(Transaction)
            .where(Transaction.transaction_id == transaction_id)
        )
        result = self.session.execute(statement=query)
        transaction_dao = result.scalar_one()
        return transaction_dao
    
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
            type_of_transaction=transaction.type_of_transaction, # type: ignore
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
        query = (
            select(Transaction)
            .where(
                Transaction.user_id == user_id
            )
        )
        if filters.month:
            query = query.where(extract('month', Transaction.registration_date) == filters.month)
        
        if filters.year:
            query = query.where(extract('year', Transaction.registration_date) == filters.year)

        if filters.description:
            query = (
                query.where(
                    Transaction.description.ilike(f"%{filters.description}%")
                )
            )
        if filters.type_of_transaction and filters.type_of_transaction == TypeOfTransaction.INCOME:
            query = (
                query.where(
                    Transaction.type_of_transaction == TypeOfTransaction.INCOME.value
                )
            )
        elif filters.type_of_transaction and filters.type_of_transaction == TypeOfTransaction.EXPENSE:
            query = (
                query.where(
                    Transaction.type_of_transaction == TypeOfTransaction.EXPENSE.value
                )
            )

        if filters.category:
            query = (
                query
                .join(Category, Transaction.category_id == Category.category_id)
                .where(func.lower(Category.name) == filters.category.lower())
            )

        count_query = (
            select(func.count())
            .select_from(query.subquery())
        )
        total_result = self.session.execute(statement=count_query)
        total_count = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = (
            query
            .order_by(Transaction.registration_date.desc())
            .limit(page_size)
            .offset(offset)
        )

        result = self.session.execute(statement=query)
        transactions: Sequence[Transaction] = result.scalars().all()
        transaction_entities = [
            TransactionEntity(
                transaction_id=transaction.transaction_id,
                description=transaction.description,
                amount=transaction.amount,
                type_of_transaction=transaction.type_of_transaction, # type: ignore
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
        transaction_dao.type_of_transaction = edit_transaction.type_of_transaction # type: ignore
        transaction_dao.registration_date = edit_transaction.registration_date
        transaction_dao.due_date = edit_transaction.due_date # type: ignore
        transaction_dao.category_id = category_id
        
        self.session.commit()
        self.session.refresh(transaction_dao)
        return TransactionEntity(
            transaction_id=transaction_dao.transaction_id,
            description=transaction_dao.description,
            amount=transaction_dao.amount,
            type_of_transaction=transaction_dao.type_of_transaction, # type: ignore
            registration_date=transaction_dao.registration_date,
            due_date=transaction_dao.due_date, # type: ignore
            user_id=transaction_dao.user_id,
            category_id=transaction_dao.category_id,
        )
        
    
    def save(self, new_transaction: SaveTransaction, user_id: int, category_id: int) -> TransactionEntity:
        
        transaction_dao = Transaction(
            description=new_transaction.description,
            amount=new_transaction.amount,
            type_of_transaction=new_transaction.type_of_transaction, # type: ignore
            registration_date=new_transaction.registration_date,
            due_date=new_transaction.due_date, # type: ignore
            user_id=user_id,
            category_id=category_id,
        )
        self.session.add(transaction_dao)
        self.session.commit()
        self.session.refresh(transaction_dao)
        
        return TransactionEntity(
            transaction_id=transaction_dao.transaction_id,
            description=transaction_dao.description,
            amount=transaction_dao.amount,
            type_of_transaction=transaction_dao.type_of_transaction, # type: ignore
            registration_date=transaction_dao.registration_date,
            due_date=transaction_dao.due_date, # type: ignore
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
                        (Transaction.type_of_transaction == "expense", Transaction.amount) # type: ignore
                    )
                ).label("total_expense"),
                func.sum(
                    case(
                        (Transaction.type_of_transaction == "income", Transaction.amount) # type: ignore
                    )
                ).label("total_income"),
            )
            .where(
                (Transaction.user_id == user_id)
                & (Transaction.registration_date >= start_date)
                & (Transaction.registration_date <= end_date)
            )
        ).first()

        total_expense: Decimal = result.total_expense if result and result.total_expense else Decimal(0)
        total_income: Decimal = result.total_income if result and result.total_income else Decimal(0)

        return DashboardValues(
            total_expense=total_expense,
            total_income=total_income,
        )
