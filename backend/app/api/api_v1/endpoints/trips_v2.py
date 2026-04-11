from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Adjust these imports based on your exact project structure
from app.core.database import get_db
from app.schemas.trip_schemas_v2 import TripCreateRequest, TripResponse
from app.services.trips_service_v2 import create_trip

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/", 
    response_model=TripResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create an AI-Optimized Trip",
    description="""
    Creates a new delivery manifest. 
    This endpoint automatically fetches the driver's vehicle type, calculates the optimal physical route using simulated annealing, 
    injects live weather and traffic data, and uses a PyTorch DeepFM model to predict real-world friction.
    """
)
async def create_new_trip(
    request: TripCreateRequest, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # Pass the validated Pydantic payload directly to our Master Orchestrator
        trip_response = await create_trip(session=db, request=request)
        return trip_response
        
    except ValueError as ve:
        # Catch our custom validation errors (e.g., "Invalid Driver ID")
        logger.warning(f"Validation Error during V2 Trip Creation: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
        
    except Exception as e:
        # Catch unexpected mathematical or database crashes
        logger.error(f"Fatal Error during V2 Trip Creation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An internal error occurred while generating the optimized route."
        )