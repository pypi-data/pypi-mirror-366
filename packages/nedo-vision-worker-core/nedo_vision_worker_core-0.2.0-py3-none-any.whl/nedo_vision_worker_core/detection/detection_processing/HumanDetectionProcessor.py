from typing import Any, Dict, List, Tuple

import numpy as np
from shapely.geometry import Polygon
from .DetectionProcessor import DetectionProcessor
from ...pipeline.PipelineConfigManager import PipelineConfigManager
from ...repositories.RestrictedAreaRepository import RestrictedAreaRepository
from ...util.PersonRestrictedAreaMatcher import PersonRestrictedAreaMatcher


class HumanDetectionProcessor(DetectionProcessor):
    code = "human"
    labels = ["in_restricted_area"]
    violation_labels = ["in_restricted_area"]

    def __init__(self):
        self.repository = RestrictedAreaRepository()
        self.restricted_areas = []

    def update(self, config_manager: PipelineConfigManager):
        config = config_manager.get_feature_config(self.code, [])
        area_list = config.get("restrictedArea", [])
        self.restricted_areas = [
            [(p["x"], p["y"]) for p in area] for area in area_list
        ]

    def process(self, detections: List[Dict[str, Any]], dimension: Tuple[int, int]) -> List[Dict[str, Any]]:
        persons = [d for d in detections if d["label"] == "person"]

        height, width = dimension
        area_polygons = []

        for area in self.restricted_areas:
            points = [(int(x * width), int(y * height)) for x, y in area]
            area_polygons.append(Polygon(points))

        matched_results = PersonRestrictedAreaMatcher.match_persons_with_restricted_areas(
            persons, area_polygons
        )

        return matched_results

    def save_to_db(self, pipeline_id: str, worker_source_id: str, frame_counter: int, tracked_objects: List[Dict[str, Any]], frame: np.ndarray, frame_drawer):
        """Save the processed detections to the database if the feature is enabled."""
        self.repository.save_area_violation(
            pipeline_id, worker_source_id, frame_counter, tracked_objects, frame, frame_drawer
        )
