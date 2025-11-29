"""
Tests for ParkingSpotDetector
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from app.core.detector import ParkingSpotDetector


@pytest.fixture
def sample_mask(tmp_path):
    """Create a sample mask image for testing"""
    mask_path = tmp_path / "test_mask.png"
    # Create a simple mask with a few rectangles
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(mask, (10, 10), (30, 30), 255, -1)
    cv2.rectangle(mask, (50, 50), (70, 70), 255, -1)
    cv2.imwrite(str(mask_path), mask)
    return str(mask_path)


def test_detector_initialization(sample_mask):
    """Test detector initialization"""
    detector = ParkingSpotDetector(sample_mask)
    assert detector.mask is not None
    assert detector.mask.shape == (100, 100)


def test_detect_spots(sample_mask):
    """Test spot detection"""
    detector = ParkingSpotDetector(sample_mask)
    spots = detector.detect_spots()
    assert len(spots) == 2
    assert all(len(spot) == 4 for spot in spots)


def test_get_spot_roi(sample_mask):
    """Test ROI extraction"""
    detector = ParkingSpotDetector(sample_mask)
    spots = detector.detect_spots()
    
    # Create a test frame
    frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    roi = detector.get_spot_roi(frame, spots[0])
    assert roi is not None
    assert len(roi.shape) == 3

