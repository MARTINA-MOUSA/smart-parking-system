"""
API routes for parking system
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
from app.api.schemas import (
    SpotResponse,
    StatisticsResponse,
    SystemStatusResponse,
    ProcessVideoRequest
)
from app.db.database import get_db_session
from app.services.parking_service import ParkingService
from app.utils.config import settings
from datetime import datetime

router = APIRouter()


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(db: Session = Depends(get_db_session)):
    """Get system status"""
    try:
        spots = ParkingService.get_all_spots(db)
        available = sum(1 for _ in spots)  # Placeholder
        
        return SystemStatusResponse(
            status="operational",
            version=settings.APP_VERSION,
            total_spots=len(spots),
            available_spots=available,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spots", response_model=List[SpotResponse])
async def get_all_spots(db: Session = Depends(get_db_session)):
    """Get all parking spots"""
    try:
        spots = ParkingService.get_all_spots(db)
        return spots
    except Exception as e:
        logger.error(f"Error getting spots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spots/{spot_index}", response_model=SpotResponse)
async def get_spot(spot_index: int, db: Session = Depends(get_db_session)):
    """Get specific parking spot"""
    try:
        spot = ParkingService.get_spot_by_index(db, spot_index)
        if not spot:
            raise HTTPException(status_code=404, detail="Spot not found")
        return spot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting spot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get current statistics"""
    # This would be connected to the active video processor
    # For now, return placeholder data
    return StatisticsResponse(
        total_spots=0,
        available_spots=0,
        occupied_spots=0,
        unknown_spots=0,
        availability_rate=0.0,
        total_frames=0,
        processed_frames=0,
        current_frame=0
    )


@router.post("/process")
async def process_video(
    request: ProcessVideoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Start video processing"""
    try:
        # This would start the video processing in background
        # For now, return success
        return {
            "message": "Video processing started",
            "video_path": request.video_path
        }
    except Exception as e:
        logger.error(f"Error starting video processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

