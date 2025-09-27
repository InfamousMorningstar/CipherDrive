#!/bin/bash
# Backend startup script

set -e

echo "Starting CipherDrive Backend..."

# Set Python path to current directory
export PYTHONPATH=/app:$PYTHONPATH

# Initialize database
echo "Initializing database..."
python -c "from database import create_tables; create_tables()" || echo "Database initialization failed, but continuing..."

# Start the application
echo "Starting FastAPI server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1