"""
LamiGo Backend - Main Entry Point
Last-Mile Delivery Optimization Platform for Sri Lanka
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router

# Initialize FastAPI application
app = FastAPI(
    title="LamiGo API",
    description="Last-Mile Delivery Optimization Platform for Sri Lanka",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration - Allow Station Manager and Customer Portal
origins = [
    "http://localhost:3000",  # Station Manager Web Portal
    "http://localhost:3001",  # Customer Portal
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint for the LamiGo backend."""
    return {
        "status": "healthy",
        "message": "LamiGo Backend is Running",
        "version": "1.0.0",
    }


@app.get("/api/health", tags=["health"])
def api_health():
    """API health check endpoint."""
    return {"status": "ok", "api_version": "v1"}
