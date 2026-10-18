---
name: architecture
description: Use ao criar, alterar ou revisar código no backend Fintracker (FastAPI + SQLAlchemy + Clean Architecture) — novos endpoints, use cases, repositórios, entidades, DTOs, exceções, models ORM ou migrations — ou quando precisar entender em qual camada algo deve morar e como as camadas se conectam.
---

# Arquitetura do Fintracker

Backend Python 3.12 / FastAPI com Clean Architecture em quatro camadas. Regra central: **dependências apontam para dentro** — `api` → `usecases` → `domain` ← `infra`. O domínio não importa nada de `app.api`, `app.usecases` nem `app.infra`.

## Mapa das camadas

```
app/
├── main.py                 # FastAPI app, CORS, exception handlers, Prometheus Instrumentator
├── domain/                 # Puro: sem FastAPI, sem SQLAlchemy
│   ├── entities/           # dataclasses: TransactionEntity, SaveTransaction, CategoryEntity, UserEntity, PagedResponse[T]
│   ├── value_objects/      # dataclasses frozen + StrEnums: TransactionsFilter, PaginationParams, JWTPayload, DashboardValues...
│   ├── abstractions/       # repositories.py (Protocol), usecases.py (ABC), token.py / password_handler.py (ABC)
│   ├── exceptions/         # BaseDomainException + ExceptionType, um arquivo por recurso
│   └── business_logic/     # funções puras: conversor.py (BRL/datas/validações), validators.py
├── usecases/<recurso>/     # uma classe por caso de uso, herda AbstractUseCase, async execute()
├── infra/
│   ├── repositories/       # Adapter<Recurso>Repo — implementa a abstração com SQLAlchemy
│   ├── database/           # registry, models ORM (orm_<recurso>.py), session.py (LocalSessionMaker)
│   ├── migrations/         # Alembic (env.py usa mapped_registry.metadata)
│   ├── auth/               # TokenProvider (PyJWT), AdapterPasswordHandler (bcrypt)
│   └── configs/settings.py # pydantic-settings, lê .env
└── api/
    ├── handlers.py         # BaseDomainException → 4xx via ExceptionType; Exception → 500
    ├── dependencies/       # base.py (get_db, get_current_user, get_pagination_params) + um arquivo por recurso
    └── v1/
        ├── __init__.py     # api_v1_router (prefixo /api/v1) inclui os routers
        ├── endpoints/      # <recurso>_router por arquivo
        └── dtos/           # Pydantic: request/response, aliases camelCase
```

## Fluxo de uma requisição

```
HTTP → endpoint (router com Depends(get_current_user) → request.state.user = JWTPayload)
     → DTO Pydantic valida payload (formato BRL, data DD/MM/YYYY, regras status/tipo)
     → endpoint converte DTO → entidade/VO de domínio (SaveTransaction, TransactionsFilter...)
     → Depends(get_<acao>_use_case) monta use case com Adapter*Repo(session=db)
     → use_case.execute(...) valida existência/regras e lança exceções de domínio
     → repositório consulta ORM, faz commit e devolve entidade de domínio (nunca o model ORM)
     → endpoint retorna entidade; response_model (DTO) serializa com from_attributes
```

Exceção de domínio sobe até `app/api/handlers.py` → `{"detail": exc.message}` com status mapeado de `ExceptionType`.

## Regras por camada

### domain
- Só stdlib (dataclasses, enum, decimal, datetime, re). Proibido importar FastAPI, Pydantic, SQLAlchemy.
- Entidades de leitura: `@dataclass` com id (`TransactionEntity`). Comandos de escrita: `@dataclass(frozen=True)` sem id, prefixo `Save`/`PartialUpdate` (`SaveTransaction`, `PartialUpdateCategory`).
- Value objects: `@dataclass(frozen=True)`; enums são `StrEnum` (`TypeOfTransaction`, `TransactionStatus`).
- Abstrações de repositório: classes `Protocol` em `abstractions/repositories.py`, herdando `AbstractRepository`. Prefira assinaturas tipadas (como `AbstractUserRepository`) em vez de `*args, **kwargs -> Any`.
- Exceções: uma subclasse de `BaseDomainException` por erro, com mensagem default e `name`/`type` fixos:
  ```python
  class CategoryNotFoundException(BaseDomainException):
      def __init__(self, message: str = "Category not found"):
          super().__init__(message=message, name="CategoryNotFound", type=ExceptionType.NOT_FOUND)
  ```
  Novo status HTTP → adicionar membro em `ExceptionType` **e** case em `get_status_code_by_exception_type`.

### usecases
- Arquivo em `app/usecases/<recurso>/<acao>.py`; classe `<Acao><Recurso>UseCase(AbstractUseCase)`.
- Construtor recebe **somente abstrações** (`AbstractUserRepository`, `TokenProviderAbstraction`...), atribuídas como `self.<x>_repo`.
- `async def execute(self, ...)` com kwargs nomeados e retorno tipado (entidade, VO ou `PagedResponse[T]`).
- Padrão de autorização: resolver `user_id = self.user_repo.get_user_id_by_username(username)` → se falso, `UserNotFoundException`. Verificar existência (`exists`, `get_category_by_id`) antes de buscar/alterar/deletar — os repositórios **não** checam isso (`scalar_one()` estoura).
- Regras de unicidade (ex.: nome de categoria) ficam aqui, não no repo.

### infra
- Repositório: `class Adapter<Recurso>Repo(Abstract<Recurso>Repository)` em `app/infra/repositories/<recurso>.py`, `__init__(self, session: SQLAlchemySession)`.
- Usa SQLAlchemy 2.0 (`select(...)`, `self.session.execute(statement=...)`), **sync**. Escritas fazem `add` → `commit` → `refresh` dentro do próprio método.
- Sempre converter model ORM → entidade de domínio antes de retornar.
- Paginação: método retorna `tuple[list[Entity], int]` (itens, total) usando `select(func.count()).select_from(query.subquery())`; o use case monta `PagedResponse`.
- Models ORM: `@mapped_registry.mapped_as_dataclass` em `app/infra/database/orm_<recurso>.py`, PK com `init=False`. **Todo model novo deve ser importado em `app/infra/database/__init__.py`**, senão o autogenerate do Alembic não enxerga.
- Settings: instanciar `Settings()` (com `# type: ignore`), nunca ler `os.environ` direto.

### api
- Router: `<recurso>_router = APIRouter(prefix="/<recurso>", dependencies=[Depends(get_current_user)])` e registrar em `app/api/v1/__init__.py`. Só `users_router` (login/register) é público.
- Usuário corrente: `request.state.user.sub` (username) — passe `username=` ao use case.
- Dependências: uma função `async def get_<acao>_<recurso>_use_case(db: Session = Depends(get_db))` por use case em `app/api/dependencies/<recurso>.py`. É o **único** lugar onde classes concretas de infra são instanciadas.
- Endpoints: `response_model=<DTO>`, `status_code=HTTPStatus.<X>`, sem lógica de negócio — só montar entidade/VO e `return await use_case.execute(...)`.
- DTOs: Pydantic v2, `ConfigDict(from_attributes=True, populate_by_name=True)`; campos snake_case com `Field(alias="camelCase")`. Paginados herdam `Pagination[T]` e renomeiam `items` via alias (`transactions`, `categories`).

## Contrato com o frontend (pt-BR)
- Valores monetários entram/saem como string `"R$ 1.000,00"` (`clean_brl_format_to_decimal` / `format_decimal_to_brl_format`).
- Datas entram/saem como `DD/MM/YYYY` (`validate_date_format` / `format_date_to_brazilian_date_text_format`).
- Query params e JSON em camelCase (`itemsPerPage`, `typeOfTransaction`, `totalOfPages`, `next`, `prev`).
- Mensagens de validação de entrada ao usuário em português; mensagens de not found/exists em inglês (padrão atual).
- Despesa (`expense`) exige `due_date` e status em `paying | already_paid | not_paid`; receita (`income`) só aceita `received`.

## Convenções gerais
- Imports absolutos a partir de `app.`; kwargs nomeados nas chamadas entre camadas.
- Linha máx. 100, ruff (E,W,F,I,B,C4,UP,N,SIM,RUF), mypy strict + plugin pydantic. Rodar `ruff check . --fix && ruff format . && mypy .`.
- Commits em Conventional Commits (semantic-release no `main`: `feat` → minor, `fix`/`perf` → patch).
- Migrations: `alembic revision --autogenerate -m "..."` → revisar arquivo gerado em `app/infra/migrations/versions/`.

## Adicionando funcionalidade
Siga o checklist em [references/new-feature-checklist.md](references/new-feature-checklist.md).

## Dívidas conhecidas (não replicar)
- `AbstractTransactionRepository` / `AbstractCategoryRepository` usam `*args, **kwargs -> Any` — código novo deve tipar assinaturas.
- `orm_transaction.py` usa `@validates` chamando `domain.business_logic.validators` — validação deve ficar em DTO/use case/domínio, não no ORM.
- `GetOneTransactionUseCase`, update e delete não verificam se a transação pertence ao `user_id` — ao mexer nesses fluxos, filtrar por dono.
- `execute()` é `async` mas repositórios são sync (bloqueiam o event loop); manter consistência até migração planejada para `AsyncSession`.
- Defaults `datetime.now()` em dataclasses (`SaveCategory.updated_at`) são avaliados no import — use `field(default_factory=datetime.now)`.
- `tests/` praticamente vazio: use cases são testáveis com fakes das abstrações (sem DB), prefira esse padrão.
