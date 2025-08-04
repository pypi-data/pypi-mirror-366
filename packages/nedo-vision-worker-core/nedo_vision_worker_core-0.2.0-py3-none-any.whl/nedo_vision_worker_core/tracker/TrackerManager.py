import uuid
import time
import numpy as np
from .SFSORT import SFSORT

class TrackerManager:
    def __init__(self, attribute_labels=None, exclusive_attribute_groups=None):
        self.tracker = SFSORT({
            "dynamic_tuning": True,
            "cth": 0.5,
            "high_th": 0.6,
            "match_th_first": 0.67,
            "match_th_second": 0.2,
            "low_th": 0.1,
            "new_track_th": 0.7,
            "marginal_timeout": 7,
            "central_timeout": 30
        })
        self.track_uuid_map = {}
        self.track_count_map = {}
        self.track_attributes_presence = {}
        self.track_last_seen = {}
        self.track_timeout_seconds = 5
        self.attribute_labels = attribute_labels or []
        self.exclusive_attribute_groups = exclusive_attribute_groups or []

    def track_objects(self, detections):
        if not detections:
            self._cleanup_stale_tracks()
            return []

        bboxes = np.array([d["bbox"] for d in detections], dtype=np.float32)
        confidences = np.array([d["confidence"] for d in detections], dtype=np.float32)
        tracks = self.tracker.update(bboxes, confidences)

        results = self._generate_tracking_results(detections, tracks)
        self._cleanup_stale_tracks()
        return results

    def _generate_tracking_results(self, detections, tracks):
        tracked_results = []
        detection_map = {tuple(d["bbox"]): d for d in detections}

        for track in tracks:
            track_id = int(track[1])
            bbox = track[0].tolist()
            data = detection_map.get(tuple(bbox))

            if not data:
                continue

            obj_uuid = self._assign_uuid(track_id)

            self.track_count_map[obj_uuid] += 1
            self.track_last_seen[obj_uuid] = time.time()  # Time-based last seen

            attributes = data.get("attributes", [])
            filtered_attributes = self._filter_exclusive_attributes(attributes)
            self._update_attribute_presence(obj_uuid, filtered_attributes)

            for attr in filtered_attributes:
                label = attr["label"]
                if label in self.track_attributes_presence[obj_uuid]:
                    attr["count"] = self.track_attributes_presence[obj_uuid][label]

            tracked_results.append({
                "uuid": obj_uuid,
                "track_id": track_id,
                "detections": self.track_count_map[obj_uuid],
                "label": data["label"],
                "confidence": data["confidence"],
                "bbox": bbox,
                "attributes": filtered_attributes
            })

        return tracked_results

    def _assign_uuid(self, track_id):
        if track_id not in self.track_uuid_map:
            new_uuid = str(uuid.uuid4())
            self.track_uuid_map[track_id] = new_uuid
            self.track_count_map[new_uuid] = 0
            self.track_attributes_presence[new_uuid] = {attr: 0 for attr in self.attribute_labels}
        return self.track_uuid_map[track_id]

    def _filter_exclusive_attributes(self, attributes):
        if not attributes:
            return []

        # Group attributes by label to handle multiple instances
        attrs_by_label = {}
        for attr in attributes:
            label = attr["label"]
            if label not in attrs_by_label:
                attrs_by_label[label] = []
            attrs_by_label[label].append(attr)

        # Multi-instance classes that can have multiple instances per person
        MULTI_INSTANCE_CLASSES = ["boots", "gloves", "goggles", "no_gloves"]
        # Negative classes that are exclusive with their positive counterparts
        NEGATIVE_CLASSES = ["no_helmet", "no_vest", "no_goggles", "no_boots"]
        
        # For exclusive groups, keep only the highest confidence per group
        filtered_attrs = []
        for group in self.exclusive_attribute_groups:
            group_attrs = []
            for label in group:
                if label in attrs_by_label:
                    group_attrs.extend(attrs_by_label[label])
            if group_attrs:
                # Keep only the highest confidence in this exclusive group
                best = max(group_attrs, key=lambda a: a["confidence"])
                filtered_attrs.append(best)

        # For multi-instance classes, add all instances (but respect exclusive logic above)
        exclusive_labels = set(l for group in self.exclusive_attribute_groups for l in group)
        for label, attrs in attrs_by_label.items():
            # Skip if already handled by exclusive logic
            if label in exclusive_labels:
                continue
            # Add all instances of multi-instance classes
            if label in MULTI_INSTANCE_CLASSES:
                filtered_attrs.extend(attrs)
        
        # Special case: for multi-instance classes, we want to allow multiple instances
        # even if they were in exclusive groups, but we need to handle the negative classes properly
        for label, attrs in attrs_by_label.items():
            # If this is a multi-instance class and not a negative class, add all instances
            if label in MULTI_INSTANCE_CLASSES and label not in NEGATIVE_CLASSES:
                # Check which attributes were already added
                for attr in attrs:
                    already_added = any(
                        a["label"] == label and list(a["bbox"]) == list(attr["bbox"]) 
                        for a in filtered_attrs
                    )
                    if not already_added:
                        filtered_attrs.append(attr)

        return filtered_attrs

    def _update_attribute_presence(self, uuid, attributes):
        current_frame_attrs = set(attr["label"] for attr in attributes)
        for label in self.attribute_labels:
            if label in current_frame_attrs:
                self.track_attributes_presence[uuid][label] += 1
            else:
                self.track_attributes_presence[uuid][label] = 0

    def _cleanup_stale_tracks(self):
        now = time.time()
        expired = [
            uuid for uuid, last_seen in self.track_last_seen.items()
            if now - last_seen > self.track_timeout_seconds
        ]

        for obj_uuid in expired:
            track_ids_to_remove = [tid for tid, uid in self.track_uuid_map.items() if uid == obj_uuid]
            for tid in track_ids_to_remove:
                self.track_uuid_map.pop(tid, None)

            self.track_count_map.pop(obj_uuid, None)
            self.track_attributes_presence.pop(obj_uuid, None)
            self.track_last_seen.pop(obj_uuid, None)
