# 🚀 AAYUR AI Deployment Guide

**Complete guide for deploying the AAYUR AI application**

---

## 📋 Prerequisites

### System Requirements
- **Python:** 3.8 or higher
- **Node.js:** 16.x or higher
- **npm:** 8.x or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** 2GB free space

### Required Software
- Git
- Python pip
- Node.js and npm
- Virtual environment tool (venv or conda)

---

## 🔧 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory:
```env
# Database
DATABASE_URL=sqlite:///./aayurai.db

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=AayurAI

# CORS Settings (adjust for production)
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Model Paths
PULSE_MODEL_PATH=models/pulse/pulse_experiment_20260130_233906/final_model.pth
TONGUE_MODEL_PATH=models/tongue/model.pth
SYMPTOM_MODEL_PATH=models/symptom/model.pth

# Logging
LOG_LEVEL=INFO
```

### 5. Initialize Database
```bash
# Database will be created automatically on first run
# Or run migrations if using Alembic
alembic upgrade head
```

### 6. Start Backend Server

#### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 7. Verify Backend
Open browser and navigate to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/consultations/health

---

## 🎨 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure API URL
Edit `frontend/src/services/api.js`:
```javascript
// Development
const API_URL = 'http://localhost:8000/api/v1';

// Production (update with your domain)
const API_URL = 'https://your-domain.com/api/v1';
```

### 4. Start Development Server
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

### 5. Build for Production
```bash
npm run build
```

Build output will be in `frontend/dist/` directory.

---

## 🐳 Docker Deployment (Recommended)

### 1. Using Docker Compose
```bash
# From project root
docker-compose up -d
```

This will start:
- Backend on port 8000
- Frontend on port 80

### 2. Individual Docker Containers

#### Backend
```bash
cd backend
docker build -t aayurai-backend .
docker run -d -p 8000:8000 aayurai-backend
```

#### Frontend
```bash
cd frontend
docker build -t aayurai-frontend .
docker run -d -p 80:80 aayurai-frontend
```

---

## ☁️ Cloud Deployment Options

### Option 1: AWS Deployment

#### Backend (EC2 + RDS)
1. Launch EC2 instance (t3.medium or larger)
2. Install Python and dependencies
3. Set up RDS PostgreSQL database
4. Configure security groups (port 8000)
5. Use systemd or supervisor for process management
6. Set up Nginx as reverse proxy
7. Configure SSL with Let's Encrypt

#### Frontend (S3 + CloudFront)
1. Build frontend: `npm run build`
2. Upload `dist/` to S3 bucket
3. Enable static website hosting
4. Create CloudFront distribution
5. Configure custom domain
6. Set up SSL certificate

### Option 2: Heroku Deployment

#### Backend
```bash
cd backend
heroku create aayurai-backend
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

#### Frontend
```bash
cd frontend
heroku create aayurai-frontend
heroku buildpacks:set heroku/nodejs
git push heroku main
```

### Option 3: DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings:
   - **Backend:** Python app, port 8000
   - **Frontend:** Static site from `frontend/dist`
3. Set environment variables
4. Deploy

### Option 4: Vercel (Frontend) + Railway (Backend)

#### Frontend on Vercel
```bash
cd frontend
vercel --prod
```

#### Backend on Railway
1. Connect GitHub repository
2. Select backend directory
3. Railway auto-detects Python
4. Set environment variables
5. Deploy

---

## 🔒 Production Configuration

### Backend Security

#### 1. Update CORS Settings
```python
# backend/app/core/config.py
BACKEND_CORS_ORIGINS = [
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com"
]
```

#### 2. Use Production Database
```env
DATABASE_URL=postgresql://user:password@host:5432/aayurai
```

#### 3. Enable HTTPS
```bash
# Using Nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. Set Secret Keys
```env
SECRET_KEY=your-super-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### Frontend Configuration

#### 1. Update API URL
```javascript
// frontend/src/services/api.js
const API_URL = process.env.VITE_API_URL || 'https://api.your-domain.com/api/v1';
```

#### 2. Environment Variables
Create `frontend/.env.production`:
```env
VITE_API_URL=https://api.your-domain.com/api/v1
```

#### 3. Build Optimization
```javascript
// frontend/vite.config.js
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
  },
});
```

---

## 🧪 Testing Deployment

### 1. Backend Health Check
```bash
curl http://localhost:8000/api/v1/consultations/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Frontend-Backend Integration
```bash
python test_frontend_backend_integration.py
```

### 3. End-to-End Test
1. Open frontend in browser
2. Complete full assessment flow
3. Verify results display correctly
4. Check browser console for errors
5. Test on mobile device

---

## 📊 Monitoring & Logging

### Backend Logging
Logs are stored in `backend/logs/app.log`

View logs:
```bash
tail -f backend/logs/app.log
```

### Frontend Monitoring
Use browser DevTools:
- Console for JavaScript errors
- Network tab for API calls
- Performance tab for load times

### Production Monitoring Tools
- **Backend:** Sentry, New Relic, DataDog
- **Frontend:** Google Analytics, LogRocket
- **Infrastructure:** CloudWatch, Prometheus, Grafana

---

## 🔄 Continuous Deployment

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app/backend && git pull && systemctl restart aayurai-backend'

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          cd frontend
          npm install
          npm run build
          aws s3 sync dist/ s3://your-bucket/
```

---

## 🛠️ Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### Module Not Found
```bash
pip install -r requirements.txt --force-reinstall
```

#### Database Connection Error
- Check DATABASE_URL in .env
- Verify database is running
- Check firewall settings

### Frontend Issues

#### API Connection Failed
- Verify backend is running
- Check CORS settings
- Verify API_URL in api.js
- Check browser console for errors

#### Build Fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### White Screen
- Check browser console for errors
- Verify all routes are configured
- Check for JavaScript errors

---

## 📈 Performance Optimization

### Backend
- Use Redis for caching
- Enable gzip compression
- Optimize database queries
- Use connection pooling
- Implement rate limiting

### Frontend
- Enable code splitting
- Lazy load components
- Optimize images
- Use CDN for static assets
- Enable browser caching

---

## 🔐 Security Checklist

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] API rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF tokens implemented
- [ ] Regular security updates

---

## 📞 Support

### Documentation
- **API Docs:** http://localhost:8000/docs
- **Frontend README:** frontend/README.md
- **Backend README:** backend/README.md

### Common Commands

#### Backend
```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Check logs
tail -f logs/app.log
```

#### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] No console errors
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Backup strategy in place

### Post-Deployment
- [ ] Health checks passing
- [ ] Frontend loads correctly
- [ ] API endpoints responding
- [ ] Database connected
- [ ] Logs being written
- [ ] Monitoring active
- [ ] Error tracking enabled

---

## 🎉 Success!

Your AAYUR AI application should now be deployed and running!

**Access Points:**
- **Frontend:** https://your-domain.com
- **Backend API:** https://api.your-domain.com
- **API Docs:** https://api.your-domain.com/docs

---

*Deployment guide created by Kiro AI Assistant*  
*Last updated: February 8, 2026*
