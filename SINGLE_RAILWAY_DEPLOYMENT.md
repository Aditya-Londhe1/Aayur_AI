# 🚀 Single Railway Deployment Guide

## Deploy Full-Stack AayurAI on Railway (One Service)

**Advantages:**
- ✅ Single deployment
- ✅ One URL for everything
- ✅ No CORS issues
- ✅ Simpler configuration
- ✅ Lower cost (one service)
- ✅ Easier to manage

---

## 📋 How It Works

Railway will:
1. Install Python dependencies (backend)
2. Install Node dependencies (frontend)
3. Build frontend (`npm run build`)
4. Start FastAPI server
5. Serve frontend from `/` 
6. Serve API from `/api/v1`

**Result:** One URL serves both frontend and backend!

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Railway deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/aayurai.git

# Push
git push -u origin main
```

### Step 2: Deploy on Railway

1. **Go to Railway**
   - Visit https://railway.app
   - Sign up/Login with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your AayurAI repository
   - Railway will auto-detect configuration

3. **Add PostgreSQL Database**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Wait for provisioning (1-2 minutes)
   - `DATABASE_URL` will be set automatically

4. **Set Environment Variables**
   
   Click on your service → "Variables" → Add these:

   ```bash
   # Required
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_random_32_char_string
   ENVIRONMENT=production
   
   # Optional (for email features)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=noreply@yourdomain.com
   ```

   **Generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 5-10 minutes for build
   - Railway will:
     - Install backend dependencies
     - Install frontend dependencies
     - Build frontend
     - Start server

6. **Get Your URL**
   - Click "Settings" → "Domains"
   - Copy the Railway URL (e.g., `https://aayurai-production.up.railway.app`)
   - Your app is live! 🎉

---

## 🔧 Configuration Files

All necessary files are already configured:

### `nixpacks.toml` (Build Configuration)
```toml
[phases.setup]
nixPkgs = ["python311", "nodejs-18_x"]

[phases.install]
cmds = [
    "cd backend && pip install -r requirements.txt",
    "cd frontend && npm install"
]

[phases.build]
cmds = [
    "cd frontend && npm run build"
]

[start]
cmd = "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### `railway.json` (Railway Configuration)
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `backend/Procfile` (Start Command)
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### `frontend/.env.production` (Frontend Config)
```bash
VITE_API_URL=/api/v1
```

---

## 🌐 How URLs Work

After deployment, your single Railway URL serves everything:

```
https://your-app.railway.app/
├── /                          → Frontend (React app)
├── /assessment                → Frontend route
├── /results                   → Frontend route
├── /voice-assistant           → Frontend route
├── /api/v1/health            → Backend API
├── /api/v1/consultations     → Backend API
├── /api/v1/pulse             → Backend API
└── /docs                      → API documentation
```

**No CORS issues!** Frontend and backend are on the same domain.

---

## ✅ Post-Deployment Checks

### 1. Check Backend Health
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Check Frontend
- Visit `https://your-app.railway.app`
- Should see the home page
- Check browser console for errors

### 3. Check API Documentation
- Visit `https://your-app.railway.app/docs`
- Should see FastAPI Swagger UI

### 4. Test Complete Flow
1. Go to Assessment page
2. Complete a consultation
3. View results
4. Download PDF

---

## 🔍 Troubleshooting

### Build Fails

**Issue:** Frontend build fails
```bash
# Check Railway logs
railway logs
```

**Solution:**
- Ensure `frontend/package.json` has `build` script
- Check Node version compatibility
- Verify all dependencies are in `package.json`

### Frontend Shows 404

**Issue:** Frontend routes return 404
**Solution:**
- Ensure `frontend/dist` was created during build
- Check Railway logs for build errors
- Verify `main.py` serves static files correctly

### API Returns 500

**Issue:** Backend errors
**Solution:**
- Check Railway logs for Python errors
- Verify `DATABASE_URL` is set
- Run migrations: `railway run alembic upgrade head`

### Database Connection Error

**Issue:** Cannot connect to database
**Solution:**
- Verify PostgreSQL is added to project
- Check `DATABASE_URL` environment variable
- Ensure database is running

---

## 🎯 Environment Variables Reference

### Required Variables

```bash
# Database (auto-set by Railway when you add PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Security
SECRET_KEY=your_random_32_char_string
ALGORITHM=HS256

# Environment
ENVIRONMENT=production
```

### Optional Variables

```bash
# Email (if using email features)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (not needed for single deployment)
# CORS_ORIGINS=*
```

---

## 💰 Cost Estimation

### Railway Pricing

**Free Tier:**
- $5 free credit per month
- 500 hours execution time
- 100 GB bandwidth
- 1 GB RAM
- Perfect for starting!

**Usage Estimate:**
- One service (backend + frontend)
- PostgreSQL database
- Estimated: $5-10/month after free credit

**Pro Plan:**
- $20/month
- Unlimited execution hours
- 100 GB bandwidth included
- Priority support

---

## 🔐 Security Checklist

- [x] HTTPS enabled (automatic on Railway)
- [x] Environment variables secured
- [x] Database credentials protected
- [x] No CORS issues (same domain)
- [x] API keys in environment variables
- [x] No sensitive data in code
- [x] Input validation enabled
- [x] SQL injection protection

---

## 📊 Monitoring

### Railway Dashboard

1. **View Logs**
   - Click on service
   - Go to "Logs" tab
   - See real-time logs

2. **Monitor Metrics**
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

3. **Check Deployments**
   - View deployment history
   - Rollback if needed
   - See build logs

### Set Up Alerts

1. Go to project settings
2. Add webhook for notifications
3. Configure for:
   - Deployment failures
   - High resource usage
   - Downtime alerts

---

## 🚀 Custom Domain (Optional)

### Add Custom Domain

1. **In Railway:**
   - Go to service settings
   - Click "Domains"
   - Click "Add Domain"
   - Enter your domain (e.g., `aayurai.com`)

2. **Update DNS:**
   - Add CNAME record:
     ```
     Type: CNAME
     Name: @ (or www)
     Value: <railway-provided-value>
     ```

3. **Wait for Propagation:**
   - DNS changes take 5-60 minutes
   - Railway will auto-configure SSL

---

## 🔄 Updates & Redeployment

### Automatic Deployment

Railway auto-deploys on git push:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Railway automatically:
# 1. Detects push
# 2. Rebuilds application
# 3. Deploys new version
```

### Manual Deployment

```bash
# Using Railway CLI
railway up

# Or trigger from dashboard
# Click "Deploy" → "Redeploy"
```

---

## 📝 Maintenance

### View Logs
```bash
railway logs
```

### Run Migrations
```bash
railway run alembic upgrade head
```

### Access Database
```bash
railway run psql $DATABASE_URL
```

### Restart Service
```bash
railway restart
```

---

## 🎓 Best Practices

1. **Use Environment Variables**
   - Never hardcode secrets
   - Use Railway variables

2. **Monitor Regularly**
   - Check logs daily
   - Monitor resource usage
   - Set up alerts

3. **Keep Dependencies Updated**
   - Update `requirements.txt`
   - Update `package.json`
   - Test before deploying

4. **Backup Database**
   - Railway provides automatic backups
   - Export data regularly
   - Test restore process

5. **Use Git Tags**
   - Tag releases: `git tag v1.0.0`
   - Easy rollback if needed

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project created from GitHub repo
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Health check passes
- [ ] Frontend loads correctly
- [ ] API endpoints work
- [ ] Complete consultation test
- [ ] Custom domain added (optional)
- [ ] Monitoring configured

---

## 🎉 Success!

Your full-stack AayurAI application is now live on Railway!

**What You Have:**
- ✅ Single URL for everything
- ✅ Automatic HTTPS
- ✅ PostgreSQL database
- ✅ Auto-deployment on push
- ✅ Monitoring dashboard
- ✅ Scalable infrastructure

**Next Steps:**
1. Share your URL with users
2. Monitor usage and performance
3. Collect feedback
4. Iterate and improve

---

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app
- **Project Issues:** GitHub Issues

---

## 🔗 Quick Links

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Railway Templates](https://railway.app/templates)
- [Railway Pricing](https://railway.app/pricing)

---

**Deployment Time:** 10-15 minutes  
**Difficulty:** Easy  
**Cost:** Free tier available ($5 credit/month)  
**Maintenance:** Minimal (auto-updates)

---

**Made with ❤️ for easy deployment**

*One command, one service, one URL - that's it!*
