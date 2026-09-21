import os
import sqlite3
from datetime import datetime


DB_PATH = "data/tracker.db"


class Storage:
    def __init__(self, db_path=DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def start_job(self, job_id, input_path):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO jobs(job_id, input_path, started_at) VALUES (?, ?, ?)",
            (job_id, input_path, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def add_point(self, job_id, frame_idx, x, y, xs, ys, track_id):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO points(job_id, frame_idx, x, y, x_stab, y_stab, track_id)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (job_id, frame_idx, x, y, xs, ys, track_id)
        )
        self.conn.commit()

    def finish_job(self, job_id, metrics):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE jobs SET finished_at=?, precision=?, recall=?, "
            "f1=?, mota=?, avg_frame_ms=?, total_frames=? "
            "WHERE job_id=?",
            (
                datetime.utcnow().isoformat(),
                metrics.get("precision", 0.0),
                metrics.get("recall", 0.0),
                metrics.get("f1", 0.0),
                metrics.get("mota", 0.0),
                metrics["avg_frame_ms"],
                metrics["total_frames"],
                job_id,
            )
        )
        self.conn.commit()

    def get_metrics(self, job_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,))
        cols = [d[0] for d in cur.description]
        row = cur.fetchone()
        return dict(zip(cols, row)) if row else None

    def list_jobs(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM jobs ORDER BY started_at DESC")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def get_full_report(self, job_id):
        """Возвращает метаданные + все точки траектории для job_id."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM points WHERE job_id=? ORDER BY frame_idx",
            (job_id,)
        )
        cols = [d[0] for d in cur.description]
        points = [dict(zip(cols, r)) for r in cur.fetchall()]

        return {
            "job": self.get_metrics(job_id),
            "points": points,
        }