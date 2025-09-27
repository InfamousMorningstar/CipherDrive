#!/bin/bash
# CipherDrive Quick Setup Script for TrueNAS SCALE
# Usage: ./setup.sh [your-truenas-ip] [your-pool-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TRUENAS_IP=${1:-"localhost"}
SSD_POOL="app-pool"
HDD_POOL="Centauri"
SSD_APP_DIR="/mnt/${SSD_POOL}/cipherdrive"
HDD_APP_DIR="/mnt/${HDD_POOL}/cipherdrive"

echo -e "${BLUE}🚀 CipherDrive Setup Script for TrueNAS SCALE${NC}"
echo "================================================"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

echo "Setting up CipherDrive on TrueNAS SCALE..."
echo "TrueNAS IP: $TRUENAS_IP"
echo "SSD Pool: $SSD_POOL"
echo "HDD Pool: $HDD_POOL"
echo "SSD App Directory: $SSD_APP_DIR"
echo "HDD App Directory: $HDD_APP_DIR"
echo ""

# Create directories
print_status "Creating application directories..."
mkdir -p "$SSD_APP_DIR"/{postgres,backend,frontend,logs}
mkdir -p "$HDD_APP_DIR"/{uploads,ssl}
mkdir -p "/mnt/${HDD_POOL}/backups/cipherdrive"
chmod -R 755 "$SSD_APP_DIR"
chmod -R 755 "$HDD_APP_DIR"
chmod 700 "$SSD_APP_DIR/postgres"

# Generate secure passwords and secrets
print_status "Generating secure passwords and secrets..."
DB_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 64)
JWT_REFRESH_SECRET=$(openssl rand -base64 64)
CSRF_SECRET=$(openssl rand -base64 32)

# Create environment file
print_status "Creating environment configuration..."
cat > "$APP_DIR/.env" << EOF
# Database Configuration
DATABASE_URL=postgresql://cipherdrive_user:${DB_PASSWORD}@postgres:5432/cipherdrive_db
POSTGRES_USER=cipherdrive_user
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=cipherdrive_db

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET}
JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET}
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://${TRUENAS_IP}:3000
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600
ENVIRONMENT=production
DEFAULT_USER_QUOTA_GB=5
MAX_UPLOAD_SIZE_MB=100

# Security Configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
CSRF_SECRET=${CSRF_SECRET}

# Optional Email Configuration (uncomment and configure if needed)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# SMTP_FROM_EMAIL=your-email@gmail.com
EOF

# Create Docker Compose file
print_status "Creating Docker Compose configuration..."
cat > "$APP_DIR/docker-compose.yml" << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: cipherdrive-postgres
    environment:
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
      POSTGRES_DB: \${POSTGRES_DB}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - ${APP_DIR}/postgres:/var/lib/postgresql/data
    networks:
      - cipherdrive-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    build: ./backend
    container_name: cipherdrive-backend
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - .env
    volumes:
      - ${APP_DIR}/uploads:/app/uploads
    ports:
      - "8000:8000"
    networks:
      - cipherdrive-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build: ./frontend
    container_name: cipherdrive-frontend
    depends_on:
      - backend
    environment:
      REACT_APP_API_URL: http://${TRUENAS_IP}:8000
    ports:
      - "3000:3000"
    networks:
      - cipherdrive-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  cipherdrive-network:
    driver: bridge

volumes:
  postgres_data:
  uploads_data:
EOF

# Create backup script
print_status "Creating backup script..."
cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="/mnt/${POOL_NAME}/cipherdrive/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Starting backup: $DATE"

# Backup database
docker exec cipherdrive-postgres pg_dump -U cipherdrive_user cipherdrive_db > $BACKUP_DIR/database_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /mnt/${POOL_NAME}/cipherdrive/uploads

# Keep only last 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x "$APP_DIR/backup.sh"

# Create health check script
print_status "Creating health check script..."
cat > "$APP_DIR/health-check.sh" << 'EOF'
#!/bin/bash
echo "=== CipherDrive Health Check ==="
echo "Date: $(date)"
echo ""

echo "Container Status:"
docker ps --filter "name=cipherdrive" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "Disk Usage:"
df -h /mnt/${POOL_NAME}/cipherdrive/
echo ""

echo "Database Status:"
docker exec cipherdrive-postgres pg_isready -U cipherdrive_user || echo "Database not ready"
echo ""

echo "Backend Health:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "Backend not responding"
echo ""

echo "Frontend Health:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000 || echo "Frontend not responding"
echo ""

echo "=== Health Check Complete ==="
EOF

chmod +x "$APP_DIR/health-check.sh"

# Create management script
print_status "Creating management script..."
cat > "$APP_DIR/manage.sh" << EOF
#!/bin/bash
# CipherDrive Management Script

case \$1 in
    start)
        echo "Starting CipherDrive..."
        cd $APP_DIR && docker compose up -d
        ;;
    stop)
        echo "Stopping CipherDrive..."
        cd $APP_DIR && docker compose down
        ;;
    restart)
        echo "Restarting CipherDrive..."
        cd $APP_DIR && docker compose restart
        ;;
    logs)
        echo "Showing logs..."
        cd $APP_DIR && docker compose logs -f
        ;;
    status)
        echo "Checking status..."
        cd $APP_DIR && docker compose ps
        ;;
    backup)
        echo "Running backup..."
        $APP_DIR/backup.sh
        ;;
    health)
        echo "Running health check..."
        $APP_DIR/health-check.sh
        ;;
    update)
        echo "Updating CipherDrive..."
        cd $APP_DIR && docker compose pull && docker compose up -d
        ;;
    clean)
        echo "Cleaning up unused images..."
        docker image prune -f
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|logs|status|backup|health|update|clean}"
        exit 1
        ;;
esac
EOF

chmod +x "$APP_DIR/manage.sh"

# Create Portainer stack template
print_status "Creating Portainer stack template..."
cat > "$APP_DIR/portainer-stack.yml" << EOF
# Copy this content to Portainer Stack
# Stack name: cipherdrive

version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: cipherdrive-postgres
    environment:
      POSTGRES_USER: cipherdrive_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: cipherdrive_db
    volumes:
      - ${APP_DIR}/postgres:/var/lib/postgresql/data
    networks:
      - cipherdrive-network
    restart: unless-stopped

  backend:
    image: python:3.11-slim
    container_name: cipherdrive-backend
    working_dir: /app
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://cipherdrive_user:${DB_PASSWORD}@postgres:5432/cipherdrive_db
      JWT_SECRET_KEY: ${JWT_SECRET}
      ALLOWED_ORIGINS: http://${TRUENAS_IP}:3000
    volumes:
      - ${APP_DIR}/backend:/app
      - ${APP_DIR}/uploads:/app/uploads
    ports:
      - "8000:8000"
    networks:
      - cipherdrive-network
    restart: unless-stopped
    command: |
      bash -c "
        pip install fastapi[all] sqlalchemy psycopg2-binary python-multipart python-jose[cryptography] passlib[bcrypt] slowapi pillow uvicorn &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000
      "

  frontend:
    image: node:18-alpine
    container_name: cipherdrive-frontend
    working_dir: /app
    depends_on:
      - backend
    environment:
      REACT_APP_API_URL: http://${TRUENAS_IP}:8000
    volumes:
      - ${APP_DIR}/frontend:/app
    ports:
      - "3000:3000"
    networks:
      - cipherdrive-network
    restart: unless-stopped
    command: |
      sh -c "
        npm install react react-dom react-router-dom axios &&
        npm start
      "

networks:
  cipherdrive-network:
    driver: bridge
EOF

# Set proper permissions
print_status "Setting permissions..."
chown -R 999:999 "$APP_DIR/postgres"  # PostgreSQL user
chown -R 1000:1000 "$APP_DIR/uploads"  # Application user

print_status "Setup completed successfully!"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Copy your application files to:"
echo "   - Backend: $APP_DIR/backend/"
echo "   - Frontend: $APP_DIR/frontend/"
echo ""
echo "2. To start with Docker Compose:"
echo "   cd $APP_DIR && docker compose up -d"
echo ""
echo "3. To use with Portainer:"
echo "   - Copy content from $APP_DIR/portainer-stack.yml"
echo "   - Create new stack in Portainer"
echo ""
echo "4. Management commands:"
echo "   $APP_DIR/manage.sh {start|stop|restart|logs|status|backup|health}"
echo ""
echo -e "${YELLOW}🔐 Security Information:${NC}"
echo "Database Password: $DB_PASSWORD"
echo "Environment file: $APP_DIR/.env"
echo ""
echo -e "${GREEN}✅ Access URLs (after deployment):${NC}"
echo "Frontend: http://$TRUENAS_IP:3000"
echo "Backend API: http://$TRUENAS_IP:8000/docs"
echo ""
print_warning "Remember to change default admin credentials after first login!"
echo ""