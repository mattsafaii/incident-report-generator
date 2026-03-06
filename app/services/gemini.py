import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

from app.models import AnalysisResult

DESCRIBE_PROMPT = """You are a security camera footage analyst. Watch this video carefully and describe everything you observe in detail.

For each notable moment, provide:
- The approximate timestamp (HH:MM:SS)
- What is happening (actions, movements, interactions)
- Descriptions of all people visible (clothing, build, distinguishing features)
- Any vehicles, objects, or environmental details relevant to security

Be thorough and precise. Focus on facts — what you can actually see. Note entrances, exits, interactions with doors/windows/property, and any suspicious behavior.

Format your response as a chronological list of observations."""

REPORT_PROMPT = """You are a security incident report writer. Based on the following observations from security camera footage, produce a structured incident report in JSON format.

{context}

OBSERVATIONS:
{observations}

You MUST respond with valid JSON matching this exact schema:
{{
  "classification": "Theft | Trespassing | Vandalism | Suspicious Activity | Undetermined",
  "confidence": "High | Medium | Low",
  "incident_summary": "A narrative description of what occurred",
  "timeline": [
    {{"timestamp": "HH:MM:SS", "description": "What happened at this moment"}}
  ],
  "key_frame_indices": [0, 3, 7],
  "subject_description": "Physical description of persons/vehicles observed",
  "recommended_actions": ["Action 1", "Action 2"]
}}

Rules:
- classification must be exactly one of: Theft, Trespassing, Vandalism, Suspicious Activity, or Undetermined
- confidence must be exactly one of: High, Medium, or Low
- key_frame_indices are zero-based indices referring to approximate seconds in the video where the most important moments occur (2-4 indices)
- timeline entries should use timestamps from the observations
- Respond ONLY with the JSON object. No markdown, no explanation, no code fences."""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, handling markdown code fences."""
    text = text.strip()
    match = re.match(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def _wait_for_file(client: genai.Client, file_ref, timeout: int = 300) -> None:
    """Poll until an uploaded file is in ACTIVE state."""
    start = time.time()
    while time.time() - start < timeout:
        f = client.files.get(name=file_ref.name)
        if f.state == "ACTIVE":
            return
        if f.state == "FAILED":
            raise RuntimeError("Gemini file processing failed")
        time.sleep(2)
    raise RuntimeError(f"Gemini file processing timed out after {timeout}s")


async def analyze_video_gemini(
    api_key: str,
    video_path: Path,
    incident_type: str | None = None,
    location: str | None = None,
    camera_id: str | None = None,
) -> AnalysisResult:
    """Two-pass video analysis using Gemini."""
    client = genai.Client(api_key=api_key)

    # Upload video to Gemini
    file_ref = client.files.upload(file=str(video_path))
    _wait_for_file(client, file_ref)

    try:
        # Pass 1: Describe the video
        describe_response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[file_ref, DESCRIBE_PROMPT],
        )
        observations = describe_response.text

        # Pass 2: Structure into report
        context_parts = []
        if incident_type:
            context_parts.append(f"Suspected incident type: {incident_type}")
        if location:
            context_parts.append(f"Camera location: {location}")
        if camera_id:
            context_parts.append(f"Camera ID: {camera_id}")
        context = "\n".join(context_parts) if context_parts else "No additional context provided."

        report_prompt = REPORT_PROMPT.format(
            context=context,
            observations=observations,
        )

        report_response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=report_prompt,
        )

        parsed = _extract_json(report_response.text)
        return AnalysisResult(**parsed)

    finally:
        # Clean up uploaded file
        try:
            client.files.delete(name=file_ref.name)
        except Exception:
            pass
