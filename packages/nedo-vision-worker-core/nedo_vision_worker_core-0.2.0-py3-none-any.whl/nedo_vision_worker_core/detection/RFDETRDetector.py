import cv2
import logging
try:
    from rfdetr import RFDETRBase
    RFDETR_AVAILABLE = True
except ImportError:
    RFDETR_AVAILABLE = False
    RFDETRBase = None

from ..database.DatabaseManager import DatabaseManager
from .BaseDetector import BaseDetector

logging.getLogger("ultralytics").setLevel(logging.WARNING)

class RFDETRDetector(BaseDetector):
    def __init__(self, model):
        if not RFDETR_AVAILABLE:
            raise ImportError(
                "RF-DETR is required but not installed. Install it manually with:\n"
                "pip install rfdetr @ git+https://github.com/roboflow/rf-detr.git@1e63dbad402eea10f110e86013361d6b02ee0c09\n"
                "See the documentation for more details."
            )
        self.model = None
        self.metadata = None

        if model:
            self.load_model(model)

    def load_model(self, model):
        self.metadata = model
        path = DatabaseManager.STORAGE_PATHS["models"] / model.file
        
        if not path.is_file() or path.stat().st_size == 0:
            logging.error(f"❌ Model file not found or empty: {path}")
            self.model = None
            return False
            
        try:
            self.model = RFDETRBase(pretrain_weights=path.as_posix())
            self.model.optimize_for_inference()
            return True
        except Exception as e:
            logging.error(f"❌ Error loading RFDETR model {model.name}: {e}")
            self.model = None
            return False

    def detect_objects(self, frame, confidence_threshold=0.7):
        if self.model is None:
            return []

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model.predict(frame_rgb, confidence_threshold)

        detections = []
        for class_id, conf, xyxy in zip(results.class_id, results.confidence, results.xyxy): 
            detections.append({
                "label": self.model.class_names[class_id],
                "confidence": conf,
                "bbox": xyxy
            })

        return detections
