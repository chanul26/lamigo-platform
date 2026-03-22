from fastapi import APIRouter

# Import ALL feature routers (Added 'contexts')
from app.api.api_v1.endpoints import (
    auth, organizations, branches, users, recipients, 
    packages, preferences, trips, incidents, tasks, instructions, contexts
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(branches.router, prefix="/branches", tags=["Branches"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Staff"])
api_router.include_router(recipients.router, prefix="/recipients", tags=["Recipients"])
api_router.include_router(packages.router, prefix="/packages", tags=["Packages"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["Delivery Preferences"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Delivery Tasks"])
api_router.include_router(instructions.router, prefix="/instructions", tags=["Task Instructions"])

# Plug in Delivery Contexts
api_router.include_router(contexts.router, prefix="/contexts", tags=["Delivery Context (ML)"])