import cv2
import numpy as np


class CameraStabilizer:
    def __init__(self):
        self.prev_gray = None

    def estimate_transform(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.prev_gray is None:
            self.prev_gray = gray
            return np.eye(3)

        pts_prev = cv2.goodFeaturesToTrack(
            self.prev_gray,
            maxCorners=200,
            qualityLevel=0.01,
            minDistance=30
        )
        if pts_prev is None:
            self.prev_gray = gray
            return np.eye(3)

        pts_curr, status, _ = cv2.calcOpticalFlowPyrLK(
            self.prev_gray, gray, pts_prev, None
        )
        good_prev = pts_prev[status.flatten() == 1]
        good_curr = pts_curr[status.flatten() == 1]

        H = np.eye(3)
        if len(good_prev) >= 4:
            H, _ = cv2.findHomography(good_prev, good_curr, cv2.RANSAC, 3.0)
            if H is None:
                H = np.eye(3)

        self.prev_gray = gray
        return H

    @staticmethod
    def compensate(point, H):
        pt = np.array([point[0], point[1], 1.0])
        new_pt = H @ pt
        return float(new_pt[0] / new_pt[2]), float(new_pt[1] / new_pt[2])