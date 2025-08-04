import logging
import time
from .VideoStream import VideoStream
import threading

class VideoStreamManager:
    """Manages multiple video streams dynamically using VideoStream threads."""

    def __init__(self):
        self.streams = {}  # Store streams as {worker_source_id: VideoStream}
        self.running = False
        self.lock = threading.Lock()  # Add thread lock

    def add_stream(self, worker_source_id, url):
        """Adds a new video stream if it's not already active."""
        if worker_source_id not in self.streams:
            self.streams[worker_source_id] = VideoStream(url)  # Create and start the VideoStream thread

        else:
            logging.warning(f"⚠️ Stream {worker_source_id} is already active.")

    def remove_stream(self, worker_source_id):
        """Removes and stops a video stream."""
        if not worker_source_id:
            return

        with self.lock:
            if worker_source_id not in self.streams:
                logging.warning(f"⚠️ Stream {worker_source_id} not found in manager.")
                return

            logging.info(f"🛑 Removing video stream: {worker_source_id}")

            # Get reference before removing from dict
            stream = self.streams.pop(worker_source_id, None)

        if stream:
            try:
                stream.stop()

            except Exception as e:
                logging.error(f"❌ Error stopping stream {worker_source_id}: {e}")
            finally:
                stream = None  # Ensure cleanup

        logging.info(f"✅ Stream {worker_source_id} removed successfully.")

    def start_all(self):
        """Starts all video streams."""
        logging.info("🔄 Starting all video streams...")
        for stream in self.streams.values():
            if not stream.is_alive():
                stream.start()  # Start thread if not already running
        self.running = True
    def stop_all(self):
        """Stops all video streams."""
        logging.info("🛑 Stopping all video streams...")
        
        with self.lock:
            # Get a list of IDs to avoid modification during iteration
            stream_ids = list(self.streams.keys())
            
        # Stop each stream
        for worker_source_id in stream_ids:
            try:
                self.remove_stream(worker_source_id)
            except Exception as e:
                logging.error(f"Error stopping stream {worker_source_id}: {e}")
        
        self.running = False

    def get_frame(self, worker_source_id):
        """Retrieves the latest frame for a specific stream."""
        with self.lock:  # Add lock protection for stream access
            stream = self.streams.get(worker_source_id)
            if stream is None:
                return None

            # Check if stream is still running
            if not stream.running:
                return None

            try:
                # **Ignore warnings for the first 5 seconds**
                elapsed_time = time.time() - stream.start_time
                if elapsed_time < 5:
                    return None

                # Check if video file has ended
                if stream.is_file and stream.is_video_ended():
                    logging.debug(f"Video file {worker_source_id} has ended, waiting for restart...")
                    # Small delay to allow the video to restart
                    time.sleep(0.1)
                    return None

                return stream.get_frame()  # Already returns a copy
            except Exception as e:
                logging.error(f"Error getting frame from stream {worker_source_id}: {e}")
                return None

    def get_active_stream_ids(self):
        """Returns a list of active stream IDs."""
        return list(self.streams.keys())

    def get_stream_url(self, worker_source_id):
        """Returns the URL of a specific stream."""
        stream = self.streams.get(worker_source_id)
        return stream.source if stream else None
    
    def has_stream(self, worker_source_id):
        """Checks if a stream is active."""
        return worker_source_id in self.streams

    def is_running(self):
        """Checks if the manager is running."""
        return self.running

    def is_video_file(self, worker_source_id):
        """Check if a stream is a video file."""
        stream = self.streams.get(worker_source_id)
        return stream.is_file if stream else False
