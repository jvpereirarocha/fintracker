FROM python:3.12.4-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

RUN groupadd -r admin && useradd -r -g admin admin
RUN chown -R admin:admin /app
RUN chown -R admin:admin /app/app/migrations
RUN chown admin:admin /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN apt-get update \
    && apt-get install -y g++ gcc+ curl libpq-dev unixodbc unixodbc-dev \
    && apt-get install -y locales \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=10s --timeout=5s \
    CMD curl -f http://localhost:8000/users/test || exit 1

SHELL ["/bin/bash"]
USER admin

CMD ["/bin/bash", "/app/entrypoint.sh"]
