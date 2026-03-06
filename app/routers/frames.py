from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import TEMP_DIR

router = APIRouter()


@router.get("/frames/{job_id}/{frame_id}")
async def get_frame(job_id: str, frame_id: str):
    frame_path = TEMP_DIR / job_id / f"{frame_id}.jpg"
    if not frame_path.exists():
        raise HTTPException(404, "Frame not found")
    # Prevent directory traversal
    if not frame_path.resolve().is_relative_to(TEMP_DIR.resolve()):
        raise HTTPException(403, "Access denied")
    return FileResponse(frame_path, media_type="image/jpeg")
