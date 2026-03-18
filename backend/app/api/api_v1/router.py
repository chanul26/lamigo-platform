from fastapi import APIRouter

# Import the individual feature routers
from app.api.api_v1.endpoints import auth, organizations, branches, trips

# Create the master router
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(branches.router, prefix="/branches", tags=["Branches"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips & Tasks"])