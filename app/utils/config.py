"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Smart Parking System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Video Processing
    VIDEO_FPS: int = 30
    PROCESSING_STEP: int = 30
    DIFF_THRESHOLD: float = 0.4
    RESIZE_WIDTH: int = 15
    RESIZE_HEIGHT: int = 15
    
    # Model Prediction
    CONFIDENCE_THRESHOLD: float = 0.5
    INVERT_PREDICTION: bool = False  # Set to True if model labels are reversed
    
    # Model & Mask Paths
    MODEL_PATH: str = "./models/model.p"
    MASK_PATH: str = "./data/masks/mask_1920_1080.png"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/parking.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Directories
    VIDEOS_DIR: str = "./data/videos"
    MASKS_DIR: str = "./data/masks"
    MODELS_DIR: str = "./models"
    OUTPUT_DIR: str = "./outputs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def get_model_path(self) -> Path:
        """Get absolute path to model file"""
        return Path(self.MODEL_PATH).resolve()
    
    def get_mask_path(self) -> Path:
        """Get absolute path to mask file"""
        return Path(self.MASK_PATH).resolve()
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        dirs = [
            self.VIDEOS_DIR,
            self.MASKS_DIR,
            self.MODELS_DIR,
            self.OUTPUT_DIR,
            Path(self.LOG_FILE).parent
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

