from pydantic import BaseModel
from typing import Optional


class FrameMetadata(BaseModel):
    frame_id: str
    timestamp: str
    timestamp_seconds: float
    motion_score: float
    selected: bool
    url: str


class UploadResponse(BaseModel):
    job_id: str
    duration_seconds: float


class ExtractFramesResponse(BaseModel):
    job_id: str
    total_frames_extracted: int
    selected_frame_count: int
    frames: list[FrameMetadata]


class AnalyzeRequest(BaseModel):
    job_id: str
    api_key: str
    provider: str = "gemini"  # "gemini" or "claude"
    incident_type: Optional[str] = None
    location: Optional[str] = None
    camera_id: Optional[str] = None


class TimelineEntry(BaseModel):
    timestamp: str
    description: str


class AnalysisResult(BaseModel):
    classification: str
    confidence: str
    incident_summary: str
    timeline: list[TimelineEntry]
    key_frame_indices: list[int]
    subject_description: str
    recommended_actions: list[str]


class AnalyzeResponse(BaseModel):
    job_id: str
    analysis: AnalysisResult


class ExportRequest(BaseModel):
    job_id: str
    report_data: dict
