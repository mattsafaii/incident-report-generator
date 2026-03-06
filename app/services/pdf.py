import base64
import uuid
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.config import TEMP_DIR, TEMPLATES_DIR

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _frame_to_data_uri(frame_path: Path) -> str:
    with open(frame_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def generate_pdf(job_id: str, report_data: dict) -> Path:
    """Render report_data into a PDF. Returns path to generated PDF file."""
    job_dir = TEMP_DIR / job_id
    template = env.get_template("report.html")

    # Build screenshot data URIs from key_frame_indices
    screenshots = []
    key_indices = report_data.get("key_frame_indices", [])
    timeline = report_data.get("timeline", [])

    for idx in key_indices[:4]:  # Max 4 screenshots per PRD
        # Frames are 1-indexed on disk (frame_0001.jpg), indices are 0-based
        frame_path = job_dir / f"frame_{idx + 1:04d}.jpg"
        if frame_path.exists():
            # Find a caption from timeline or use generic
            caption = "Key frame"
            if idx < len(timeline):
                entry = timeline[idx]
                desc = entry.get("description", "") if isinstance(entry, dict) else ""
                if desc:
                    caption = desc

            minutes, secs = divmod(idx, 60)
            hours, minutes = divmod(minutes, 60)
            ts_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"

            screenshots.append({
                "data_uri": _frame_to_data_uri(frame_path),
                "timestamp": ts_str,
                "caption": caption,
            })

    report_id = str(uuid.uuid4())[:8].upper()
    html_content = template.render(
        report_id=report_id,
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        classification=report_data.get("classification", "Undetermined"),
        confidence=report_data.get("confidence", "Low"),
        incident_summary=report_data.get("incident_summary", ""),
        location=report_data.get("location"),
        camera_id=report_data.get("camera_id"),
        reporting_party=report_data.get("reporting_party"),
        timeline=report_data.get("timeline", []),
        screenshots=screenshots,
        subject_description=report_data.get("subject_description", ""),
        recommended_actions=report_data.get("recommended_actions", []),
    )

    pdf_path = job_dir / "report.pdf"
    HTML(string=html_content).write_pdf(str(pdf_path))
    return pdf_path
