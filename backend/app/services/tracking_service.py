import logging
from datetime import datetime, timezone
from decimal import Decimal
from app.core.dynamodb import dynamodb_resource
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.package import Package
from app.models.delivery_task import DeliveryTask
from app.models.enums import PackageStatus, TaskStatus, FailureType

logger = logging.getLogger(__name__)

# This matches the table name you just created in AWS
TRACKING_TABLE_NAME = "LamiGo_DriverLocations"

def log_driver_location(
    driver_id: str, 
    lat: float, 
    lng: float, 
    status: str, 
    trip_id: str = None, 
    task_id: str = None
):
    """
    Writes a high-velocity GPS ping to DynamoDB.
    This will be called via FastAPI BackgroundTasks to ensure zero latency.
    """
    try:
        table = dynamodb_resource.Table(TRACKING_TABLE_NAME)
        
        # Build the item matching your data architecture
        item = {
            "driver_id": driver_id,                                # Partition Key
            "timestamp": datetime.now(timezone.utc).isoformat(),   # Sort Key
            # Boto3 DynamoDB requires Python floats to be cast to strings or Decimals
            "lat": str(lat),                                       
            "lng": str(lng),
            "status": status
        }
        
        # Add optional GSI (Global Secondary Index) fields if the driver is on an active trip
        if trip_id:
            item["trip_id"] = str(trip_id)
        if task_id:
            item["task_id"] = str(task_id)
            
        # Insert into AWS
        table.put_item(Item=item)
        
        # Note: We do NOT use logger.info() here. If 50 drivers ping every 10 seconds, 
        # it would spam our server logs. We only log errors.
        
    except Exception as e:
        logger.error(f"Failed to write GPS location to DynamoDB for driver {driver_id}: {e}")


def reject_customer_delivery(db: Session, tracking_id: str):
    """
    Handles the logic when a customer clicks 'Reject Date' on the public portal.
    Resets the package to TO_BE_DELIVERED and fails the active DeliveryTask.
    """
    # 1. Find the package
    package = db.query(Package).filter(Package.tracking_id == tracking_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # 2. Revert package status so it goes back to the Station Manager's dashboard
    package.status = PackageStatus.TO_BE_DELIVERED

    # 3. Find the active delivery task
    active_task = db.query(DeliveryTask).filter(
        DeliveryTask.package_id == package.package_id,
        DeliveryTask.status.in_([TaskStatus.SCHEDULED, TaskStatus.ON_TRIP])
    ).first()

    # 4. Mark the task as failed specifically because the customer cancelled
    if active_task:
        active_task.status = TaskStatus.FAILED
        active_task.failure_type = FailureType.CANCELLED_BY_RECIPIENT

    # Save changes to the database
    db.commit()
    
    return {"message": "Delivery successfully rejected and rescheduled."}