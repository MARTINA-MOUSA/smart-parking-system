"""
Model Diagnostics Tool
Helps diagnose model prediction issues
"""

import cv2
import numpy as np
from pathlib import Path
from loguru import logger
from app.core.predictor import ParkingSpotPredictor
from app.core.detector import ParkingSpotDetector
from app.utils.config import settings


def diagnose_model(video_path: str, num_samples: int = 10):
    """
    Diagnose model predictions on sample spots
    
    Args:
        video_path: Path to video file
        num_samples: Number of spots to sample for diagnosis
    """
    logger.info("Starting model diagnostics...")
    
    # Initialize components
    detector = ParkingSpotDetector(str(settings.get_mask_path()))
    predictor = ParkingSpotPredictor(
        str(settings.get_model_path()),
        resize_size=(settings.RESIZE_WIDTH, settings.RESIZE_HEIGHT)
    )
    
    # Detect spots
    spots = detector.detect_spots()
    logger.info(f"Detected {len(spots)} spots")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return
    
    # Read a frame
    ret, frame = cap.read()
    if not ret:
        logger.error("Failed to read frame from video")
        cap.release()
        return
    
    # Sample spots
    sample_indices = np.linspace(0, len(spots) - 1, min(num_samples, len(spots)), dtype=int)
    
    logger.info("\n" + "=" * 60)
    logger.info("MODEL DIAGNOSTICS REPORT")
    logger.info("=" * 60)
    
    predictions_summary = {"empty": 0, "occupied": 0}
    
    for idx in sample_indices:
        spot = spots[idx]
        x1, y1, w, h = spot
        
        # Extract ROI
        roi = frame[y1:y1 + h, x1:x1 + w, :]
        
        if roi is None or roi.size == 0:
            logger.warning(f"Spot {idx}: Invalid ROI")
            continue
        
        # Get prediction with probabilities if available
        try:
            if hasattr(predictor.model, 'predict_proba'):
                from skimage.transform import resize
                img_resized = resize(roi, (*predictor.resize_size, 3))
                if img_resized.max() > 1.0:
                    img_resized = img_resized / 255.0
                flat_data = img_resized.flatten().reshape(1, -1)
                probabilities = predictor.model.predict_proba(flat_data)[0]
                prediction = predictor.model.predict(flat_data)[0]
                
                empty_prob = probabilities[0]
                occupied_prob = probabilities[1]
                
                status = "EMPTY" if prediction == 0 else "OCCUPIED"
                predictions_summary[status.lower()] += 1
                
                logger.info(f"\nSpot {idx} (x={x1}, y={y1}, w={w}, h={h}):")
                logger.info(f"  Prediction: {status} (class {prediction})")
                logger.info(f"  Empty probability: {empty_prob:.3f}")
                logger.info(f"  Occupied probability: {occupied_prob:.3f}")
                logger.info(f"  Confidence: {max(empty_prob, occupied_prob):.3f}")
            else:
                prediction = predictor.predict(roi)
                status = "EMPTY" if prediction else "OCCUPIED"
                predictions_summary[status.lower()] += 1
                
                logger.info(f"\nSpot {idx} (x={x1}, y={y1}, w={w}, h={h}):")
                logger.info(f"  Prediction: {status}")
                logger.info(f"  (Model does not support probability predictions)")
        
        except Exception as e:
            logger.error(f"Spot {idx}: Error during prediction - {e}")
    
    cap.release()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total spots analyzed: {len(sample_indices)}")
    logger.info(f"Predicted as EMPTY: {predictions_summary['empty']}")
    logger.info(f"Predicted as OCCUPIED: {predictions_summary['occupied']}")
    logger.info(f"\nRecommendations:")
    
    if predictions_summary['occupied'] > predictions_summary['empty'] * 2:
        logger.info("  ⚠ Most spots are predicted as OCCUPIED")
        logger.info("  - Consider checking if model labels are reversed")
        logger.info("  - Try setting INVERT_PREDICTION=true in .env")
        logger.info("  - Or retrain the model with more balanced data")
    
    if hasattr(predictor.model, 'predict_proba'):
        logger.info("  ✓ Model supports probability predictions")
        logger.info("  - You can adjust CONFIDENCE_THRESHOLD in .env")
    else:
        logger.info("  ⚠ Model does not support probability predictions")
        logger.info("  - Consider using a model with predict_proba() method")



