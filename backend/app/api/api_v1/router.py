from fastapi import APIRouter

# Import the individual feature routers
from app.api.api_v1.endpoints import auth, organizations, recipients # <-- Added recipients here

# Create the master router
api_router = APIRouter()

# Plug in the Auth feature
# Notice we put the specific "/auth" prefix and tags here!
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

# Plug in the Recipient feature
api_router.include_router(recipients.router, prefix="/recipients", tags=["Recipients"]) # <-- Added this line

# Later, when you build other features, you'll just add them like this:
# from app.api.endpoints import trips, packages, drivers
# api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
# api_router.include_router(packages.router, prefix="/packages", tags=["Packages"])