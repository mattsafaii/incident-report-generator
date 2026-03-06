import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ACCEPTED_EXTENSIONS, MAX_FILE_SIZE_MB, TEMP_DIR
from app.models import UploadResponse
from app.services.video import validate_video

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ACCEPTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format: {suffix}")

    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    video_path = job_dir / f"source{suffix}"
    total_bytes = 0
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    try:
        with open(video_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    shutil.rmtree(job_dir)
                    raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB}MB limit")
                f.write(chunk)
    finally:
        await file.close()

    try:
        duration = validate_video(video_path)
    except ValueError as e:
        shutil.rmtree(job_dir)
        raise HTTPException(400, str(e))

    return UploadResponse(
        job_id=job_id,
        duration_seconds=round(duration, 2),
    )
