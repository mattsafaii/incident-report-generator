import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR, TEMP_DIR
from app.routers import analyze, export, frames, upload
from app.utils.cleanup import cleanup_expired_jobs

app = FastAPI(title="Incident Report Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure temp dir exists
TEMP_DIR.mkdir(exist_ok=True)

# API routes (must be before static mount)
app.include_router(upload.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(frames.router, prefix="/api")
app.include_router(export.router, prefix="/api")

# Static files (catch-all, serves index.html at /)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.on_event("startup")
async def start_cleanup_loop():
    async def periodic_cleanup():
        while True:
            cleanup_expired_jobs()
            await asyncio.sleep(300)

    asyncio.create_task(periodic_cleanup())
