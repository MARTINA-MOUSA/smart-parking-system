"""
Video Processor Module
Handles video processing and real-time parking spot monitoring
"""

import cv2
import numpy as np
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from loguru import logger
from app.core.detector import ParkingSpotDetector
from app.core.predictor import ParkingSpotPredictor


class VideoProcessor:
    """Processes video streams to monitor parking spots"""
    
    def __init__(
        self,
        detector: ParkingSpotDetector,
        predictor: ParkingSpotPredictor,
        processing_step: int = 30,
        diff_threshold: float = 0.4
    ):
        """
        Initialize video processor
        
        Args:
            detector: ParkingSpotDetector instance
            predictor: ParkingSpotPredictor instance
            processing_step: Process every Nth frame
            diff_threshold: Threshold for detecting significant changes
        """
        self.detector = detector
        self.predictor = predictor
        self.processing_step = processing_step
        self.diff_threshold = diff_threshold
        
        self.spots = []
        self.spots_status: List[Optional[bool]] = []
        self.diffs: List[Optional[float]] = []
        self.previous_frame: Optional[np.ndarray] = None
        self.frame_number = 0
        
        # Statistics
        self.total_frames = 0
        self.processed_frames = 0
    
    def _calculate_difference(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate difference between two images
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Mean absolute difference
        """
        if img1.shape != img2.shape:
            return float('inf')
        
        return float(np.abs(np.mean(img1) - np.mean(img2)))
    
    def _update_differences(self, current_frame: np.ndarray) -> None:
        """Update difference values for all spots"""
        if self.previous_frame is None:
            return
        
        for spot_idx, spot in enumerate(self.spots):
            x1, y1, w, h = spot
            
            # Extract ROI from both frames
            current_roi = current_frame[y1:y1 + h, x1:x1 + w, :]
            previous_roi = self.previous_frame[y1:y1 + h, x1:x1 + w, :]
            
            # Calculate difference
            self.diffs[spot_idx] = self._calculate_difference(current_roi, previous_roi)
    
    def _get_spots_to_check(self) -> List[int]:
        """
        Get list of spot indices that need status checking
        Uses difference threshold to prioritize changed spots
        """
        if self.previous_frame is None:
            # First frame: check all spots
            return list(range(len(self.spots)))
        
        # Get spots with significant changes
        if not self.diffs or max(self.diffs) == 0:
            return list(range(len(self.spots)))
        
        max_diff = max(self.diffs)
        threshold = max_diff * self.diff_threshold
        
        spots_to_check = [
            idx for idx, diff in enumerate(self.diffs)
            if diff is not None and diff >= threshold
        ]
        
        # Always check at least some spots
        if not spots_to_check:
            spots_to_check = list(range(len(self.spots)))
        
        return spots_to_check
    
    def _update_spot_statuses(self, frame: np.ndarray) -> None:
        """Update status for spots that need checking"""
        from app.utils.config import settings
        
        spots_to_check = self._get_spots_to_check()
        confidence_threshold = getattr(settings, 'CONFIDENCE_THRESHOLD', 0.5)
        
        for spot_idx in spots_to_check:
            spot = self.spots[spot_idx]
            x1, y1, w, h = spot
            spot_roi = frame[y1:y1 + h, x1:x1 + w, :]
            
            if spot_roi is not None and spot_roi.size > 0:
                status = self.predictor.predict(spot_roi, confidence_threshold=confidence_threshold)
                
                if getattr(settings, 'INVERT_PREDICTION', False):
                    status = not status
                
                self.spots_status[spot_idx] = status
    
    def initialize(self, video_path: Optional[str] = None, cap: Optional[cv2.VideoCapture] = None) -> bool:
        """
        Initialize processor with video source
        
        Args:
            video_path: Path to video file
            cap: VideoCapture object (alternative to video_path)
            
        Returns:
            True if successful
        """
        try:
            if cap is not None:
                self.cap = cap
            elif video_path:
                video_file = Path(video_path)
                if not video_file.exists():
                    abs_path = video_file.resolve()
                    if not abs_path.exists():
                        error_msg = f"Video file not found: {video_path}"
                        logger.error(error_msg)
                        raise FileNotFoundError(error_msg)
                    video_path = str(abs_path)
                
                self.cap = cv2.VideoCapture(video_path)
                if not self.cap.isOpened():
                    error_msg = f"Failed to open video: {video_path}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                
                if fps <= 0 or frame_count <= 0:
                    error_msg = f"Invalid video properties: FPS={fps}, Frames={frame_count}"
                    logger.error(error_msg)
                    self.cap.release()
                    raise ValueError(error_msg)
                
                logger.info(
                    f"Video opened successfully: {video_path}\n"
                    f"  Resolution: {int(width)}x{int(height)}\n"
                    f"  FPS: {fps:.2f}\n"
                    f"  Total frames: {int(frame_count)}"
                )
            else:
                raise ValueError("Either video_path or cap must be provided")
            
            # Detect spots from mask
            self.spots = self.detector.detect_spots()
            self.spots_status = [None] * len(self.spots)
            self.diffs = [None] * len(self.spots)
            
            logger.info(f"Processor initialized with {len(self.spots)} spots")
            return True
        
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Error initializing processor: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error initializing processor: {e}", exc_info=True)
            return False
    
    def process_frame(self, frame: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        Process a single frame
        
        Args:
            frame: Input frame (if None, reads from video)
            
        Returns:
            Annotated frame with spot statuses
        """
        try:
            # Read frame if not provided
            if frame is None:
                ret, frame = self.cap.read()
                if not ret:
                    return None
            else:
                ret = True
            
            self.frame_number += 1
            self.total_frames += 1
            
            if self.frame_number % self.processing_step == 0:
                self.processed_frames += 1
                if self.previous_frame is not None:
                    self._update_differences(frame)
                self._update_spot_statuses(frame)
                self.previous_frame = frame.copy()
            
            annotated_frame = self._annotate_frame(frame.copy())
            
            return annotated_frame
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None
    
    def _annotate_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Annotate frame with spot statuses
        
        Args:
            frame: Input frame
            
        Returns:
            Annotated frame
        """
        available_count = sum(1 for s in self.spots_status if s is True)
        total_count = len(self.spots_status)
        
        for spot_idx, spot in enumerate(self.spots):
            x1, y1, w, h = spot
            status = self.spots_status[spot_idx]
            color = (0, 255, 0) if status else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 2)
        
        cv2.rectangle(frame, (80, 20), (550, 100), (0, 0, 0), -1)
        text = f'Available spots: {available_count} / {total_count}'
        cv2.putText(frame, text, (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return frame
    
    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        available = sum(1 for s in self.spots_status if s is True)
        occupied = sum(1 for s in self.spots_status if s is False)
        unknown = sum(1 for s in self.spots_status if s is None)
        
        return {
            'total_spots': len(self.spots),
            'available_spots': available,
            'occupied_spots': occupied,
            'unknown_spots': unknown,
            'availability_rate': available / len(self.spots) if self.spots else 0,
            'total_frames': self.total_frames,
            'processed_frames': self.processed_frames,
            'current_frame': self.frame_number
        }
    
    def release(self) -> None:
        """Release video capture resources"""
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
            logger.info("Video capture released")
