import os
import boto3
from uuid import UUID
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.sql_models import Driver, User, DriverFinancialProfile, DriverSettlement, Trip, DeliveryTask
from app.models.enums import TaskStatus
from app.schemas.driver_ops_schemas import DriverStatusUpdate, DriverLocationPing

# Initialize DynamoDB Client (Assumes AWS credentials are in environment variables)
dynamodb = boto3.resource(
    'dynamodb', 
    region_name=os.getenv("AWS_REGION", "ap-south-1") # Common for Sri Lanka
)
LOCATION_TABLE = dynamodb.Table("LamiGo_DriverLocations")

async def update_driver_status(db: AsyncSession, driver_id: str, payload: DriverStatusUpdate) -> dict:
    """Updates the driver's operational status in PostgreSQL."""
    result = await db.execute(select(Driver).where(Driver.driver_id == driver_id))
    driver = result.scalars().first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found.")
        
    driver.status = payload.status
    driver.status_updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    return {"status": "success", "new_status": driver.status}

async def log_driver_location(driver_id: str, payload: DriverLocationPing) -> None:
    """
    Writes the 5-second GPS ping directly to DynamoDB.
    No PostgreSQL interactions happen here to guarantee high throughput.
    """
    # Calculate TTL (e.g., expire records after 30 days to save storage costs)
    ttl_timestamp = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())
    
    try:
        # We use boto3 synchronous call here. In a strictly async FastAPI app, 
        # you might use `aioboto3`, but standard boto3 is often sufficient for simple puts.
        LOCATION_TABLE.put_item(
            Item={
                'driver_id': driver_id,                             # PK
                'timestamp': payload.timestamp.isoformat(),         # SK
                'lat': str(payload.lat),                            # DynamoDB prefers stringified floats
                'lon': str(payload.lon),                            
                'trip_id': str(payload.trip_id) if payload.trip_id else None, # GSI-PK
                'task_id': str(payload.task_id) if payload.task_id else None, # GSI-PK
                'status': payload.status.value,
                'ttl': ttl_timestamp
            }
        )
    except Exception as e:
        print(f"DynamoDB Write Failed for Driver {driver_id}: {str(e)}")
        # We do NOT raise an HTTP exception here. If a single 5-second ping fails, 
        # we don't want to crash the mobile app. We just silently drop it and log it.

async def get_driver_dashboard(db: AsyncSession, driver_id: str) -> dict:
    """
    Aggregates data from Users, Drivers, Financial Profiles, and active Trips
    to construct the exact dictionary required by Page 6 & 8 of the Flutter app.
    Enforces the Dictionary Rule.
    """
    # 1. Fetch Core Identity & Driver Data
    user_query = await db.execute(select(User).where(User.user_id == driver_id))
    user = user_query.scalars().first()
    
    driver_query = await db.execute(select(Driver).where(Driver.driver_id == driver_id))
    driver = driver_query.scalars().first()
    
    if not user or not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # 2. Fetch Financials
    fin_query = await db.execute(select(DriverFinancialProfile).where(DriverFinancialProfile.driver_id == driver_id))
    financials = fin_query.scalars().first()
    
    # Fetch recent settlements for the history array
    settlements_query = await db.execute(
        select(DriverSettlement)
        .where(DriverSettlement.driver_id == driver_id)
        .order_by(DriverSettlement.created_at.desc())
        .limit(3)
    )
    settlements = settlements_query.scalars().all()
    
    earnings_history = [
        {"date": s.created_at.strftime("%d-%m-%Y"), "amount": s.amount_paid} 
        for s in settlements
    ]

    # 3. Fetch Active Trip & Next Stop
    trip_query = await db.execute(
        select(Trip)
        .where((Trip.driver_id == driver_id) & (Trip.status == 'IN_PROGRESS'))
    )
    active_trip = trip_query.scalars().first()
    
    next_stop_dict = None
    if active_trip:
        # Find the very next task that needs to be delivered
        task_query = await db.execute(
            select(DeliveryTask).options(selectinload(DeliveryTask.package))
            .where((DeliveryTask.trip_id == active_trip.trip_id) & (DeliveryTask.status == TaskStatus.ON_TRIP))
            .order_by(DeliveryTask.sequence_number.asc())
        )
        next_task = task_query.scalars().first()
        
        if next_task and next_task.package:
            next_stop_dict = {
                "address": next_task.package.address,
                "eta": "Calculating...", # In reality, you'd calculate this via ML or Google API
                "cod_amount": next_task.package.cod_amount if next_task.package.is_cod else 0.00
            }

    # 4. Construct and return the strict dictionary (Dictionary Rule)
    return {
        "driver_name": user.preferred_name or user.full_name,
        "driver_id": driver.driver_id[-6:].upper(), # Mocking a short visual ID for the UI
        "vehicle_type": driver.vehicle_type,
        "vehicle_number": driver.vehicle_number,
        "completed_tasks_count": active_trip.delivered_count if active_trip else 0,
        "total_tasks_count": active_trip.total_tasks_count if active_trip else 0,
        "current_earnings": financials.current_payable_balance if financials else 0.00,
        "earnings_history": earnings_history,
        "next_stop": next_stop_dict
    }