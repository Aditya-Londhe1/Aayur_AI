# Railway Deployment Guide for AayurAI

## ✅ Pre-Deployment Checklist

All necessary files are present:
- ✅ `backend/requirements.txt` - Python dependencies
- ✅ `backend/Procfile` - Start command
- ✅ `backend/runtime.txt` - Python version
- ✅ `railway.json` - Railway configuration
- ✅ `nixpacks.toml` - Build configuration
- ✅ `frontend/package.json` - Node dependencies
- ✅ `backend/app/main.py` - FastAPI application
- ✅ `.gitignore` - Git ignore rules

---

## 🚀 Deployment Steps

### Option 1: Deploy Backend and Frontend Separately (Recommended)

#### Step 1: Deploy Backend to Railway

1. **Go to Railway.app**
   - Visit https://railway.app
   - Sign up or log in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your AayurAI repository

3. **Configure Backend Service**
   - Railway will auto-detect the backend
   - Set root directory: `backend`
   - Railway will use `Procfile` automatically

4. **Set Environment Variables**
   Click "Variables" and add:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_here
   CORS_ORIGINS=https://your-frontend-domain.com
   ENVIRONMENT=production
   ```

5. **Add PostgreSQL Database**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

6. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Copy the backend URL (e.g., `https://your-app.railway.app`)

#### Step 2: Deploy Frontend to Vercel/Netlify

**Option A: Vercel (Recommended)**
1. Go to https://vercel.com
2. Import your GitHub repository
3. Set root directory: `frontend`
4. Set environment variable:
   ```
   VITE_API_URL=https://your-backend.railway.app/api/v1
   ```
5. Deploy

**Option B: Netlify**
1. Go to https://netlify.com
2. Import your GitHub repository
3. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
4. Environment variables:
   ```
   VITE_API_URL=https://your-backend.railway.app/api/v1
   ```
5. Deploy

---

### Option 2: Deploy Full Stack on Railway

1. **Create New Project**
   - Go to Railway.app
   - Create new project from GitHub repo

2. **Configure Service**
   - Railway will detect both backend and frontend
   - Use `railway.json` configuration

3. **Set Environment Variables**
   ```
   DATABASE_URL=postgresql://...
   GEMINI_API_KEY=your_key
   SECRET_KEY=your_secret
   CORS_ORIGINS=*
   VITE_API_URL=/api/v1
   ```

4. **Deploy**
   - Railway will build both frontend and backend
   - Frontend will be served from backend

---

## 🔧 Environment Variables

### Required Variables

#### Backend
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Security
SECRET_KEY=your_secret_key_min_32_chars
ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-domain.com

# Environment
ENVIRONMENT=production
```

#### Frontend
```bash
VITE_API_URL=https://your-backend.railway.app/api/v1
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
```

---

## 📦 Database Setup

### Option 1: Railway PostgreSQL (Recommended)
1. In Railway project, click "New" → "Database" → "PostgreSQL"
2. Railway automatically sets `DATABASE_URL`
3. Run migrations:
   ```bash
   railway run alembic upgrade head
   ```

### Option 2: External PostgreSQL
1. Get PostgreSQL from:
   - Supabase (free tier)
   - ElephantSQL (free tier)
   - Neon (free tier)
2. Set `DATABASE_URL` in Railway variables
3. Run migrations

---

## 🔨 Build Configuration

### Backend Build
Railway uses `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Build
If deploying frontend separately:
```bash
cd frontend
npm install
npm run build
```

Output: `frontend/dist/`

---

## 🌐 Custom Domain

### Railway
1. Go to your service settings
2. Click "Settings" → "Domains"
3. Add custom domain
4. Update DNS records as shown

### Vercel/Netlify
1. Go to domain settings
2. Add custom domain
3. Update DNS records

---

## 🔍 Post-Deployment Checks

### 1. Backend Health Check
```bash
curl https://your-backend.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Frontend Check
- Visit your frontend URL
- Check browser console for errors
- Test API connectivity

### 3. Database Check
```bash
railway run python -c "from app.core.database import engine; print('DB Connected')"
```

### 4. Test Complete Flow
1. Open frontend
2. Complete a consultation
3. Verify results display
4. Check database for saved data

---

## 🐛 Troubleshooting

### Build Fails
**Issue:** Python dependencies fail to install
**Solution:** 
- Check `requirements.txt` syntax
- Ensure Python version matches `runtime.txt`
- Check Railway build logs

### Database Connection Error
**Issue:** Cannot connect to database
**Solution:**
- Verify `DATABASE_URL` is set
- Check database is running
- Run migrations: `railway run alembic upgrade head`

### CORS Errors
**Issue:** Frontend can't access backend
**Solution:**
- Update `CORS_ORIGINS` in backend env vars
- Include both http and https URLs
- Include www and non-www versions

### 502 Bad Gateway
**Issue:** Backend not responding
**Solution:**
- Check backend logs in Railway
- Verify `PORT` environment variable is used
- Check `Procfile` start command

### Frontend Shows API Error
**Issue:** Frontend can't reach backend
**Solution:**
- Verify `VITE_API_URL` is correct
- Rebuild frontend after changing env vars
- Check backend is deployed and running

---

## 📊 Monitoring

### Railway Dashboard
- View logs: Click on service → "Logs"
- Monitor metrics: CPU, Memory, Network
- Check deployments: "Deployments" tab

### Set Up Alerts
1. Go to project settings
2. Add notification webhooks
3. Configure for deployment failures

---

## 💰 Cost Estimation

### Railway Free Tier
- $5 free credit per month
- Enough for small projects
- Includes:
  - 500 hours of execution
  - 100 GB bandwidth
  - 1 GB RAM

### Paid Plan
- $5/month per service
- Unlimited execution hours
- 100 GB bandwidth included
- Additional bandwidth: $0.10/GB

### Recommendations
- Start with free tier
- Monitor usage in dashboard
- Upgrade when needed

---

## 🔐 Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong database password
- [ ] Set specific `CORS_ORIGINS` (not *)
- [ ] Enable HTTPS (automatic on Railway)
- [ ] Keep API keys in environment variables
- [ ] Don't commit `.env` files
- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Enable rate limiting (if needed)
- [ ] Set up monitoring and alerts

---

## 📝 Deployment Commands

### Deploy Backend
```bash
# From Railway CLI
railway login
railway link
railway up
```

### Run Migrations
```bash
railway run alembic upgrade head
```

### View Logs
```bash
railway logs
```

### Set Environment Variable
```bash
railway variables set KEY=value
```

---

## 🎯 Quick Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Railway account
- [ ] Create new project from GitHub
- [ ] Add PostgreSQL database
- [ ] Set environment variables
- [ ] Deploy backend
- [ ] Copy backend URL
- [ ] Deploy frontend (Vercel/Netlify)
- [ ] Set frontend env vars
- [ ] Test deployment
- [ ] Add custom domain (optional)
- [ ] Set up monitoring

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Railway Templates: https://railway.app/templates
- Railway Discord: https://discord.gg/railway
- Vercel Docs: https://vercel.com/docs
- Netlify Docs: https://docs.netlify.com

---

## ✅ Deployment Status

**Ready for Railway Deployment:** ✅

All necessary files are present:
- ✅ Backend configuration files
- ✅ Frontend build configuration
- ✅ Database migration files
- ✅ Environment variable templates
- ✅ Deployment scripts

**Next Steps:**
1. Push code to GitHub
2. Follow deployment steps above
3. Set environment variables
4. Deploy and test

---

**Estimated Deployment Time:** 15-30 minutes  
**Difficulty:** Easy  
**Cost:** Free tier available
