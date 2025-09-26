# 🤖 CipherDrive TrueNAS SCALE Automation

This script does **EVERYTHING** for you automatically on TrueNAS SCALE! No more manual setup - just run and wait!

## 🎯 What the Script Does

**The automation robot will:**
1. 📁 Create all TrueNAS storage datasets automatically
2. 🌐 Set up Docker networks
3. 🔐 Generate super secure passwords  
4. 🐳 Build and deploy all containers
5. 👥 Create admin and cipher users
6. 🚀 Launch your complete file sharing platform
7. 💾 Save all your passwords safely
8. 🌐 Test that everything works

**Total time: 5-10 minutes** ⏰

---

## 🚀 How to Use

### 🐧 **TrueNAS SCALE Setup**
```bash
# SSH into your TrueNAS SCALE server
ssh admin@your-truenas-ip

# Navigate to your project directory
cd /path/to/CipherDrive

# Make script executable
chmod +x auto-setup.sh

# Run the automation
./auto-setup.sh
```

---

## 🎊 What You Get

After the script runs, you'll have:

### 🌐 **Your Own Cloud Platform**
- **Website**: `http://YOUR-TRUENAS-IP:3000`
- **Complete file sharing system**
- **Movie/TV streaming for cipher user**
- **Admin panel for managing users**

### 👥 **Ready-to-Use Accounts**
- **Admin**: Full control, user management, all features
- **Cipher**: Download-only access to movies/TV shows

### 🔐 **Super Secure Setup**
- **Randomly generated passwords**
- **JWT authentication** 
- **Database encryption**
- **Audit logging**
- **Rate limiting**

---

## 📋 After Setup

### 🎯 **Your Login Info**
The script saves everything to `CREDENTIALS.txt`:
- 🌐 Website URL
- 👨‍💼 Admin username/password
- 🎬 Cipher username/password  
- 💾 Database password
- 🔐 Security keys

### ⚠️ **Important First Steps**
1. **Visit your website** at the URL shown
2. **Login with admin account**
3. **Change the default passwords** immediately
4. **Add your email settings** for notifications
5. **Create regular user accounts**

### 🎬 **For Movie/TV Access**
1. **Login as cipher user**
2. **Upload movies** to the movies folder
3. **Upload TV shows** to the tv folder
4. **Cipher user can download** but not upload

---

## 🛠️ Script Features

### 🤖 **Smart Detection**
- **Finds your IP address** automatically
- **Checks if Docker is installed**
- **Verifies Portainer is running**
- **Tests website accessibility**

### 🔐 **Security First**
- **Generates 64-character JWT secrets**
- **Creates unique database passwords**  
- **Uses OpenSSL for secure randomization**
- **No default passwords left unchanged**

### 📁 **TrueNAS Dataset Structure**
```
📦 /mnt/app-pool/cipherdrive/
├── 📁 uploads/          ← User files
└── 📁 logs/            ← System logs

📦 /mnt/Centauri/cipherdrive/
├── 📁 movies/           ← Movies for cipher user  
└── 📁 tv/              ← TV shows for cipher user
```

### 🐳 **Docker Services**
- **PostgreSQL 16** database with persistent storage
- **FastAPI backend** with health checks and auto-restart
- **React frontend** with nginx reverse proxy
- **Automated user creation** with secure defaults

---

## 🆘 Troubleshooting

### 🔴 **"Docker not found"**
```bash
# Install Docker first:
# Windows: Download Docker Desktop
# Linux: apt install docker.io docker-compose
```

### 🔴 **"Permission denied"**
```bash
# Run as administrator/sudo:
sudo ./auto-setup.sh
```

### 🔴 **"Can't create folders"**
```bash
# Check if you're in the right directory:
cd /path/to/CipherDrive
./auto-setup.sh
```

### 🔴 **"Website not accessible"**
- **Wait 2-3 more minutes** for containers to fully start
- **Check Docker Desktop** is running
- **Verify no firewall** is blocking port 3000

### 🔴 **"Network already exists"**
- **This is OK!** The script handles this automatically

---

## 🎯 Manual Override

If you want to **customize anything**:

1. **Edit `.env`** file before running script
2. **Modify `docker-compose-auto.yml`** for custom setup
3. **Change folder paths** in the script
4. **Set custom passwords** in environment variables

---

## 🎉 Success Indicators

**You'll know it worked when:**
- ✅ All containers show "Up" status  
- ✅ Website loads at `http://YOUR-IP:3000`
- ✅ Admin login works
- ✅ Cipher login works
- ✅ File upload/download works
- ✅ No red errors in container logs

---

## 🌟 Pro Tips

### 🚀 **Speed Up Next Time**
- **Keep your `.env`** file for future deployments
- **Backup `CREDENTIALS.txt`** somewhere safe
- **Save your Docker images** with `docker save`

### 🔐 **Security Best Practices**  
- **Change passwords** immediately after setup
- **Enable SMTP email** for notifications
- **Set up SSL/HTTPS** for external access
- **Regular backups** of database and files

### 📱 **Mobile Access**
- **Works on phones/tablets** automatically
- **Responsive design** adapts to screen size
- **Touch-friendly** file management

---

**🎊 Congratulations! You're now running enterprise-grade file sharing! 🎊**

*Made with ❤️ and lots of automation magic* ✨