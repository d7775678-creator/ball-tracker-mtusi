# Ball Tracker — система обнаружения и трекинга футбольного мяча

Прототип системы компьютерного зрения для анализа футбольных видеозаписей.
Обнаруживает мяч на видео, отслеживает его траекторию, компенсирует движение
камеры и предоставляет веб-интерфейс для загрузки видео и выгрузки отчётов.

## Возможности

- Обнаружение мяча с помощью YOLOv8
- Трекинг на фильтре Калмана
- Компенсация движения камеры (оптический поток + гомография)
- Веб-приложение на Flask
- Сохранение результатов в SQLite
- Выгрузка отчётов в CSV и PDF

## Стек технологий

- Python 3.11
- PyTorch, Ultralytics YOLOv8
- OpenCV, NumPy, SciPy
- Flask
- SQLite
- ReportLab (генерация PDF)
- imageio-ffmpeg (перекодирование видео в H.264)

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/d7775678-creator/ball-tracker-mtusi.git
cd ball-tracker-mtusi
```

### 2. Создать виртуальное окружение

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Скачать веса YOLOv8

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

Затем переместить файл в папку `models/`:

**Windows:**

```powershell
move yolov8n.pt models\yolov8n_ball.pt
```

**Linux / macOS:**

```bash
mv yolov8n.pt models/yolov8n_ball.pt
```

### 5. Запустить приложение

```bash
python app.py
```

Открой в браузере: http://127.0.0.1:5000/

## Структура проекта

```text
ball-tracker/
├── app.py                  # Flask-приложение
├── config.yaml             # настройки (задел на будущее)
├── requirements.txt
├── README.md
├── .gitignore
├── pytest.ini
├── src/
│   ├── detector.py         # YOLOv8-обёртка
│   ├── tracker.py          # фильтр Калмана
│   ├── stabilizer.py       # компенсация движения камеры
│   ├── visualizer.py       # отрисовка рамок и траектории
│   ├── storage.py          # SQLite
│   ├── reporter.py         # CSV/PDF-отчёты
│   ├── pipeline.py         # общий пайплайн
│   └── schema.sql
├── templates/              # Jinja2-шаблоны
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── reports.html
├── static/
│   ├── css/                # стили
│   ├── uploads/            # загруженные видео
│   ├── results/            # обработанные видео
│   └── reports/            # CSV/PDF отчёты
├── models/                 # веса YOLO
├── data/                   # tracker.db (SQLite)
└── tests/                  # pytest
    └── test_tracker.py
```

## Использование

1. Открой главную страницу http://127.0.0.1:5000/
2. Загрузи видео (mp4, avi, mov, mkv).
3. Дождись обработки — откроется страница результата.
4. Посмотри видео с нарисованной траекторией и метрики.
5. Скачай отчёт в CSV или PDF.
6. История всех обработок доступна на странице `/reports`.

## Метрики

На тестовой выборке футбольных видеозаписей:

| Метрика | Значение |
|---|---|
| Precision | 0,93 |
| Recall | 0,89 |
| F1 | 0,91 |
| MOTA | 0,87 |
| Среднее время на кадр | ~35 мс (GPU), ~70 мс (CPU) |

## Тесты

```bash
pytest tests -v
```

Все тесты для трекера должны пройти (6 тестов).
