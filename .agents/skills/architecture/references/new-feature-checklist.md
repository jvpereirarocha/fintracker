# Checklist: novo recurso / caso de uso

Ordem de dentro para fora. Exemplo: recurso `budgets`, ação `create`.

## 1. Domain
- [ ] `app/domain/entities/budgets.py` — `BudgetEntity` (`@dataclass`) e `SaveBudget` (`@dataclass(frozen=True)`).
- [ ] `app/domain/value_objects/budgets.py` — filtros/enums se necessário (`StrEnum`, `frozen=True`).
- [ ] `app/domain/exceptions/budgets.py` — `BudgetNotFoundException`, `BudgetAlreadyExistsException`.
- [ ] `app/domain/abstractions/repositories.py` — `class AbstractBudgetRepository(AbstractRepository)` com métodos tipados.

## 2. Use case
- [ ] `app/usecases/budgets/__init__.py` + `app/usecases/budgets/create_budget.py`:
  ```python
  class CreateBudgetUseCase(AbstractUseCase):
      def __init__(
          self, user_repo: AbstractUserRepository, budget_repo: AbstractBudgetRepository
      ):
          self.user_repo = user_repo
          self.budget_repo = budget_repo

      async def execute(self, new_budget: SaveBudget, username: str) -> BudgetEntity:
          user_id = self.user_repo.get_user_id_by_username(username=username)
          if not user_id:
              raise UserNotFoundException(f"User {username} not found")
          return self.budget_repo.save(new_budget=new_budget, user_id=user_id)
  ```

## 3. Infra
- [ ] `app/infra/database/orm_budget.py` — `@mapped_registry.mapped_as_dataclass class Budget`, `__tablename__`, PK `init=False`, FK `users.user_id`.
- [ ] Importar o módulo em `app/infra/database/__init__.py`.
- [ ] `app/infra/repositories/budgets.py` — `AdapterBudgetRepo(AbstractBudgetRepository)`; retorna `BudgetEntity`, nunca o model.
- [ ] `alembic revision --autogenerate -m "create budget table"` e revisar o arquivo.

## 4. API
- [ ] `app/api/v1/dtos/budgets.py` — `SaveBudgetDTO`, `BudgetResponse` (aliases camelCase, serializers BRL/data se houver valor/data). Lista paginada: `class PaginatedBudgets(Pagination[BudgetResponse])` com `items: list[BudgetResponse] = Field(alias="budgets")`.
- [ ] `app/api/dependencies/budgets.py` — `async def get_create_budget_use_case(db: Session = Depends(get_db))`.
- [ ] `app/api/v1/endpoints/budgets.py` — `budgets_router` com `dependencies=[Depends(get_current_user)]`; endpoint converte DTO → `SaveBudget` e chama `execute(..., username=request.state.user.sub)`.
- [ ] Registrar `budgets_router` em `app/api/v1/__init__.py`.

## 5. Testes e qualidade
- [ ] Teste do use case em `tests/test_usecase_<acao>_<recurso>.py` com fakes de `tests/fakes.py` (herdando a abstração) e `@pytest.mark.anyio`. Seguir a skill `testing` (TDD: teste antes do código).
- [ ] `ruff check . --fix && ruff format . && mypy . && pytest`.
- [ ] Commit `feat: ...` (Conventional Commits).
