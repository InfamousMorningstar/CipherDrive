# CipherDrive

<div align="center">

![CipherDrive Logo](https://img.shields.io/badge/CipherDrive-v0.1.0--alpha-red?style=for-the-badge&logo=shield&logoColor=white)

**Next-Generation Secure File Management System**

[![Status](https://img.shields.io/badge/Status-ALPHA%20TESTING-red?style=flat-square)](https://github.com/InfamousMorningstar/CipherDrive)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compatible-blue?style=flat-square&logo=docker)](https://www.docker.com/)
[![TrueNAS](https://img.shields.io/badge/TrueNAS-SCALE-green?style=flat-square&logo=truenas)](https://www.truenas.com/)

[Features](#features) • [Installation](#installation) • [Documentation](#documentation) • [Support](#support) • [Contributing](#contributing)

</div>

---

## ⚠️ **ALPHA TESTING WARNING**

> **🚨 IMPORTANT NOTICE**
> 
> **CipherDrive is currently in ALPHA testing phase and is NOT recommended for production use.**
> 
> **Known Issues & Limitations:**
> - ⚠️ **Active Development**: Features may change without notice
> - ⚠️ **Potential Data Loss**: Database schema may change between versions
> - ⚠️ **Security Vulnerabilities**: Security features are under development
> - ⚠️ **Performance Issues**: Not optimized for high-load environments
> - ⚠️ **Limited Testing**: Insufficient testing across different environments
> - ⚠️ **Breaking Changes**: Updates may require complete reinstallation
> 
> **Use at your own risk. Always backup your data before testing.**

---

## Overview

CipherDrive is a modern, secure file management and sharing platform designed for enterprise and home lab environments. Built with cutting-edge technologies, it provides secure file storage, sharing capabilities, and comprehensive user management through an intuitive web interface.

### 🎯 Target Audience
- **Home Lab Enthusiasts** running TrueNAS SCALE
- **Small to Medium Businesses** requiring secure file sharing
- **Development Teams** needing collaborative file management
- **IT Professionals** testing modern storage solutions

---

## Features

### 🔐 **Security & Authentication**
- **JWT-based Authentication** with secure token management
- **Role-based Access Control** (Admin, User, Read-only)
- **Bcrypt Password Hashing** for enhanced security
- **Session Management** with automatic logout
- **Audit Logging** for compliance and monitoring

### 📁 **File Management**
- **Secure File Upload/Download** with progress tracking
- **Multi-format Support** (Images, Videos, Audio, Documents, PDFs)
- **File Organization** with folder hierarchy
- **File Preview** for supported formats
- **Bulk Operations** for efficient management
- **Storage Quota Management** per user

### 🔗 **Sharing & Collaboration**  
- **Secure Link Sharing** with expiration dates
- **Download Limits** and access controls
- **Guest Access** for external collaboration
- **Share Analytics** and download tracking

### 🎨 **User Experience**
- **Modern React Frontend** with responsive design
- **Dark/Light Theme** support
- **Real-time Updates** and notifications
- **Mobile-friendly Interface**
- **Accessibility Compliant**

### 🏗️ **Infrastructure**
- **Docker Containerization** for easy deployment
- **TrueNAS SCALE Integration** with dataset support
- **PostgreSQL Database** for reliable data storage
- **Nginx Reverse Proxy** for optimized delivery
- **Cloudflare Tunnel** support for secure external access

---

## Installation

### Prerequisites

- **Operating System**: TrueNAS SCALE 22.02+ or Linux with Docker
- **Hardware**: 
  - Minimum: 2GB RAM, 2 CPU cores, 10GB storage
  - Recommended: 4GB RAM, 4 CPU cores, 50GB+ storage
- **Software**:
  - Docker 20.10+
  - Docker Compose 2.0+
  - Git 2.0+

### 🚀 Automated Installation (Recommended)

For TrueNAS SCALE systems, use our automated deployment script:

```bash
curl -sSL https://raw.githubusercontent.com/InfamousMorningstar/CipherDrive/main/auto-setup.sh | bash
```

**What the script does:**
- ✅ Checks system requirements
- ✅ Creates necessary TrueNAS datasets
- ✅ Configures Docker networking
- ✅ Generates secure passwords
- ✅ Deploys all services
- ✅ Provides access information

### 🔧 Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

#### 1. Clone Repository
```bash
git clone https://github.com/InfamousMorningstar/CipherDrive.git
cd CipherDrive
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env file with your specific configuration
```

#### 3. Deploy with Docker Compose
```bash
docker compose up -d --build
```

#### 4. Access Application
```
http://YOUR-IP:8069
```

</details>

### 📱 Alternative Deployment Methods

<details>
<summary>Direct Deployment Script</summary>

For environments with CDN caching issues:
```bash
curl -sSL https://raw.githubusercontent.com/InfamousMorningstar/CipherDrive/main/direct-deploy.sh | bash
```

</details>

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_DB` | Database name | `cipherdrive_db` | ✅ |
| `POSTGRES_USER` | Database username | `cipherdrive_user` | ✅ |
| `POSTGRES_PASSWORD` | Database password | Generated | ✅ |
| `JWT_SECRET` | JWT signing secret | Generated | ✅ |
| `ADMIN_EMAIL` | Initial admin email | `admin@cipherdrive.local` | ✅ |
| `ADMIN_PASSWORD` | Initial admin password | Generated | ✅ |
| `FRONTEND_URL` | Frontend URL | `http://localhost:8069` | ⭕ |

### TrueNAS Dataset Structure

```
/mnt/app-pool/cipherdrive/     # Application data
├── database/                  # PostgreSQL data
├── config/                    # Configuration files
└── logs/                      # Application logs

/mnt/Centauri/cipherdrive/     # User data storage
├── users/                     # User file storage
├── shares/                    # Shared files
└── uploads/                   # Upload staging
```

---

## Usage

### Initial Setup

1. **Access CipherDrive**: Navigate to `http://YOUR-IP:8069`
2. **Initialize System**: Click "Initialize System" on the landing page
3. **Admin Login**: Use generated admin credentials
4. **Create Users**: Add users through the admin panel
5. **Configure Storage**: Set user quotas and permissions

### User Management

```bash
# Access admin panel at /admin
# Default admin credentials are displayed during setup
```

### File Operations

- **Upload Files**: Drag & drop or click upload button
- **Create Folders**: Use the "New Folder" button
- **Share Files**: Right-click file → Share → Generate link
- **Download Files**: Click download icon or use shared links

---

## Development

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   React         │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Port 8069)   │    │   (Port 8000)   │    │   (Port 5432)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Frontend:**
- React 18
- React Router 6
- TailwindCSS
- Framer Motion
- Heroicons
- Zustand (State Management)

**Backend:**
- FastAPI (Python)
- SQLAlchemy (ORM)
- PostgreSQL
- JWT Authentication
- Pydantic (Data Validation)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Reverse Proxy)
- TrueNAS SCALE Integration

### Local Development

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend development  
cd frontend
npm install
npm run dev
```

---

## API Documentation

Once deployed, access the interactive API documentation:

- **Swagger UI**: `http://YOUR-IP:8069/api/docs`
- **ReDoc**: `http://YOUR-IP:8069/api/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | User authentication |
| `GET` | `/api/files/` | List user files |
| `POST` | `/api/files/upload` | Upload files |
| `GET` | `/api/admin/users` | Admin: List users |
| `POST` | `/api/shares/create` | Create share link |

---

## Troubleshooting

### Common Issues

<details>
<summary>🔧 Container Build Failures</summary>

**Problem**: Docker build fails with import errors
**Solution**: 
```bash
# Clean rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

</details>

<details>
<summary>🔧 Frontend Not Loading</summary>

**Problem**: Application loads but buttons don't work
**Solution**:
1. Check browser console for JavaScript errors
2. Verify all containers are running: `docker compose ps`
3. Check frontend logs: `docker compose logs frontend`

</details>

<details>
<summary>🔧 Database Connection Issues</summary>

**Problem**: Backend cannot connect to database
**Solution**:
1. Check database container status
2. Verify environment variables
3. Check logs: `docker compose logs backend db`

</details>

### Getting Help

- **GitHub Issues**: [Report bugs and issues](https://github.com/InfamousMorningstar/CipherDrive/issues)
- **Discussions**: [Community discussions](https://github.com/InfamousMorningstar/CipherDrive/discussions)
- **Documentation**: Check our [Wiki](https://github.com/InfamousMorningstar/CipherDrive/wiki)

---

## Roadmap

### 🚧 Current Development (v0.1.x)
- [ ] Bug fixes and stability improvements
- [ ] Enhanced error handling
- [ ] Performance optimizations
- [ ] Additional file format support

### 🎯 Planned Features (v0.2.x)
- [ ] Multi-tenancy support
- [ ] Advanced sharing permissions
- [ ] File versioning
- [ ] Backup and restore functionality
- [ ] Mobile application
- [ ] LDAP/Active Directory integration

### 🔮 Future Considerations (v1.0+)
- [ ] Clustering support
- [ ] Advanced analytics
- [ ] Third-party integrations
- [ ] Enterprise features

---

## Contributing

We welcome contributions! Please note this is an alpha project with frequent changes.

### Development Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Follow coding standards and include tests
4. **Test thoroughly**: Ensure all tests pass
5. **Commit changes**: Use conventional commit messages
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**: Describe changes and include screenshots

### Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## Security

### Reporting Security Issues

🚨 **DO NOT** create public GitHub issues for security vulnerabilities.

Send security reports to: `security@cipherdrive.local`

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Features

- JWT token authentication
- Password hashing with bcrypt
- Input validation and sanitization
- CORS configuration
- Rate limiting (planned)
- File type validation

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **TrueNAS Community** for inspiration and feedback
- **FastAPI** for the excellent Python web framework
- **React Community** for frontend technologies
- **Docker** for containerization platform
- **All Contributors** who help improve this project

---

## Support the Project

If you find CipherDrive useful, please consider:

- ⭐ **Starring the repository**
- 🐛 **Reporting bugs and issues**
- 💡 **Suggesting new features**
- 🔧 **Contributing code improvements**
- 📖 **Improving documentation**

---

<div align="center">

**Built with ❤️ for the Open Source Community**

[![GitHub stars](https://img.shields.io/github/stars/InfamousMorningstar/CipherDrive?style=social)](https://github.com/InfamousMorningstar/CipherDrive/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/InfamousMorningstar/CipherDrive?style=social)](https://github.com/InfamousMorningstar/CipherDrive/network/members)

</div>