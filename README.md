# Security Camera Incident Report Generator

Upload security camera footage, get a structured incident report with AI analysis and PDF export.

Turns a 30+ minute manual process into under 2 minutes. Upload a clip, extract key frames automatically, analyze with Claude's vision API, review and edit the report, then download as a professional PDF.

## Features

- **Video upload** — MP4, MOV, MKV, AVI (up to 5 minutes)
- **Smart frame extraction** — 1fps baseline with motion-based selection (top 20 frames)
- **AI analysis** — Claude classifies incidents (Theft / Trespassing), generates timeline, subject description, and recommended actions
- **Report preview** — Inline editing of all fields before export
- **PDF export** — Professional report with screenshots, timeline, and classification

## Quick Start

### Prerequisites

- Python 3.12+
- [ffmpeg](https://ffmpeg.org/download.html)
- An [Anthropic API key](https://console.anthropic.com/)

### Run locally

```bash
git clone https://github.com/mattsafaii/incident-report-generator.git
cd incident-report-generator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000, upload a video, enter your API key, and click **Analyze with Claude**.

### Run with Docker

```bash
docker compose up -d
```

The app will be available at http://localhost:8000.

## Deploy with Kamal

```bash
# 1. Configure .kamal/secrets with your server IP and Docker Hub token
cp .kamal/secrets.example .kamal/secrets

# 2. Deploy
kamal setup
```

## How It Works

1. **Upload** a video clip (30s–5min)
2. **Frame extraction** — ffmpeg extracts frames at 1fps, then motion scoring selects the most relevant frames
3. **AI analysis** — Selected frames are sent to Claude with a structured prompt that returns classification, timeline, and descriptions as JSON
4. **Preview & edit** — The report renders in-browser with all text fields editable
5. **Export** — Download as a formatted PDF with screenshots and timestamps

## Tech Stack

- **Backend**: Python, FastAPI
- **Frame extraction**: ffmpeg
- **AI**: Anthropic Claude (claude-sonnet-4-20250514) with vision
- **PDF**: WeasyPrint + Jinja2
- **Frontend**: Vanilla HTML/CSS/JS

## Privacy

- Your API key is stored in your browser's localStorage only — never sent to the server for storage
- All video processing happens on your machine (or your server)
- No telemetry, no analytics, no external calls except to the AI provider you configure

## License

MIT
