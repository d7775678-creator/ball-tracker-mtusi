CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    input_path TEXT,
    started_at TEXT,
    finished_at TEXT,
    precision REAL,
    recall REAL,
    f1 REAL,
    mota REAL,
    avg_frame_ms REAL,
    total_frames INTEGER
);

CREATE TABLE IF NOT EXISTS points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    frame_idx INTEGER,
    x REAL,
    y REAL,
    x_stab REAL,
    y_stab REAL,
    track_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_points_job ON points(job_id);