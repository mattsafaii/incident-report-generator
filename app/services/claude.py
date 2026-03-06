import json
import re
from pathlib import Path

from anthropic import Anthropic

from app.models import AnalysisResult
from app.utils.image import frame_to_base64

SYSTEM_PROMPT = """You are a security camera footage analyst. Analyze the provided security camera frames and produce a structured incident report in JSON format.

You MUST respond with valid JSON matching this exact schema:
{
  "classification": "Theft | Trespassing | Undetermined",
  "confidence": "High | Medium | Low",
  "incident_summary": "A narrative description of what occurred",
  "timeline": [
    {"timestamp": "HH:MM:SS", "description": "What happened at this moment"}
  ],
  "key_frame_indices": [0, 3, 7],
  "subject_description": "Physical description of persons/vehicles observed",
  "recommended_actions": ["Action 1", "Action 2"]
}

Rules:
- classification must be exactly one of: Theft, Trespassing, or Undetermined
- confidence must be exactly one of: High, Medium, or Low
- key_frame_indices are zero-based indices into the frames provided, selecting the 2-4 most important frames
- timeline entries should use the timestamps shown in the frame labels
- Respond ONLY with the JSON object. No markdown, no explanation, no code fences."""


def build_analysis_prompt(
    incident_type: str | None = None,
    location: str | None = None,
    camera_id: str | None = None,
) -> str:
    parts = ["Analyze these security camera frames in chronological order."]
    if incident_type:
        parts.append(f"The suspected incident type is: {incident_type}.")
    if location:
        parts.append(f"Camera location: {location}.")
    if camera_id:
        parts.append(f"Camera ID: {camera_id}.")
    parts.append("Provide your analysis as the specified JSON structure.")
    return " ".join(parts)


def _extract_json(text: str) -> dict:
    """Extract JSON from response, handling markdown code fences."""
    text = text.strip()
    # Strip markdown code fences if present
    match = re.match(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


async def analyze_frames(
    api_key: str,
    frame_paths: list[Path],
    frame_timestamps: list[str],
    incident_type: str | None = None,
    location: str | None = None,
    camera_id: str | None = None,
) -> AnalysisResult:
    """Send selected frames to Claude and return structured analysis."""
    client = Anthropic(api_key=api_key)

    # Build content blocks: interleaved image + timestamp label
    content_blocks: list[dict] = []
    for i, (frame_path, timestamp) in enumerate(zip(frame_paths, frame_timestamps)):
        b64 = frame_to_base64(frame_path)
        content_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": b64,
            },
        })
        content_blocks.append({
            "type": "text",
            "text": f"Frame {i} — Timestamp: {timestamp}",
        })

    # Final instruction text
    content_blocks.append({
        "type": "text",
        "text": build_analysis_prompt(incident_type, location, camera_id),
    })

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content_blocks}],
    )

    raw_text = response.content[0].text
    parsed = _extract_json(raw_text)
    return AnalysisResult(**parsed)
