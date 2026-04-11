from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# Import enums directly from your models
from app.models.enums import TripStatus, TaskStatus

# ==============================================================================
# 1. CREATE REQUEST (What the Manager sends to build a new Trip)
# ==============================================================================


class TripCreateRequest(BaseModel):
    """
    Payload sent from the frontend to create a new Trip.
    The backend will take these packages, fetch the driver's vehicle type,
    run the AI Routing Engine, and generate the finalized sequence automatically.
    """

    branch_id: UUID = Field(
        ..., description="The ID of the hub/branch starting the trip"
    )
    driver_id: str = Field(..., description="The Firebase UID of the assigned driver")
    scheduled_start_time: datetime = Field(
        ..., description="When the driver is expected to leave the hub (UTC)"
    )
    package_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=60,
        description="List of package UUIDs to be delivered",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "branch_id": "123e4567-e89b-12d3-a456-426614174000",
                "driver_id": "Kacju0gUqTN2ceNjZuaeM93HMXn2",
                "scheduled_start_time": "2026-03-30T14:00:00Z",
                "package_ids": [
                    "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                ],
            }
        }


# ==============================================================================
# 2. NESTED ML CONTEXT SCHEMA (For the UI)
# ==============================================================================


class DeliveryContextResponse(BaseModel):
    """
    Maps to the `DeliveryContext` DB table + AI predictions.
    Sent to the frontend so the UI can display friction warnings and weather icons.
    """

    google_dist_meters: int
    google_eta_seconds: int
    deepfm_eta_seconds: int  # The AI's predicted real-world time
    friction_factor: float  # e.g., 1.5x (Used for UI coloring: Red if > 1.2)
    weather_code: int  # For UI weather icons
    rain_volume_1h: float

    class Config:
        from_attributes = True


# ==============================================================================
# 3. INDIVIDUAL TASK SCHEMA
# ==============================================================================


class DeliveryTaskResponse(BaseModel):
    """
    Represents a single row in the `delivery_tasks` table,
    enriched with its ML Context.
    """

    task_id: UUID
    package_id: UUID
    sequence_number: int
    status: TaskStatus

    # Timeline
    estimated_arrival_time: datetime  # The AI-predicted arrival time

    # ML/Routing Context
    context: Optional[DeliveryContextResponse] = None

    class Config:
        from_attributes = True


# ==============================================================================
# 4. FULL TRIP RESPONSE SCHEMA
# ==============================================================================


class TripResponse(BaseModel):
    """
    The fully constructed, ML-optimized route returned to the Manager's dashboard.
    Maps exactly to the `Trip` DB table and includes all nested tasks.
    """

    trip_id: UUID
    branch_id: UUID
    driver_id: str
    status: TripStatus

    # Aggregated Trip Logistics
    total_tasks_count: int
    total_weight: float
    total_cod_to_collect: float

    # Core Timeline
    scheduled_start_time: datetime
    estimated_return_time_scheduled: (
        datetime  # The arrival time of the final "Return-to-Hub" leg
    )

    # The Ordered AI Sequence
    tasks: List[DeliveryTaskResponse]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "trip_id": "123e4567-e89b-12d3-a456-426614174000",
                "branch_id": "123e4567-e89b-12d3-a456-426614174000",
                "driver_id": "Kacju0gUqTN2ceNjZuaeM93HMXn2",
                "status": "SCHEDULED",
                "total_tasks_count": 2,
                "total_weight": 5.5,
                "total_cod_to_collect": 4500.00,
                "scheduled_start_time": "2026-03-30T14:00:00Z",
                "estimated_return_time_scheduled": "2026-03-30T16:30:00Z",
                "tasks": [
                    {
                        "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "package_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "sequence_number": 1,
                        "status": "SCHEDULED",
                        "estimated_arrival_time": "2026-03-30T14:15:00Z",
                        "context": {
                            "google_dist_meters": 4500,
                            "google_eta_seconds": 600,
                            "deepfm_eta_seconds": 900,
                            "friction_factor": 1.5,
                            "weather_code": 501,
                            "rain_volume_1h": 12.5,
                        },
                    }
                ],
            }
        }
