from fastapi import APIRouter

# Import the individual feature routers
from app.api.api_v1.endpoints import auth
from app.api.api_v1.endpoints import organization # <-- ADD THIS

# Create the master router
api_router = APIRouter()

# Plug in the features
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Plug in the Organization feature (Outputs to /api/v1/organizations)
api_router.include_router(organization.router, prefix="/organizations", tags=["Organizations"]) # <-- ADD THIS