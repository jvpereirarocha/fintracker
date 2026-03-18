from datetime import datetime
from functools import cache
from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy import select, extract, func

from app.database import Category, Transaction
from app.domain.abstractions.repositories import AbstractTransactionRepository
from app.domain.entities.transactions import NewTransaction, PatchTransaction, TransactionEntity
from app.domain.value_objects.transactions import TransactionsFilter, TypeOfTransaction


class AdapterTransactionRepo(AbstractTransactionRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

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
    
    def _get_attribute_value(self, new_value: Optional[Any], old_value: Any):
        return new_value or old_value
    
    def update(
        self,
        transaction_id: int,
        edit_transaction: PatchTransaction,
        category_id: Optional[int],
    ) -> TransactionEntity:
        transaction_dao = self.session.query(Transaction).where(Transaction.transaction_id == transaction_id).first()
        if not transaction_dao:
            raise ValueError("Transaction not found")
        
        transaction_dao.description = self._get_attribute_value(
            new_value=edit_transaction.description, old_value=transaction_dao.description
        )
        transaction_dao.amount = self._get_attribute_value(
            new_value=edit_transaction.amount, old_value=transaction_dao.amount
        )
        transaction_dao.type_of_transaction = self._get_attribute_value(
            new_value=edit_transaction.type_of_transaction, old_value=transaction_dao.type_of_transaction
        )
        transaction_dao.registration_date = self._get_attribute_value(
            new_value=edit_transaction.registration_date, old_value=transaction_dao.registration_date
        )
        transaction_dao.due_date = self._get_attribute_value(
            new_value=edit_transaction.due_date, old_value=transaction_dao.due_date
        )
        transaction_dao.category_id = self._get_attribute_value(
            new_value=category_id, old_value=transaction_dao.category_id
        )
        
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
        
    
    def save(self, new_transaction: NewTransaction, user_id: int, category_id: int) -> TransactionEntity:
        
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