"""
LamiGo API v1 Router
Aggregates all API endpoints under /api/v1
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, drivers, trips, incidents

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    drivers.router,
    prefix="/drivers",
    tags=["drivers"],
)

api_router.include_router(
    trips.router,
    prefix="/trips",
    tags=["trips"],
)

api_router.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["incidents"],
)
