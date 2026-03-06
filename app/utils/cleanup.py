import shutil
import time
from pathlib import Path

from app.config import CLEANUP_TIMEOUT_SECONDS, TEMP_DIR


def cleanup_expired_jobs():
    """Remove job directories older than CLEANUP_TIMEOUT_SECONDS."""
    if not TEMP_DIR.exists():
        return
    now = time.time()
    for job_dir in TEMP_DIR.iterdir():
        if job_dir.is_dir():
            age = now - job_dir.stat().st_mtime
            if age > CLEANUP_TIMEOUT_SECONDS:
                shutil.rmtree(job_dir, ignore_errors=True)
