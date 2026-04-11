import uuid
from datetime import timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.sql_models import (
    Trip,
    DeliveryTask,
    DeliveryContext,
    Package,
    Branch,
    Driver,
    Recipient,
)
from app.models.enums import TripStatus, TaskStatus, PackageStatus
from app.schemas.trip_schemas_v2 import TripCreateRequest, TripResponse

# Import our custom engines
from app.services.routing_service import optimize_trip_sequence
from app.services.external_apis import build_delivery_timeline, SERVICE_TIME_SECONDS
from app.services.ml_service import predict_trip_etas


async def create_trip(
    session: AsyncSession, request: TripCreateRequest
) -> TripResponse:
    """
    The Master Orchestrator for Trip Generation.
    1. Fetches real DB data (Driver, Branch, Packages).
    2. Runs Haversine/Google Routing Optimization.
    3. Simulates Traffic & Weather Timelines.
    4. Runs DeepFM PyTorch Inference.
    5. Saves the final optimized plan to PostgreSQL.
    """
    print("\n" + "=" * 80)
    print("🚀 INIT: LamiGo AI Trip Orchestrator (V2)")
    print("=" * 80)

    # =========================================================================
    # STEP 1: FETCH CONTEXT FROM POSTGRESQL
    # =========================================================================
    # Fetch Branch
    branch = await session.get(Branch, request.branch_id)
    if not branch:
        raise ValueError("Invalid Branch ID")

    # Fetch Driver to get Vehicle Type (Option A - Single Source of Truth)
    driver = await session.get(Driver, request.driver_id)
    if not driver:
        raise ValueError("Invalid Driver ID")
    vehicle_type = driver.vehicle_type

    # Fetch Packages AND their linked Recipients
    stmt = (
        select(Package)
        .options(selectinload(Package.recipient))
        .where(Package.package_id.in_(request.package_ids))
    )
    result = await session.execute(stmt)
    packages = result.scalars().all()

    if len(packages) != len(request.package_ids):
        raise ValueError("One or more Package IDs are invalid or missing.")

    # =========================================================================
    # STEP 2: FORMAT DATA FOR ENGINES
    # =========================================================================
    start_node = {
        "id": str(branch.branch_id),
        "lat": float(branch.gps_lat),
        "lng": float(branch.gps_lng),
    }

    waypoints = []
    waypoints_data_map = {}
    db_context_map = {}

    total_weight = 0.0
    total_cod = 0.0

    for pkg in packages:
        pkg_id_str = str(pkg.package_id)
        rec = pkg.recipient

        # Core routing data
        waypoints.append(
            {"id": pkg_id_str, "lat": float(pkg.gps_lat), "lng": float(pkg.gps_lng)}
        )
        waypoints_data_map[pkg_id_str] = {
            "lat": float(pkg.gps_lat),
            "lng": float(pkg.gps_lng),
        }

        # ML Context data
        db_context_map[pkg_id_str] = {
            "customer_id": str(rec.recipient_id) if rec else "UNKNOWN",
            "location_type": rec.location_type if rec else "HOME",
            "weight_kg": float(pkg.weight),
            "is_cod": pkg.is_cod,
            "cod_amount": float(pkg.cod_amount),
            "is_pin_verified": rec.is_location_verified if rec else False,
        }

        total_weight += float(pkg.weight)
        total_cod += float(pkg.cod_amount)

    # =========================================================================
    # STEP 3: RUN THE AI ENGINES
    # =========================================================================
    # 3A. Spatial Routing (Simulated Annealing + Google Road Check)
    optimized_sequence = await optimize_trip_sequence(
        start_node=start_node,
        end_node=start_node,  # Return to Hub
        waypoints=waypoints,
        vehicle_type=vehicle_type.value,
    )

    # 3B. Temporal Simulation (Google Future Traffic + Weather Injection)
    timeline_payload = await build_delivery_timeline(
        route_sequence=optimized_sequence,
        scheduled_start_time=request.scheduled_start_time,
        waypoints_data=waypoints_data_map,
        start_node=start_node,
        vehicle_type=vehicle_type.value,
    )

    # 3C. Deep Learning Friction Inference (PyTorch DeepFM)
    final_ml_payload = await predict_trip_etas(
        enriched_timeline=timeline_payload,
        db_context_map=db_context_map,
        vehicle_type=vehicle_type.value,
        driver_id=driver.driver_id,
    )

    # =========================================================================
    # STEP 4: RECALCULATE ABSOLUTE CLOCK WITH AI TIMES
    # =========================================================================
    # Google gave us an ETA, but the AI changed it. We must roll the clock forward
    # using the AI's predictions to get the true, physically-accurate Arrival Times.
    current_ai_clock = request.scheduled_start_time

    for step in final_ml_payload:
        if step["sequence_number"] > 1:
            current_ai_clock += timedelta(
                seconds=SERVICE_TIME_SECONDS
            )  # 10 mins at previous stop

        current_ai_clock += timedelta(
            seconds=step["deepfm_eta_seconds"]
        )  # Add AI driving time
        step["ai_absolute_arrival_time"] = current_ai_clock

    # =========================================================================
    # STEP 5: SAVE TO POSTGRESQL DATABASE
    # =========================================================================
    print("💾 Saving Optimized Trip to Database...")

    # 1. Create Trip Record
    new_trip = Trip(
        trip_id=uuid.uuid4(),
        branch_id=request.branch_id,
        driver_id=request.driver_id,
        status=TripStatus.SCHEDULED,
        total_tasks_count=len(packages),
        total_weight=total_weight,
        total_cod_to_collect=total_cod,
        scheduled_start_time=request.scheduled_start_time,
        # The last step in the payload is the Return-to-Hub leg
        estimated_return_time_scheduled=final_ml_payload[-1][
            "ai_absolute_arrival_time"
        ],
    )
    session.add(new_trip)

    task_responses = []  # For Pydantic UI response

    # 2. Create Tasks and Contexts
    for step in final_ml_payload:
        if step.get("is_return_leg", False):
            continue  # We don't create a DeliveryTask for returning to the Hub

        pkg_uuid = uuid.UUID(step["id"])
        new_task_id = uuid.uuid4()

        # Create Task
        new_task = DeliveryTask(
            task_id=new_task_id,
            trip_id=new_trip.trip_id,
            package_id=pkg_uuid,
            sequence_number=step["sequence_number"],
            status=TaskStatus.SCHEDULED,
            estimated_arrival_time=step["ai_absolute_arrival_time"],
        )
        session.add(new_task)

        # Create ML Context
        new_context = DeliveryContext(
            task_id=new_task_id,
            google_eta_seconds=step["google_eta_seconds"],
            google_dist_meters=step["google_dist_meters"],
            rain_volume_1h=step["rain_volume_1h"],
            weather_code=step["weather_code"],
        )
        session.add(new_context)

        # Update Package Status
        for pkg in packages:
            if pkg.package_id == pkg_uuid:
                pkg.status = PackageStatus.SCHEDULED

        # Build Response Dictionary for Pydantic
        task_responses.append(
            {
                "task_id": new_task_id,
                "package_id": pkg_uuid,
                "sequence_number": step["sequence_number"],
                "status": TaskStatus.SCHEDULED,
                "estimated_arrival_time": step["ai_absolute_arrival_time"],
                "context": {
                    "google_dist_meters": step["google_dist_meters"],
                    "google_eta_seconds": step["google_eta_seconds"],
                    "deepfm_eta_seconds": step["deepfm_eta_seconds"],
                    "friction_factor": step["friction_factor"],
                    "weather_code": step["weather_code"],
                    "rain_volume_1h": step["rain_volume_1h"],
                },
            }
        )

    # Commit Transaction
    await session.commit()
    print(f"✅ Trip {new_trip.trip_id} committed successfully!")

    # =========================================================================
    # STEP 6: RETURN RESPONSE
    # =========================================================================
    return TripResponse(
        trip_id=new_trip.trip_id,
        branch_id=new_trip.branch_id,
        driver_id=new_trip.driver_id,
        status=new_trip.status,
        total_tasks_count=new_trip.total_tasks_count,
        total_weight=new_trip.total_weight,
        total_cod_to_collect=new_trip.total_cod_to_collect,
        scheduled_start_time=new_trip.scheduled_start_time,
        estimated_return_time_scheduled=new_trip.estimated_return_time_scheduled,
        tasks=task_responses,
    )
