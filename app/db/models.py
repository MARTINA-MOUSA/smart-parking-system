"""
Database models for parking system
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ParkingSpot(Base):
    """Parking spot model"""
    __tablename__ = "parking_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    spot_index = Column(Integer, unique=True, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    zone = Column(String(50), nullable=True)  # Optional zone identifier
    
    # Relationships
    status_history = relationship("SpotStatus", back_populates="spot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ParkingSpot(id={self.id}, index={self.spot_index})>"


class SpotStatus(Base):
    """Historical status records for parking spots"""
    __tablename__ = "spot_status"
    
    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    is_empty = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    confidence = Column(Float, nullable=True)  # Optional confidence score
    
    # Relationships
    spot = relationship("ParkingSpot", back_populates="status_history")
    
    def __repr__(self):
        return f"<SpotStatus(spot_id={self.spot_id}, empty={self.is_empty}, time={self.timestamp})>"


class SystemStatistics(Base):
    """System-wide statistics snapshots"""
    __tablename__ = "system_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_spots = Column(Integer, nullable=False)
    available_spots = Column(Integer, nullable=False)
    occupied_spots = Column(Integer, nullable=False)
    availability_rate = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<SystemStatistics(time={self.timestamp}, available={self.available_spots}/{self.total_spots})>"

