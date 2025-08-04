import logging
import time
import signal
import os
from pathlib import Path
from typing import Callable, Dict, List, Any

from .util.DrawingUtils import DrawingUtils
from .streams.VideoStreamManager import VideoStreamManager
from .streams.StreamSyncThread import StreamSyncThread
from .pipeline.PipelineSyncThread import PipelineSyncThread
from .database.DatabaseManager import DatabaseManager
# Import models to ensure they are registered with SQLAlchemy Base registry
from . import models
import cv2


class CoreService:
    """Service class for running the Nedo Vision Core processing."""

    # Class-level callback registry for detection events
    _detection_callbacks: Dict[str, List[Callable]] = {
        'ppe_detection': [],
        'area_violation': [],
        'general_detection': []
    }

    def __init__(self, 
                 drawing_assets_path: str = None,
                 log_level: str = "INFO",
                 storage_path: str = "data",
                 rtmp_server: str = "rtmp://live.vision.sindika.co.id:1935/live"):
        """
        Initialize the Core Service.
        
        Args:
            drawing_assets_path: Path to drawing assets directory (optional, uses bundled assets by default)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            storage_path: Storage path for databases and files (default: data)
            rtmp_server: RTMP server URL for video streaming (default: rtmp://localhost:1935/live)
        """
        self.running = True
        self.video_manager = None
        self.stream_sync_thread = None
        self.pipeline_sync_thread = None
        
        # Store configuration parameters
        self.storage_path = storage_path
        self.rtmp_server = rtmp_server
        
        # Use bundled drawing assets by default
        if drawing_assets_path is None:
            # Get the path to the bundled drawing assets
            current_dir = Path(__file__).parent
            self.drawing_assets_path = str(current_dir / "drawing_assets")
        else:
            self.drawing_assets_path = drawing_assets_path
            
        self.log_level = log_level
        
        # Set up logging
        self._setup_logging()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    @classmethod
    def register_detection_callback(cls, detection_type: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback for detection events.
        
        Args:
            detection_type: Type of detection ('ppe_detection', 'area_violation', 'general_detection')
            callback: Function to call when detection occurs. Should accept a dict with detection data.
        """
        if detection_type not in cls._detection_callbacks:
            cls._detection_callbacks[detection_type] = []
        
        cls._detection_callbacks[detection_type].append(callback)
        logging.info(f"📞 Registered {detection_type} callback: {callback.__name__}")

    @classmethod
    def unregister_detection_callback(cls, detection_type: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Unregister a callback for detection events.
        
        Args:
            detection_type: Type of detection ('ppe_detection', 'area_violation', 'general_detection')
            callback: Function to unregister
        """
        if detection_type in cls._detection_callbacks and callback in cls._detection_callbacks[detection_type]:
            cls._detection_callbacks[detection_type].remove(callback)
            logging.info(f"📞 Unregistered {detection_type} callback: {callback.__name__}")

    @classmethod
    def trigger_detection_callback(cls, detection_type: str, detection_data: Dict[str, Any]):
        """
        Trigger all registered callbacks for a detection type.
        
        Args:
            detection_type: Type of detection that occurred
            detection_data: Dict containing detection information
        """
        callbacks = cls._detection_callbacks.get(detection_type, [])
        general_callbacks = cls._detection_callbacks.get('general_detection', [])
        
        # Call specific callbacks
        for callback in callbacks:
            try:
                callback(detection_data)
            except Exception as e:
                logging.error(f"❌ Error in {detection_type} callback {callback.__name__}: {e}")
        
        # Call general callbacks
        for callback in general_callbacks:
            try:
                callback(detection_data)
            except Exception as e:
                logging.error(f"❌ Error in general detection callback {callback.__name__}: {e}")

    @classmethod
    def list_callbacks(cls) -> Dict[str, List[str]]:
        """
        List all registered callbacks.
        
        Returns:
            Dict mapping detection types to callback function names
        """
        return {
            detection_type: [callback.__name__ for callback in callbacks]
            for detection_type, callbacks in cls._detection_callbacks.items()
            if callbacks
        }

    def _setup_environment(self):
        """Set up environment variables for components that still require them (like RTMPStreamer)."""
        os.environ["STORAGE_PATH"] = self.storage_path
        os.environ["RTMP_SERVER"] = self.rtmp_server

    def _setup_logging(self):
        """Configure logging settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("pika").setLevel(logging.WARNING)
        logging.getLogger("grpc").setLevel(logging.FATAL)
        logging.getLogger("ffmpeg").setLevel(logging.FATAL)
        logging.getLogger("subprocess").setLevel(logging.FATAL)

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def initialize(self):
        """Initialize all application components."""
        logging.info("🚀 Initializing Nedo Vision Core components...")

        try:
            # Set up environment variables for internal components that still need them
            self._setup_environment()

            # Initialize Database with storage path
            DatabaseManager.init_databases(storage_path=self.storage_path)

            # Initialize Drawing Utils
            DrawingUtils.initialize(self.drawing_assets_path)

            # Initialize Video Stream Manager
            self.video_manager = VideoStreamManager()

            # Start stream synchronization thread
            self.stream_sync_thread = StreamSyncThread(self.video_manager)
            self.stream_sync_thread.start()

            # Start pipeline synchronization thread (AI processing)
            self.pipeline_sync_thread = PipelineSyncThread(self.video_manager)
            self.pipeline_sync_thread.start()

            logging.info("✅ Nedo Vision Core initialized and running.")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize components: {e}", exc_info=True)
            return False

    def run(self):
        """Run the main application loop."""
        if not self.initialize():
            logging.error("❌ Failed to initialize, exiting...")
            return False
            
        try:
            logging.info("🔄 Core service is running. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
            return True
        except KeyboardInterrupt:
            logging.info("🛑 Interrupt received, shutting down...")
            return True
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False
        finally:
            self.stop()

    def stop(self):
        """Stop all application components gracefully."""
        logging.info("🛑 Stopping Nedo Vision Core...")
        
        self.running = False
        
        try:    
            if self.stream_sync_thread:
                self.stream_sync_thread.running = False
                self.stream_sync_thread.join(timeout=5)
                
            if self.pipeline_sync_thread:
                self.pipeline_sync_thread.running = False
                self.pipeline_sync_thread.join(timeout=5)

            if self.video_manager:
                self.video_manager.stop_all()
                
            # Final cleanup
            cv2.destroyAllWindows()
            for _ in range(5):  # Force windows to close
                cv2.waitKey(1)
                
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
        finally:
            logging.info("✅ Nedo Vision Core shutdown complete.") 