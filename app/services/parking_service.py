"""
Parking service - Business logic for parking spot management
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
from app.db.models import ParkingSpot, SpotStatus, SystemStatistics
from app.db.database import get_db


class ParkingService:
    """Service for managing parking spots and statistics"""
    
    @staticmethod
    def save_spots(db: Session, spots: List[tuple]) -> List[ParkingSpot]:
        """
        Save parking spots to database
        
        Args:
            db: Database session
            spots: List of (x, y, width, height) tuples
            
        Returns:
            List of created ParkingSpot objects
        """
        try:
            saved_spots = []
            
            for idx, (x, y, w, h) in enumerate(spots):
                # Check if spot already exists
                existing = db.query(ParkingSpot).filter(
                    ParkingSpot.spot_index == idx
                ).first()
                
                if existing:
                    # Update existing
                    existing.x = x
                    existing.y = y
                    existing.width = w
                    existing.height = h
                    saved_spots.append(existing)
                else:
                    # Create new
                    spot = ParkingSpot(
                        spot_index=idx,
                        x=x,
                        y=y,
                        width=w,
                        height=h
                    )
                    db.add(spot)
                    saved_spots.append(spot)
            
            db.commit()
            logger.info(f"Saved {len(saved_spots)} parking spots to database")
            return saved_spots
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving spots: {e}")
            raise
    
    @staticmethod
    def save_status(
        db: Session,
        spot_id: int,
        is_empty: bool,
        confidence: Optional[float] = None
    ) -> SpotStatus:
        """
        Save spot status to database
        
        Args:
            db: Database session
            spot_id: Parking spot ID
            is_empty: True if empty, False if occupied
            confidence: Optional confidence score
            
        Returns:
            Created SpotStatus object
        """
        try:
            status = SpotStatus(
                spot_id=spot_id,
                is_empty=is_empty,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            db.add(status)
            db.commit()
            return status
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving status: {e}")
            raise
    
    @staticmethod
    def save_statistics(
        db: Session,
        total_spots: int,
        available_spots: int,
        occupied_spots: int,
        availability_rate: float
    ) -> SystemStatistics:
        """
        Save system statistics snapshot
        
        Args:
            db: Database session
            total_spots: Total number of spots
            available_spots: Number of available spots
            occupied_spots: Number of occupied spots
            availability_rate: Availability rate (0-1)
            
        Returns:
            Created SystemStatistics object
        """
        try:
            stats = SystemStatistics(
                total_spots=total_spots,
                available_spots=available_spots,
                occupied_spots=occupied_spots,
                availability_rate=availability_rate,
                timestamp=datetime.utcnow()
            )
            db.add(stats)
            db.commit()
            return stats
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving statistics: {e}")
            raise
    
    @staticmethod
    def get_all_spots(db: Session) -> List[ParkingSpot]:
        """Get all parking spots"""
        return db.query(ParkingSpot).all()
    
    @staticmethod
    def get_spot_by_index(db: Session, spot_index: int) -> Optional[ParkingSpot]:
        """Get spot by index"""
        return db.query(ParkingSpot).filter(
            ParkingSpot.spot_index == spot_index
        ).first()
    
    @staticmethod
    def get_latest_statistics(db: Session, limit: int = 100) -> List[SystemStatistics]:
        """Get latest statistics"""
        return db.query(SystemStatistics).order_by(
            SystemStatistics.timestamp.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_spot_history(
        db: Session,
        spot_id: int,
        limit: int = 100
    ) -> List[SpotStatus]:
        """Get status history for a spot"""
        return db.query(SpotStatus).filter(
            SpotStatus.spot_id == spot_id
        ).order_by(
            SpotStatus.timestamp.desc()
        ).limit(limit).all()

