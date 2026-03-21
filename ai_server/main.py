"""
main.py – Production-ready FastAPI entry point for thtwaat-ai-voice
Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging – structured, goes to stdout so Render captures it
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("thtwaat")

# ---------------------------------------------------------------------------
# Optional module imports – fail gracefully so the server still starts
# ---------------------------------------------------------------------------
def _try_import(module_name: str):
    try:
        mod = __import__(module_name)
        logger.info("Loaded module: %s", module_name)
        return mod
    except ImportError as exc:
        logger.warning("Module '%s' not available: %s", module_name, exc)
        return None

research_engine  = _try_import("research_engine")
deep_script      = _try_import("deep_script")
voice_engine     = _try_import("voice_engine")
image_generator  = _try_import("image_generator")
video_generator  = _try_import("video_generator")

# ---------------------------------------------------------------------------
# Lifespan – startup / shutdown hooks
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting thtwaat-ai-voice …")
    # Add any heavy one-time init here (model loading, DB pool, etc.)
    yield
    logger.info("Shutting down thtwaat-ai-voice …")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Thtwaat AI Voice",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Static files & templates
# ---------------------------------------------------------------------------
STATIC_DIR = Path("static")
TEMPLATES_DIR = Path("templates")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# Global exception handler – no more naked 500s
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

# ---------------------------------------------------------------------------
# Helper: safe subprocess runner
# ---------------------------------------------------------------------------
def run_subprocess(cmd: list[str], timeout: int = 120) -> dict[str, Any]:
    """
    Run an external command safely (no shell=True).
    Returns {"returncode": int, "stdout": str, "stderr": str}.
    Raises RuntimeError on timeout or non-zero exit.
    """
    logger.info("Running subprocess: %s", cmd)
    try:
        result = subprocess.run(
            cmd,                    # list – never shell=True
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,            # we handle non-zero ourselves
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Subprocess timed out after {timeout}s: {cmd}") from exc
    except FileNotFoundError as exc:
        raise RuntimeError(f"Executable not found: {cmd[0]}") from exc

    if result.returncode != 0:
        logger.error("Subprocess failed (rc=%d): %s", result.returncode, result.stderr)
        raise RuntimeError(
            f"Subprocess exited {result.returncode}: {result.stderr.strip()}"
        )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }

# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default="ar", pattern=r"^[a-z]{2}$")

class ScriptRequest(BaseModel):
    research_data: str = Field(..., min_length=1)
    style: str = Field(default="educational")

class VoiceRequest(BaseModel):
    script: str = Field(..., min_length=1)
    voice_id: str = Field(default="default")

class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    count: int = Field(default=1, ge=1, le=10)

class VideoRequest(BaseModel):
    script: str = Field(..., min_length=1)
    voice_path: str = Field(default="")
    image_paths: list[str] = Field(default_factory=list)

# ---------------------------------------------------------------------------
# Routes – Dashboard
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health():
    """Render health-check endpoint."""
    return {
        "status": "ok",
        "modules": {
            "research_engine":  research_engine is not None,
            "deep_script":      deep_script is not None,
            "voice_engine":     voice_engine is not None,
            "image_generator":  image_generator is not None,
            "video_generator":  video_generator is not None,
        },
    }

# ---------------------------------------------------------------------------
# Routes – Pipeline steps
# ---------------------------------------------------------------------------
@app.post("/api/research")
async def research(req: ResearchRequest):
    if research_engine is None:
        raise HTTPException(503, "research_engine module not available")
    try:
        result = await asyncio.to_thread(
            research_engine.run, req.topic, req.language
        )
        return {"status": "ok", "data": result}
    except Exception as exc:
        logger.exception("Research failed")
        raise HTTPException(500, str(exc)) from exc


@app.post("/api/script")
async def generate_script(req: ScriptRequest):
    if deep_script is None:
        raise HTTPException(503, "deep_script module not available")
    try:
        result = await asyncio.to_thread(
            deep_script.generate, req.research_data, req.style
        )
        return {"status": "ok", "script": result}
    except Exception as exc:
        logger.exception("Script generation failed")
        raise HTTPException(500, str(exc)) from exc


@app.post("/api/voice")
async def generate_voice(req: VoiceRequest, background_tasks: BackgroundTasks):
    if voice_engine is None:
        raise HTTPException(503, "voice_engine module not available")
    try:
        # Heavy TTS – run in thread pool so the event loop stays free
        output_path = await asyncio.to_thread(
            voice_engine.synthesize, req.script, req.voice_id
        )
        return {"status": "ok", "output_path": str(output_path)}
    except Exception as exc:
        logger.exception("Voice generation failed")
        raise HTTPException(500, str(exc)) from exc


@app.post("/api/images")
async def generate_images(req: ImageRequest):
    if image_generator is None:
        raise HTTPException(503, "image_generator module not available")
    try:
        paths = await asyncio.to_thread(
            image_generator.generate, req.prompt, req.count
        )
        return {"status": "ok", "image_paths": paths}
    except Exception as exc:
        logger.exception("Image generation failed")
        raise HTTPException(500, str(exc)) from exc


@app.post("/api/video")
async def generate_video(req: VideoRequest):
    if video_generator is None:
        raise HTTPException(503, "video_generator module not available")
    try:
        output_path = await asyncio.to_thread(
            video_generator.assemble,
            req.script,
            req.voice_path,
            req.image_paths,
        )
        return {"status": "ok", "video_path": str(output_path)}
    except Exception as exc:
        logger.exception("Video generation failed")
        raise HTTPException(500, str(exc)) from exc


# ---------------------------------------------------------------------------
# Full pipeline – fire-and-forget via BackgroundTasks
# ---------------------------------------------------------------------------
_job_store: dict[str, dict] = {}   # in-memory; swap for Redis on Render

def _run_full_pipeline(job_id: str, topic: str, language: str):
    _job_store[job_id] = {"status": "running", "step": "research"}
    try:
        research_data = research_engine.run(topic, language) if research_engine else ""
        _job_store[job_id]["step"] = "script"

        script = deep_script.generate(research_data) if deep_script else ""
        _job_store[job_id]["step"] = "voice"

        voice_path = voice_engine.synthesize(script) if voice_engine else ""
        _job_store[job_id]["step"] = "images"

        image_paths = image_generator.generate(script, 5) if image_generator else []
        _job_store[job_id]["step"] = "video"

        video_path = (
            video_generator.assemble(script, voice_path, image_paths)
            if video_generator else ""
        )

        _job_store[job_id] = {
            "status": "done",
            "video_path": str(video_path),
        }
        logger.info("Pipeline %s complete → %s", job_id, video_path)

    except Exception as exc:
        logger.exception("Pipeline %s failed", job_id)
        _job_store[job_id] = {"status": "error", "detail": str(exc)}


@app.post("/api/pipeline")
async def full_pipeline(req: ResearchRequest, background_tasks: BackgroundTasks):
    import uuid
    job_id = str(uuid.uuid4())
    _job_store[job_id] = {"status": "queued"}
    background_tasks.add_task(_run_full_pipeline, job_id, req.topic, req.language)
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/pipeline/{job_id}")
async def pipeline_status(job_id: str):
    job = _job_store.get(job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    return job


# ---------------------------------------------------------------------------
# Dev entry point (production uses uvicorn main:app directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,   # never True in production
        log_level="info",
    )