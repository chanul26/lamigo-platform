from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.sql_models import Trip, DeliveryTask, Branch, Package
from app.schemas.trip_schemas import TripCreate, TripUpdate, DeliveryTaskCreate

async def create_trip(db: AsyncSession, trip_in: TripCreate) -> Trip:
    """Creates a new route manifest."""
    # 1. Verify the branch exists
    branch_result = await db.execute(select(Branch).where(Branch.branch_id == trip_in.branch_id))
    if not branch_result.scalars().first():
        raise HTTPException(status_code=404, detail=f"Branch {trip_in.branch_id} not found.")

    # 2. Create the empty trip (Aggregates like weight/cod start at 0.00 by default)
    new_trip = Trip(**trip_in.model_dump())
    db.add(new_trip)
    await db.commit()
    await db.refresh(new_trip)
    
    return new_trip

async def get_trip(db: AsyncSession, trip_id: UUID) -> Trip:
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")
    return trip

async def add_task_to_trip(db: AsyncSession, trip_id: UUID, task_in: DeliveryTaskCreate) -> DeliveryTask:
    """Adds a package to a route and updates the route's total aggregates."""
    # 1. Fetch the parent Trip
    trip = await get_trip(db, trip_id)

    # 2. Verify the Package exists and fetch its data
    pkg_result = await db.execute(select(Package).where(Package.package_id == task_in.package_id))
    pkg = pkg_result.scalars().first()
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package {task_in.package_id} not found.")

    # 3. Create the new Delivery Task
    new_task = DeliveryTask(**task_in.model_dump(), trip_id=trip_id)
    db.add(new_task)

    # 4. Automatically update the Trip's aggregate data
    trip.total_tasks_count += 1
    trip.total_weight += pkg.weight
    if pkg.is_cod:
        trip.total_cod_to_collect += pkg.cod_amount

    # Commit both the new task AND the updated trip record together
    await db.commit()
    await db.refresh(new_task)
    
    return new_task

async def get_trip_tasks(db: AsyncSession, trip_id: UUID) -> list[DeliveryTask]:
    """Returns all stops on a route, ordered by their sequence number."""
    result = await db.execute(
        select(DeliveryTask)
        .where(DeliveryTask.trip_id == trip_id)
        .order_by(DeliveryTask.sequence_number)
    )
    return list(result.scalars().all())
