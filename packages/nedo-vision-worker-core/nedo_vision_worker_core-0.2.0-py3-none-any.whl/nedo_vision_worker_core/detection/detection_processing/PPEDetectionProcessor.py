from typing import Any, Dict, List, Tuple

import numpy as np
from ...ai.FrameDrawer import FrameDrawer
from .DetectionProcessor import DetectionProcessor
from ...pipeline.PipelineConfigManager import PipelineConfigManager
from ...repositories.PPEDetectionRepository import PPEDetectionRepository
from ...util.PersonAttributeMatcher import PersonAttributeMatcher

class PPEDetectionProcessor(DetectionProcessor):
    code = "ppe"
    icons = {
        "helmet": "icons/helmet-green.png",
        "no_helmet": "icons/helmet-red.png",
        "vest": "icons/vest-green.png",
        "no_vest": "icons/vest-red.png"
    }
    labels = ["helmet", "no_helmet", "vest", "no_vest", "gloves", "no_gloves", "goggles", "no_goggles", "boots", "no_boots"]
    violation_labels = ["no_helmet", "no_vest", "no_gloves", "no_goggles", "no_boots"]
    compliance_labels = ["helmet", "vest", "gloves", "goggles", "boots"]
    exclusive_labels = [("helmet", "no_helmet"), ("vest", "no_vest"), ("gloves", "no_gloves"), ("goggles", "no_goggles"), ("boots", "no_boots")]

    def __init__(self):
        self.ppe_storage = PPEDetectionRepository()
        self.types = []

    def update(self, config_manager: PipelineConfigManager):
        config = config_manager.get_feature_config(self.code, [])
        self.types = config.get("ppeType", [])

    def process(self, detections: List[Dict[str, Any]], dimension: Tuple[int, int]) -> List[Dict[str, Any]]:
        persons = [d for d in detections if d["label"] == "person"]
        ppe_attributes = [d for d in detections if any(x in d["label"] for x in self.types)]

        matched_results = PersonAttributeMatcher.match_persons_with_attributes(
            persons, ppe_attributes, coverage_threshold=0.5
        )

        return matched_results

    def save_to_db(self, pipeline_id: str, worker_source_id: str, frame_counter: int, tracked_objects: List[Dict[str, Any]], frame: np.ndarray, frame_drawer: FrameDrawer):
        self.ppe_storage.save_ppe_detection(
            pipeline_id, worker_source_id, frame_counter, tracked_objects, frame, frame_drawer
        )
