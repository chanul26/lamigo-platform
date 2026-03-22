from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, RoleChecker
from app.models.sql_models import Trip
from app.models.enums import UserRole
from app.schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse
from app.services import task_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # IDOR Security: Verify the trip belongs to the Manager's branch
    user_role = current_user.get("role")
    if user_role == UserRole.STATION_MANAGER:
        secure_branch = current_user.get("branch_id")
        trip = await db.scalar(select(Trip).where(Trip.trip_id == task_in.trip_id))
        
        if not trip or trip.branch_id != secure_branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access Denied: You cannot assign tasks to a trip outside your branch."
            )
            
    return await task_service.create_task(db, task_in)


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    trip_id: Optional[UUID] = Query(None, description="Filter tasks by specific trip"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await task_service.get_all_tasks(db, trip_id=trip_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await task_service.get_task(db, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdate,
    # Drivers need to update task status (e.g. COMPLETED) from the mobile app
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await task_service.update_task(db, task_id, task_in)