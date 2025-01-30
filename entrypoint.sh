#!/bin/sh
# Run database migrations
alembic upgrade head

# Start the application
exec uvicorn main:api --host 0.0.0.0 --port 8000