"""
Parking Spot Detector Module
Handles detection and extraction of parking spots from mask images
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from loguru import logger


class ParkingSpotDetector:
    """Detects parking spots from mask images using connected components"""
    
    def __init__(self, mask_path: str, scale_coef: float = 1.0):
        """
        Initialize the detector
        
        Args:
            mask_path: Path to the mask image file
            scale_coef: Scaling coefficient for coordinates
        """
        self.mask_path = mask_path
        self.scale_coef = scale_coef
        self.mask = None
        self.spots = []
        self._load_mask()
    
    def _load_mask(self) -> None:
        """Load and validate mask image"""
        try:
            self.mask = cv2.imread(self.mask_path, cv2.IMREAD_GRAYSCALE)
            if self.mask is None:
                raise ValueError(f"Failed to load mask from {self.mask_path}")
            logger.info(f"Mask loaded successfully: {self.mask.shape}")
        except Exception as e:
            logger.error(f"Error loading mask: {e}")
            raise
    
    def detect_spots(self) -> List[Tuple[int, int, int, int]]:
        """
        Detect parking spots from the mask using connected components
        
        Returns:
            List of tuples (x, y, width, height) for each parking spot
        """
        if self.mask is None:
            raise ValueError("Mask not loaded. Call _load_mask() first.")
        
        try:
            # Apply connected components analysis
            connected_components = cv2.connectedComponentsWithStats(
                self.mask, 4, cv2.CV_32S
            )
            
            (total_labels, label_ids, values, centroids) = connected_components
            
            spots = []
            for i in range(1, total_labels):  # Skip background (label 0)
                x1 = int(values[i, cv2.CC_STAT_LEFT] * self.scale_coef)
                y1 = int(values[i, cv2.CC_STAT_TOP] * self.scale_coef)
                w = int(values[i, cv2.CC_STAT_WIDTH] * self.scale_coef)
                h = int(values[i, cv2.CC_STAT_HEIGHT] * self.scale_coef)
                
                # Filter out very small regions (noise)
                if w > 10 and h > 10:
                    spots.append((x1, y1, w, h))
            
            self.spots = spots
            logger.info(f"Detected {len(spots)} parking spots")
            return spots
        
        except Exception as e:
            logger.error(f"Error detecting spots: {e}")
            raise
    
    def get_spot_roi(self, frame: np.ndarray, spot: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extract Region of Interest (ROI) for a specific spot from frame
        
        Args:
            frame: Input video frame
            spot: Tuple (x, y, width, height)
            
        Returns:
            Cropped image of the spot or None if invalid
        """
        try:
            x1, y1, w, h = spot
            
            # Validate coordinates
            if (x1 < 0 or y1 < 0 or 
                x1 + w > frame.shape[1] or 
                y1 + h > frame.shape[0]):
                logger.warning(f"Invalid spot coordinates: {spot}")
                return None
            
            return frame[y1:y1 + h, x1:x1 + w, :]
        
        except Exception as e:
            logger.error(f"Error extracting ROI: {e}")
            return None
    
    def get_all_spots_roi(self, frame: np.ndarray) -> List[Optional[np.ndarray]]:
        """
        Extract ROI for all spots from frame
        
        Args:
            frame: Input video frame
            
        Returns:
            List of cropped images for each spot
        """
        rois = []
        for spot in self.spots:
            roi = self.get_spot_roi(frame, spot)
            rois.append(roi)
        return rois

