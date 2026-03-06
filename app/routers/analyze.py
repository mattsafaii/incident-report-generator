from fastapi import APIRouter, HTTPException

from app.config import TEMP_DIR
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.claude import analyze_frames
from app.services.motion import compute_motion_scores, select_frames

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    job_dir = TEMP_DIR / req.job_id
    if not job_dir.exists():
        raise HTTPException(404, f"Job {req.job_id} not found. It may have expired.")

    all_frames = sorted(job_dir.glob("frame_*.jpg"))
    if not all_frames:
        raise HTTPException(404, "No frames found for this job")

    # Re-derive selected frames (stateless approach)
    scored = compute_motion_scores(job_dir)
    annotated = select_frames(scored)

    selected_paths = []
    selected_timestamps = []
    for i, (path, _score, sel) in enumerate(annotated):
        if sel:
            selected_paths.append(path)
            minutes, secs = divmod(i, 60)
            hours, minutes = divmod(minutes, 60)
            selected_timestamps.append(f"{hours:02d}:{minutes:02d}:{secs:02d}")

    try:
        result = await analyze_frames(
            api_key=req.api_key,
            frame_paths=selected_paths,
            frame_timestamps=selected_timestamps,
            incident_type=req.incident_type,
            location=req.location,
            camera_id=req.camera_id,
        )
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise HTTPException(401, "Authentication failed. Check your API key.")
        raise HTTPException(502, f"AI analysis error: {error_msg}")

    return AnalyzeResponse(job_id=req.job_id, analysis=result)
