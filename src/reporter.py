import os
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


REPORTS_DIR = "static/reports"


def build_csv_report(job_id, data):
    """Сохраняет CSV с точками траектории и метриками."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"report_{job_id}.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Таблица точек траектории
        w.writerow(["frame", "x", "y", "x_stab", "y_stab", "track_id"])
        for p in data["points"]:
            w.writerow([
                p["frame_idx"], p["x"], p["y"],
                p["x_stab"], p["y_stab"], p["track_id"],
            ])

        # Пустая строка-разделитель
        w.writerow([])
        w.writerow(["=== Итоговые метрики ==="])

        # Метаданные и метрики
        for k, v in (data["job"] or {}).items():
            w.writerow([k, v])

    return path


def build_pdf_report(job_id, data):
    """Сохраняет PDF с титульной страницей и таблицей точек."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"report_{job_id}.pdf")

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm,
                 "Ball Tracker — отчёт об обработке видео")

    # Job ID
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 3 * cm, f"Job ID: {job_id}")

    # Блок метрик
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 4 * cm, "Метрики:")

    c.setFont("Helvetica", 11)
    y = height - 4.7 * cm
    job = data["job"] or {}
    for key in ("started_at", "finished_at", "total_frames",
                "avg_frame_ms", "precision", "recall", "f1", "mota"):
        if key in job:
            c.drawString(2 * cm, y, f"{key}: {job[key]}")
            y -= 0.55 * cm

    # Таблица точек
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Точки траектории (первые 50 кадров):")
    y -= 0.7 * cm

    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, y, "frame     x        y       x_stab   y_stab   track_id")
    y -= 0.4 * cm

    for p in data["points"][:50]:
        c.drawString(
            2 * cm, y,
            f"{p['frame_idx']:>5}   "
            f"{p['x']:>7.1f}  {p['y']:>7.1f}   "
            f"{p['x_stab']:>7.1f}  {p['y_stab']:>7.1f}   "
            f"{p['track_id']}"
        )
        y -= 0.4 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 9)

    c.save()
    return path