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
    
    def predict(self, spot_image: np.ndarray) -> bool:
        """
        Predict if a parking spot is empty or occupied
        
        Args:
            spot_image: BGR image of the parking spot
            
        Returns:
            True if empty, False if occupied
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call _load_model() first.")
        
        try:
            # Resize image to model input size
            img_resized = resize(spot_image, (*self.resize_size, 3))
            
            # Flatten image to feature vector
            flat_data = img_resized.flatten().reshape(1, -1)
            
            # Predict
            prediction = self.model.predict(flat_data)[0]
            
            # Map prediction to boolean (0 = empty, 1 = occupied)
            return self.EMPTY if prediction == 0 else self.OCCUPIED
        
        except Exception as e:
            logger.error(f"Error predicting spot status: {e}")
            # Default to occupied on error (safer assumption)
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
                predictions.append(self.OCCUPIED)  # Default to occupied if invalid
        
        return predictions
