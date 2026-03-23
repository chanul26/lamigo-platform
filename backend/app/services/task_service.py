from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import DeliveryTask, Trip, Package
from app.models.enums import TaskStatus, PackageStatus
from app.schemas.task_schemas import TaskCreate, TaskUpdate

def _task_to_dict(task: DeliveryTask) -> dict:
    """Safely converts a DeliveryTask model to a dict to prevent MissingGreenlet errors."""
    task_dict = task.__dict__.copy()
    task_dict.pop("_sa_instance_state", None)
    return task_dict


async def create_task(db: AsyncSession, task_in: TaskCreate) -> dict:
    # 1. Verify Trip exists
    trip = await db.scalar(select(Trip).where(Trip.trip_id == task_in.trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # 2. Verify Package exists
    package = await db.scalar(select(Package).where(Package.package_id == task_in.package_id))
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # 3. Prevent assigning a package that is already delivered
    if package.status in [PackageStatus.COMPLETED, PackageStatus.FAILED]:
        raise HTTPException(status_code=400, detail="Cannot assign a completed or failed package to a new trip.")

    # 4. Create the Task
    new_task = DeliveryTask(
        **task_in.model_dump(),
        status=TaskStatus.SCHEDULED
    )
    db.add(new_task)

    # 5. ATOMIC UPDATE: Sync Package and Trip states
    package.status = PackageStatus.SCHEDULED
    trip.total_tasks_count += 1
    trip.total_weight += package.weight
    if package.is_cod:
        trip.total_cod_to_collect += package.cod_amount

    await db.commit()
    await db.refresh(new_task)
    return _task_to_dict(new_task)


async def get_all_tasks(db: AsyncSession, trip_id: Optional[UUID] = None) -> List[dict]:
    query = select(DeliveryTask)
    
    if trip_id:
        query = query.where(DeliveryTask.trip_id == trip_id)
        
    query = query.order_by(DeliveryTask.sequence_number.asc())
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [_task_to_dict(task) for task in tasks]


async def get_task(db: AsyncSession, task_id: UUID) -> dict:
    result = await db.execute(select(DeliveryTask).where(DeliveryTask.task_id == task_id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery Task not found")
    return _task_to_dict(task)


async def update_task(db: AsyncSession, task_id: UUID, task_in: TaskUpdate) -> dict:
    result = await db.execute(select(DeliveryTask).where(DeliveryTask.task_id == task_id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery Task not found")
        
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    # ATOMIC UPDATE: If task is completed/failed, sync the Package table
    if task_in.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        package = await db.scalar(select(Package).where(Package.package_id == task.package_id))
        if package:
            package.status = PackageStatus.COMPLETED if task_in.status == TaskStatus.COMPLETED else PackageStatus.FAILED
            
            # Update trip delivered counters
            if task_in.status == TaskStatus.COMPLETED:
                trip = await db.scalar(select(Trip).where(Trip.trip_id == task.trip_id))
                if trip:
                    trip.delivered_count += 1
        
    await db.commit()
    await db.refresh(task)
    return _task_to_dict(task)