# CipherDrive - Secure File Sharing Platform

A secure, feature-rich file sharing platform designed for TrueNAS SCALE deployment with Cloudflare Tunnel integration.



## FeaturesA secure, feature-rich file sharing platform designed for TrueNAS SCALE deployment with Cloudflare Tunnel integration.A modern, lightweight file sharing and storage solution designed for deployment on TrueNAS SCALE servers using Docker and Portainer. Built with FastAPI backend, React frontend, and PostgreSQL database.



- **Role-Based Access Control**: Admin, normal user, and cipher (download-only) user roles

- **Secure File Sharing**: Expiring links with download limits

- **Comprehensive Audit Logging**: Track all user activities and file operations## 🚀 Features## 🚀 Features

- **Storage Quotas**: Configurable per-user storage limits

- **Multi-Format Support**: Images, videos, audio, documents, and more

- **Modern UI**: React frontend with TailwindCSS and Framer Motion

- **Docker Ready**: Full containerization with Docker Compose- **Role-Based Access Control**: Admin, normal user, and cipher (download-only) user roles### Core Features

- **TrueNAS Integration**: Optimized for TrueNAS SCALE datasets

- **Cloudflare Tunnel**: Secure external access without port forwarding- **Secure File Sharing**: Expiring links with download limits- **Secure Authentication**: JWT-based auth with bcrypt password hashing



## Quick Start- **Comprehensive Audit Logging**: Track all user activities and file operations- **File Management**: Upload, download, organize files in folders



### Automated Setup (Recommended)- **Storage Quotas**: Configurable per-user storage limits- **File Sharing**: Generate shareable links with expiry dates and download limits



For TrueNAS SCALE, use the automated setup script:- **Multi-Format Support**: Images, videos, audio, documents, and more- **User Management**: Admin panel for user administration and quota management



```bash- **Modern UI**: React frontend with TailwindCSS and Framer Motion- **File Preview**: Built-in preview for images, text files, and PDFs

# Make script executable

chmod +x auto-setup.sh- **Docker Ready**: Full containerization with Docker Compose- **Responsive UI**: Modern, mobile-friendly interface with dark/light themes



# Run the setup- **TrueNAS Integration**: Optimized for TrueNAS SCALE datasets

./auto-setup.sh

```- **Cloudflare Tunnel**: Secure external access without port forwarding### Security Features



The script will:- CSRF and XSS protection

- Create all necessary TrueNAS datasets

- Generate secure passwords## 🏗️ Architecture- Rate limiting to prevent abuse

- Set up Docker networks

- Deploy all services- Security headers (CSP, HSTS, etc.)

- Provide login credentials

### Backend (FastAPI)- File type and size validation

### Manual Setup

- **Authentication**: JWT tokens with bcrypt password hashing- Audit logging for all operations

#### 1. Prerequisites

- **Database**: PostgreSQL 16 with SQLAlchemy ORM- Password strength validation

- TrueNAS SCALE 22.02 or later

- Docker and Docker Compose- **Security**: Rate limiting, CSRF protection, security headers

- Cloudflare account (for tunnel setup)

- **File Management**: Upload, download, delete with quota enforcement### Admin Features

#### 2. Create TrueNAS Datasets

- **Sharing**: Secure links with expiration and download limits- User management and quota control

```bash

# Create datasets in TrueNAS web interface:- **Audit Trail**: Comprehensive logging to file and database- System monitoring and audit logs

/mnt/app-pool/cipherdrive/uploads    # User uploads

/mnt/Centauri/cipherdrive/movies     # Cipher user movies- Bulk operations and file management

/mnt/Centauri/cipherdrive/tv         # Cipher user TV shows

```### Frontend (React + Vite)- Storage analytics and reporting



#### 3. Configure Environment- **Modern Stack**: React 18, TailwindCSS, Framer Motion



```bash- **Responsive Design**: Mobile-first approach## 🏗️ Architecture

# Copy and edit environment file

cp .env.example .env- **Real-time Updates**: WebSocket integration

nano .env

```- **File Preview**: Support for images, videos, documents```



Key settings to change:
- **Admin Panel**: User management and system monitoring

cipherdrive/
├── backend/                 # FastAPI backend

- `ADMIN_PASSWORD`: Set admin user password

- `CIPHER_PASSWORD`: Set cipher user password## 📋 Prerequisites│   ├── app/



#### 4. Deploy│   │   ├── main.py         # FastAPI application



```bash- TrueNAS SCALE 22.02 or later│   │   ├── auth.py         # Authentication & JWT

# Create external network

docker network create proxy-net- Docker and Docker Compose│   │   ├── users.py        # User management



# Start services- Cloudflare account (for tunnel setup)│   │   ├── files.py        # File operations

docker-compose up -d

```- SMTP server (for email notifications)│   │   ├── models.py       # SQLAlchemy models



## User Roles│   │   ├── database.py     # Database configuration



### Admin User## 🚀 Quick Start│   │   ├── security.py     # Security middleware

- **Username**: admin (configurable)

- **Capabilities**: Full system access, user management, all file operations│   │   └── utils.py        # Utility functions

- **Default Quota**: 100GB

### 1. Clone the Repository│   ├── uploads/            # File storage directory

### Regular User  

- **Capabilities**: File upload/download, sharing, personal storage│   ├── Dockerfile          # Backend container config

- **Default Quota**: 10GB

```bash│   └── requirements.txt    # Python dependencies

### Cipher User

- **Username**: cipher (configurable)git clone https://github.com/yourusername/CipherDrive.git├── frontend/               # React frontend

- **Capabilities**: Download-only access to movies and TV shows

- **Quota**: Unlimitedcd CipherDrive│   ├── src/

- **Restrictions**: Cannot upload files or create shares

```│   │   ├── components/     # React components

## TrueNAS SCALE Deployment

│   │   ├── store/          # Zustand state management

### Option 1: Portainer (Recommended)

### 2. Configure Environment│   │   └── utils/          # Frontend utilities

1. Install Portainer from TrueNAS SCALE Apps

2. Create Stack named `cipherdrive`│   ├── Dockerfile          # Frontend container config

3. Copy `docker-compose.yml` content

4. Set environment variables from `.env````bash│   └── package.json        # Node.js dependencies

5. Deploy stack

# Copy the example environment file├── docker-compose.yml      # Multi-service orchestration

### Option 2: CLI Deployment

cp .env.example .env└── .env.example           # Environment variables template

```bash

# SSH into TrueNAS SCALE```

ssh admin@your-truenas-ip

# Edit the environment file with your settings

# Navigate to app directory

cd /mnt/app-pool/cipherdrive-confignano .env## 📋 Prerequisites



# Upload project files (docker-compose.yml, .env)```

# Create network and deploy

docker network create proxy-net### For TrueNAS SCALE Deployment:

docker-compose up -d

```Key configuration items:- TrueNAS SCALE 22.02 or later



## Cloudflare Tunnel Setup- `JWT_SECRET_KEY`: Generate with `openssl rand -hex 32`- Portainer CE installed and configured



### 1. Create Tunnel- `POSTGRES_PASSWORD`: Use a strong database password- At least 2GB RAM allocated for the application



```bash- `ADMIN_PASSWORD`: Set admin user password- 10GB+ storage space for uploads

# Install cloudflared

curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb- `CIPHER_PASSWORD`: Set cipher user password

sudo dpkg -i cloudflared.deb

- `SMTP_*`: Configure email settings### For Development:

# Login and create tunnel

cloudflared tunnel login- `TRUENAS_*_PATH`: Adjust for your dataset paths- Docker and Docker Compose

cloudflared tunnel create cipherdrive

```- Node.js 18+ (for frontend development)



### 2. Configure DNS### 3. Set Up TrueNAS Datasets- Python 3.9+ (for backend development)



In Cloudflare Dashboard:- PostgreSQL (for database)

- Add CNAME record pointing to your tunnel

- Name: `files` (or preferred subdomain)Create the following datasets in TrueNAS:

- Target: `TUNNEL-ID.cfargotunnel.com`

```bash## 🚢 Deployment on TrueNAS SCALE

### 3. Configure Ingress

/mnt/app-pool/cipherdrive/uploads    # User uploads

Create tunnel configuration:

```yaml/mnt/Centauri/cipherdrive/movies     # Cipher user movies### Method 1: Using Portainer (Recommended)

tunnel: TUNNEL-ID

credentials-file: /root/.cloudflared/TUNNEL-ID.json/mnt/Centauri/cipherdrive/tv         # Cipher user TV shows



ingress:```1. **Access Portainer**

  - hostname: files.yourdomain.com

    service: http://cipherdrive-frontend:3000   - Navigate to your TrueNAS SCALE Portainer interface

  - service: http_status:404

```### 4. Create External Network   - Usually accessible at `http://your-truenas-ip:9000`



## Configuration



### Environment Variables```bash2. **Create Docker Network**



Key configuration options in `.env`:# Create the proxy network for Cloudflare Tunnel   ```bash



```bashdocker network create proxy-net   # In Portainer Console or TrueNAS Shell

# Security

JWT_SECRET_KEY=your-jwt-secret```   docker network create dropbox-lite-network

POSTGRES_PASSWORD=your-db-password

   ```

# Users  

ADMIN_USERNAME=admin### 5. Deploy with Docker Compose

ADMIN_PASSWORD=your-admin-password

CIPHER_USERNAME=cipher3. **Setup Environment Variables**

CIPHER_PASSWORD=your-cipher-password

```bash   - In Portainer, go to "Stacks" → "Add Stack"

# Storage

MAX_FILE_SIZE_BYTES=104857600  # 100MB# Start all services   - Name: `dropbox-lite`

DEFAULT_USER_QUOTA=10737418240  # 10GB

docker-compose up -d   - Copy the docker-compose.yml content below

# Email (optional)

SMTP_HOST=smtp.gmail.com

SMTP_USERNAME=your-email@gmail.com

SMTP_PASSWORD=your-app-password# Check logs4. **Configure Storage**

```

docker-compose logs -f   ```yaml

### File Storage Paths

   # Add to your docker-compose.yml volumes section

```

/mnt/app-pool/cipherdrive/uploads/  # User uploads# Check service status   volumes:

/mnt/Centauri/cipherdrive/movies/   # Movies (cipher access)

/mnt/Centauri/cipherdrive/tv/       # TV shows (cipher access)docker-compose ps     postgres_data:

/mnt/app-pool/cipherdrive/logs/     # Application logs

``````       driver: local



## Security Features       driver_opts:



- **JWT Authentication** with access and refresh tokens## 🔧 TrueNAS SCALE Deployment         type: none

- **bcrypt Password Hashing** for secure credential storage

- **Rate Limiting** on sensitive endpoints         o: bind

- **CSRF Protection** for web requests

- **Security Headers** (HSTS, CSP, X-Frame-Options)### Option 1: Portainer (Recommended)         device: /mnt/your-pool/dropbox-lite/postgres

- **Input Validation** and sanitization

- **Comprehensive Audit Logging** to file and database     uploads:



## Monitoring1. **Install Portainer** from TrueNAS SCALE Apps       driver: local  



### Health Checks2. **Create Stack**:       driver_opts:



```bash   - Name: `cipherdrive`         type: none

# Check service health

curl http://your-ip:3000/api/health   - Compose file: Copy contents of `docker-compose.yml`         o: bind



# View logs   - Environment variables: Copy from `.env`         device: /mnt/your-pool/dropbox-lite/uploads

docker-compose logs -f backend

docker exec cipherdrive-backend tail -f /app/logs/audit.log   ```

```

3. **Configure Volumes**:

### Database Maintenance

   - Ensure dataset paths exist: `/mnt/app-pool/cipherdrive/uploads`5. **Deploy Stack**

```bash

# Backup database   - Set proper permissions: `chown -R 1000:1000 /mnt/app-pool/cipherdrive`   - Paste the configuration and click "Deploy the stack"

docker exec cipherdrive-db pg_dump -U cipherdrive_user cipherdrive_db > backup.sql

   - Wait for all services to start (check logs for any issues)

# View database stats

docker exec cipherdrive-backend python -c "from app.database import get_database_stats; print(get_database_stats())"### Option 2: CLI Deployment

```

### Method 2: Command Line Deployment

## Troubleshooting

```bash

### Common Issues

# SSH into TrueNAS SCALE1. **Prepare Directories**

**Permission denied errors:**

```bashssh admin@your-truenas-ip   ```bash

sudo chown -R 1000:1000 /mnt/app-pool/cipherdrive

sudo chown -R 1000:1000 /mnt/Centauri/cipherdrive   # Create app directory

```

# Create project directory   mkdir -p /mnt/your-pool/dropbox-lite

**Database connection issues:**

- Verify PostgreSQL container is runningmkdir -p /mnt/app-pool/cipherdrive-config   cd /mnt/your-pool/dropbox-lite

- Check database credentials in `.env`

- Ensure network connectivity between containerscd /mnt/app-pool/cipherdrive-config   



**File upload issues:**   # Create required directories

- Check available disk space

- Verify upload directory permissions# Upload docker-compose.yml and .env files   mkdir -p postgres uploads

- Review file size limits in configuration

# (Use SCP or web interface)   chmod 755 uploads

### Debug Mode

   ```

Enable detailed logging:

```bash# Create external network

# In .env file

DEBUG=truedocker network create proxy-net2. **Download Application**

LOG_LEVEL=DEBUG

   ```bash

# Restart services

docker-compose restart# Start services   # Clone or copy the application files

```

docker-compose up -d   git clone <your-repo> .

## API Documentation

```   # OR upload the project files manually

Interactive API documentation available at:

- Swagger UI: `http://your-ip:3000/api/docs`   ```

- ReDoc: `http://your-ip:3000/api/redoc`

## 🌐 Cloudflare Tunnel Setup

## Development

3. **Configure Environment**

### Local Development

### 1. Create Tunnel   ```bash

```bash

# Backend   # Copy and edit environment variables

cd backend

python -m venv venv```bash   cp .env.example .env

source venv/bin/activate

pip install -r requirements.txt# Install cloudflared   nano .env

uvicorn app.main:app --reload

curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb   ```

# Frontend  

cd frontendsudo dpkg -i cloudflared.deb

npm install

npm run dev4. **Deploy Services**

```

# Login to Cloudflare   ```bash

### Testing

cloudflared tunnel login   docker-compose up -d

```bash

# Backend tests   ```

cd backend

pytest# Create tunnel



# Frontend testscloudflared tunnel create cipherdrive## ⚙️ Configuration

cd frontend  

npm test

```

# Note the tunnel ID from output### Environment Variables

## Contributing

```

1. Fork the repository

2. Create a feature branchCreate a `.env` file with the following variables:

3. Make changes with tests

4. Submit a pull request### 2. Configure DNS



## License```bash



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.In Cloudflare Dashboard:# Database Configuration



## Support1. Go to **DNS** sectionDATABASE_URL=postgresql://dropbox_user:secure_password@postgres:5432/dropbox_lite



- **Issues**: Open an issue on GitHub2. Add CNAME record:POSTGRES_USER=dropbox_user

- **Documentation**: Check this README and inline code comments

- **Security**: Report security issues privately to the maintainers   - Name: `files` (or your preferred subdomain)POSTGRES_PASSWORD=secure_password



---   - Target: `TUNNEL-ID.cfargotunnel.com`POSTGRES_DB=dropbox_lite



**CipherDrive** - Secure file sharing for the modern age 🔐

### 3. Configure Tunnel# JWT Configuration

JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here

Create `config.yml`:JWT_REFRESH_SECRET_KEY=your-super-secure-refresh-secret-here

```yamlACCESS_TOKEN_EXPIRE_MINUTES=30

tunnel: TUNNEL-IDREFRESH_TOKEN_EXPIRE_DAYS=7

credentials-file: /root/.cloudflared/TUNNEL-ID.json

# Email Configuration (Optional)

ingress:SMTP_HOST=smtp.gmail.com

  - hostname: files.yourdomain.comSMTP_PORT=587

    service: http://cipherdrive-frontend:3000SMTP_USERNAME=your-email@gmail.com

    originRequest:SMTP_PASSWORD=your-app-password

      noTLSVerify: trueSMTP_FROM_EMAIL=your-email@gmail.com

  - service: http_status:404

```# Application Configuration

ALLOWED_ORIGINS=http://localhost:3000,http://your-truenas-ip:3000

### 4. Add to Docker ComposeUPLOAD_DIR=/app/uploads

MAX_FILE_SIZE=100000000

Add Cloudflare tunnel service to `docker-compose.yml`:ENVIRONMENT=production

```yaml

  cloudflare-tunnel:# File Storage Configuration

    image: cloudflare/cloudflared:latestDEFAULT_USER_QUOTA_GB=5

    container_name: cipherdrive-tunnelMAX_UPLOAD_SIZE_MB=100

    restart: unless-stoppedALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf,doc,docx,txt,zip

    command: tunnel --no-autoupdate run

    environment:# Security Configuration

      - TUNNEL_TOKEN=YOUR_TUNNEL_TOKENRATE_LIMIT_REQUESTS=100

    networks:RATE_LIMIT_WINDOW=3600

      - proxy-netCSRF_SECRET=your-csrf-secret-key

``````



## 🔐 Security Configuration### Docker Compose Configuration



### 1. Generate Secure Secrets```yaml

version: '3.8'

```bash

# JWT Secretservices:

openssl rand -hex 32  postgres:

    image: postgres:15

# CSRF Secret    container_name: dropbox-lite-postgres

openssl rand -hex 32    environment:

      POSTGRES_USER: ${POSTGRES_USER}

# Database Password      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

openssl rand -base64 32      POSTGRES_DB: ${POSTGRES_DB}

```    volumes:

      - postgres_data:/var/lib/postgresql/data

### 2. Set Proper Permissions    networks:

      - dropbox-lite-network

```bash    restart: unless-stopped

# Upload directories    healthcheck:

sudo chown -R 1000:1000 /mnt/app-pool/cipherdrive      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]

sudo chmod -R 755 /mnt/app-pool/cipherdrive      interval: 30s

      timeout: 10s

# Movie/TV directories (cipher user access)      retries: 3

sudo chown -R 1000:1000 /mnt/Centauri/cipherdrive

sudo chmod -R 755 /mnt/Centauri/cipherdrive  backend:

```    build: ./backend

    container_name: dropbox-lite-backend

### 3. Firewall Configuration    depends_on:

      postgres:

```bash        condition: service_healthy

# Only allow necessary ports (if not using Cloudflare Tunnel)    environment:

ufw allow 80/tcp      - DATABASE_URL=${DATABASE_URL}

ufw allow 443/tcp      - JWT_SECRET_KEY=${JWT_SECRET_KEY}

ufw deny 8000/tcp  # Block direct backend access      - JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY}

```      - SMTP_HOST=${SMTP_HOST}

      - SMTP_PORT=${SMTP_PORT}

## 👥 User Management      - SMTP_USERNAME=${SMTP_USERNAME}

      - SMTP_PASSWORD=${SMTP_PASSWORD}

### Default Users      - SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL}

    volumes:

After deployment, three users are created:      - uploads:/app/uploads

    networks:

1. **Admin User**      - dropbox-lite-network

   - Username: `admin`    restart: unless-stopped

   - Role: Admin (full access)    healthcheck:

   - Can: Manage users, access all files, system administration      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

      interval: 30s

2. **Cipher User**      timeout: 10s

   - Username: `cipher`      retries: 3

   - Role: Cipher (download-only)

   - Can: Only access movies and TV shows, download only  frontend:

    build: ./frontend

### Adding Users    container_name: dropbox-lite-frontend

    depends_on:

Via Admin Panel:      - backend

1. Login as admin    ports:

2. Go to Admin Panel      - "3000:80"

3. Click "Add User"    networks:

4. Set role and quota limits      - dropbox-lite-network

    restart: unless-stopped

Via API:

```bash  nginx:

curl -X POST "https://files.yourdomain.com/api/admin/users" \    image: nginx:alpine

  -H "Authorization: Bearer YOUR_TOKEN" \    container_name: dropbox-lite-nginx

  -H "Content-Type: application/json" \    depends_on:

  -d '{      - backend

    "username": "newuser",      - frontend

    "email": "user@domain.com",    ports:

    "password": "secure_password",      - "80:80"

    "full_name": "New User",      - "443:443"

    "role": "user",    volumes:

    "quota_bytes": 10737418240      - ./nginx.conf:/etc/nginx/nginx.conf:ro

  }'      - ./ssl:/etc/nginx/ssl:ro

```    networks:

      - dropbox-lite-network

## 📊 Monitoring & Maintenance    restart: unless-stopped



### Health Checksvolumes:

  postgres_data:

```bash    driver: local

# Check service health    driver_opts:

curl https://files.yourdomain.com/api/health      type: none

      o: bind

# Check frontend health      device: /mnt/your-pool/dropbox-lite/postgres

curl https://files.yourdomain.com/health  uploads:

```    driver: local

    driver_opts:

### Logs      type: none

      o: bind

```bash      device: /mnt/your-pool/dropbox-lite/uploads

# Application logs

docker-compose logs -f backendnetworks:

  dropbox-lite-network:

# Audit logs    driver: bridge

docker exec cipherdrive-backend tail -f /app/logs/audit.log```



# Database logs### Nginx Configuration

docker-compose logs -f db

```Create `nginx.conf` for reverse proxy:



### Backups```nginx

events {

1. **Database Backup**:    worker_connections 1024;

```bash}

# Manual backup

docker exec cipherdrive-db pg_dump -U cipherdrive_user cipherdrive_db > backup.sqlhttp {

    upstream backend {

# Automated backup (add to cron)        server backend:8000;

0 2 * * * docker exec cipherdrive-db pg_dump -U cipherdrive_user cipherdrive_db > /backups/cipherdrive_$(date +\%Y\%m\%d).sql    }

```

    upstream frontend {

2. **File Backup**:        server frontend:80;

```bash    }

# Backup uploads

rsync -av /mnt/app-pool/cipherdrive/uploads/ /backups/uploads/    server {

```        listen 80;

        server_name _;

### Updates        client_max_body_size 100M;



```bash        # Frontend

# Pull latest images        location / {

docker-compose pull            proxy_pass http://frontend;

            proxy_set_header Host $host;

# Restart services            proxy_set_header X-Real-IP $remote_addr;

docker-compose up -d            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            proxy_set_header X-Forwarded-Proto $scheme;

# Run database migrations (if needed)        }

docker exec cipherdrive-backend alembic upgrade head

```        # Backend API

        location /api/ {

## 🐛 Troubleshooting            proxy_pass http://backend/;

            proxy_set_header Host $host;

### Common Issues            proxy_set_header X-Real-IP $remote_addr;

            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

1. **Permission Denied**            proxy_set_header X-Forwarded-Proto $scheme;

   ```bash            proxy_read_timeout 300s;

   sudo chown -R 1000:1000 /mnt/app-pool/cipherdrive            proxy_send_timeout 300s;

   sudo chown -R 1000:1000 /mnt/Centauri/cipherdrive        }

   ```

        # Health check

2. **Database Connection Error**        location /health {

   - Check PostgreSQL is running: `docker-compose ps`            proxy_pass http://backend/health;

   - Verify credentials in `.env`        }

   - Check network connectivity    }

}

3. **File Upload Issues**```

   - Check disk space: `df -h`

   - Verify upload directory permissions## 🛠️ Development Setup

   - Check file size limits in `.env`

### Backend Development

4. **Cloudflare Tunnel Issues**

   - Verify tunnel token1. **Setup Python Environment**

   - Check DNS configuration   ```bash

   - Ensure network connectivity   cd backend

   python -m venv venv

### Debug Mode   source venv/bin/activate  # On Windows: venv\Scripts\activate

   pip install -r requirements.txt

Enable debug logging:   ```

```bash

# Set in .env2. **Database Setup**

DEBUG=true   ```bash

LOG_LEVEL=DEBUG   # Start PostgreSQL (or use Docker)

   docker run -d \

# Restart services     --name postgres-dev \

docker-compose restart     -e POSTGRES_USER=dropbox_user \

```     -e POSTGRES_PASSWORD=password \

     -e POSTGRES_DB=dropbox_lite \

## 📚 API Documentation     -p 5432:5432 \

     postgres:15

Once deployed, access the interactive API documentation at:   ```

- Swagger UI: `https://files.yourdomain.com/api/docs`

- ReDoc: `https://files.yourdomain.com/api/redoc`3. **Run Backend**

   ```bash

## 🤝 Contributing   cd app

   uvicorn main:app --reload --host 0.0.0.0 --port 8000

1. Fork the repository   ```

2. Create a feature branch

3. Make your changes### Frontend Development

4. Add tests if applicable

5. Submit a pull request1. **Setup Node.js Environment**

   ```bash

## 📄 License   cd frontend

   npm install

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.   ```



## 🆘 Support2. **Configure API URL**

   ```bash

- **Documentation**: Check this README and inline code comments   # In .env.local

- **Issues**: Open an issue on GitHub   REACT_APP_API_URL=http://localhost:8000

- **Security**: Report security issues privately   ```



## 🔧 Development3. **Run Frontend**

   ```bash

### Local Development   npm start

   ```

```bash

# Backend## 📖 API Documentation

cd backend

python -m venv venvOnce deployed, API documentation is available at:

source venv/bin/activate  # On Windows: venv\Scripts\activate- Swagger UI: `http://your-server/docs`

pip install -r requirements.txt- ReDoc: `http://your-server/redoc`

uvicorn app.main:app --reload

### Key Endpoints

# Frontend

cd frontend**Authentication:**

npm install- `POST /auth/login` - User login

npm run dev- `POST /auth/refresh` - Refresh tokens

```- `POST /auth/logout` - User logout

- `POST /auth/password-reset-request` - Request password reset

### Running Tests- `POST /auth/password-reset` - Reset password



```bash**File Operations:**

# Backend tests- `GET /files/` - List files

cd backend- `POST /files/upload` - Upload file

pytest- `GET /files/{file_id}/download` - Download file

- `DELETE /files/{file_id}` - Delete file

# Frontend tests- `POST /files/share` - Create share link

cd frontend

npm test**User Management:**

```- `GET /users/me` - Get current user info

- `PUT /users/me` - Update user profile

---- `GET /users/` - List all users (admin only)

- `POST /users/` - Create user (admin only)

**CipherDrive** - Secure file sharing for the modern age 🔐
## 🔧 Maintenance

### Backup Strategy

1. **Database Backup**
   ```bash
   # Create backup
   docker exec dropbox-lite-postgres pg_dump -U dropbox_user dropbox_lite > backup.sql
   
   # Restore backup
   docker exec -i dropbox-lite-postgres psql -U dropbox_user dropbox_lite < backup.sql
   ```

2. **File Backup**
   ```bash
   # Backup uploads directory
   tar -czf uploads-backup-$(date +%Y%m%d).tar.gz /mnt/your-pool/dropbox-lite/uploads
   ```

### Log Management

1. **View Logs**
   ```bash
   # View all services logs
   docker-compose logs -f
   
   # View specific service
   docker-compose logs -f backend
   ```

2. **Log Rotation**
   ```bash
   # Configure in docker-compose.yml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

### Updates and Maintenance

1. **Update Application**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Rebuild and restart
   docker-compose up -d --build
   ```

2. **Database Migrations**
   ```bash
   # Run inside backend container
   docker exec -it dropbox-lite-backend python -m alembic upgrade head
   ```

## 🔍 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check database status
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down
docker volume rm dropbox-lite_postgres_data
docker-compose up -d
```

**2. File Upload Issues**
```bash
# Check upload directory permissions
ls -la /mnt/your-pool/dropbox-lite/uploads

# Fix permissions
chmod -R 755 /mnt/your-pool/dropbox-lite/uploads
```

**3. Memory Issues**
```bash
# Check container memory usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

### Performance Tuning

1. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_files_user_id ON files(user_id);
   CREATE INDEX idx_files_created_at ON files(created_at);
   CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
   ```

2. **File Storage Optimization**
   - Use SSD storage for database
   - Configure appropriate PostgreSQL settings
   - Enable gzip compression in Nginx

## 📞 Support

For support and troubleshooting:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Ensure all environment variables are correctly set
4. Verify network connectivity between containers

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Note**: Replace `your-truenas-ip`, `your-pool`, and other placeholder values with your actual server details before deployment.