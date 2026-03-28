"""
Unauthenticated endpoints for the customer tracking portal (SMS deep links).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.tracking_schemas import (
    PublicRecipientLocationResponse,
    PublicRecipientLocationUpdate,
    PublicTrackingDetailResponse,
)
from app.services import public_tracking_service

router = APIRouter()


@router.get(
    "/tracking/{tracking_id}",
    response_model=PublicTrackingDetailResponse,
    summary="Public package tracking (no auth)",
)
async def get_public_tracking(
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Lookup a package by its public tracking_id (e.g. LMG-12345-ABCDE).
    No Firebase / Bearer token required.
    """
    detail = await public_tracking_service.get_public_tracking_by_tracking_id(
        db, tracking_id=tracking_id
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No package found for this tracking number.",
        )
    return detail


@router.patch(
    "/tracking/{tracking_id}/location",
    response_model=PublicRecipientLocationResponse,
    summary="Update recipient GPS from public tracking link (no auth)",
)
async def patch_public_recipient_location(
    tracking_id: str,
    body: PublicRecipientLocationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Updates the linked Recipient's coordinates for this tracking number
    and sets is_location_verified = True. Intended for customer self-service pin drops.
    """
    updated, err = await public_tracking_service.update_recipient_location_by_tracking_id(
        db,
        tracking_id=tracking_id,
        gps_lat=body.gps_lat,
        gps_lng=body.gps_lng,
    )
    if err == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No package found for this tracking number.",
        )
    if err == "no_recipient":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This package has no linked recipient to update.",
        )

    return PublicRecipientLocationResponse(
        message="Delivery location updated successfully.",
        recipient=updated,
    )
