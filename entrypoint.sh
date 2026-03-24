#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "First of all, let's run the migrations"
alembic upgrade head

echo "Latest, we will run the server"
exec uvicorn 'app.main:app' --host 0.0.0.0 --port 8000 --reload
