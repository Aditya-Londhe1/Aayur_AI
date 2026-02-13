# Railway Deployment Checklist ✅

## Pre-Deployment (Complete ✅)

- [x] All tests passed (9/9)
- [x] Backend files ready
- [x] Frontend files ready
- [x] Deployment files created
- [x] Documentation complete

---

## Files Created for Railway

✅ **Backend Files:**
- `backend/Procfile` - Start command for Railway
- `backend/runtime.txt` - Python 3.11
- `backend/requirements.txt` - All dependencies

✅ **Root Files:**
- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration

✅ **Frontend Files:**
- `frontend/package.json` - Node dependencies
- `frontend/vite.config.js` - Build configuration

---

## Deployment Steps

### 1. Prepare Repository
- [ ] Commit all changes
- [ ] Push to GitHub
- [ ] Ensure repository is public or Railway has access

### 2. Deploy Backend on Railway

- [ ] Go to https://railway.app
- [ ] Sign up/Login with GitHub
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository
- [ ] Set root directory: `backend`

### 3. Add Database

- [ ] Click "New" → "Database" → "PostgreSQL"
- [ ] Wait for database to provision
- [ ] `DATABASE_URL` will be set automatically

### 4. Set Environment Variables

Required variables:
- [ ] `GEMINI_API_KEY` - Your Gemini API key
- [ ] `SECRET_KEY` - Random 32+ character string
- [ ] `CORS_ORIGINS` - Your frontend URL
- [ ] `ENVIRONMENT` - Set to "production"

Optional variables:
- [ ] `SMTP_HOST` - If using email
- [ ] `SMTP_USER` - Email username
- [ ] `SMTP_PASSWORD` - Email password

### 5. Deploy Backend

- [ ] Click "Deploy"
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check logs for errors
- [ ] Copy backend URL (e.g., `https://your-app.railway.app`)

### 6. Test Backend

- [ ] Visit `https://your-backend-url/health`
- [ ] Should see: `{"status": "healthy"}`
- [ ] Test API endpoints

### 7. Deploy Frontend (Choose One)

**Option A: Vercel (Recommended)**
- [ ] Go to https://vercel.com
- [ ] Import GitHub repository
- [ ] Set root directory: `frontend`
- [ ] Add env var: `VITE_API_URL=https://your-backend.railway.app/api/v1`
- [ ] Deploy

**Option B: Netlify**
- [ ] Go to https://netlify.com
- [ ] Import GitHub repository
- [ ] Base directory: `frontend`
- [ ] Build command: `npm run build`
- [ ] Publish directory: `frontend/dist`
- [ ] Add env var: `VITE_API_URL=https://your-backend.railway.app/api/v1`
- [ ] Deploy

**Option C: Railway (Full Stack)**
- [ ] Use same Railway project
- [ ] Frontend will be served from backend
- [ ] Set `VITE_API_URL=/api/v1`

### 8. Update Backend CORS

- [ ] Go to Railway backend service
- [ ] Update `CORS_ORIGINS` with frontend URL
- [ ] Example: `https://your-app.vercel.app`
- [ ] Redeploy backend

### 9. Test Complete Application

- [ ] Visit frontend URL
- [ ] Test home page loads
- [ ] Complete a consultation
- [ ] Check pulse analysis works
- [ ] Test voice AI (if applicable)
- [ ] Verify results display
- [ ] Test PDF download

### 10. Post-Deployment

- [ ] Set up custom domain (optional)
- [ ] Configure monitoring
- [ ] Set up error alerts
- [ ] Document deployment URLs
- [ ] Share with users!

---

## Environment Variables Reference

### Backend (Railway)
```
DATABASE_URL=<auto-set-by-railway>
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_random_32_char_string
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
ALGORITHM=HS256
```

### Frontend (Vercel/Netlify)
```
VITE_API_URL=https://your-backend.railway.app/api/v1
```

---

## Quick Commands

### Generate SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Backend Health
```bash
curl https://your-backend.railway.app/health
```

### View Railway Logs
```bash
railway logs
```

---

## Troubleshooting

### Build Fails
- Check Railway logs
- Verify `requirements.txt` is correct
- Ensure Python version matches

### Database Error
- Verify PostgreSQL is added
- Check `DATABASE_URL` is set
- Run migrations if needed

### CORS Error
- Update `CORS_ORIGINS` in backend
- Include frontend URL
- Redeploy backend

### Frontend Can't Connect
- Verify `VITE_API_URL` is correct
- Check backend is running
- Test backend health endpoint

---

## Success Criteria

✅ Backend deployed and healthy  
✅ Database connected  
✅ Frontend deployed  
✅ API calls working  
✅ Complete consultation works  
✅ No CORS errors  
✅ All features functional  

---

## Estimated Time

- Backend deployment: 10-15 minutes
- Database setup: 2-3 minutes
- Frontend deployment: 5-10 minutes
- Testing: 5-10 minutes

**Total: 25-40 minutes**

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Vercel Docs: https://vercel.com/docs
- Your deployment guide: `RAILWAY_DEPLOYMENT_GUIDE.md`

---

**Status:** ✅ Ready for Deployment  
**All Files Present:** ✅ Yes  
**Tests Passed:** ✅ 9/9  
**Documentation:** ✅ Complete
