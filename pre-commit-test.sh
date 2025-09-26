#!/bin/bash
# pre-commit-test.sh - Run before pushing any changes

set -e
echo "🔍 Running pre-commit tests..."

# Test 1: Python syntax validation
echo "1. Testing Python syntax..."
find backend -name "*.py" -exec python -m py_compile {} \;
echo "✅ Python syntax validation passed"

# Test 2: Docker build test
echo "2. Testing Docker builds..."
if command -v docker &> /dev/null; then
    echo "Building backend..."
    docker build -t cipherdrive-backend-test backend/
    echo "Building frontend..."  
    docker build -t cipherdrive-frontend-test frontend/
    echo "✅ Docker builds successful"
else
    echo "⚠️ Docker not available, skipping build test"
fi

# Test 3: Import validation (if venv exists)
if [ -d "test_env" ]; then
    echo "3. Testing Python imports..."
    source test_env/bin/activate || test_env\\Scripts\\activate.bat
    cd backend
    python -c "
import sys
from main import app
from routers.admin import router
from routers.users import router
from utils.email import send_welcome_email
print('✅ All critical imports successful')
" || echo "❌ Import test failed"
    cd ..
    deactivate
fi

echo "🎉 Pre-commit tests completed!"