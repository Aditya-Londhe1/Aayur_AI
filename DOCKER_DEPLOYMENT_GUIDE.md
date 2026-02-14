# 🐳 Docker Deployment Guide

## Deploy AayurAI with Docker

This guide covers deploying the full-stack AayurAI application using Docker and Docker Compose.

---

## 📋 Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- 4GB+ RAM available
- 10GB+ disk space

### Install Docker

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/aayurai.git
cd aayurai
```

### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Database
DB_PASSWORD=your_secure_password_here

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Security
SECRET_KEY=your_random_32_char_string

# Optional: Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
```

### 3. Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application
- **Frontend:** http://localhost:8000
- **API:** http://localhost:8000/api/v1
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🏗️ Architecture

### Docker Compose Services

```
┌─────────────────────────────────────┐
│         AayurAI Application         │
│  (Frontend + Backend in one image)  │
│         Port: 8000                  │
└─────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│       PostgreSQL Database           │
│         Port: 5432                  │
└─────────────────────────────────────┘
```

### Dockerfile Stages

**Stage 1: Frontend Builder**
- Uses Node.js 18 Alpine
- Installs dependencies
- Builds React app
- Output: `frontend/dist/`

**Stage 2: Backend + Frontend**
- Uses Python 3.11 Slim
- Installs Python dependencies
- Copies backend code
- Copies built frontend from Stage 1
- Serves everything from FastAPI

---

## 📦 Docker Images

### Build Custom Image
```bash
# Build with tag
docker build -t aayurai:latest .

# Build with specific version
docker build -t aayurai:v1.0.0 .
```

### Image Size
- **Frontend Builder:** ~500MB (discarded)
- **Final Image:** ~1.5GB
  - Python 3.11: ~400MB
  - Dependencies: ~800MB
  - Application: ~300MB

---

## 🔧 Configuration

### Environment Variables

**Required:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

**Optional:**
```bash
# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
PORT=8000
```

### Generate SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🎯 Docker Compose Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app
```

### Build & Deploy
```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Database Operations
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U aayurai -d aayurai

# Run migrations
docker-compose exec app alembic upgrade head

# Create database backup
docker-compose exec postgres pg_dump -U aayurai aayurai > backup.sql

# Restore database
docker-compose exec -T postgres psql -U aayurai aayurai < backup.sql
```

### Maintenance
```bash
# View running containers
docker-compose ps

# Check resource usage
docker stats

# Remove stopped containers
docker-compose rm

# Remove all (including volumes)
docker-compose down -v

# Prune unused images
docker image prune -a
```

---

## 🔍 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs app
```

**Common issues:**
- Missing environment variables
- Database not ready
- Port already in use

**Solution:**
```bash
# Check if port is in use
lsof -i :8000

# Kill process using port
kill -9 <PID>

# Restart services
docker-compose restart
```

### Database Connection Error

**Check database status:**
```bash
docker-compose ps postgres
docker-compose logs postgres
```

**Solution:**
```bash
# Restart database
docker-compose restart postgres

# Wait for health check
docker-compose ps
```

### Frontend Not Loading

**Check if frontend was built:**
```bash
docker-compose exec app ls -la /app/frontend/dist
```

**Solution:**
```bash
# Rebuild with no cache
docker-compose build --no-cache app
docker-compose up -d
```

### Out of Memory

**Check memory usage:**
```bash
docker stats
```

**Solution:**
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory

# Or reduce services
docker-compose down
docker-compose up -d app postgres
```

---

## 🚀 Production Deployment

### 1. Use Production Environment File
```bash
cp .env.example .env.production
# Edit .env.production with production values
```

### 2. Build Production Image
```bash
docker-compose -f docker-compose.yml build
```

### 3. Deploy with Production Config
```bash
docker-compose -f docker-compose.yml up -d
```

### 4. Set Up Reverse Proxy (Nginx)

Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Set Up SSL (Let's Encrypt)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U aayurai
```

### Logs
```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f app

# Save logs to file
docker-compose logs > logs.txt
```

### Resource Monitoring
```bash
# Real-time stats
docker stats

# Container inspection
docker inspect aayurai-app

# Disk usage
docker system df
```

---

## 🔐 Security Best Practices

### 1. Use Strong Passwords
```bash
# Generate secure password
openssl rand -base64 32
```

### 2. Don't Expose Database Port
```yaml
# Remove from docker-compose.yml
ports:
  - "5432:5432"  # Remove this line
```

### 3. Use Docker Secrets
```bash
# Create secret
echo "my_secret_password" | docker secret create db_password -

# Use in docker-compose.yml
secrets:
  - db_password
```

### 4. Run as Non-Root User
Add to Dockerfile:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### 5. Keep Images Updated
```bash
# Update base images
docker-compose pull
docker-compose up -d --build
```

---

## 💾 Backup & Restore

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U aayurai aayurai > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# Decompress
gunzip backup_20260214.sql.gz

# Restore
docker-compose exec -T postgres psql -U aayurai aayurai < backup_20260214.sql
```

### Backup Volumes
```bash
# Backup volume
docker run --rm -v aayurai_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz /data

# Restore volume
docker run --rm -v aayurai_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /
```

---

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run migrations
docker-compose exec app alembic upgrade head
```

### Update Dependencies
```bash
# Update Python packages
docker-compose exec app pip install --upgrade -r requirements.txt

# Rebuild image
docker-compose build --no-cache app
docker-compose up -d
```

### Clean Up
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale app service
docker-compose up -d --scale app=3

# Use load balancer (Nginx)
# Configure upstream in nginx.conf
```

### Vertical Scaling
```bash
# Increase resources in docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 🎯 Performance Optimization

### 1. Use Multi-Stage Builds
Already implemented in Dockerfile

### 2. Minimize Image Size
```dockerfile
# Use Alpine images
FROM python:3.11-alpine

# Remove unnecessary files
RUN rm -rf /var/cache/apk/*
```

### 3. Use Build Cache
```bash
# Build with cache
docker-compose build

# Use BuildKit
DOCKER_BUILDKIT=1 docker-compose build
```

### 4. Optimize Dependencies
```bash
# Use --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt
```

---

## 📝 Docker Compose Reference

### Full docker-compose.yml
See `docker-compose.yml` in project root

### Environment Variables
See `.env.example` for all available variables

### Volumes
- `postgres_data` - Database data
- `./uploads` - User uploads
- `./models` - ML models
- `./logs` - Application logs

### Networks
- `aayurai-network` - Bridge network for all services

---

## ✅ Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] `.env` file created with all variables
- [ ] `SECRET_KEY` generated
- [ ] `GEMINI_API_KEY` obtained
- [ ] Database password set
- [ ] Images built successfully
- [ ] Services started
- [ ] Health check passes
- [ ] Frontend accessible
- [ ] API endpoints working
- [ ] Database connected
- [ ] Logs monitored
- [ ] Backups configured

---

## 🆘 Support

- **Docker Docs:** https://docs.docker.com
- **Docker Compose Docs:** https://docs.docker.com/compose
- **Project Issues:** GitHub Issues

---

**Deployment Time:** 15-20 minutes  
**Difficulty:** Medium  
**Maintenance:** Low (automated)  
**Scalability:** High

---

**Made with 🐳 for easy containerized deployment**
