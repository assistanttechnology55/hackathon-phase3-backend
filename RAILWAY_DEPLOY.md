# Railway Deployment Guide - Backend

## Step-by-Step Instructions

### 1. Push Backend to GitHub

1. **Initialize git in backend folder**:
```bash
cd D:\hackathon-2\phase-3\backend
git init
git add .
git commit -m "Initial backend commit"
```

2. **Create a new GitHub repository**:
   - Go to https://github.com/new
   - Create a repo named `hackathon-phase3-backend`
   - Make it **Public** or **Private**

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/hackathon-phase3-backend.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway

1. **Go to Railway**: https://railway.app/

2. **Sign up/Login** with GitHub

3. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your backend repository

4. **Configure Environment Variables**:
   In Railway dashboard, go to Variables tab and add:

   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | Your Neon database URL |
   | `OPENAI_API_KEY` | Your OpenAI API key |
   | `BETTER_AUTH_SECRET` | Your secret key |
   | `BETTER_AUTH_URL` | Your Railway URL |
   | `PORT` | `8000` |

5. **Deploy**:
   - Railway will automatically detect Python and start building
   - Wait for deployment to complete (~2-3 minutes)
   - Your backend will be live at: `https://your-project-name.up.railway.app`

### 3. Update CORS for Frontend

After deployment, update `app/main.py` CORS origins to include your Railway URL.

### 4. Test the Deployment

1. **Health Check**: Visit `https://your-project-name.up.railway.app/health`
2. **API Docs**: Visit `https://your-project-name.up.railway.app/docs`

---

## Quick Commands Reference

```bash
cd D:\hackathon-2\phase-3\backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
