#!/bin/bash
set -e

echo "Initializing database..."
python -c "from db import initializeDB; initializeDB()"

echo "Starting Flask..."
exec python app.py
