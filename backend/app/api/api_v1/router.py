from fastapi import APIRouter

# Import ALL feature routers (Added 'commissions')
from app.api.api_v1.endpoints import (
    auth, organizations, branches, users, recipients, 
    packages, preferences, trips, incidents, tasks, instructions, contexts, drivers, commissions, financial_profiles
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
api_router.include_router(drivers.router, prefix="/drivers", tags=["Driver Operations"])
api_router.include_router(contexts.router, prefix="/contexts", tags=["Delivery Context (ML)"])
api_router.include_router(commissions.router, prefix="/commissions", tags=["Financial Commissions"])

# Plug in Driver Financial Profiles
api_router.include_router(financial_profiles.router, prefix="/financial-profiles", tags=["Driver Financials"])