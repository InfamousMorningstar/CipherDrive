#!/bin/bash
# Direct deployment script - bypassing cache issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'  
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🤖 CipherDrive Direct Deploy${NC}"
echo -e "${BLUE}============================${NC}"
echo ""

# Get TrueNAS IP
TRUENAS_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}✅ TrueNAS IP: $TRUENAS_IP${NC}"

# Clean up any existing installation
echo -e "${CYAN}🤖 Cleaning up existing installation...${NC}"
rm -rf CipherDrive
docker compose down 2>/dev/null || true
docker system prune -f

# Clone repository
echo -e "${CYAN}🤖 Downloading CipherDrive...${NC}"
git clone https://github.com/InfamousMorningstar/CipherDrive.git
cd CipherDrive

# Generate passwords
JWT_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -base64 24)
ADMIN_PASSWORD=$(openssl rand -base64 16)

# Create environment file
cat > .env << EOF
# Database Configuration
POSTGRES_DB=cipherdrive_db
POSTGRES_USER=cipherdrive_user  
POSTGRES_PASSWORD=$DB_PASSWORD

# JWT Configuration
JWT_SECRET=$JWT_SECRET

# Admin Configuration
ADMIN_EMAIL=admin@cipherdrive.local
ADMIN_PASSWORD=$ADMIN_PASSWORD

# Application URLs
FRONTEND_URL=http://$TRUENAS_IP:8069
EOF

echo -e "${GREEN}✅ Configuration created${NC}"

# Deploy using the actual docker-compose.yml
echo -e "${CYAN}🤖 Deploying CipherDrive...${NC}"
docker compose up -d --build

echo -e "${GREEN}✅ Deployment started!${NC}"
echo ""
echo -e "${YELLOW}📍 Access CipherDrive at: http://$TRUENAS_IP:8069${NC}"
echo -e "${YELLOW}🔑 Admin password: $ADMIN_PASSWORD${NC}"
echo ""
echo -e "${CYAN}Check status with: docker compose ps${NC}"
echo -e "${CYAN}View logs with: docker compose logs -f${NC}"