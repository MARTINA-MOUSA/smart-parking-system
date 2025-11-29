"""
Main script to run the parking system
Can be used for both video processing and API server
"""

import cv2
import argparse
from pathlib import Path
from loguru import logger
from app.core.detector import ParkingSpotDetector
from app.core.predictor import ParkingSpotPredictor
from app.core.processor import VideoProcessor
from app.utils.config import settings
from app.utils.logger import setup_logger


def process_video(video_path: str, output_path: str = None, display: bool = True):
    """
    Process a video file and display results
    
    Args:
        video_path: Path to input video
        output_path: Optional path to save output video
        display: Whether to display video in window
    """
    # Resolve video path
    video_file = Path(video_path)
    if not video_file.is_absolute():
        video_file = Path.cwd() / video_file
    
    logger.info(f"Starting video processing: {video_file}")
    
    # Check if video file exists before initializing components
    if not video_file.exists():
        logger.error(
            f"Video file not found: {video_file}\n"
            f"Current working directory: {Path.cwd()}\n"
            f"Please ensure the video file exists at the specified path."
        )
        return
    
    # Initialize components
    try:
        detector = ParkingSpotDetector(str(settings.get_mask_path()))
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        return
    
    try:
        predictor = ParkingSpotPredictor(
            str(settings.get_model_path()),
            resize_size=(settings.RESIZE_WIDTH, settings.RESIZE_HEIGHT)
        )
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {e}")
        return
    
    processor = VideoProcessor(
        detector=detector,
        predictor=predictor,
        processing_step=settings.PROCESSING_STEP,
        diff_threshold=settings.DIFF_THRESHOLD
    )
    
    # Initialize processor
    if not processor.initialize(video_path=str(video_file)):
        logger.error("Failed to initialize processor. Please check the error messages above.")
        return
    
    # Setup video writer if output path provided
    writer = None
    if output_path:
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        logger.info(f"Output video will be saved to: {output_path}")
    
    # Process video
    try:
        while True:
            frame = processor.process_frame()
            
            if frame is None:
                break
            
            # Write frame if writer available
            if writer:
                writer.write(frame)
            
            # Display frame
            if display:
                cv2.namedWindow('Parking System', cv2.WINDOW_NORMAL)
                cv2.imshow('Parking System', frame)
                
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    logger.info("Processing stopped by user")
                    break
        
        # Print statistics
        stats = processor.get_statistics()
        logger.info(f"Processing complete. Statistics: {stats}")
    
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    
    finally:
        processor.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        logger.info("Resources released")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Smart Parking System")
    parser.add_argument(
        "--video",
        type=str,
        help="Path to input video file"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save output video"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Don't display video window"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server instead of processing video"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    setup_logger()
    
    if args.api:
        # Start API server
        import uvicorn
        logger.info("Starting API server...")
        uvicorn.run(
            "app.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.DEBUG
        )
    elif args.video:
        # Process video
        process_video(
            args.video,
            output_path=args.output,
            display=not args.no_display
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

