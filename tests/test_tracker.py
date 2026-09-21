from src.tracker import BallTracker, iou


def test_iou_identical():
    """IoU двух одинаковых рамок = 1.0"""
    a = [0, 0, 10, 10]
    assert abs(iou(a, a) - 1.0) < 1e-6


def test_iou_disjoint():
    """IoU непересекающихся рамок = 0"""
    a = [0, 0, 10, 10]
    b = [20, 20, 30, 30]
    assert iou(a, b) == 0.0


def test_iou_half_overlap():
    """IoU с частичным пересечением"""
    a = [0, 0, 10, 10]
    b = [5, 5, 15, 15]
    expected = 25 / 175
    assert abs(iou(a, b) - expected) < 1e-6


def test_tracker_creates_track():
    """Трекер создаёт трек по первой детекции"""
    tracker = BallTracker(min_hits=1)
    tracker.update([{"bbox": [0, 0, 10, 10]}])
    tracks = tracker.update([{"bbox": [1, 1, 11, 11]}])
    assert len(tracks) == 1
    assert tracks[0].hits >= 1


def test_tracker_keeps_id_on_same_object():
    """ID сохраняется при небольшом смещении мяча"""
    tracker = BallTracker(min_hits=1)
    tracker.update([{"bbox": [100, 100, 120, 120]}])
    tracks1 = tracker.update([{"bbox": [102, 102, 122, 122]}])
    first_id = tracks1[0].id

    tracks2 = tracker.update([{"bbox": [104, 104, 124, 124]}])
    assert tracks2[0].id == first_id


def test_tracker_no_detections_returns_empty():
    """При отсутствии детекций трекер возвращает пустой список"""
    tracker = BallTracker(min_hits=1)
    tracker.update([{"bbox": [0, 0, 10, 10]}])
    tracks = tracker.update([])
    assert len(tracks) == 0