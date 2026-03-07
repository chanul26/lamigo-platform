from fastapi import APIRouter
from app.api.api_v1.endpoints.auth import router as auth_router

# Main v1 router that groups all endpoints
api_router = APIRouter()

# Register the auth endpoints under /auth prefix
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])