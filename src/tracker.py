import numpy as np
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment


def iou(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter + 1e-6)


class KalmanTrack:
    _next_id = 1

    def __init__(self, bbox):
        self.id = KalmanTrack._next_id
        KalmanTrack._next_id += 1

        self.kf = KalmanFilter(dim_x=7, dim_z=4)

        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        s = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        r = (bbox[2] - bbox[0]) / ((bbox[3] - bbox[1]) + 1e-6)

        self.kf.x[:4] = np.array([[cx], [cy], [s], [r]])
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ], dtype=float)
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ], dtype=float)
        self.kf.R[2:, 2:] *= 10.0
        self.kf.P[4:, 4:] *= 1000.0

        self.time_since_update = 0
        self.hits = 0

    @property
    def center(self):
        return float(self.kf.x[0, 0]), float(self.kf.x[1, 0])

    @property
    def bbox(self):
        cx, cy, s, r = self.kf.x[:4, 0]
        w = np.sqrt(max(s, 1) * r)
        h = max(s, 1) / max(w, 1e-6)
        return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

    def predict(self):
        self.kf.predict()
        self.time_since_update += 1

    def update(self, bbox):
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        s = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        r = (bbox[2] - bbox[0]) / ((bbox[3] - bbox[1]) + 1e-6)
        self.kf.update(np.array([[cx], [cy], [s], [r]]))
        self.time_since_update = 0
        self.hits += 1


class BallTracker:
    def __init__(self, max_age=30, min_hits=2, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks = []

    def update(self, detections):
        for trk in self.tracks:
            trk.predict()

        if not self.tracks:
            for det in detections:
                self.tracks.append(KalmanTrack(det["bbox"]))
            return []

        cost = np.zeros((len(self.tracks), len(detections)))
        for i, trk in enumerate(self.tracks):
            for j, det in enumerate(detections):
                cost[i, j] = 1.0 - iou(trk.bbox, det["bbox"])

        rows, cols = linear_sum_assignment(cost)
        matched_det = set()
        for r, c in zip(rows, cols):
            if cost[r, c] <= 1 - self.iou_threshold:
                self.tracks[r].update(detections[c]["bbox"])
                matched_det.add(c)

        for j, det in enumerate(detections):
            if j not in matched_det:
                self.tracks.append(KalmanTrack(det["bbox"]))

        self.tracks = [
            t for t in self.tracks if t.time_since_update <= self.max_age
        ]

        return [
            t for t in self.tracks
            if t.time_since_update == 0 and t.hits >= self.min_hits
        ]