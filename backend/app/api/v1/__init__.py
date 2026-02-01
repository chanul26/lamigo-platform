from fastapi import APIRouter
from .endpoints import packages, drivers

api_router = APIRouter()

api_router.include_router(packages.router, prefix="/packages", tags=["packages"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
