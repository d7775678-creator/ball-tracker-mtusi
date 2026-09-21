import cv2
from collections import deque


class Visualizer:
    def __init__(self, history_len=60):
        self.trajectory = deque(maxlen=history_len)

    def draw(self, frame, detections, tracks, point):
        # Рисуем рамки детекций зелёным
        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Рисуем текущую точку и траекторию красным
        if point is not None:
            px, py = int(point[0]), int(point[1])
            self.trajectory.append((px, py))
            cv2.circle(frame, (px, py), 5, (0, 0, 255), -1)

        for i in range(1, len(self.trajectory)):
            cv2.line(
                frame,
                self.trajectory[i - 1],
                self.trajectory[i],
                (0, 0, 255),
                2
            )
        return frame