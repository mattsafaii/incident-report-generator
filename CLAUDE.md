# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Security Camera Incident Report Generator — a FastAPI web app that accepts security camera video, extracts frames via ffmpeg, analyzes them with Claude's vision API, and exports PDF incident reports. Built for ZoneBrite.

## Commands

```bash
# Run dev server (requires .venv activated and ffmpeg installed)
source .venv/bin/activate
uvicorn app.main:app --reload

# Install dependencies
pip install -r requirements.txt

# Docker
docker compose up -d
```

No test suite exists yet.

## Architecture

**Pipeline flow:** Upload video → ffmpeg extracts frames at 1fps → motion scoring selects top 20 frames → Claude vision API analyzes frames → user reviews/edits report → WeasyPrint generates PDF.

**Backend (Python/FastAPI):**
- `app/main.py` — FastAPI app, mounts routers under `/api` and serves static files at `/`
- `app/config.py` — constants (max file size, duration, frame limits, paths)
- `app/models.py` — Pydantic request/response models
- `app/routers/` — API endpoints: `upload.py` (POST /api/upload), `analyze.py` (POST /api/analyze), `frames.py` (GET frame images), `export.py` (POST /api/export)
- `app/services/video.py` — ffmpeg wrapper: validation and 1fps frame extraction
- `app/services/motion.py` — motion scoring (pixel diff between consecutive frames) and temporal-spread frame selection
- `app/services/claude.py` — builds multimodal prompt with base64 frames, calls Claude API, parses JSON response into `AnalysisResult`
- `app/services/pdf.py` — Jinja2 template rendering + WeasyPrint PDF generation
- `app/templates/report.html` — Jinja2 HTML template for PDF output
- `app/utils/cleanup.py` — periodic cleanup of expired job directories (1hr TTL)

**Frontend (vanilla HTML/CSS/JS):**
- `static/` — single-page app with modular JS files (upload, analysis, report, export, config)
- API key stored in browser localStorage, never persisted server-side

**Job lifecycle:** Each upload creates a UUID job directory under `temp/`. Frames are stored as `frame_NNNN.jpg`. Source video is deleted after frame extraction. Jobs auto-expire after 1 hour.

## Key Details

- System dependency: `ffmpeg` must be installed (used via subprocess)
- System dependency: WeasyPrint requires native libs (libpango, libcairo, etc.) — see Dockerfile for the full list
- Claude model used: `claude-sonnet-4-20250514` (hardcoded in `app/services/claude.py`)
- Frame files are 1-indexed on disk (`frame_0001.jpg`) but 0-indexed in the API/analysis
- Motion scoring resizes frames to 320x240 grayscale for performance
- Deployment via Kamal 2 — config in `config/deploy.yml`, secrets in `.kamal/secrets`

## Milestones

### Completed

- **M1 — Core pipeline**: Upload → frame extraction → Anthropic backend → JSON output
- **M2 — Report generation**: JSON → PDF with screenshots
- **M3 — Frontend**: Upload UI + report preview + editing + PDF download

### Remaining

- **M4 — Multi-backend**: Add Ollama (local) and OpenAI-compatible API support. Add backend selector to the config panel. Detect if Ollama is running locally and list available vision models. Show quality warning when local models are selected.
- **M5 — Privacy layer**: Face and license plate blurring using OpenCV + YuNet (faces) / YOLO (plates). Runs locally before frames reach any external API. Per-session toggle (default OFF). Show blurring preview before submitting.
- **M6 — Packaging**: Docker Compose production setup, comprehensive setup docs, environment variable documentation.

## AI Prompt Tuning

The Claude system prompt lives in `app/services/claude.py`. Known areas for improvement:
- JSON output occasionally wrapped in markdown code fences (fallback stripping exists)
- Timeline granularity could be improved with real footage
- Subject descriptions could be more detailed
- Classification confidence calibration needs real-world testing
