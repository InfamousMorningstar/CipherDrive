# CipherDrive Portainer Deployment Guide

## Prerequisites

1. **TrueNAS SCALE** with Portainer installed
2. **GitHub Repository**: https://github.com/InfamousMorningstar/CipherDrive
3. **Datasets Created**:
   - SSD Pool (`app-pool`): postgres, logs
   - HDD Pool (`Centauri`): uploads, shares, ssl

## Step 1: Prepare TrueNAS Directories

SSH into your TrueNAS and run:

```bash
# Create required directories
mkdir -p /mnt/app-pool/cipherdrive/{postgres,logs}
mkdir -p /mnt/Centauri/cipherdrive/{uploads,shares,ssl}

# Set proper permissions
chmod -R 755 /mnt/app-pool/cipherdrive
chmod -R 755 /mnt/Centauri/cipherdrive
chmod 700 /mnt/app-pool/cipherdrive/postgres
```

## Step 2: Deploy via Portainer

### Option A: Using Docker Compose Stack (Recommended)

1. **Access Portainer**: Navigate to your TrueNAS Portainer interface
2. **Create Stack**:
   - Go to **Stacks** → **Add stack**
   - Name: `cipherdrive`
   - Build method: **Git Repository**

3. **Repository Configuration**:
   - Repository URL: `https://github.com/InfamousMorningstar/CipherDrive`
   - Repository reference: `refs/heads/main`
   - Compose path: `docker-compose.portainer.yml`
   - AutoSync: ✅ Enable (for automatic updates)

4. **Environment Variables**:
   ```env
   POSTGRES_PASSWORD=your_secure_database_password
   JWT_SECRET_KEY=your_32_char_jwt_secret_key
   JWT_REFRESH_SECRET_KEY=your_32_char_refresh_secret
   ADMIN_EMAIL=admin@cipherdrive.local
   ADMIN_PASSWORD=your_secure_admin_password
   FRONTEND_URL=http://YOUR_TRUENAS_IP:8069
   ALLOWED_ORIGINS=http://YOUR_TRUENAS_IP:8069,http://localhost:8069
   ```

5. **Deploy**: Click **Deploy the stack**

### Option B: Using Stack File Upload

1. **Download Compose File**: Save `docker-compose.portainer.yml` from GitHub
2. **Upload Method**:
   - Build method: **Upload**
   - Upload the `docker-compose.portainer.yml` file
   - Add environment variables as above

## Step 3: Monitor Deployment

1. **Check Containers**: Go to **Containers** in Portainer
2. **Expected Containers**:
   - `cipherdrive_db` (PostgreSQL)
   - `cipherdrive_backend` (FastAPI)
   - `cipherdrive_frontend` (React)

3. **Check Logs**: Click on each container to view logs
4. **Health Status**: All containers should show "healthy" status

## Step 4: Access CipherDrive

- **Frontend**: http://YOUR_TRUENAS_IP:8069
- **Backend API**: http://YOUR_TRUENAS_IP:8000/docs
- **Admin Login**: Use ADMIN_EMAIL and ADMIN_PASSWORD from environment

## Step 5: Configure Reverse Proxy (Optional)

If using Cloudflare Tunnel or Nginx Proxy Manager:

1. **Frontend**: Point to `cipherdrive_frontend:8069`
2. **API**: Point `/api/*` to `cipherdrive_backend:8000`

## Troubleshooting

### Container Build Issues
```bash
# Check build logs in Portainer
# Or manually build:
docker build https://github.com/InfamousMorningstar/CipherDrive.git#main -f backend/Dockerfile
```

### Database Connection Issues
```bash
# Check database logs
docker logs cipherdrive_db

# Verify database is accessible
docker exec cipherdrive_db psql -U cipherdrive_user -d cipherdrive_db -c "SELECT 1;"
```

### Permission Issues
```bash
# Fix file permissions
chmod -R 755 /mnt/app-pool/cipherdrive
chmod -R 755 /mnt/Centauri/cipherdrive
chown -R 999:999 /mnt/app-pool/cipherdrive/postgres
```

## Updates

With AutoSync enabled, Portainer will automatically pull updates from GitHub. To manually update:

1. Go to **Stacks** → **cipherdrive**
2. Click **Update the stack**
3. Portainer will pull latest changes and redeploy

## Backup Strategy

```bash
# Database backup
docker exec cipherdrive_db pg_dump -U cipherdrive_user cipherdrive_db > backup.sql

# File backup
tar -czf uploads_backup.tar.gz /mnt/Centauri/cipherdrive/uploads
```