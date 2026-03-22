from fastapi import APIRouter

# Import ALL feature routers for the platform
from app.api.api_v1.endpoints import (
    auth, organizations, branches, users, recipients, 
    packages, preferences, trips, incidents
)


api_router = APIRouter()

# Core features
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(branches.router, prefix="/branches", tags=["Branches"])
api_router.include_router(recipients.router, prefix="/recipients", tags=["Recipients"])



# Chanul's new feature
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])