from fastapi import APIRouter

# Import ONLY the features that currently exist on the dev branch + your new incidents
from app.api.api_v1.endpoints import auth, organizations, branches, recipients, incidents 

# Create the master router
api_router = APIRouter()

# Plug in the features
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(branches.router, prefix="/branches", tags=["Branches"])
api_router.include_router(recipients.router, prefix="/recipients", tags=["Recipients"])

# Plug in the new Incidents route
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])