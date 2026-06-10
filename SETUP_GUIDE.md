# State Identification Module - Full Stack Setup

## Overview

This is a full-stack application with:
- **Backend**: FastAPI (Python) - handles emotional state analysis
- **Frontend**: React + Vite - provides UI for analysis
- **Core**: state_management_module - contains EMA/PRISM logic

## Project Structure

```
state_management_module/
├── backend/                    # FastAPI application
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration & settings
│   ├── routes/                 # API endpoints
│   │   ├── health.py          # Health check
│   │   └── analysis.py        # Analysis endpoints
│   └── services/               # Business logic layer
│       └── emotional_state_service.py
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── pages/             # Page components
│   │   │   ├── LandingPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── api/               # API client
│   │   │   ├── client.js      # Axios setup
│   │   │   └── endpoints.js   # API calls
│   │   └── hooks/             # Custom React hooks
│   │       ├── useAnalyze.js
│   │       ├── useEmaScores.js
│   │       └── useStates.js
│   ├── package.json
│   └── .env                   # Frontend env vars
├── core/                       # Core logic modules
│   ├── orchestrator.py
│   ├── emotional_detector.py
│   ├── temporal_extractor.py
│   └── user_profile.py
├── requirements.txt           # Python dependencies
└── .env                       # Root env (HF_TOKEN, PORT, etc.)
```

## Prerequisites

- **Python 3.9+** (with venv activated)
- **Node.js 18+** (for frontend)
- **Virtual Environment** (already activated at root level)

## Installation & Setup

### 1. Backend Setup (Python)

```bash
# Navigate to project root
cd /home/vaibhav-mishra/projects/AEI/state_management_module

# Ensure venv is activated (should already be)
source venv/bin/activate

# Install backend dependencies (if not already installed)
pip install -r requirements.txt

# Ensure FastAPI + uvicorn are installed
pip install fastapi uvicorn python-dotenv
```

### 2. Frontend Setup (Node.js)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Install axios for API calls
npm install axios

# Install recharts for charts
npm install recharts
```

### 3. Environment Configuration

Create `.env` file at project root (if not exists):

```bash
# HuggingFace Configuration
HF_TOKEN=your_huggingface_token

# Backend Server Configuration
BACKEND_PORT=8000
FLASK_ENV=development

# Database (optional)
DATABASE_URL=sqlite:///./test.db
```

Frontend already has `.env`:
```bash
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Option 1: Run Both in Separate Terminals

**Terminal 1 - Backend:**
```bash
cd /home/vaibhav-mishra/projects/AEI/state_management_module
source venv/bin/activate
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /home/vaibhav-mishra/projects/AEI/state_management_module/frontend
npm run dev
```

Then open: http://localhost:5173

### Option 2: Using npm scripts (add to package.json)

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "backend": "python -m uvicorn backend.main:app --reload --port 8000"
  }
}
```

## API Endpoints

### Health Check
```
GET /health
Response: { "status": "ok", "message": "..." }
```

### Analyze Message
```
POST /api/analyze
Body: { "message": "string", "user_id": "string" }
Response: {
  "message": "...",
  "short_term_state": "...",
  "mid_term_state": "...",
  "long_term_state": "...",
  "significance_score": 7.4,
  "emotions": { ... },
  "timestamp": "..."
}
```

### Get Current States
```
GET /api/states?user_id=default_user
Response: {
  "short_term": "Neutral",
  "mid_term": "Stable",
  "long_term": "Positive",
  "short_term_score": 5.0,
  "mid_term_score": 5.0,
  "long_term_score": 5.0
}
```

### Get EMA Timeline
```
GET /api/ema-scores?user_id=default_user&days=1
Response: {
  "data": [
    { "time": "00:00", "shortTerm": 5.2, "midTerm": 5.0, "longTerm": 5.1 },
    ...
  ]
}
```

## Frontend Components

### LandingPage
- Hero section with Lightfall background
- "Analyze Now" button → navigates to `/dashboard`
- "View Docs" button → links to documentation

### DashboardPage
- Fixed sidebar with navigation
- Stat cards showing current states
- EMA score timeline chart
- Message input for analysis
- Significance score display

## Custom Hooks

### useAnalyze()
```javascript
const { analyze, loading, error, result, reset } = useAnalyze();
await analyze("Your message here");
```

### useEmaScores(userId, days)
```javascript
const { data, loading, error } = useEmaScores('default_user', 1);
// data is array of EMA data points for chart
```

### useStates(userId)
```javascript
const { states, loading, error, refetch } = useStates('default_user');
// states includes short_term, mid_term, long_term + scores
```

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Try different port
python -m uvicorn backend.main:app --reload --port 8001
```

### Frontend can't connect to backend
- Check backend is running on http://localhost:8000
- Check VITE_API_URL in frontend/.env
- Check browser console for CORS errors
- Ensure backend has CORS middleware enabled

### Module import errors
```bash
# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

## Next Steps

1. ✅ Backend API endpoints created
2. ✅ Frontend API client configured
3. ✅ React hooks for data fetching created
4. ✅ Environment variables set up
5. 🔄 Wire DashboardPage to real API calls
6. 🔄 Add state management (Context API)
7. 🔄 Add error handling & loading states
8. 🔄 Add authentication (if needed)
9. 🔄 Deploy backend & frontend

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [Axios Docs](https://axios-http.com/)
- [Recharts Docs](https://recharts.org/)
