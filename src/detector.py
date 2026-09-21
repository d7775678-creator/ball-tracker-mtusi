from ultralytics import YOLO
import numpy as np


class BallDetector:
    def __init__(self, weights_path, conf=0.35, iou=0.5):
        self.model = YOLO(weights_path)
        self.conf = conf
        self.iou = iou

    def detect(self, frame):
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            verbose=False
        )[0]

        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            # 32 = "sports ball" в стандартном датасете COCO.
            # Если позже будешь использовать свою дообученную модель
            # (с одним классом ball = 0) — поменяй 32 на 0.
            if cls_id != 32:
                continue

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            detections.append({
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "conf": float(box.conf[0]),
                "cx": float((x1 + x2) / 2),
                "cy": float((y1 + y2) / 2),
            })
        return detections