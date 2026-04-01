FROM python:3.12.4-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y g++ gcc+ curl libpq-dev unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN groupadd -r admin && useradd -r -g admin admin

COPY --chown=admin:admin requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=admin:admin entrypoint.sh alembic.ini ./
COPY --chown=admin:admin app/ ./app/

RUN chmod +x /src/entrypoint.sh


HEALTHCHECK --interval=10s --timeout=5s \
    CMD curl -f http://localhost:8000/api/v1/test || exit 1

USER admin
EXPOSE 8000

CMD ["/bin/bash", "/src/entrypoint.sh"]
