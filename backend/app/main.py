from fastapi import FastAPI
from app.core.config import settings

# Initialize the FastAPI application with global project metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
)

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to verify the API is running and responding successfully.
    Accessible via standard web browsers.
    """
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}",
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "status": "online"
    }