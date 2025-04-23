#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -p 5432 -U postgres; do
    sleep 1
done

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Migrations completed!" 