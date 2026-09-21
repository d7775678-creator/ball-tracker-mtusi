import os
import uuid
from flask import (Flask, render_template, request, redirect,
                   url_for, send_file)
from werkzeug.utils import secure_filename

from src.pipeline import process_video
from src.storage import Storage
from src.reporter import build_csv_report, build_pdf_report

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["RESULTS_FOLDER"] = "static/results"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

ALLOWED_EXT = {"mp4", "avi", "mov", "mkv"}


def allowed_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file or file.filename == "":
        return "Файл не выбран", 400
    if not allowed_file(file.filename):
        return "Недопустимый формат файла", 400

    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{secure_filename(file.filename)}"
    in_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(in_path)

    out_path = os.path.join(
        app.config["RESULTS_FOLDER"],
        f"{job_id}_processed.mp4"
    )

    try:
        process_video(in_path, out_path, job_id=job_id)
    except Exception as e:
        return f"Ошибка при обработке: {e}", 500

    return redirect(url_for("result", job_id=job_id))


@app.route("/result/<job_id>")
def result(job_id):
    storage = Storage()
    metrics = storage.get_metrics(job_id)
    video_url = url_for("static",
                        filename=f"results/{job_id}_processed.mp4")
    return render_template("result.html",
                           job_id=job_id,
                           video_url=video_url,
                           metrics=metrics)


@app.route("/reports")
def reports():
    storage = Storage()
    return render_template("reports.html", jobs=storage.list_jobs())

@app.route("/reports/<job_id>/<fmt>")
def download_report(job_id, fmt):
    storage = Storage()
    data = storage.get_full_report(job_id)

    if data["job"] is None:
        return "Отчёт не найден", 404

    if fmt == "csv":
        path = build_csv_report(job_id, data)
    elif fmt == "pdf":
        path = build_pdf_report(job_id, data)
    else:
        return "Неизвестный формат", 400

    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)
    app.run(debug=True)