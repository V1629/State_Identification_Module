"""
Main FastAPI Application
Integrates state_management_module with HTTP API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .routes import analysis, health
from .config import settings

# Initialize FastAPI app
app = FastAPI(
    title="State Identification Module API",
    description="Emotional state analysis and tracking API",
    version="1.0.0",
    debug = True
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://state-identification-frontend.onrender.com"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(analysis.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
