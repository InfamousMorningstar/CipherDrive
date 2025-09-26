#!/bin/bash
# 🤖 CipherDrive Auto-Setup Robot
# This script does EVERYTHING for you automatically!

set -e  # Stop if anything goes wrong

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for fun
ROBOT="🤖"
CHECK="✅"
CROSS="❌"
ROCKET="🚀"
FOLDER="📁"
NETWORK="🌐"
KEY="🔐"
DOCKER="🐳"

echo -e "${BLUE}${ROBOT} CipherDrive Auto-Setup Robot${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}I'll do EVERYTHING for you! Just sit back and watch! ${ROCKET}${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${CYAN}${ROBOT} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get TrueNAS IP
print_status "Finding your TrueNAS IP address..."
TRUENAS_IP=$(hostname -I | awk '{print $1}')
if [ -z "$TRUENAS_IP" ]; then
    TRUENAS_IP="localhost"
fi
print_success "Found IP: $TRUENAS_IP"

# Check prerequisites
print_status "Checking if everything is ready..."

if ! command_exists curl; then
    print_error "curl is not installed. Installing..."
    apt-get update && apt-get install -y curl
fi

if ! command_exists docker; then
    print_error "Docker is not installed!"
    echo "Please install Docker first, then run this script again."
    exit 1
fi

# Check if Portainer is accessible
print_status "Checking if Portainer is running..."
if curl -s "http://$TRUENAS_IP:31015" > /dev/null; then
    print_success "Portainer is running!"
else
    print_warning "Cannot reach Portainer at http://$TRUENAS_IP:31015"
    print_warning "Make sure Portainer is installed and running"
fi

# Generate secure passwords
print_status "Generating super secure passwords..."
JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | base64)
DB_PASSWORD=$(openssl rand -base64 24 2>/dev/null || head -c 24 /dev/urandom | base64)
ADMIN_PASSWORD=$(openssl rand -base64 16 2>/dev/null || head -c 16 /dev/urandom | base64)
CIPHER_PASSWORD=$(openssl rand -base64 16 2>/dev/null || head -c 16 /dev/urandom | base64)
print_success "Generated secure passwords!"

# Create datasets function
create_dataset() {
    local dataset_path="$1"
    print_status "Creating dataset: $dataset_path"
    
    # Create directory if it doesn't exist
    if [ ! -d "$dataset_path" ]; then
        mkdir -p "$dataset_path"
        print_success "Created: $dataset_path"
    else
        print_success "Already exists: $dataset_path"
    fi
    
    # Set proper permissions
    chown -R 1000:1000 "$dataset_path" 2>/dev/null || true
    chmod -R 755 "$dataset_path" 2>/dev/null || true
}

# Create all required TrueNAS directories
print_status "${FOLDER} Creating TrueNAS storage folders..."
create_dataset "/mnt/app-pool/cipherdrive"
create_dataset "/mnt/app-pool/cipherdrive/uploads"
create_dataset "/mnt/app-pool/cipherdrive/logs"
create_dataset "/mnt/Centauri/cipherdrive"
create_dataset "/mnt/Centauri/cipherdrive/movies"
create_dataset "/mnt/Centauri/cipherdrive/tv"
print_success "All TrueNAS storage folders created!"

# Create Docker network
print_status "${NETWORK} Creating Docker network..."
if docker network ls | grep -q "proxy-net"; then
    print_success "Network 'proxy-net' already exists!"
else
    docker network create proxy-net
    print_success "Created network 'proxy-net'!"
fi

# Create .env file
print_status "${KEY} Creating environment configuration..."
cat > .env << EOF
# 🔐 CipherDrive Configuration (Auto-generated)
# Generated on: $(date)

# Security Settings
JWT_SECRET_KEY=$JWT_SECRET
CSRF_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | base64)

# Database Settings
POSTGRES_DB=cipherdrive_db
POSTGRES_USER=cipherdrive_user
POSTGRES_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://cipherdrive_user:$DB_PASSWORD@db:5432/cipherdrive_db

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_EMAIL=admin@cipherdrive.local
ADMIN_FULL_NAME=System Administrator

# Cipher User (Movies/TV only)
CIPHER_USERNAME=cipher
CIPHER_PASSWORD=$CIPHER_PASSWORD
CIPHER_EMAIL=cipher@cipherdrive.local
CIPHER_FULL_NAME=Media User

# File Storage
UPLOAD_BASE_DIR=/app/uploads
MAX_FILE_SIZE_BYTES=104857600
DEFAULT_USER_QUOTA=10737418240
DEFAULT_ADMIN_QUOTA=107374182400

# Email Settings (Configure these manually)
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Frontend Settings
VITE_API_BASE_URL=/api
VITE_APP_NAME=CipherDrive

# Logging
AUDIT_LOG_ENABLED=true
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
EOF
print_success "Environment file created!"

# Create simplified docker-compose.yml for auto-deployment
print_status "${DOCKER} Creating Docker Compose configuration..."
cat > docker-compose-auto.yml << EOF
version: '3.8'

services:
  # Database
  db:
    image: postgres:16-alpine
    container_name: cipherdrive-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: \${POSTGRES_DB}
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - proxy-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: cipherdrive-backend
    restart: unless-stopped
    environment:
      DATABASE_URL: \${DATABASE_URL}
      JWT_SECRET_KEY: \${JWT_SECRET_KEY}
      ADMIN_USERNAME: \${ADMIN_USERNAME}
      ADMIN_PASSWORD: \${ADMIN_PASSWORD}
      ADMIN_EMAIL: \${ADMIN_EMAIL}
      CIPHER_USERNAME: \${CIPHER_USERNAME}
      CIPHER_PASSWORD: \${CIPHER_PASSWORD}
      CIPHER_EMAIL: \${CIPHER_EMAIL}
      UPLOAD_BASE_DIR: \${UPLOAD_BASE_DIR}
      MAX_FILE_SIZE_BYTES: \${MAX_FILE_SIZE_BYTES}
      SMTP_ENABLED: \${SMTP_ENABLED}
      AUDIT_LOG_ENABLED: \${AUDIT_LOG_ENABLED}
      LOG_LEVEL: \${LOG_LEVEL}
    volumes:
      - /mnt/app-pool/cipherdrive/uploads:/app/uploads
      - /mnt/Centauri/cipherdrive:/mnt/media:ro
      - /mnt/app-pool/cipherdrive/logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    networks:
      - proxy-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_BASE_URL: \${VITE_API_BASE_URL}
    container_name: cipherdrive-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: \${VITE_API_BASE_URL}
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - proxy-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  proxy-net:
    external: true

volumes:
  db_data:
    driver: local
EOF
print_success "Docker Compose configuration created!"

# Deploy the stack
print_status "${ROCKET} Deploying CipherDrive..."
echo ""
echo -e "${YELLOW}🎬 Starting the magic show...${NC}"
echo ""

# Build and start services
docker-compose -f docker-compose-auto.yml up -d --build

print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service health..."
if docker-compose -f docker-compose-auto.yml ps | grep -q "Up"; then
    print_success "Services are running!"
else
    print_warning "Some services might not be ready yet..."
fi

# Save credentials for user
print_status "Saving your login credentials..."
cat > CREDENTIALS.txt << EOF
🎉 CipherDrive Setup Complete!
================================

🌐 Access your CipherDrive at:
   http://$TRUENAS_IP:3000

👨‍💼 Admin Login:
   Username: admin
   Password: $ADMIN_PASSWORD

🎬 Movie User Login:
   Username: cipher  
   Password: $CIPHER_PASSWORD

💾 Database Password: $DB_PASSWORD
🔐 JWT Secret: $JWT_SECRET

📅 Setup completed: $(date)
💻 TrueNAS IP: $TRUENAS_IP

⚠️  IMPORTANT: Keep this file safe and change passwords after first login!
EOF

print_success "Credentials saved to CREDENTIALS.txt"

# Final status check
echo ""
echo -e "${GREEN}🎊 SETUP COMPLETE! 🎊${NC}"
echo ""
echo -e "${CYAN}🌟 Your CipherDrive is ready!${NC}"
echo ""
echo -e "${YELLOW}📍 Access it at: ${GREEN}http://$TRUENAS_IP:3000${NC}"
echo ""
echo -e "${PURPLE}👨‍💼 Admin Login:${NC}"
echo -e "   Username: ${GREEN}admin${NC}"
echo -e "   Password: ${GREEN}$ADMIN_PASSWORD${NC}"
echo ""
echo -e "${PURPLE}🎬 Movie User Login:${NC}"
echo -e "   Username: ${GREEN}cipher${NC}"
echo -e "   Password: ${GREEN}$CIPHER_PASSWORD${NC}"
echo ""
echo -e "${RED}⚠️  Important: Change these passwords after your first login!${NC}"
echo ""
echo -e "${BLUE}📋 Your credentials are saved in: ${GREEN}CREDENTIALS.txt${NC}"
echo ""
echo -e "${CYAN}🎉 Enjoy your new secure file sharing platform!${NC}"

# Check if website is accessible
print_status "Testing if your website is working..."
sleep 5
if curl -s "http://$TRUENAS_IP:3000" > /dev/null; then
    print_success "Website is UP and running! 🚀"
else
    print_warning "Website might still be starting up. Give it a few more minutes."
    print_warning "If it doesn't work, check: docker-compose -f docker-compose-auto.yml logs"
fi

echo ""
echo -e "${GREEN}${ROBOT} Robot job complete! You're all set! ${ROCKET}${NC}"