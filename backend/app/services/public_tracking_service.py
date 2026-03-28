"""
Public (unauthenticated) tracking lookups for the customer portal.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import PackageStatus, TaskStatus
from app.models.sql_models import DeliveryTask, Package, Recipient
from app.schemas.tracking_schemas import (
    PublicCurrentTaskOut,
    PublicRecipientOut,
    PublicTrackingDetailResponse,
)


async def get_public_tracking_by_tracking_id(
    db: AsyncSession,
    tracking_id: str,
) -> Optional[PublicTrackingDetailResponse]:
    """
    Load package by public tracking_id with nested recipient.
    When status is ON_TRIP or DELIVERING_NOW, attach active delivery_task ETA + sequence if present.
    """
    result = await db.execute(
        select(Package)
        .where(Package.tracking_id == tracking_id)
        .options(selectinload(Package.recipient))
    )
    package = result.scalar_one_or_none()
    if not package:
        return None

    recipient_out: Optional[PublicRecipientOut] = None
    if package.recipient is not None:
        r = package.recipient
        recipient_out = PublicRecipientOut(
            recipient_id=r.recipient_id,
            name=r.name,
            phone_number=r.phone_number,
            address=r.address,
            location_type=r.location_type,
            floor_number=r.floor_number,
            is_location_verified=bool(r.is_location_verified),
            gps_lat=r.gps_lat,
            gps_lng=r.gps_lng,
        )

    current_task: Optional[PublicCurrentTaskOut] = None
    if package.status in (PackageStatus.ON_TRIP, PackageStatus.DELIVERING_NOW):
        task_result = await db.execute(
            select(DeliveryTask)
            .where(
                DeliveryTask.package_id == package.package_id,
                DeliveryTask.status.in_(
                    [TaskStatus.ON_TRIP, TaskStatus.DELIVERING_NOW]
                ),
            )
            .order_by(DeliveryTask.sequence_number.asc())
            .limit(1)
        )
        task = task_result.scalar_one_or_none()
        if task is not None:
            current_task = PublicCurrentTaskOut(
                estimated_arrival_time=task.estimated_arrival_time,
                sequence_number=task.sequence_number,
            )

    return PublicTrackingDetailResponse(
        package_id=package.package_id,
        tracking_id=package.tracking_id,
        branch_id=package.branch_id,
        status=package.status,
        weight=package.weight,
        is_cod=bool(package.is_cod),
        cod_amount=package.cod_amount,
        delivery_charge=package.delivery_charge,
        sender_name=package.sender_name,
        sender_phone=package.sender_phone,
        recipient_name=package.recipient_name,
        address=package.address,
        gps_lat=package.gps_lat,
        gps_lng=package.gps_lng,
        num_of_attempts=package.num_of_attempts or 0,
        completed_at=package.completed_at,
        created_at=package.created_at,
        updated_at=package.updated_at,
        recipient=recipient_out,
        current_task=current_task,
    )


async def update_recipient_location_by_tracking_id(
    db: AsyncSession,
    tracking_id: str,
    gps_lat: float,
    gps_lng: float,
) -> tuple[Optional[PublicRecipientOut], str]:
    """
    Resolve package by tracking_id, update linked Recipient GPS and mark verified.

    Returns (recipient_out, error_code):
      - ("", "") on success with recipient_out set
      - (None, "not_found") if no package matches tracking_id
      - (None, "no_recipient") if package has no linked recipient row to update
    """
    result = await db.execute(
        select(Package).where(Package.tracking_id == tracking_id)
    )
    package = result.scalar_one_or_none()
    if not package:
        return None, "not_found"

    if package.recipient_id is None:
        return None, "no_recipient"

    rec_result = await db.execute(
        select(Recipient).where(Recipient.recipient_id == package.recipient_id)
    )
    recipient = rec_result.scalar_one_or_none()
    if not recipient:
        return None, "no_recipient"

    recipient.gps_lat = Decimal(str(gps_lat))
    recipient.gps_lng = Decimal(str(gps_lng))
    recipient.is_location_verified = True

    await db.commit()
    await db.refresh(recipient)

    out = PublicRecipientOut(
        recipient_id=recipient.recipient_id,
        name=recipient.name,
        phone_number=recipient.phone_number,
        address=recipient.address,
        location_type=recipient.location_type,
        floor_number=recipient.floor_number,
        is_location_verified=bool(recipient.is_location_verified),
        gps_lat=recipient.gps_lat,
        gps_lng=recipient.gps_lng,
    )
    return out, ""
