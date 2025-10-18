# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment Setup

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] `.gitignore` configured (excludes `.env`, `node_modules`, `__pycache__`, etc.)
- [ ] `render.yaml` in root directory
- [ ] All deployment files present:
  - [ ] `Backend/build.sh`
  - [ ] `Backend/runtime.txt`
  - [ ] `Backend/requirements.txt`
  - [ ] `Backend/.env.example`
  - [ ] `Frontend/.env.example`

### Environment Variables Ready
- [ ] Supabase DATABASE_URL (Session Pooler connection string)
- [ ] GROQ_API_KEY from https://console.groq.com
- [ ] Frontend URL (will get after deployment)
- [ ] Backend URL (will get after deployment)

## 📦 Render Account Setup

- [ ] Render account created at https://render.com
- [ ] GitHub account connected to Render
- [ ] Repository access granted to Render

## 🔧 Backend Deployment (Web Service)

### Configuration
- [ ] New Web Service created
- [ ] Repository connected
- [ ] Root Directory set to: `Backend`
- [ ] Runtime set to: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt && chmod +x build.sh && ./build.sh`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Instance Type: `Free`

### Environment Variables Set
- [ ] `DATABASE_URL` = Your Supabase connection string
- [ ] `GROQ_API_KEY` = Your Groq API key
- [ ] `PYTHON_VERSION` = 3.12.0
- [ ] `ALLOWED_ORIGINS` = * (initially, update after frontend deployed)

### Verification
- [ ] Build logs show successful completion
- [ ] Service status is "Live"
- [ ] Health endpoint works: `https://YOUR-BACKEND.onrender.com/api/v1/health`
- [ ] Database info endpoint works: `https://YOUR-BACKEND.onrender.com/api/v1/database/info`
- [ ] Copy backend URL for frontend configuration

## 🎨 Frontend Deployment (Static Site)

### Configuration
- [ ] New Static Site created
- [ ] Same repository selected
- [ ] Root Directory set to: `Frontend`
- [ ] Build Command: `npm install && npm run build`
- [ ] Publish Directory: `dist`

### Environment Variables Set
- [ ] `VITE_API_BASE_URL` = Your backend URL from above

### Verification
- [ ] Build logs show successful completion
- [ ] Site status is "Live"
- [ ] Frontend loads correctly
- [ ] Copy frontend URL

## 🔒 Security Updates

- [ ] Update backend `ALLOWED_ORIGINS` to frontend URL:
  - Go to backend service → Environment
  - Update: `ALLOWED_ORIGINS=https://YOUR-FRONTEND.onrender.com`
  - Service will auto-redeploy

## ✅ Post-Deployment Testing

### Functionality Tests
- [ ] Frontend loads at: `https://YOUR-FRONTEND.onrender.com`
- [ ] Search works (try "theft", "murder")
- [ ] Search returns results from PostgreSQL
- [ ] Chatbot opens and responds
- [ ] Chatbot uses Groq API
- [ ] No CORS errors in browser console
- [ ] API docs accessible: `https://YOUR-BACKEND.onrender.com/docs`

### Database Verification
- [ ] Visit: `https://YOUR-BACKEND.onrender.com/api/v1/database/info`
- [ ] Verify response shows:
  - `"database_type": "PostgreSQL (Supabase)"`
  - `"is_cloud_database": true`
  - `"law_sections_count": 1056`
  - `"status": "Connected ✅"`

### Performance Check
- [ ] First load (after spin-down) takes 30-60 seconds - **NORMAL for free tier**
- [ ] Subsequent loads are fast
- [ ] Search responds in < 2 seconds
- [ ] Chatbot streams responses

## 🐛 Troubleshooting

### Backend Issues
- **Build fails**: Check `build.sh` permissions and dependencies
- **Database errors**: Verify DATABASE_URL is correct
- **Import errors**: Check all models are imported in `build.sh`
- **Service crashes**: Check Render logs for Python errors

### Frontend Issues
- **Blank page**: Check browser console for errors
- **API errors**: Verify `VITE_API_BASE_URL` is correct
- **CORS errors**: Update `ALLOWED_ORIGINS` in backend

### Database Issues
- **Connection refused**: Check Supabase project is running
- **No data**: Verify 1,056 sections were migrated
- **Timeout**: Check Supabase connection pooler settings

## 📝 Important Notes

### Free Tier Limitations
⚠️ **Backend spins down after 15 minutes of inactivity**
- First request will take 30-60 seconds (cold start)
- Normal behavior for Render free tier
- Consider paid tier ($7/month) for always-on

### ML Model Loading
- Sentence transformers download during build (~100MB)
- First build takes 5-10 minutes
- Cached for subsequent builds

### Database
- Supabase free tier: 500MB storage, 2GB bandwidth
- Session pooler recommended for Render
- Monitor usage in Supabase dashboard

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ Frontend loads at custom Render URL
- ✅ Search returns law sections from cloud database
- ✅ Chatbot responds using Groq AI
- ✅ No console errors
- ✅ `/api/v1/database/info` shows Supabase connection
- ✅ All 1,056 law sections accessible

## 📚 Resources

- **Render Docs**: https://render.com/docs
- **Render Free Tier**: https://render.com/docs/free
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

## 🆘 Support

If deployment fails:
1. Check Render build/deployment logs
2. Verify all environment variables
3. Test locally first: `cd Backend && uvicorn app.main:app`
4. Check Supabase database is accessible
5. Review `INTEGRATION_README.md` for detailed steps

---

**Deployment Date**: __________
**Backend URL**: __________
**Frontend URL**: __________
**Status**: ⬜ In Progress | ⬜ Complete | ⬜ Failed
