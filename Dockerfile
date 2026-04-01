FROM python:3.12.4-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Instalamos as dependências de build aqui
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ gcc libpq-dev unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalamos as dependências em uma pasta específica
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12.4-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 unixodbc curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

RUN groupadd -r admin && useradd -r -g admin admin

COPY --chown=admin:admin entrypoint.sh alembic.ini ./
COPY --chown=admin:admin app/ ./app/

RUN chmod +x /src/entrypoint.sh


HEALTHCHECK --interval=10s --timeout=5s \
    CMD curl -f http://localhost:8000/api/v1/test || exit 1

USER admin
EXPOSE 8000

CMD ["/bin/bash", "/src/entrypoint.sh"]
