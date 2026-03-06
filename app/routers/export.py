from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import TEMP_DIR
from app.models import ExportRequest
from app.services.pdf import generate_pdf

router = APIRouter()


@router.post("/export")
async def export_pdf(req: ExportRequest):
    job_dir = TEMP_DIR / req.job_id
    if not job_dir.exists():
        raise HTTPException(404, f"Job {req.job_id} not found. It may have expired.")

    try:
        pdf_path = generate_pdf(req.job_id, req.report_data)
    except Exception as e:
        raise HTTPException(500, f"PDF generation failed: {str(e)}")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"incident-report-{req.job_id[:8]}.pdf",
    )
