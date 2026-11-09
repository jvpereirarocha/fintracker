COMPOSE      := docker compose
COMPOSE_TEST := docker compose -f docker-compose.test.yaml

.DEFAULT_GOAL := help
.PHONY: help up down logs migrate test test-down test-local lint format typecheck

help: ## List available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- app (dev)

up: ## Build and start the API and database in the background
	$(COMPOSE) up --build -d

down: ## Stop the API and database
	$(COMPOSE) down

logs: ## Follow the API logs
	$(COMPOSE) logs -f web

migrate: ## Apply migrations inside the running API container
	$(COMPOSE) exec web alembic upgrade head

# ------------------------------------------------------------------ tests

# Extra pytest flags, e.g. `make test ARGS="-v -k dashboard"`
ARGS ?= --tb=short -q

# `run` attaches the terminal straight to the tests container: pytest output and
# colors show as-is, without compose's interactive menu redrawing over them
test: ## Start a clean test database, run migrations + pytest, then tear it all down
	$(COMPOSE_TEST) build tests
	$(COMPOSE_TEST) run --rm tests sh -c "alembic upgrade head && pytest $(ARGS)"; \
		status=$$?; \
		$(COMPOSE_TEST) --progress quiet down -v --remove-orphans; \
		exit $$status

test-down: ## Remove leftover test containers
	$(COMPOSE_TEST) --progress quiet down -v --remove-orphans

test-local: ## Run pytest on the host, without Docker
	pytest --tb=short -q

# --------------------------------------------------------------- quality

lint: ## Lint with ruff (auto-fix)
	ruff check . --fix

format: ## Format with ruff
	ruff format .

typecheck: ## Type-check with mypy
	mypy .
