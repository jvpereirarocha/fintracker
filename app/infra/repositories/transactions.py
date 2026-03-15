from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy import select, and_, extract, func

from app.database import Transaction as TableTransaction
from app.domain.abstractions.repositories import AbstractTransactionRepository
from app.domain.entities.transactions import TransactionEntity
from app.domain.value_objects.transactions import TransactionsFilter, TypeOfTransaction


class SqlTransactionRepo(AbstractTransactionRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def fetch_all(
        self,
        filters: TransactionsFilter,
        page: int,
        page_size: int,
    ) -> tuple[list[TransactionEntity], int]:
        query = (
            select(TableTransaction)
            .where(
                TableTransaction.user_id == filters.user_id
            )
        )
        if filters.month:
            query = query.where(extract('month', TableTransaction.registration_date) == filters.month)
        
        if filters.year:
            query = query.where(extract('year', TableTransaction.registration_date) == filters.year)

        if filters.description:
            query = (
                query.where(
                    TableTransaction.description.ilike(f"{filters.description}")
                )
            )
        if filters.type_of_transaction and filters.type_of_transaction == TypeOfTransaction.INCOME:
            query = (
                query.where(
                    TableTransaction.type_of_transaction == TypeOfTransaction.INCOME.value
                )
            )
        elif filters.type_of_transaction and filters.type_of_transaction == TypeOfTransaction.EXPENSE:
            query = (
                query.where(
                    TableTransaction.type_of_transaction == TypeOfTransaction.EXPENSE.value
                )
            )

        count_query = (
            select(func.count())
            .select_from(TableTransaction)
            .where(
                TableTransaction.user_id == filters.user_id
            )
        )
        total_result = self.session.execute(statement=count_query)
        total_count = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.limit(page_size).offset(offset)

        result = self.session.execute(statement=query)
        transactions: list[TableTransaction] = result.scalars().all()
        entities = [
            TransactionEntity(
                transaction_id=transaction.transaction_id,
                description=transaction.description,
                amount=transaction.amount,
                type_of_transaction=transaction.type_of_transaction,
                registration_date=transaction.registration_date,
                user_id=transaction.user_id
            )
            for transaction in transactions
        ]
        return entities, total_count