import os
import cv2
import threading
import time
import logging
from typing import Optional


class VideoStream(threading.Thread):
    """Threaded class for capturing video from a source, with automatic reconnection.
    
    This class provides a thread-safe way to capture video frames from various sources
    (cameras, files, network streams) with automatic reconnection on failure.
    
    Attributes:
        source: The video source (int for webcams, string for files/URLs)
        reconnect_interval: Time in seconds to wait before reconnecting on failure
        retry_limit: Maximum number of consecutive retries before giving up
    """
    def __init__(
        self, 
        source: str, 
        reconnect_interval: int = 5,
        retry_limit: int = 5,
        max_reconnect_attempts: int = 10,
        reconnect_backoff_factor: float = 1.5
    ):
        super().__init__()
        
        # Stream configuration
        self.source = source
        self.reconnect_interval = reconnect_interval
        self.retry_limit = retry_limit
        
        # Stream state
        self.capture = None
        self.running = True
        self.connected = False
        self.start_time = time.time()
        self.is_file = isinstance(source, (int, str, bytes, os.PathLike)) and os.path.isfile(source)
        self.fps = 30  # Default FPS until determined
        self.frame_count = 0
        
        # Reconnection control
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_attempts = 0
        self.reconnect_backoff_factor = reconnect_backoff_factor
        self.current_reconnect_interval = reconnect_interval
        
        # Thread synchronization
        self.lock = threading.Lock()
        self._latest_frame = None
        
        # Start the capture thread
        self.start()

    def _initialize_capture(self) -> bool:
        """Initialize or reinitialize the capture device.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"🔄 Attempting to connect to stream: {self.source} (attempt {self.reconnect_attempts + 1}/{self.max_reconnect_attempts})")
            
            # Clean up existing capture if needed
            if self.capture:
                self.capture.release()
                
            # Create new capture object
            self.capture = cv2.VideoCapture(self.source)
            
            if not self.capture.isOpened():
                logging.error(f"❌ Failed to open video source: {self.source}")
                return False
                
            # Get FPS if available or estimate it
            self.fps = self.capture.get(cv2.CAP_PROP_FPS)
            
            # Check FPS validity and estimate if needed
            if not self.fps or self.fps <= 0 or self.fps > 240:
                if self.reconnect_attempts:
                    return False

                logging.warning(f"⚠️ Invalid FPS reported ({self.fps}). Using default 30 FPS.")
                self.fps = 30
            
            if self.is_file:
                total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
                duration = (total_frames / self.fps) if self.fps > 0 and total_frames > 0 else 0
                logging.info(f"✅ Connected to video file {self.source} at {self.fps:.2f} FPS, {total_frames} frames, {duration:.2f}s duration")
            else:
                logging.info(f"✅ Connected to stream {self.source} at {self.fps:.2f} FPS")
                
            self.connected = True
            return True
            
        except Exception as e:
            logging.error(f"❌ Error initializing capture for {self.source}: {e}")
            self.connected = False
            if self.capture:
                try:
                    self.capture.release()
                except:
                    pass
                self.capture = None
            return False

    def run(self):
        """Main thread loop that continuously captures frames with automatic reconnection."""
        retry_count = 0
        frame_interval = 0  # Will be calculated once we know the FPS
        
        while self.running:
            try:
                # Check if we should exit
                if not self.running:
                    break
                    
                # (Re)connect if needed
                if self.capture is None or not self.capture.isOpened():
                    # Check if we've exceeded the maximum reconnection attempts
                    if self.reconnect_attempts >= self.max_reconnect_attempts:
                        logging.error(f"❌ Exceeded maximum reconnection attempts ({self.max_reconnect_attempts}) for {self.source}. Giving up.")
                        self.running = False
                        break
                    
                    if retry_count:
                        self.reconnect_attempts += 1

                    if not self._initialize_capture():
                        # Apply exponential backoff to reconnection interval
                        self.current_reconnect_interval *= self.reconnect_backoff_factor
                        
                        logging.warning(f"⚠️ Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} "
                                      f"failed. Next attempt in {self.current_reconnect_interval:.1f}s...")
                        
                        # Check for thread stop before sleeping
                        if not self.running:
                            break
                            
                        time.sleep(self.current_reconnect_interval)
                        continue
                    
                    # Reset counters on successful connection
                    retry_count = 0
                    # Only reset reconnect_attempts if we've been connected for a meaningful duration
                    # This prevents rapid success/fail cycles from resetting the counter
                    if self.connected:
                        self.reconnect_attempts = 0
                        self.current_reconnect_interval = self.reconnect_interval
                    
                    frame_interval = 1.0 / self.fps if self.fps > 0 else 0.033
                
                # Check if we should exit before reading frame
                if not self.running:
                    break
                
                # Read the next frame
                read_start = time.time()
                ret, frame = self.capture.read()
                
                # Handle frame read failure
                if not ret or frame is None or frame.size == 0:
                    if self.is_file:
                        # For video files, check if we've reached the end
                        current_pos = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
                        total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
                        
                        # If we're at or beyond the end of the video, restart from beginning
                        if current_pos >= total_frames - 1:
                            logging.info(f"🔄 Video file {self.source} reached end. Restarting from beginning...")
                            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            # Reset retry count for video files when restarting
                            retry_count = 0
                            continue
                        else:
                            # We're not at the end, this might be a real error
                            retry_count += 1
                            logging.warning(f"⚠️ Failed to read frame from {self.source} at position {current_pos}/{total_frames} (attempt {retry_count}/{self.retry_limit})")
                    else:
                        # For non-file sources (cameras, streams), increment retry count
                        retry_count += 1
                        logging.warning(f"⚠️ Failed to read frame from {self.source} (attempt {retry_count}/{self.retry_limit})")
                    
                    if retry_count > self.retry_limit:
                        logging.error(f"❌ Too many consecutive frame failures. Reconnecting...")
                        self.connected = False
                        if self.capture and self.running:  # Only release if we're still running
                            try:
                                self.capture.release()
                                self.capture = None
                            except Exception as e:
                                logging.error(f"Error releasing capture during failure: {e}")
                        continue
                    
                    if not self.running:
                        break

                    time.sleep(0.1)
                    continue
                
                # Reset retry count on successful frame
                retry_count = 0
                self.frame_count += 1
                
                # Store the frame - but make sure we're still running first
                if not self.running:
                    break
                    
                with self.lock:
                    self._latest_frame = frame.copy()
                
                # Regulate frame rate to match source FPS for efficiency
                # This helps prevent CPU overuse when reading from fast sources
                elapsed = time.time() - read_start
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0 and self.running:  # Check running before sleep
                    time.sleep(sleep_time)
                    
            except cv2.error as cv_err:
                logging.error(f"❌ OpenCV error in frame processing: {cv_err}")
                self.connected = False
                if not self.running:
                    break
                time.sleep(1)  # Brief pause before retry
                
            except Exception as e:
                logging.error(f"❌ Error in VideoStream {self.source}: {e}", exc_info=True)
                self.connected = False
                if not self.running:
                    break
                time.sleep(self.reconnect_interval)
        
        # Final cleanup
        self._cleanup()

    def _cleanup(self):
        """Release resources and perform cleanup."""
        try:
            if self.capture:
                self.capture.release()
                self.capture = None
                
            with self.lock:
                self._latest_frame = None
                        
            self.connected = False
            logging.info(f"🔴 Stream {self.source} stopped and cleaned up.")
            
        except Exception as e:
            logging.error(f"Error during final VideoStream cleanup: {e}")

    def get_frame(self) -> Optional[cv2.Mat]:
        """Returns the latest available frame (thread-safe).
        
        Returns:
            A copy of the latest frame or None if no frames are available
        """
        if not self.running:
            return None
        
        with self.lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
        return None

    def is_video_ended(self) -> bool:
        """Check if a video file has reached its end (only for video files).
        
        Returns:
            True if video file has ended, False otherwise
        """
        if not self.is_file or not self.capture or not self.capture.isOpened():
            return False
            
        try:
            current_pos = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
            return current_pos >= total_frames - 1
        except Exception:
            return False

    def stop(self):
        """Stops the video stream and releases resources safely."""
        if not self.running:  # Prevent multiple stops
            return
    
        # Step 1: Signal the thread to stop
        self.running = False
        
        # Step 2: Wait for any ongoing OpenCV operations to complete
        time.sleep(0.2)  # Short delay to let operations finish
        
        # Step 3: Explicitly release capture device before joining thread
        # This is critical to avoid segmentation faults in some OpenCV implementations
        if self.capture:
            try:
                logging.debug(f"Releasing capture device for {self.source}")
                with self.lock:  # Use lock to ensure thread isn't accessing capture during release
                    if self.capture:
                        self.capture.release()
                        self.capture = None
            except Exception as e:
                logging.error(f"Error releasing capture device: {e}")
        
        # Step 4: Clear any references to frames to help garbage collection
        with self.lock:
            self._latest_frame = None
                
        # Step 5: Wait for thread to exit
        try:
            if self.is_alive():
                logging.debug(f"Waiting for thread to exit for stream {self.source}")
                self.join(timeout=30)  # Reduced timeout since we already released resources
                
                # Check if thread is still alive
                if self.is_alive():
                    logging.warning(f"⚠️ Stream {self.source} thread did not exit cleanly within timeout")
        except Exception as e:
            logging.error(f"Error joining thread: {e}")
        
        # Final status update
        self.connected = False