"""
Main FastAPI Application
Integrates state_management_module with HTTP API
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from dotenv import load_dotenv

# Add project root to path so we can import from backend.*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

from backend.routes import analysis, health
from backend.routes import auth
from backend.config import settings
from backend.database import MongoDB


# ==================== Lifespan (Startup/Shutdown) ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle — connect/disconnect MongoDB"""
    # Startup
    if settings.MONGODB_URI:
        try:
            await MongoDB.connect(settings.MONGODB_URI)
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("⚠️  Server starting WITHOUT database — auth/state persistence disabled")
    else:
        print("⚠️  MONGODB_URI not set — database features disabled")
    yield
    # Shutdown
    await MongoDB.disconnect()


# ==================== App Initialization ====================

app = FastAPI(
    title="State Identification Module API",
    description="Emotional state analysis and tracking API",
    version="1.0.0",
    debug=True,
    lifespan=lifespan,
)

# Load dynamic frontend URL from environment if it exists
frontend_url = os.getenv("FRONTEND_URL", "https://state-identification-frontend.onrender.com")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:5174", 
        "http://127.0.0.1:5174", 
        "http://localhost:3000", 
        frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
