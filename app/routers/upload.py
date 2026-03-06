import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ACCEPTED_EXTENSIONS, MAX_FILE_SIZE_MB, TEMP_DIR
from app.models import FrameMetadata, UploadResponse
from app.services.motion import compute_motion_scores, select_frames
from app.services.video import extract_frames_1fps, validate_video

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ACCEPTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format: {suffix}")

    # Create job directory
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Stream upload to disk in chunks
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

    # Validate video duration
    try:
        duration = validate_video(video_path)
    except ValueError as e:
        shutil.rmtree(job_dir)
        raise HTTPException(400, str(e))

    # Extract frames at 1fps
    try:
        frame_count = extract_frames_1fps(video_path, job_dir)
    except RuntimeError as e:
        shutil.rmtree(job_dir)
        raise HTTPException(500, str(e))

    if frame_count == 0:
        shutil.rmtree(job_dir)
        raise HTTPException(400, "No frames could be extracted from this video")

    # Motion scoring and selection
    scored = compute_motion_scores(job_dir)
    annotated = select_frames(scored)

    # Build response
    frames_meta = []
    for i, (path, score, selected) in enumerate(annotated):
        frame_id = path.stem
        timestamp_seconds = float(i)
        minutes, secs = divmod(int(timestamp_seconds), 60)
        hours, minutes = divmod(minutes, 60)
        ts_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        frames_meta.append(FrameMetadata(
            frame_id=frame_id,
            timestamp=ts_str,
            timestamp_seconds=timestamp_seconds,
            motion_score=round(score, 2),
            selected=selected,
            url=f"/api/frames/{job_id}/{frame_id}",
        ))

    selected_count = sum(1 for f in frames_meta if f.selected)

    # Delete source video to save disk space
    video_path.unlink(missing_ok=True)

    return UploadResponse(
        job_id=job_id,
        duration_seconds=round(duration, 2),
        total_frames_extracted=frame_count,
        selected_frame_count=selected_count,
        frames=frames_meta,
    )
