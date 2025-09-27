#!/bin/bash
# Alternative startup script that doesn't require strict directory validation

set -e

echo "Starting CipherDrive Backend (flexible mode)..."

# Set Python path to current directory
export PYTHONPATH=/app:$PYTHONPATH

# Create directories if they don't exist (but don't fail if we can't)
echo "Ensuring directories exist (best effort)..."
mkdir -p /data/uploads /data/shares /app/logs /app/config 2>/dev/null || echo "Note: Some directories couldn't be created, but continuing..."

# Initialize database (allow failure)
echo "Initializing database..."
python -c "from database import create_tables; create_tables()" 2>/dev/null || echo "Database initialization failed, but continuing..."

# Start the application with reduced worker count for stability
echo "Starting FastAPI server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info