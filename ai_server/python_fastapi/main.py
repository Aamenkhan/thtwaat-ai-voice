import asyncio
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("thtwaat")

# ---------------------------------------------------------------------------
# Paths — works regardless of cwd
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).resolve().parent.parent   # ai_server/
STATIC_DIR = BASE_DIR / "static"
TMPL_DIR   = BASE_DIR.parent / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "images").mkdir(exist_ok=True)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ---------------------------------------------------------------------------
# Safe module loader
# ---------------------------------------------------------------------------
def _load(name: str):
    try:
        m = __import__(name)
        logger.info("loaded: %s", name)
        return m
    except Exception as e:
        logger.warning("skipped %s — %s", name, e)
        return None

research_engine   = _load("research_engine")
deep_script       = _load("deep_script")
voice_engine      = _load("voice_engine")
image_generator   = _load("image_generator")
video_generator   = _load("video_generator")
ai_recommendation = _load("ai_recommendation")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Thtwaat AI starting …")
    yield

app = FastAPI(title="Thtwaat AI Voice", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Static files — skip if dir somehow vanished
try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception as e:
    logger.warning("Static mount skipped: %s", e)

# Jinja2 — optional
_templates = None
try:
    if TMPL_DIR.exists():
        from fastapi.templating import Jinja2Templates
        _templates = Jinja2Templates(directory=str(TMPL_DIR))
except Exception:
    pass

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    topic: str    = Field(..., min_length=1, max_length=500)
    language: str = Field(default="ar")

class ScriptRequest(BaseModel):
    research_data: str = Field(..., min_length=1)
    style: str         = Field(default="educational")

class VoiceRequest(BaseModel):
    script:       str  = Field(..., min_length=1)
    age:          str  = Field(default="young_adult")
    gender:       str  = Field(default="neutral")
    reduce_noise: bool = Field(default=True)

class VideoRequest(BaseModel):
    script:     str       = Field(..., min_length=1)
    voice_path: str       = Field(...)
    image_urls: List[str] = Field(default_factory=list)

# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return JSONResponse({"status": "API working", "version": "2.0.0"})

@app.get("/health")
async def health():
    return JSONResponse({
        "status": "ok",
        "modules": {
            "research_engine":   research_engine   is not None,
            "deep_script":       deep_script       is not None,
            "voice_engine":      voice_engine      is not None,
            "image_generator":   image_generator   is not None,
            "video_generator":   video_generator   is not None,
            "ai_recommendation": ai_recommendation is not None,
        },
    })

@app.get("/dashboard")
async def dashboard(request: Request):
    if _templates:
        return _templates.TemplateResponse("dashboard.html", {"request": request})
    return JSONResponse({"page": "dashboard", "templates": "unavailable"})

@app.get("/analytics")
async def analytics(request: Request):
    if _templates:
        return _templates.TemplateResponse("analytics.html", {"request": request})
    return JSONResponse({"page": "analytics", "templates": "unavailable"})

@app.get("/marketplace")
async def marketplace(request: Request):
    if _templates:
        return _templates.TemplateResponse("marketplace.html", {"request": request})
    return JSONResponse({"page": "marketplace", "templates": "unavailable"})

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.post("/api/research")
async def api_research(req: ResearchRequest):
    if not research_engine:
        raise HTTPException(503, "research_engine unavailable")
    try:
        data = await asyncio.to_thread(research_engine.run, req.topic, req.language)
        return JSONResponse({"status": "ok", "data": data})
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/script")
async def api_script(req: ScriptRequest):
    if not deep_script:
        raise HTTPException(503, "deep_script unavailable")
    try:
        script = await asyncio.to_thread(deep_script.generate, req.research_data, req.style)
        return JSONResponse({"status": "ok", "script": script})
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/voice")
async def api_voice(req: VoiceRequest):
    if not voice_engine:
        raise HTTPException(503, "voice_engine unavailable")
    try:
        name = f"voice_{uuid.uuid4().hex}.wav"
        path = str(STATIC_DIR / name)
        await asyncio.to_thread(
            voice_engine.synthesize_advanced,
            text=req.script,
            output_path=path,
            language="hi",
            age=req.age,
            gender=req.gender,
            reduce_noise=req.reduce_noise,
        )
        return JSONResponse({"status": "ok", "output_path": f"/static/{name}"})
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/generate-video")
async def api_generate_video(req: VideoRequest):
    if not video_generator:
        raise HTTPException(503, "video_generator unavailable")
    try:
        audio_path  = str(STATIC_DIR / Path(req.voice_path).name)
        image_paths: List[str] = []
        if req.image_urls:
            import requests as _r
            for i, url in enumerate(req.image_urls):
                dest = str(STATIC_DIR / "images" / f"img_{uuid.uuid4().hex[:6]}_{i}.jpg")
                try:
                    r = _r.get(url, timeout=10)
                    r.raise_for_status()
                    Path(dest).write_bytes(r.content)
                    image_paths.append(dest)
                except Exception:
                    logger.warning("Could not fetch: %s", url)
        video_path = await asyncio.to_thread(
            video_generator.assemble, req.script, audio_path, image_paths or None
        )
        if not video_path:
            raise HTTPException(500, "Video assembly failed")
        return JSONResponse({"status": "ok", "video_path": video_path})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/recommendations")
async def api_recommendations(context: str = "general"):
    if not ai_recommendation:
        raise HTTPException(503, "ai_recommendation unavailable")
    try:
        recs = await asyncio.to_thread(ai_recommendation.get_recommendations, context)
        return JSONResponse({"status": "ok", "recommendations": recs})
    except Exception as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
_jobs: Dict[str, Dict[str, Any]] = {}

def _run_pipeline(job_id: str, topic: str, language: str):
    _jobs[job_id]["status"] = "running"
    try:
        _jobs[job_id]["step"] = "research"
        research_data = (
            research_engine.run(topic, language) if research_engine else f"Placeholder: {topic}"
        )
        _jobs[job_id]["step"] = "script"
        script = deep_script.generate(research_data) if deep_script else research_data

        _jobs[job_id]["step"] = "voice"
        voice_name = f"voice_{job_id}.wav"
        if voice_engine:
            voice_engine.synthesize_advanced(
                script, language=language,
                output_path=str(STATIC_DIR / voice_name), reduce_noise=True,
            )

        _jobs[job_id]["step"] = "images"
        images = image_generator.generate(script, 3) if image_generator else []

        _jobs[job_id].update({
            "status": "done", "step": "complete",
            "script": script, "images": images,
            "voice_path": f"/static/{voice_name}",
        })
    except Exception as e:
        logger.exception("Pipeline %s failed", job_id)
        _jobs[job_id].update({"status": "error", "detail": str(e)})

@app.post("/api/pipeline")
async def api_pipeline(req: ResearchRequest, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "step": "starting", "topic": req.topic}
    bg.add_task(_run_pipeline, job_id, req.topic, req.language)
    return JSONResponse({"job_id": job_id, "status": "queued"})

@app.get("/api/pipeline/{job_id}")
async def api_pipeline_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return JSONResponse(job)

# ---------------------------------------------------------------------------
# Flutter multipart compat
# ---------------------------------------------------------------------------
@app.post("/api/generate")
async def api_generate(text: str = Form(None), voice: UploadFile = File(None)):
    if not text or not voice:
        return JSONResponse({"error": "Missing text or voice file"}, status_code=400)
    if not voice_engine:
        return JSONResponse({"error": "TTS engine unavailable"}, status_code=503)
    spk  = str(STATIC_DIR / f"spk_{uuid.uuid4().hex}.wav")
    name = f"voice_{uuid.uuid4().hex}.wav"
    out  = str(STATIC_DIR / name)
    try:
        Path(spk).write_bytes(await voice.read())
        voice_engine.synthesize_advanced(
            text=text, output_path=out, speaker_wav=spk, language="hi", reduce_noise=True,
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        if os.path.exists(spk):
            os.remove(spk)
    return FileResponse(out, filename=name, media_type="audio/wav")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
