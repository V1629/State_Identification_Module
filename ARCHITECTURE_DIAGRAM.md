# Integration Architecture Diagram

## System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                    STATE IDENTIFICATION MODULE                     │
│                    Full-Stack Application                          │
└────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                              │
│                         http://localhost:5173                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Landing Page                                │   │
│  │  • Hero Section                                               │   │
│  │  • "Analyze Now" Button → /dashboard                        │   │
│  │  • Lightfall Background                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                            ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Dashboard Page                              │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ Stat Cards:                                              │  │   │
│  │  │ • Short-Term State                                       │  │   │
│  │  │ • Mid-Term State                                         │  │   │
│  │  │ • Long-Term State                                        │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ EMA Chart (recharts)                                     │  │   │
│  │  │ • Short-Term Line (Indigo)                               │  │   │
│  │  │ • Mid-Term Line (Emerald)                                │  │   │
│  │  │ • Long-Term Line (Rose)                                  │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ Message Input Section                                    │  │   │
│  │  │ • Textarea for message                                   │  │   │
│  │  │ • Analyze Button                                         │  │   │
│  │  │ • Significance Score Display                             │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  HOOKS:                                                                 │
│  • useAnalyze() → POST /api/analyze                                    │
│  • useStates() → GET /api/states                                       │
│  • useEmaScores() → GET /api/ema-scores                                │
│                                                                          │
│  API LAYER:                                                             │
│  • api/client.js (axios + interceptors)                                │
│  • api/endpoints.js (all API methods)                                  │
└──────────────────────────────────────────────────────────────────────────┘
                                    ↕
                        HTTP JSON (CORS Enabled)
                                    ↕
┌──────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                             │
│                         http://localhost:8000                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  main.py                                                                │
│  ├── FastAPI app setup                                                  │
│  ├── CORS Middleware                                                    │
│  ├── Routes registration                                                │
│  └── uvicorn server                                                     │
│                                                                          │
│  routes/health.py                                                       │
│  └── GET /health → {"status": "ok"}                                    │
│                                                                          │
│  routes/analysis.py                                                     │
│  ├── POST /api/analyze                                                  │
│  │   Input: message, user_id                                            │
│  │   Output: states, significance_score, emotions                      │
│  │                                                                      │
│  ├── GET /api/states                                                    │
│  │   Returns: short_term, mid_term, long_term + scores                │
│  │                                                                      │
│  ├── GET /api/ema-scores                                                │
│  │   Returns: 8 EMA data points for chart                              │
│  │                                                                      │
│  └── POST /api/reset                                                    │
│      Resets user state (for testing)                                    │
│                                                                          │
│  services/emotional_state_service.py                                    │
│  ├── EmotionalStateService class                                        │
│  ├── analyze_message()                                                  │
│  ├── get_user_state()                                                   │
│  └── reset_user()                                                       │
│                                                                          │
│  config.py                                                              │
│  ├── Pydantic Settings                                                  │
│  ├── Loads .env variables                                               │
│  └── HF_TOKEN, BACKEND_PORT, DATABASE_URL                              │
└──────────────────────────────────────────────────────────────────────────┘
                                    ↕
                            Python Imports
                                    ↕
┌──────────────────────────────────────────────────────────────────────────┐
│                      CORE LOGIC (state_management_module)               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  core/orchestrator.py                                                   │
│  ├── Orchestrator class                                                 │
│  ├── analyze_message()                                                  │
│  ├── ImpactCalculator                                                   │
│  └── State management                                                   │
│                                                                          │
│  core/emotional_detector.py                                             │
│  ├── classify_emotions()                                                │
│  ├── HuggingFace integration                                            │
│  └── Emotion classification                                             │
│                                                                          │
│  core/temporal_extractor.py                                             │
│  ├── TemporalExtractor class                                            │
│  ├── Time-based state extraction                                        │
│  └── Temporal analysis                                                  │
│                                                                          │
│  core/user_profile.py                                                   │
│  ├── UserProfile class                                                  │
│  ├── short_term_ema, mid_term_ema, long_term_ema                       │
│  └── Emotional state tracking                                           │
│                                                                          │
│  core/chat_logger.py                                                    │
│  ├── ChatLogger class                                                   │
│  └── Message logging                                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Message Analysis

```
1. USER INTERACTION
   ┌─────────────────────────────┐
   │ User types message          │
   │ Clicks "Analyze" button     │
   └──────────────┬──────────────┘
                  ↓
   
2. FRONTEND PROCESSING
   ┌──────────────────────────────────┐
   │ DashboardPage Component          │
   │ message = "I feel great today!"  │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ useAnalyze Hook                  │
   │ setLoading(true)                 │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ api/endpoints.js                 │
   │ analyzeMessage(message)          │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ api/client.js                    │
   │ POST /api/analyze                │
   │ {message, user_id}               │
   └──────────────┬───────────────────┘
                  ↓
   
3. NETWORK REQUEST
   ┌──────────────────────────────────┐
   │ HTTP POST                        │
   │ localhost:8000/api/analyze       │
   │ JSON payload                     │
   └──────────────┬───────────────────┘
                  ↓
   
4. BACKEND PROCESSING
   ┌──────────────────────────────────┐
   │ FastAPI Handler                  │
   │ routes/analysis.py               │
   │ analyze_message()                │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ EmotionalStateService            │
   │ Validate & prepare data          │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ core/orchestrator.py             │
   │ orchestrator.analyze_message()   │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ core/emotional_detector.py       │
   │ HuggingFace API Call             │
   │ classify_emotions(message)       │
   │ Returns: {emotion: probability}  │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ core/temporal_extractor.py       │
   │ Extract temporal patterns        │
   │ Calculate impact score           │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ core/user_profile.py             │
   │ Update EMA scores:               │
   │ • short_term_ema                 │
   │ • mid_term_ema                   │
   │ • long_term_ema                  │
   └──────────────┬───────────────────┘
                  ↓
   
5. RESPONSE GENERATION
   ┌──────────────────────────────────┐
   │ Build Response JSON              │
   │ {                                │
   │   message,                       │
   │   short_term_state: "Positive",  │
   │   mid_term_state: "Stable",      │
   │   long_term_state: "Positive",   │
   │   significance_score: 7.4,       │
   │   emotions: {...},               │
   │   timestamp                      │
   │ }                                │
   └──────────────┬───────────────────┘
                  ↓
   
6. RETURN TO FRONTEND
   ┌──────────────────────────────────┐
   │ HTTP 200 Response with JSON      │
   │ Back over network                │
   └──────────────┬───────────────────┘
                  ↓
   
7. FRONTEND UPDATE
   ┌──────────────────────────────────┐
   │ useAnalyze Hook receives response│
   │ setResult(data)                  │
   │ setLoading(false)                │
   └──────────────┬───────────────────┘
                  ↓
   ┌──────────────────────────────────┐
   │ DashboardPage Re-renders         │
   │ Displays:                        │
   │ • Stat cards update              │
   │ • Significance score: 7.4        │
   │ • Chart data refreshes           │
   │ • Input clears                   │
   └──────────────────────────────────┘
```

---

## Component Tree

```
App.jsx
├── BrowserRouter
│   └── Routes
│       ├── Route "/" → LandingPage
│       │   ├── Lightfall (background)
│       │   ├── Badge ("Emotional AI Analysis")
│       │   ├── H1 ("Understand Every Emotional State")
│       │   ├── P (description)
│       │   └── Buttons
│       │       ├── "Analyze Now" (onClick → navigate /dashboard)
│       │       └── "View Docs"
│       │
│       └── Route "/dashboard" → DashboardPage
│           ├── Sidebar
│           │   ├── Logo ("SIM")
│           │   ├── Nav Items
│           │   └── Version
│           │
│           └── Main Content
│               ├── Topbar
│               │   ├── Title
│               │   └── Status Badge
│               │
│               ├── Stat Cards (Grid)
│               │   ├── Short-Term State Card
│               │   ├── Mid-Term State Card
│               │   └── Long-Term State Card
│               │
│               ├── EMA Chart
│               │   ├── LineChart (recharts)
│               │   └── 3 Lines (Short/Mid/Long term)
│               │
│               └── Input Section
│                   ├── Message Input (Left)
│                   │   ├── Textarea
│                   │   └── Analyze Button
│                   │
│                   └── Significance Score (Right)
│                       ├── Score Display
│                       └── Badge
```

---

## Environment Variables Flow

```
.env (Root)
├── HF_TOKEN → backend/config.py → core/emotional_detector.py
├── BACKEND_PORT → backend/main.py → uvicorn server
├── FLASK_ENV → backend/config.py
└── DATABASE_URL → backend/config.py

frontend/.env
└── VITE_API_URL → api/client.js → axios baseURL
```

---

## State Management Flow

```
Global User State
├── UserProfile (in core/user_profile.py)
│   ├── user_id: string
│   ├── short_term_ema: float (0-10)
│   ├── mid_term_ema: float (0-10)
│   ├── long_term_ema: float (0-10)
│   ├── short_term_state: string
│   ├── mid_term_state: string
│   └── long_term_state: string
│
├── Frontend Component State (React)
│   ├── message: string (input)
│   ├── loading: boolean (analyzing)
│   ├── error: string | null
│   ├── result: AnalyzeResponse
│   └── states: StatesResponse
│
└── Backend Service State
    └── EmotionalStateService.user_profiles
        └── {user_id: UserProfile}
```

---

## Request/Response Examples

### Request: POST /api/analyze
```json
{
  "message": "I just got promoted at work! This is amazing!",
  "user_id": "user123"
}
```

### Response: 200 OK
```json
{
  "message": "I just got promoted at work! This is amazing!",
  "short_term_state": "Positive",
  "mid_term_state": "Elevated",
  "long_term_state": "Positive",
  "significance_score": 8.7,
  "emotions": {
    "joy": 0.92,
    "pride": 0.85,
    "contentment": 0.78,
    "surprise": 0.71
  },
  "timestamp": "2026-06-10T14:30:45.123456"
}
```

---

## Integration Checklist

- [x] Backend FastAPI app created
- [x] Analysis endpoints implemented
- [x] Frontend API client setup
- [x] React hooks for data fetching created
- [x] React Router pages ready
- [x] Environment variables configured
- [x] CORS enabled in backend
- [x] Error handling in place
- [x] Loading states implemented
- [x] Documentation complete
- [ ] Wire DashboardPage to hooks (NEXT)
- [ ] Add Context API for global state (OPTIONAL)
- [ ] Deploy to production (LATER)
