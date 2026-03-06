from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

MAX_FILE_SIZE_MB = 500
MAX_DURATION_SECONDS = 300  # 5 minutes
MAX_FRAMES_TO_MODEL = 20
FRAME_MAX_WIDTH = 1024
ACCEPTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi"}
CLEANUP_TIMEOUT_SECONDS = 3600  # 1 hour
