"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SpotBase(BaseModel):
    """Base spot schema"""
    spot_index: int
    x: int
    y: int
    width: int
    height: int
    zone: Optional[str] = None


class SpotResponse(SpotBase):
    """Spot response schema"""
    id: int
    current_status: Optional[bool] = None
    
    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    """Status response schema"""
    spot_id: int
    is_empty: bool
    timestamp: datetime
    confidence: Optional[float] = None
    
    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    """Statistics response schema"""
    total_spots: int
    available_spots: int
    occupied_spots: int
    unknown_spots: int
    availability_rate: float
    total_frames: int
    processed_frames: int
    current_frame: int


class SystemStatusResponse(BaseModel):
    """System status response"""
    status: str
    version: str
    total_spots: int
    available_spots: int
    timestamp: datetime


class ProcessVideoRequest(BaseModel):
    """Video processing request"""
    video_path: str
    save_to_db: bool = True

