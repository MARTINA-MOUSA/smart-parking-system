"""
Parking Spot Status Predictor Module
Uses ML model to predict if a parking spot is empty or occupied
"""

import pickle
import numpy as np
from typing import Tuple
from pathlib import Path
from loguru import logger
from skimage.transform import resize


class ParkingSpotPredictor:
    """Predicts parking spot status (empty/occupied) using ML model"""
    
    EMPTY = True
    OCCUPIED = False
    
    def __init__(self, model_path: str, resize_size: Tuple[int, int] = (15, 15)):
        """
        Initialize the predictor
        
        Args:
            model_path: Path to the trained model file
            resize_size: Target size for image resizing (width, height)
        """
        self.model_path = model_path
        self.resize_size = resize_size
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the trained ML model"""
        try:
            model_file = Path(self.model_path)
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info(f"Model loaded successfully from {self.model_path}")
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict(self, spot_image: np.ndarray, confidence_threshold: float = 0.5) -> bool:
        """
        Predict if a parking spot is empty or occupied
        
        Args:
            spot_image: BGR image of the parking spot
            confidence_threshold: Minimum confidence to make a prediction (0-1)
            
        Returns:
            True if empty, False if occupied
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call _load_model() first.")
        
        try:
            if spot_image is None or spot_image.size == 0:
                logger.warning("Empty spot image provided, defaulting to occupied")
                return self.OCCUPIED
            
            img_resized = resize(spot_image, (*self.resize_size, 3))
            
            if img_resized.max() > 1.0:
                img_resized = img_resized / 255.0
            
            flat_data = img_resized.flatten().reshape(1, -1)
            
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(flat_data)[0]
                empty_prob = probabilities[0]
                occupied_prob = probabilities[1]
                
                if empty_prob >= confidence_threshold:
                    return self.EMPTY
                elif occupied_prob >= confidence_threshold:
                    return self.OCCUPIED
                else:
                    return self.EMPTY if empty_prob > occupied_prob else self.OCCUPIED
            else:
                prediction = self.model.predict(flat_data)[0]
                
                if prediction == 0:
                    return self.EMPTY
                elif prediction == 1:
                    return self.OCCUPIED
                else:
                    logger.warning(f"Unexpected prediction value: {prediction}, defaulting to occupied")
                    return self.OCCUPIED
        
        except Exception as e:
            logger.error(f"Error predicting spot status: {e}", exc_info=True)
            return self.OCCUPIED
    
    def predict_batch(self, spot_images: list) -> list:
        """
        Predict status for multiple spots
        
        Args:
            spot_images: List of spot images
            
        Returns:
            List of predictions (True=empty, False=occupied)
        """
        predictions = []
        for img in spot_images:
            if img is not None:
                predictions.append(self.predict(img))
            else:
                predictions.append(self.OCCUPIED)
        
        return predictions
