import logging
import os
import time
import threading
from ..database.DatabaseManager import DatabaseManager
from ..repositories.WorkerSourceRepository import WorkerSourceRepository
from .VideoStreamManager import VideoStreamManager

class StreamSyncThread(threading.Thread):
    """Thread responsible for synchronizing video streams from the database in real-time."""

    def __init__(self, manager: VideoStreamManager, polling_interval=5):
        super().__init__()  # Set as a daemon so it stops with the main process

        self.source_file_path = DatabaseManager.STORAGE_PATHS["files"] / "source_files"

        self.manager = manager
        self.polling_interval = polling_interval
        self.worker_source_repo = WorkerSourceRepository()
        self.running = True

    def _get_source_file_path(self, file):
        """Returns the file path for a given source file."""
        return self.source_file_path / os.path.basename(file)

    def run(self):
        """Continuously updates the VideoStreamManager with database changes."""
        while self.running:
            try:
                sources = self.worker_source_repo.get_worker_sources()
                db_sources = {
                    source.id: (source.url if source.type_code == "live" else self._get_source_file_path(source.file_path), source.status_code) for source in sources
                    }  # Store latest sources
                active_stream_ids = set(self.manager.get_active_stream_ids())

                # **1️⃣ Add new streams**
                for source_id, (url, status_code) in db_sources.items():
                    if source_id not in active_stream_ids and status_code == "connected":
                        logging.info(f"🟢 Adding new stream: {source_id} ({url})")
                        self.manager.add_stream(source_id, url)

                # **2️⃣ Remove deleted streams**
                for stream_id in active_stream_ids:
                    if stream_id not in db_sources or db_sources[stream_id][1] != "connected":
                        logging.info(f"🔴 Removing deleted stream: {stream_id}")
                        self.manager.remove_stream(stream_id)

                active_stream_ids = set(self.manager.get_active_stream_ids())

                # **3️⃣ Update streams if URL has changed**
                for source_id, (url, status_code) in db_sources.items():
                    if source_id in active_stream_ids:
                        existing_url = self.manager.get_stream_url(source_id)
                        if existing_url != url:
                            logging.info(f"🟡 Updating stream {source_id}: New URL {url}")
                            self.manager.remove_stream(source_id)
                            self.manager.add_stream(source_id, url)

            except Exception as e:
                logging.error(f"⚠️ Error syncing streams from database: {e}")

            time.sleep(self.polling_interval)  # Poll every X seconds

    def stop(self):
        """Stops the synchronization thread."""
        self.running = False
