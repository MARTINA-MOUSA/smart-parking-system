"""
Script to check if all required files and setup are in place
"""

from pathlib import Path
from loguru import logger
from app.utils.config import settings
from app.utils.logger import setup_logger


def check_setup():
    """Check if all required files exist"""
    setup_logger()
    
    logger.info("Checking Smart Parking System setup...")
    logger.info("=" * 60)
    
    all_ok = True
    
    # Check mask file
    mask_path = settings.get_mask_path()
    logger.info(f"\n1. Checking mask file...")
    if mask_path.exists():
        logger.info(f"   ✓ Mask file found: {mask_path}")
    else:
        logger.error(f"   ✗ Mask file NOT found: {mask_path}")
        logger.info(f"   Please place your mask image at: {mask_path}")
        all_ok = False
    
    # Check model file
    model_path = settings.get_model_path()
    logger.info(f"\n2. Checking model file...")
    if model_path.exists():
        logger.info(f"   ✓ Model file found: {model_path}")
    else:
        logger.error(f"   ✗ Model file NOT found: {model_path}")
        logger.info(f"   Please place your ML model at: {model_path}")
        all_ok = False
    
    # Check data directories
    logger.info(f"\n3. Checking data directories...")
    dirs_to_check = {
        "Videos": Path(settings.VIDEOS_DIR),
        "Masks": Path(settings.MASKS_DIR),
        "Models": Path(settings.MODELS_DIR),
        "Outputs": Path(settings.OUTPUT_DIR),
    }
    
    for name, dir_path in dirs_to_check.items():
        if dir_path.exists():
            logger.info(f"   ✓ {name} directory exists: {dir_path}")
            # List files if any
            files = list(dir_path.glob("*"))
            if files:
                logger.info(f"     Found {len(files)} file(s)")
        else:
            logger.warning(f"   ⚠ {name} directory does not exist: {dir_path}")
            logger.info(f"     Creating directory...")
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"     ✓ Directory created")
    
    # Check for video files
    videos_dir = Path(settings.VIDEOS_DIR)
    logger.info(f"\n4. Checking for video files...")
    if videos_dir.exists():
        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi"))
        if video_files:
            logger.info(f"   ✓ Found {len(video_files)} video file(s):")
            for vf in video_files:
                logger.info(f"     - {vf.name}")
        else:
            logger.warning(f"   ⚠ No video files found in {videos_dir}")
            logger.info(f"     Supported formats: .mp4, .avi")
            logger.info(f"     Example usage: python run.py --video {videos_dir}/your_video.mp4")
    
    # Check database
    logger.info(f"\n5. Checking database...")
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if db_path.exists():
        logger.info(f"   ✓ Database file exists: {db_path}")
    else:
        logger.info(f"   ℹ Database will be created on first run: {db_path}")
    
    logger.info("\n" + "=" * 60)
    
    if all_ok:
        logger.info("✓ Setup check completed successfully!")
        logger.info("\nYou can now run:")
        logger.info("  python run.py --video ./data/videos/your_video.mp4")
    else:
        logger.warning("⚠ Setup incomplete. Please fix the issues above.")
        logger.info("\nAfter fixing, you can run:")
        logger.info("  python run.py --video ./data/videos/your_video.mp4")
    
    return all_ok


if __name__ == "__main__":
    check_setup()

