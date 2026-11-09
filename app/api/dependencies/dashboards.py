from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.base import get_db
from app.infra.repositories.transactions import AdapterTransactionRepo
from app.infra.repositories.users import AdapterUserRepo
from app.usecases.dashboards.expenses_by_category import ExpensesByCategoryUseCase
from app.usecases.dashboards.monthly_summary import MonthlySummaryUseCase
from app.usecases.dashboards.resume import DashboardResumeUseCase


async def get_dashboard_resume_use_case(db: Session = Depends(get_db)) -> DashboardResumeUseCase:
    user_repo = AdapterUserRepo(session=db)
    transaction_repo = AdapterTransactionRepo(session=db)
    return DashboardResumeUseCase(user_repo=user_repo, transaction_repo=transaction_repo)


async def get_monthly_summary_use_case(db: Session = Depends(get_db)) -> MonthlySummaryUseCase:
    return MonthlySummaryUseCase(
        user_repo=AdapterUserRepo(session=db),
        transaction_repo=AdapterTransactionRepo(session=db),
    )


async def get_expenses_by_category_use_case(
    db: Session = Depends(get_db),
) -> ExpensesByCategoryUseCase:
    return ExpensesByCategoryUseCase(
        user_repo=AdapterUserRepo(session=db),
        transaction_repo=AdapterTransactionRepo(session=db),
    )
