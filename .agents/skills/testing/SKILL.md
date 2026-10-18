---
name: testing
description: Use ao implementar qualquer feature, correção de bug ou refatoração no backend Fintracker, ANTES de escrever código de produção — define o ciclo TDD (red → green → refactor), onde cada tipo de teste mora, como fazer fakes das abstrações de repositório, testar use cases async com anyio e testar endpoints com TestClient + dependency_overrides.
---

# Testes com TDD no Fintracker

**Regra de ferro:** nenhuma linha de código de produção sem um teste falhando antes. Bug report → primeiro um teste que reproduz o bug. Escreveu código antes do teste? Apague e recomece pelo teste.

Arquitetura das camadas: ver skill `architecture` (`.agents/skills/architecture/SKILL.md`).

## Ciclo

1. **RED** — escreva **um** teste pequeno descrevendo **um** comportamento. Rode e **veja falhar pelo motivo certo** (assert falhando ou `ImportError`/`AttributeError` do que ainda não existe — não erro de setup/fixture).
   ```bash
   pytest tests/test_usecase_create_category.py -q
   ```
2. **GREEN** — código mínimo para passar. Nada de generalizar, nada de "já que estou aqui". Rode o arquivo de novo → verde.
3. **REFACTOR** — com tudo verde: remova duplicação, melhore nomes, tipagem. Rode a suíte inteira após cada mudança:
   ```bash
   pytest -q && ruff check . --fix && ruff format . && mypy .
   ```
4. Repita para o próximo comportamento (próximo caso de borda, próximo erro).

Nunca pule a etapa de ver falhar: teste que nunca falhou não prova nada.

## Ordem de dentro para fora

Ao criar feature nova (ver checklist em `architecture/references/new-feature-checklist.md`), dirija cada camada por testes nesta ordem:

| Camada | O que testar | Dependências | Tipo |
|---|---|---|---|
| `domain/business_logic`, entidades, VOs | funções puras, `__post_init__`, properties (`PagedResponse.total_of_pages`, `DashboardResume.monthly_balance`) | nenhuma | sync, `parametrize` |
| `usecases` | regras de negócio, autorização, exceções de domínio, o que é passado ao repo | **fakes** das abstrações | async, `@pytest.mark.anyio` |
| `api` (endpoints + DTOs) | status HTTP, aliases camelCase, formato BRL/data, mapeamento exceção → status, auth 401 | `TestClient` + `app.dependency_overrides` com use case real + fakes | sync |
| `infra/repositories` | queries SQL, filtros, paginação | Postgres real (ainda não existe infra — ver abaixo) | integração |

Maior parte do esforço vai em **use cases** — é onde a lógica de negócio mora e não precisa de banco.

## Estrutura de arquivos

```
tests/
├── conftest.py                       # env vars de teste + fixtures anyio_backend e client (já existe)
├── fakes.py                          # FakeUserRepo, FakeTransactionRepo, FakeCategoryRepo, make_* (já existe)
├── test_domain_<modulo>.py           # ex.: test_domain_conversor.py
├── test_usecase_<acao>_<recurso>.py  # ex.: test_usecase_create_category.py
└── test_api_<recurso>.py             # ex.: test_api_categories.py
```

Nome do teste descreve comportamento: `test_create_category_raises_when_name_already_exists`, não `test_create_2`.

## Regras essenciais

- **`conftest.py` define env vars antes de qualquer import de `app.infra`/`app.main`.** `Settings()` é instanciado no import (`session.py`, `auth/token.py`) e CI não tem `.env`. Usar `os.environ.setdefault(...)` — env vars têm prioridade sobre `.env`, então os testes nunca apontam para o banco real. `create_engine` não conecta no import, então API tests rodam sem Postgres.
- **Async:** `pytest-asyncio` **não** está instalado. Use `@pytest.mark.anyio` (plugin do `anyio`, já em `requirements.txt`) + fixture `anyio_backend` retornando `"asyncio"` no `conftest.py`.
- **Fakes, não mocks.** Classes em `tests/fakes.py` com estado em memória (`dict`). Testam comportamento, não chamadas. `unittest.mock` só para verificar interação quando não há outro jeito.
- Fake **herda explicitamente** a abstração (`class FakeUserRepo(AbstractUserRepository)`), igual aos adapters. Sem herança, mypy exige o `Protocol` completo e rejeita o fake (`incompatible type "FakeUserRepo"; expected "AbstractUserRepository"`).
- Fake implementa só os métodos que os use cases chamam, com as **mesmas assinaturas e retornos** do adapter real (ex.: `get_user_id_by_username` retorna `0` quando não acha, como `AdapterUserRepo`). Reaproveite e estenda os fakes e builders existentes (`make_transaction`, `make_filters`) em vez de criar novos por arquivo.
- **Use case não importa nada de `app.infra`** no teste — se precisar, a arquitetura está errada.
- **API tests:** override da *factory* do use case (`get_create_category_use_case`) e de `get_current_user`; sempre `app.dependency_overrides.clear()` no teardown (use fixture). Nunca override de `get_db` com sessão real.
- Para testar 500/handlers: `TestClient(app, raise_server_exceptions=False)`.
- Um comportamento por teste; Arrange / Act / Assert separados por linha em branco.
- Afirmar sobre **contrato público**: retorno do `execute`, exceção lançada (`pytest.raises(XException)`), estado do fake, JSON da resposta. Não testar métodos privados (`_get_transaction_by_id`).
- Datas: passe datas explícitas; código que usa `date.today()` (ex.: `DashboardResumeUseCase`) — teste com `month`/`year` explícitos ou injete o relógio.

## Exemplos completos

Templates validados (conftest, fakes, use case, API, domínio): [references/examples.md](references/examples.md).

## Testes de integração (repositórios)

Ainda não existe infra. Ao criar: marcar `@pytest.mark.integration`, banco Postgres separado (`docker compose up db`, porta 5433, DB `fintracker_test`), `mapped_registry.metadata.create_all` na fixture de sessão, transação com rollback por teste. Não misturar com a suíte unitária padrão (`pytest -m "not integration"` no pre-commit).

## Checklist antes de dizer "pronto"

- [ ] Cada comportamento novo tem teste que eu **vi falhar** antes de implementar
- [ ] Casos de erro cobertos (usuário inexistente, recurso inexistente, duplicado, payload inválido)
- [ ] `pytest -q` verde, sem warnings novos
- [ ] `ruff check .`, `ruff format --check .`, `mypy .` limpos
- [ ] Commit: `test: ...` para só testes; `feat:`/`fix:` quando inclui produção
