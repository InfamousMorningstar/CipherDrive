# TrueNAS SCALE Deployment Guide

This guide provides detailed instructions for deploying CipherDrive on TrueNAS SCALE using Portainer.

## Prerequisites

- TrueNAS SCALE 22.02 or later
- Portainer CE installed and configured
- At least 2GB RAM available for the application
- 10GB+ storage space for uploads and database

## Step-by-Step Deployment

### 1. Prepare Storage Pool

1. **Create Dataset**
   ```
   Storage → Pools → Create Dataset
   Name: cipherdrive
   Path: /mnt/your-pool/cipherdrive
   ```

2. **Create Subdirectories**
   - Navigate to System → Shell
   ```bash
   mkdir -p /mnt/your-pool/cipherdrive/{postgres,uploads,ssl}
   chmod -R 755 /mnt/your-pool/cipherdrive
   ```

### 2. Access Portainer

1. Navigate to your TrueNAS SCALE interface
2. Go to Apps → Installed Applications
3. Click on Portainer to access the web interface
4. Default URL: `http://your-truenas-ip:9000`

### 3. Create Docker Network

1. In Portainer, go to Networks → Add network
   - Name: `cipherdrive-network`
   - Driver: bridge
   - Click "Create the network"

### 4. Deploy via Stack

1. **Navigate to Stacks**
   - Click "Stacks" in the left sidebar
   - Click "Add stack"
   - Name: `cipherdrive`

2. **Stack Configuration**
   Copy and paste the following docker-compose configuration:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: cipherdrive-postgres
    environment:
      POSTGRES_USER: cipherdrive_user
      POSTGRES_PASSWORD: change_this_secure_password_123
      POSTGRES_DB: cipherdrive_db
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - /mnt/your-pool/cipherdrive/postgres:/var/lib/postgresql/data
    networks:
      - cipherdrive-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cipherdrive_user -d cipherdrive_db"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  backend:
    image: python:3.11-slim
    container_name: cipherdrive-backend
    working_dir: /app
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://cipherdrive_user:change_this_secure_password_123@postgres:5432/cipherdrive_db
      JWT_SECRET_KEY: your-super-secure-jwt-secret-key-change-this-in-production
      JWT_REFRESH_SECRET_KEY: your-super-secure-refresh-secret-change-this-too
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
      ALLOWED_ORIGINS: http://localhost:3000,http://your-truenas-ip:3000
      UPLOAD_DIR: /app/uploads
      MAX_FILE_SIZE: 104857600
      ENVIRONMENT: production
    volumes:
      - /mnt/your-pool/cipherdrive/uploads:/app/uploads
      - /mnt/your-pool/cipherdrive/backend:/app
    command: |
      bash -c "
        pip install fastapi[all] sqlalchemy psycopg2-binary python-multipart \
                   python-jose[cryptography] passlib[bcrypt] python-decouple \
                   slowapi pillow jinja2 aiofiles uvicorn[standard] &&
        python -c 'from app.database import init_database; init_database()' &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000
      "
    ports:
      - "8000:8000"
    networks:
      - cipherdrive-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    image: node:18-alpine
    container_name: cipherdrive-frontend
    working_dir: /app
    depends_on:
      - backend
    environment:
      REACT_APP_API_URL: http://your-truenas-ip:8000
    volumes:
      - /mnt/your-pool/cipherdrive/frontend:/app
    command: |
      sh -c "
        npm install &&
        npm install react react-dom react-router-dom axios react-hot-toast \
                   framer-motion @heroicons/react zustand tailwindcss \
                   @tailwindcss/forms postcss autoprefixer &&
        npm run build &&
        npx serve -s build -l 3000
      "
    ports:
      - "3000:3000"
    networks:
      - cipherdrive-network
    restart: unless-stopped

networks:
  cipherdrive-network:
    external: false
```

3. **Important Replacements**
   Before deploying, replace the following placeholders:
   - `your-pool`: Your actual TrueNAS pool name
   - `your-truenas-ip`: Your TrueNAS server IP address
   - `change_this_secure_password_123`: A strong database password
   - `your-super-secure-jwt-secret-key-change-this-in-production`: A strong JWT secret
   - `your-super-secure-refresh-secret-change-this-too`: A strong refresh token secret

### 5. Upload Application Files

Since we're using volume mounts, you need to upload the application files to your TrueNAS server:

1. **Using TrueNAS Web Interface**
   - Go to Storage → your-pool → cipherdrive
   - Create folders: `backend`, `frontend`
   - Upload all backend files to the backend folder
   - Upload all frontend files to the frontend folder

2. **Using SCP/SFTP** (Recommended)
   ```bash
   # From your local machine
   scp -r backend/ root@your-truenas-ip:/mnt/your-pool/cipherdrive/
   scp -r frontend/ root@your-truenas-ip:/mnt/your-pool/cipherdrive/
   ```

3. **Using Shell** (if files are already on TrueNAS)
   ```bash
   # In TrueNAS Shell
   cd /mnt/your-pool/cipherdrive
   # Copy your application files here
   ```

### 6. Deploy the Stack

1. After configuring the stack YAML, click "Deploy the stack"
2. Wait for all services to start (this may take several minutes on first run)
3. Monitor the logs for any errors:
   - Click on the stack name
   - View logs for each service

### 7. Verify Deployment

1. **Check Service Status**
   - In Portainer, go to Containers
   - Ensure all containers are "Running"

2. **Access Application**
   - Frontend: `http://your-truenas-ip:3000`
   - Backend API: `http://your-truenas-ip:8000/docs`

3. **Create Admin User**
   - Navigate to the frontend
   - Use the registration form to create your first admin user

## Alternative: Apps Catalog Installation

If you prefer using the TrueNAS SCALE Apps catalog:

### 1. Create Custom App

1. **Prepare Chart**
   ```bash
   # Create Helm chart structure
   mkdir -p cipherdrive-chart/{templates,charts}
   ```

2. **Chart.yaml**
   ```yaml
   apiVersion: v2
   name: cipherdrive
   description: Secure file sharing platform
   version: 1.0.0
   appVersion: "1.0.0"
   ```

3. **values.yaml**
   ```yaml
   postgresql:
     enabled: true
     auth:
       username: cipherdrive_user
       password: secure_password
       database: cipherdrive_db
   
   backend:
     image: your-registry/cipherdrive-backend:latest
     replicaCount: 1
   
   frontend:
     image: your-registry/cipherdrive-frontend:latest
     replicaCount: 1
   ```

## Networking Configuration

### Port Forwarding (Optional)

To access from outside your network:

1. **Router Configuration**
   - Forward port 3000 to your TrueNAS IP
   - Forward port 8000 for direct API access (optional)

2. **TrueNAS Firewall**
   ```bash
   # Allow ports through TrueNAS firewall
   iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
   iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
   ```

### Reverse Proxy with Nginx Proxy Manager

For better security and SSL:

1. **Install Nginx Proxy Manager** via TrueNAS Apps
2. **Create Proxy Host**
   - Domain: `cipherdrive.yourdomain.com`
   - Forward to: `your-truenas-ip:3000`
   - Enable SSL with Let's Encrypt

## Monitoring and Maintenance

### Health Checks

Create a monitoring script:

```bash
#!/bin/bash
# /mnt/your-pool/cipherdrive/health-check.sh

echo "Checking CipherDrive services..."

# Check if containers are running
docker ps --filter "name=cipherdrive" --format "table {{.Names}}\t{{.Status}}"

# Check disk usage
df -h /mnt/your-pool/cipherdrive/

# Check database connection
docker exec cipherdrive-postgres pg_isready -U cipherdrive_user

echo "Health check complete."
```

### Automated Backups

```bash
#!/bin/bash
# /mnt/your-pool/cipherdrive/backup.sh

BACKUP_DIR="/mnt/your-pool/backups/cipherdrive"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec cipherdrive-postgres pg_dump -U cipherdrive_user cipherdrive_db > $BACKUP_DIR/database_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /mnt/your-pool/cipherdrive/uploads

# Keep only last 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Cron Jobs

Add to TrueNAS cron jobs:

```bash
# Daily backup at 2 AM
0 2 * * * /mnt/your-pool/cipherdrive/backup.sh

# Weekly health check
0 8 * * 1 /mnt/your-pool/cipherdrive/health-check.sh
```

## Troubleshooting TrueNAS Specific Issues

### Container Won't Start

```bash
# Check container logs
docker logs cipherdrive-backend
docker logs cipherdrive-frontend
docker logs cipherdrive-postgres

# Check permissions
ls -la /mnt/your-pool/cipherdrive/
chmod -R 755 /mnt/your-pool/cipherdrive/
```

### Database Issues

```bash
# Reset database
docker stop cipherdrive-postgres
rm -rf /mnt/your-pool/cipherdrive/postgres/*
docker start cipherdrive-postgres
```

### Network Connectivity

```bash
# Check network
docker network ls | grep cipherdrive
docker network inspect cipherdrive-network

# Test connectivity
docker exec cipherdrive-backend ping postgres
```

### Performance Issues

1. **Increase Container Resources**
   ```yaml
   # Add to service definition
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '0.5'
   ```

2. **Optimize PostgreSQL**
   ```yaml
   postgres:
     environment:
       POSTGRES_INITDB_ARGS: "--data-checksums"
     command: postgres -c shared_buffers=256MB -c max_connections=100
   ```

## Security Considerations

1. **Change Default Passwords**
   - Update all default passwords in the configuration
   - Use strong, unique passwords for database and JWT secrets

2. **Network Security**
   - Consider using a VPN for external access
   - Implement proper firewall rules
   - Use HTTPS with SSL certificates

3. **Regular Updates**
   - Keep TrueNAS SCALE updated
   - Update container images regularly
   - Monitor security advisories

## Support

For TrueNAS SCALE specific issues:
- Check TrueNAS SCALE documentation
- Review Portainer logs
- Consult TrueNAS community forums
- Verify system resources and storage availability