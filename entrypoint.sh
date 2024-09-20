echo "Exporting environment variables..."
export $(grep -v '^#' .env | xargs)

echo "Now, let's run the migrations"
alembic upgrade head

echo "Latest, we will run the server"
uvicorn 'app.main:app' --host 0.0.0.0 --port 8000 --reload
