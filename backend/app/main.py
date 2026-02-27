"""
LamiGo Backend - Main Entry Point
Last-Mile Delivery Optimization Platform for Sri Lanka
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api_v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Last-Mile Delivery Optimization Platform for Sri Lanka",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint for the LamiGo backend."""
    return {
        "status": "healthy",
        "message": "LamiGo Backend is Running",
        "version": settings.APP_VERSION,
    }


@app.get("/api/health", tags=["health"])
def api_health():
    """API health check endpoint."""
    return {"status": "ok", "api_version": "v1"}
