#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

read -p "Enter PostgreSQL username: " POSTGRES_USER
# Using -s hides the password input from the screen for security
read -sp "Enter PostgreSQL password: " POSTGRES_PASSWORD
echo "" # Adds a newline after the hidden password input
read -p "Enter PostgreSQL database name: " POSTGRES_DB

echo "Backing up database..."

# 1. Use -e PGPASSWORD=... to pass the password securely to the container
# 2. Use -i instead of -it to prevent corrupting the .sql file with terminal characters
# 3. Removed 'exec' so the script can continue to the final echo statement
docker container exec -i -e PGPASSWORD="$POSTGRES_PASSWORD" dbfinanc-api pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > backup.sql

echo "Backup complete!"
