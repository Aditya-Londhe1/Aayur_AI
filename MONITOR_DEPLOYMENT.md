# 👀 Monitor Your Railway Deployment

## What's Happening Now

Railway detected your push and is building your app using Nixpacks!

---

## How to Monitor

### 1. Go to Railway Dashboard
Visit: https://railway.app/dashboard

### 2. Click on Your Service
Find your AayurAI project and click on it

### 3. View Deployment Logs
Click on "Deployments" tab → Click on the latest deployment

---

## What You Should See

### ✅ Good Signs (Nixpacks Build):

```
[info] Using Nixpacks
[info] Installing Python 3.11
[info] Installing Node.js 18
[info] Running: cd backend && pip install -r requirements.txt
[info] Running: cd frontend && npm install
[info] Running: cd frontend && npm run build
[info] Starting: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
[info] ✓ Deployment successful
```

### ❌ Bad Signs (Would indicate issues):

```
[error] Using Detected Dockerfile
[error] Failed to build
[error] Missing environment variable
```

---

## Build Timeline

```
0:00 - Push detected
0:30 - Installing Python 3.11
1:00 - Installing Node.js 18
2:00 - Installing backend dependencies (pip)
3:00 - Installing frontend dependencies (npm)
4:00 - Building frontend (npm run build)
6:00 - Starting server (uvicorn)
7:00 - Health check
8:00 - ✓ Deployment complete!
```

**Total Time:** 5-8 minutes

---

## After Deployment Completes

### 1. Get Your URL

Railway Dashboard → Your Service → Settings → Domains

Copy the URL (e.g., `https://aayurai-production.up.railway.app`)

### 2. Test Health Endpoint

```bash
curl https://your-app.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-14T...",
  "locale": "en",
  "message": "System is healthy"
}
```

### 3. Visit Frontend

Open in browser: `https://your-app.railway.app`

**Should see:**
- ✅ Home page loads
- ✅ Navigation works
- ✅ No console errors
- ✅ SVG icons display

### 4. Check API Documentation

Open: `https://your-app.railway.app/docs`

**Should see:**
- ✅ FastAPI Swagger UI
- ✅ All endpoints listed
- ✅ Can test endpoints

### 5. Complete Test Flow

1. Go to Assessment page
2. Fill out consultation form
3. Submit
4. View results
5. Test all features:
   - Pulse analysis
   - Tongue analysis
   - Voice AI
   - PDF download
   - Feedback

---

## Environment Variables Check

Make sure these are set in Railway:

### Required:
- [ ] `GEMINI_API_KEY` - Your Gemini API key
- [ ] `SECRET_KEY` - Random 32-char string

### Auto-Set:
- [x] `DATABASE_URL` - Set when PostgreSQL added
- [x] `PORT` - Railway sets automatically

### To Check:
Railway Dashboard → Your Service → Variables

---

## Common Issues & Solutions

### Issue 1: Build Fails - Missing GEMINI_API_KEY

**Error:**
```
[error] GEMINI_API_KEY environment variable not set
```

**Solution:**
1. Railway Dashboard → Your Service → Variables
2. Add: `GEMINI_API_KEY` = your_key
3. Redeploy (Railway will auto-redeploy)

---

### Issue 2: Build Fails - Missing SECRET_KEY

**Error:**
```
[error] SECRET_KEY environment variable not set
```

**Solution:**
1. Generate key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Railway Dashboard → Your Service → Variables
3. Add: `SECRET_KEY` = generated_key
4. Redeploy

---

### Issue 3: Frontend Build Fails

**Error:**
```
[error] npm run build failed
```

**Solution:**
Check Railway logs for specific error. Common causes:
- Missing dependencies in `package.json`
- Syntax errors in frontend code
- Environment variable issues

**Fix:**
1. Fix the issue locally
2. Test: `cd frontend && npm run build`
3. Commit and push
4. Railway will auto-redeploy

---

### Issue 4: Database Connection Error

**Error:**
```
[error] Could not connect to database
[error] DATABASE_URL not set
```

**Solution:**
1. Railway Dashboard → New → Database → PostgreSQL
2. Wait for provisioning (1-2 minutes)
3. `DATABASE_URL` will be set automatically
4. Railway will auto-redeploy

---

### Issue 5: Still Using Dockerfile

**Error:**
```
[info] Using Detected Dockerfile
```

**Solution:**
1. Make sure `Dockerfile` is renamed to `Dockerfile.docker`
2. Check `.railwayignore` exists
3. Force Nixpacks:
   - Railway Dashboard → Settings → Build
   - Builder: Select "Nixpacks"
4. Redeploy

---

## Manual Redeploy

If you need to manually trigger a redeploy:

1. Railway Dashboard → Your Service
2. Click "Deployments"
3. Click "Deploy" button (top right)
4. Select "Redeploy"

---

## View Logs in Real-Time

### In Railway Dashboard:
1. Click on your service
2. Click "Logs" tab
3. Watch real-time logs

### Using Railway CLI (Optional):
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs
```

---

## Success Checklist

After deployment completes, verify:

- [ ] Build completed successfully (no errors)
- [ ] Service status: Running (green)
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads at root URL
- [ ] API docs accessible at /docs
- [ ] Can complete a consultation
- [ ] Results page displays correctly
- [ ] PDF download works
- [ ] Voice AI responds
- [ ] All features functional

---

## Performance Monitoring

### Check Service Metrics:

Railway Dashboard → Your Service → Metrics

**Monitor:**
- CPU usage (should be < 50% normally)
- Memory usage (should be < 512MB normally)
- Network traffic
- Request count
- Response times

### Set Up Alerts (Optional):

1. Railway Dashboard → Project Settings
2. Add webhook for notifications
3. Configure alerts for:
   - Deployment failures
   - High CPU/memory usage
   - Service downtime

---

## Next Steps After Successful Deployment

### 1. Custom Domain (Optional)

Railway Dashboard → Your Service → Settings → Domains
- Click "Add Domain"
- Enter your domain (e.g., `aayurai.com`)
- Update DNS records as instructed
- SSL certificate auto-configured

### 2. Share Your App

Your app is live! Share the URL:
- With doctors for testing
- With users for feedback
- On social media
- In documentation

### 3. Monitor Usage

- Check Railway metrics daily
- Monitor error logs
- Track user feedback
- Plan for scaling if needed

### 4. Continuous Deployment

Now set up! Every time you push to GitHub:
- Railway auto-detects changes
- Builds and deploys automatically
- Zero downtime deployment

---

## Troubleshooting Commands

```bash
# Check git status
git status

# View recent commits
git log --oneline -5

# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test health endpoint
curl https://your-app.railway.app/health

# Test API endpoint
curl https://your-app.railway.app/api/v1/health

# View Railway logs (if CLI installed)
railway logs

# Redeploy (if CLI installed)
railway up
```

---

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app
- **Nixpacks Docs:** https://nixpacks.com

---

## Estimated Timeline

- **Now:** Monitoring deployment
- **+5-8 min:** Build completes
- **+8-10 min:** Service running
- **+10 min:** Testing complete
- **+15 min:** Fully deployed and verified! 🎉

---

**Current Status:** 🔄 DEPLOYING

Watch your Railway dashboard for progress!

---

*Good luck! Your app should be live in about 10 minutes!* 🚀
