# Criminal Law Knowledge Base - Integration Guide

> **Kamado Legal AI Assistant** - A comprehensive legal search and chatbot system with cloud database

## 🚀 Project Overview

**Section Sense** is a full-stack application for searching and understanding Indian Criminal Law (BNS/BNSS/BSA) with an AI-powered chatbot assistant.

### Tech Stack
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python 3.12
- **Database:** Supabase PostgreSQL (Cloud)
- **AI:** Groq API (llama-3.1-8b-instant)
- **Search:** Universal Search Service (works with SQLite & PostgreSQL)

---

## 📂 Project Structure

```
BDA lab/
├── Backend/                          # FastAPI Backend
│   ├── .env                         # Environment variables (DB config)
│   ├── requirements.txt             # Python dependencies
│   ├── app/
│   │   ├── main.py                 # FastAPI application & routes
│   │   ├── database.py             # PostgreSQL connection
│   │   ├── schemas.py              # Pydantic models
│   │   ├── models/
│   │   │   ├── law_models.py      # Law section models
│   │   │   └── chat_models.py     # Chat storage models
│   │   └── services/
│   │       ├── universal_search_service.py   # Search engine
│   │       ├── chatbot_service.py           # Chatbot API
│   │       └── explanation_service.py       # Legal explanations
│   └── migrations/
│       ├── create_schema.sql       # Database schema
│       └── add_chat_storage.sql    # Chat storage schema
│
├── Frontend/                        # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatGPTChatbot.tsx # ChatGPT-style chatbot
│   │   │   ├── SearchResults.tsx   # Law section search UI
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.ts             # Backend API calls
│   │   └── App.tsx
│   └── package.json
│
└── INTEGRATION_README.md           # This file
```

---

## 🗄️ Database

**Using:** Supabase PostgreSQL (Cloud Database)

### Database Info:
- **Provider:** Supabase
- **Region:** ap-south-1 (Mumbai)
- **Connection:** Session Pooler (IPv4)
- **Tables:** 9 tables
- **Law Sections:** 1,056 sections (BNS/BNSS/BSA)

### Tables:
- `law_sections` - Indian criminal law sections
- `legal_cases` - Legal cases and judgments
- `case_citations` - Case citations
- `case_section_association` - Many-to-many relationships
- `case_similarities` - Case similarity scores
- `law_amendments` - Amendment tracking
- `search_queries` - Search analytics
- `chat_conversations` - Chatbot conversation history
- `chat_messages` - Individual chat messages

---

## ⚙️ Quick Start

### Prerequisites
- Python 3.12+ with Anaconda
- Node.js 18+
- Supabase account (already configured)

### 1. Start Backend (FastAPI)

```bash
# Open Terminal 1
cd "Backend"
python -m uvicorn app.main:app --reload
```

**Backend will run on:** http://127.0.0.1:8000

**API Documentation:** http://127.0.0.1:8000/docs

### 2. Start Frontend (React + Vite)

```bash
# Open Terminal 2
cd "Frontend"
npm run dev
```

**Frontend will run on:** http://localhost:5173

---

## 🔌 API Endpoints

### System Endpoints
- `GET /` - API information
- `GET /api/v1/health` - Health check
- `GET /api/v1/database/info` - Database information (verify Supabase connection)

### Search Endpoints
- `POST /api/v1/search` - Search law sections
- `GET /api/v1/search/sections` - Get all sections
- `GET /api/v1/sections/{code}` - Get specific section
- `GET /api/v1/suggestions?query=...` - Search suggestions

### Chatbot Endpoints
- `POST /chatbot/stream` - Streaming chat responses (ChatGPT-style)
- `POST /chatbot` - Non-streaming chat
- `GET /chatbot/health` - Chatbot service health
- `POST /chatbot/conversations/save` - Save conversation to database
- `GET /chatbot/conversations` - List all conversations
- `GET /chatbot/conversations/{id}` - Get specific conversation
- `DELETE /chatbot/conversations/{id}` - Delete conversation

### Explanation Endpoints
- `POST /api/v1/explain` - Get legal explanations

---

## 🌟 Key Features

### 1. **Law Section Search**
- Semantic search with relevance ranking
- 1,056+ law sections (BNS/BNSS/BSA)
- Category filtering
- Real-time suggestions
- Detailed section information

### 2. **Kamado AI Chatbot**
- ChatGPT-style streaming responses
- Conversation history (saved to PostgreSQL)
- Multiple chat sessions
- Plain text responses (no markdown formatting)
- Legal expertise on Indian Criminal Law
- Context-aware responses (remembers last 10 messages)

### 3. **Cloud Database**
- Supabase PostgreSQL
- Automatic backups
- High availability
- Session pooler for IPv4 compatibility

---

## 🔧 Configuration Files

### Backend Configuration (.env)
```env
# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# Groq API (for chatbot)
GROQ_API_KEY=your_groq_api_key_here
```

### Frontend Configuration
- **API Base URL:** Configured in `src/services/api.ts`
- **Default:** http://localhost:8000

---

## 🧪 Testing the Integration

### 1. Verify Database Connection
```bash
cd Backend
python -c "from app.database import DATABASE_URL; print('Using:', 'PostgreSQL (Supabase)' if DATABASE_URL.startswith('postgresql') else 'SQLite')"
```

**Expected:** `Using: PostgreSQL (Supabase)`

### 2. Check API Health
Visit: http://127.0.0.1:8000/api/v1/database/info

**Expected Response:**
```json
{
  "database_type": "PostgreSQL (Supabase)",
  "is_cloud_database": true,
  "law_sections_count": 1056,
  "chat_conversations_count": 0,
  "status": "Connected ✅"
}
```

### 3. Test Search
1. Open frontend: http://localhost:5173
2. Search for "theft" or "murder"
3. Should return relevant law sections

### 4. Test Chatbot
1. Click chat button in bottom-right
2. Ask: "What is BNS Section 101?"
3. Should get streaming response about theft

---

## 📊 Database Schema

### Law Sections Table
```sql
CREATE TABLE law_sections (
    id SERIAL PRIMARY KEY,
    section_code VARCHAR(50) UNIQUE NOT NULL,
    section_number VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    punishment TEXT,
    ...
);
```

### Chat Storage Tables
```sql
CREATE TABLE chat_conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ...
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(100) REFERENCES chat_conversations(conversation_id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    ...
);
```

---

## 🐛 Troubleshooting

### Backend won't start
1. Check if port 8000 is free: `netstat -ano | findstr :8000`
2. Verify Python environment: `python --version` (should be 3.12+)
3. Check database connection in `.env` file

### Frontend won't start
1. Check if port 5173 is free
2. Delete `node_modules` and run `npm install` again
3. Check if backend is running first

### Database connection errors
1. Verify Supabase project is active
2. Check connection string in `Backend/.env`
3. Run: `python Backend/verify_database.py` (if file exists)

### Chatbot not responding
1. Check GROQ_API_KEY in `.env`
2. Verify API key is valid
3. Check backend logs for errors

---

## 📝 Development Notes

### Adding New Endpoints
1. Add route in `Backend/app/main.py`
2. Add Pydantic schema in `Backend/app/schemas.py`
3. Add API call in `Frontend/src/services/api.ts`
4. Use in components with proper error handling

### Database Migrations
- Schema files: `Backend/migrations/*.sql`
- Run in Supabase SQL Editor to update schema
- Models: `Backend/app/models/*.py`

### Code Style
- Backend: PEP 8 (Python)
- Frontend: ESLint + Prettier (TypeScript/React)

---

## 🚀 Production Deployment (Render)

### Prerequisites
1. **GitHub Account**: Push your code to GitHub
2. **Render Account**: Sign up at https://render.com
3. **Supabase Account**: Already set up with PostgreSQL database
4. **Groq API Key**: Get from https://console.groq.com

### Step 1: Prepare Your Repository

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit for Render deployment"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub Repository**
4. **Configure Backend Service**:
   - **Name**: `criminal-law-api` (or your choice)
   - **Region**: Singapore (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `Backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && chmod +x build.sh && ./build.sh`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

5. **Add Environment Variables** (in Render dashboard):
   ```
   DATABASE_URL = postgresql://postgres.lwssvbpipedxtosjqbcn:Sachin3Shruti@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
   GROQ_API_KEY = your_groq_api_key_here
   ALLOWED_ORIGINS = https://your-frontend-url.onrender.com
   PYTHON_VERSION = 3.12.0
   ```

6. **Click "Create Web Service"**
7. **Wait for deployment** (5-10 minutes first time)
8. **Your backend URL**: `https://criminal-law-api.onrender.com`

### Step 3: Deploy Frontend to Render

1. **Go to Render Dashboard** → **"New +"** → **"Static Site"**
2. **Select Same GitHub Repository**
3. **Configure Frontend Service**:
   - **Name**: `criminal-law-frontend`
   - **Region**: Singapore
   - **Branch**: `main`
   - **Root Directory**: `Frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Add Environment Variable**:
   ```
   VITE_API_BASE_URL = https://your-backend-url.onrender.com
   ```
   *(Replace with your actual backend URL from Step 2)*

5. **Click "Create Static Site"**
6. **Your frontend URL**: `https://criminal-law-frontend.onrender.com`

### Step 4: Update Backend CORS

After frontend is deployed, update backend environment variable:
```
ALLOWED_ORIGINS = https://criminal-law-frontend.onrender.com
```

### Step 5: Test Production Deployment

1. **Visit Frontend URL**: `https://criminal-law-frontend.onrender.com`
2. **Test Search**: Search for "theft" or "murder"
3. **Test Chatbot**: Click chat icon, ask about law sections
4. **Check Health**: Visit `https://your-backend-url.onrender.com/api/v1/health`

### Important Notes

⚠️ **Free Tier Limitations**:
- Backend spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free (enough for one service)

💡 **Optimization Tips**:
- Use Render's "Keep Alive" service (paid)
- Implement proper caching
- Optimize ML model loading in `build.sh`

🔒 **Security Best Practices**:
- Never commit `.env` files
- Use environment variables for all secrets
- Set specific CORS origins (not `*`)
- Enable HTTPS (automatic on Render)

### Alternative: Deploy Using render.yaml

You can use the included `render.yaml` file for Infrastructure as Code:

1. **Push to GitHub** with `render.yaml` in root
2. **In Render Dashboard**: "New +" → "Blueprint"
3. **Select Repository**
4. **Render will auto-detect** `render.yaml`
5. **Set environment variables** as prompted
6. **Deploy both services** together

---

## 🔧 Environment Variables Reference

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
GROQ_API_KEY=your_groq_api_key_here
ALLOWED_ORIGINS=https://your-frontend.onrender.com,http://localhost:5173
PORT=8000  # Optional, Render sets this automatically
```

### Frontend (.env)
```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## 📖 Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **Supabase Docs:** https://supabase.com/docs
- **Groq API:** https://console.groq.com
- **Render Docs:** https://render.com/docs

---

## 👥 Support

For issues or questions:
1. Check this README
2. Check API documentation: http://localhost:8000/docs (local) or your Render URL/docs (production)
3. Review Render deployment logs
4. Check Supabase database status

---

**Last Updated:** October 19, 2025
**Database:** Supabase PostgreSQL (Cloud)
**Status:** Production-Ready ✅
**Deployment:** Render-Ready 🚀

### Environment Variables
Create a `.env.local` file in the Frontend directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Backend Configuration
The backend uses SQLite by default. Database configuration is in `Backend/app/database.py`.

## Development

### Frontend Development
```bash
cd Frontend
npm install
npm run dev
```

### Backend Development
```bash
cd Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### API Documentation
Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Ensure Python 3.8+ is installed
   - Check if port 8000 is available
   - Verify all dependencies are installed

2. **Frontend can't connect to backend**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend
   - Verify API_BASE_URL in frontend config

3. **Database errors**
   - Check if database file exists
   - Verify database permissions
   - Run database migrations if needed

### Port Conflicts
- Backend: Change port in `Backend/app/main.py` (line 367)
- Frontend: Change port in `Frontend/vite.config.ts`

## Features

### Implemented
- ✅ Real-time search integration
- ✅ Error handling and loading states
- ✅ TypeScript type safety
- ✅ Responsive UI components
- ✅ API service layer
- ✅ CORS configuration

### Backend Features
- ✅ FastAPI with automatic documentation
- ✅ SQLAlchemy ORM
- ✅ Pydantic data validation
- ✅ CORS middleware
- ✅ Health check endpoint
- ✅ Search analytics

### Frontend Features
- ✅ React with TypeScript
- ✅ Tailwind CSS styling
- ✅ Shadcn/ui components
- ✅ React Query for state management
- ✅ Custom hooks for API integration
- ✅ Responsive design

## Next Steps

1. **Data Population**: Add real legal data to the database
2. **Authentication**: Implement user authentication
3. **Advanced Search**: Add filters and advanced search options
4. **Caching**: Implement response caching
5. **Testing**: Add unit and integration tests
6. **Deployment**: Set up production deployment

## Support

For issues or questions:
1. Check the console for error messages
2. Verify both services are running
3. Check network connectivity
4. Review the API documentation at http://localhost:8000/docs
