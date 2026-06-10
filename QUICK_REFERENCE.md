# 📚 Quick Reference Card

## 🚀 Start the Application (2 Commands)

```bash
# Terminal 1
source venv/bin/activate && python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Then open: **http://localhost:5173**

---

## 📍 File Locations Cheat Sheet

| What | Where |
|------|-------|
| Backend Entry Point | `backend/main.py` |
| API Routes | `backend/routes/analysis.py` |
| API Client Setup | `frontend/src/api/client.js` |
| API Methods | `frontend/src/api/endpoints.js` |
| Analyze Hook | `frontend/src/hooks/useAnalyze.js` |
| States Hook | `frontend/src/hooks/useStates.js` |
| EMA Chart Hook | `frontend/src/hooks/useEmaScores.js` |
| Landing Page | `frontend/src/pages/LandingPage.jsx` |
| Dashboard Page | `frontend/src/pages/DashboardPage.jsx` |
| App Router | `frontend/src/App.jsx` |
| Config | `backend/config.py` |
| Settings | `.env` (root), `frontend/.env` |

---

## 🔌 API Endpoints

### Analyze Message
```javascript
POST /api/analyze
{message: "text", user_id: "user"}
→ {short_term_state, mid_term_state, long_term_state, significance_score, ...}
```

### Get States
```javascript
GET /api/states?user_id=user
→ {short_term, mid_term, long_term, short_term_score, ...}
```

### Get EMA Timeline
```javascript
GET /api/ema-scores?user_id=user&days=1
→ {data: [{time, shortTerm, midTerm, longTerm}, ...]}
```

### Health Check
```javascript
GET /health
→ {status: "ok", message: "..."}
```

---

## ⚙️ React Hooks Usage

### useAnalyze
```javascript
const { analyze, loading, error, result, reset } = useAnalyze();
await analyze("message");
```

### useStates
```javascript
const { states, loading, error, refetch } = useStates('user_id');
// states.short_term, states.short_term_score, etc.
```

### useEmaScores
```javascript
const { data, loading, error } = useEmaScores('user_id', 1);
// data ready for recharts
```

---

## 🛠️ Common Commands

| Task | Command |
|------|---------|
| Activate venv | `source venv/bin/activate` |
| Start backend | `python -m uvicorn backend.main:app --reload --port 8000` |
| Start frontend | `cd frontend && npm run dev` |
| Install pip deps | `pip install -r requirements.txt` |
| Install npm deps | `npm install axios recharts` |
| Check backend health | `curl http://localhost:8000/health` |
| Test API call | `curl -X POST http://localhost:8000/api/analyze -H "Content-Type: application/json" -d '{"message":"test", "user_id":"user"}'` |
| Kill port 8000 | `lsof -i :8000 && kill -9 <PID>` |
| Git push | `git push -u origin main` |

---

## 📋 Environment Variables

### Root `.env`
```bash
HF_TOKEN=your_token_here
BACKEND_PORT=8000
FLASK_ENV=development
DATABASE_URL=sqlite:///./test.db
```

### `frontend/.env`
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🎯 Data Flow Summary

```
Message Input (Frontend)
    ↓
useAnalyze Hook
    ↓
POST /api/analyze
    ↓
FastAPI Route
    ↓
Core Logic (Orchestrator)
    ↓
Emotional Detection + State Update
    ↓
Response with Results
    ↓
Display in Frontend
```

---

## ❌ Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `lsof -i :8000 && kill -9 <PID>` |
| CORS error | Check backend has CORS middleware |
| Module not found | `pip install -r requirements.txt` |
| npm packages missing | `npm install axios recharts` |
| .env not loading | Restart backend & check file exists |
| API returns 500 | Check backend console for errors |
| Frontend won't connect | Check VITE_API_URL in frontend/.env |

---

## 📊 Component Integration Checklist

- [x] Backend API created
- [x] Frontend API client created
- [x] React hooks created
- [x] Environment configured
- [x] CORS enabled
- [ ] Wire Dashboard to hooks (NEXT STEP)
- [ ] Add toast notifications (OPTIONAL)
- [ ] Deploy (LATER)

---

## 🔗 Important Links

- Backend Docs: http://localhost:8000/docs (FastAPI Swagger)
- Frontend Dev: http://localhost:5173
- Setup Guide: `SETUP_GUIDE.md`
- Integration Summary: `INTEGRATION_SUMMARY.md`
- Architecture: `ARCHITECTURE_DIAGRAM.md`

---

## 💡 Pro Tips

1. **Auto-reload**: Both backend (`--reload`) and frontend (`npm run dev`) auto-refresh
2. **API Testing**: Use http://localhost:8000/docs to test endpoints interactively
3. **Console Logs**: Check both browser console and terminal for errors
4. **Git**: Already configured with .gitignore
5. **Hooks**: Always call them at top-level of component (React rules)
6. **Error Handling**: All hooks have error states - use them!

---

## 📦 Dependencies Installed

**Python (via requirements.txt):**
- fastapi, uvicorn, pydantic, python-dotenv ✅

**Node.js (install separately):**
```bash
npm install axios recharts
```

---

## 🚨 Before You Deploy

1. [ ] Test all endpoints
2. [ ] Set real HF_TOKEN in .env
3. [ ] Test error scenarios
4. [ ] Check CORS for production domain
5. [ ] Review .gitignore
6. [ ] Run tests
7. [ ] Build frontend: `npm run build`
8. [ ] Deploy backend & frontend separately

---

## 📞 Quick Support

**Issue**: Backend won't connect to core modules
**Fix**: Make sure sys.path is set correctly in `backend/routes/analysis.py`

**Issue**: States not updating
**Fix**: Check user_id is consistent across calls

**Issue**: Chart shows dummy data
**Fix**: Wire `useEmaScores` hook to dashboard

**Issue**: Button doesn't navigate
**Fix**: Check React Router is set up in App.jsx ✅ (Already done!)

---

## 🎓 Architecture at a Glance

```
Frontend (React)
    ↕ HTTP/JSON
Backend (FastAPI)  
    ↕ Python Imports
Core Logic (Python)
```

**Files You Created Today:**
- ✅ backend/main.py
- ✅ backend/config.py
- ✅ backend/routes/analysis.py, health.py
- ✅ backend/services/emotional_state_service.py
- ✅ frontend/src/api/client.js, endpoints.js
- ✅ frontend/src/hooks/useAnalyze.js, useStates.js, useEmaScores.js
- ✅ frontend/.env
- ✅ .gitignore
- ✅ .env.example
- ✅ Documentation files

---

## ✨ What's Working

| Feature | Status |
|---------|--------|
| Frontend pages | ✅ Ready |
| API endpoints | ✅ Ready |
| React hooks | ✅ Ready |
| Routing | ✅ Ready |
| Environment vars | ✅ Ready |
| CORS | ✅ Ready |
| Error handling | ✅ Ready |

---

## 🎉 You're All Set!

Everything is configured and ready to use. Just run the two commands and start coding!
