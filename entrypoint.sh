#!/bin/bash
set -e

echo "Initializing database..."
python -c "from db import initializeDB; initializeDB()"

echo "Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 5000
