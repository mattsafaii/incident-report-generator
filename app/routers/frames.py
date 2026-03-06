from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import TEMP_DIR
from app.models import ExtractFramesResponse, FrameMetadata
from app.services.motion import compute_motion_scores, select_frames
from app.services.video import extract_frames_1fps

router = APIRouter()


def _find_video(job_dir):
    for ext in (".mp4", ".mov", ".mkv", ".avi"):
        path = job_dir / f"source{ext}"
        if path.exists():
            return path
    return None


@router.post("/extract-frames/{job_id}", response_model=ExtractFramesResponse)
async def extract_frames(job_id: str):
    job_dir = TEMP_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(404, f"Job {job_id} not found. It may have expired.")

    # Skip if frames already extracted
    existing = sorted(job_dir.glob("frame_*.jpg"))
    if not existing:
        video_path = _find_video(job_dir)
        if not video_path:
            raise HTTPException(404, "Source video not found.")

        try:
            frame_count = extract_frames_1fps(video_path, job_dir)
        except RuntimeError as e:
            raise HTTPException(500, str(e))

        if frame_count == 0:
            raise HTTPException(400, "No frames could be extracted from this video")

    scored = compute_motion_scores(job_dir)
    annotated = select_frames(scored)

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

    return ExtractFramesResponse(
        job_id=job_id,
        total_frames_extracted=len(frames_meta),
        selected_frame_count=selected_count,
        frames=frames_meta,
    )


@router.get("/frames/{job_id}/{frame_id}")
async def get_frame(job_id: str, frame_id: str):
    frame_path = TEMP_DIR / job_id / f"{frame_id}.jpg"
    if not frame_path.exists():
        raise HTTPException(404, "Frame not found")
    if not frame_path.resolve().is_relative_to(TEMP_DIR.resolve()):
        raise HTTPException(403, "Access denied")
    return FileResponse(frame_path, media_type="image/jpeg")
