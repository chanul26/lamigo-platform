from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, organizations, delivery_preferences

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(delivery_preferences.router, prefix="/delivery-preferences", tags=["Delivery Preferences"])