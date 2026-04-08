"""
main.py – Cleaned production-ready FastAPI entry point for thtwaat-ai-voice
Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging – structured
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("thtwaat")

# ---------------------------------------------------------------------------
# Optional module imports – fail gracefully
# ---------------------------------------------------------------------------
def _try_import(module_name: str):
    try:
        mod = __import__(module_name)
        logger.info("Loaded module: %s", module_name)
        return mod
    except ImportError as exc:
        logger.warning("Module '%s' not available: %s", module_name, exc)
        return None

research_engine   = _try_import("research_engine")
deep_script       = _try_import("deep_script")
voice_engine      = _try_import("voice_engine")
image_generator   = _try_import("image_generator")
video_generator   = _try_import("video_generator")
ai_recommendation = _try_import("ai_recommendation")

# ---------------------------------------------------------------------------
# Lifespan – startup / shutdown hooks
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("static/images", exist_ok=True)
    logger.info("Starting thtwaat-ai-voice engine …")
    yield
    logger.info("Shutting down thtwaat-ai-voice engine …")

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Thtwaat AI Voice",
    version="1.1.0",
    lifespan=lifespan,
)

STATIC_DIR = Path("static")
TEMPLATES_DIR = Path("templates")

if not STATIC_DIR.exists():
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default="ar")

class ScriptRequest(BaseModel):
    research_data: str = Field(..., min_length=1)
    style: str = Field(default="educational")

class VoiceRequest(BaseModel):
    script: str = Field(..., min_length=1)
    voice_id: str = Field(default="default")
    age: str = Field(default="young_adult") # kid, teen, young_adult, senior
    gender: str = Field(default="neutral") # male, female, neutral
    reduce_noise: bool = Field(default=True)

# ---------------------------------------------------------------------------
# Routes – Dashboard
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/marketplace", response_class=HTMLResponse)
async def marketplace(request: Request):
    return templates.TemplateResponse("marketplace.html", {"request": request})

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "modules": {
            "research_engine":  research_engine is not None,
            "deep_script":      deep_script is not None,
            "voice_engine":     voice_engine is not None,
            "image_generator":  image_generator is not None,
            "video_generator":  video_generator is not None,
            "ai_recommendation": ai_recommendation is not None,
        },
    }

@app.get("/api/recommendations")
async def get_market_recommendations(context: str = "general"):
    if not ai_recommendation: raise HTTPException(503, "Recommendation engine unavailable")
    try:
        recommendations = await asyncio.to_thread(ai_recommendation.get_recommendations, context)
        return {"status": "ok", "recommendations": recommendations}
    except Exception as exc:
        raise HTTPException(500, str(exc))

# ---------------------------------------------------------------------------
# Routes – Pipeline steps
# ---------------------------------------------------------------------------
@app.post("/api/research")
async def research(req: ResearchRequest):
    if not research_engine: raise HTTPException(503, "research_engine unavailable")
    try:
        result = await asyncio.to_thread(research_engine.run, req.topic, req.language)
        return {"status": "ok", "data": result}
    except Exception as exc:
        raise HTTPException(500, str(exc))

@app.post("/api/script")
async def generate_script(req: ScriptRequest):
    if not deep_script: raise HTTPException(503, "deep_script unavailable")
    try:
        result = await asyncio.to_thread(deep_script.generate, req.research_data, req.style)
        return {"status": "ok", "script": result}
    except Exception as exc:
        raise HTTPException(500, str(exc))

@app.post("/api/voice")
async def generate_voice(req: VoiceRequest):
    if not voice_engine: raise HTTPException(503, "voice_engine unavailable")
    try:
        if voice_engine:
            output_name = f"voice_{uuid.uuid4()}.wav"
            output_path = STATIC_DIR / output_name
            # Use synthesize_advanced for micro-level control
            await asyncio.to_thread(
                voice_engine.synthesize_advanced,
                text=req.script,
                output_path=str(output_path),
                speaker_wav="speaker.wav",
                language="hi",
                age=req.age,
                gender=req.gender,
                reduce_noise=req.reduce_noise
            )
            return {"status": "ok", "output_path": f"/static/{output_name}"}
        else:
            return {"status": "mock", "output_path": "/static/mock_voice.wav"}
    except Exception as exc:
        raise HTTPException(500, str(exc))

# ---------------------------------------------------------------------------
# Full pipeline – fire-and-forget via BackgroundTasks
# ---------------------------------------------------------------------------
_job_store: Dict[str, Dict] = {}

def _run_full_pipeline(job_id: str, topic: str, language: str):
    _job_store[job_id]["status"] = "running"
    try:
        # 1. Research
        _job_store[job_id]["step"] = "research"
        research_data = research_engine.run(topic, language) if research_engine else f"Topic info for {topic}"
        
        # 2. Script
        _job_store[job_id]["step"] = "script"
        script = deep_script.generate(research_data) if deep_script else research_data
        
        # 3. Voice
        _job_store[job_id]["step"] = "voice"
        voice_filename = f"voice_{job_id}.wav"
        voice_path = str(STATIC_DIR / voice_filename)
        if voice_engine:
            voice_engine.synthesize_advanced(
                script, 
                language=language, 
                output_path=voice_path,
                # In basic pipeline, use defaults for age/gender
                reduce_noise=True
            )
        
        # 4. Images (Internet)
        _job_store[job_id]["step"] = "images"
        image_urls = image_generator.generate(script, 3) if image_generator else []
        
        # 5. Finalize (Video Generation Disabled)
        _job_store[job_id].update({
            "status": "done",
            "step": "complete",
            "script": script,
            "images": image_urls,
            "voice_path": f"/static/{voice_filename}"
        })
        logger.info("Pipeline %s complete (Ready: Script, Voice, Images).", job_id)

    except Exception as exc:
        logger.exception("Pipeline %s failed", job_id)
        _job_store[job_id].update({"status": "error", "detail": str(exc)})

@app.post("/api/pipeline")
async def full_pipeline(req: ResearchRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _job_store[job_id] = {"status": "queued", "step": "starting", "topic": req.topic}
    background_tasks.add_task(_run_full_pipeline, job_id, req.topic, req.language)
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/pipeline/{job_id}")
async def pipeline_status(job_id: str):
    job = _job_store.get(job_id)
    if not job: raise HTTPException(404, "Job not found")
    return job

# ---------------------------------------------------------------------------
# Flutter API Compat (/api/generate)
# ---------------------------------------------------------------------------
@app.post("/api/generate")
async def api_generate(text: str = Form(None), voice: UploadFile = File(None)):
    if not text or not voice: return {"error": "Missing data"}

    speaker_file = f"speaker_{uuid.uuid4()}.wav"
    with open(speaker_file, "wb") as f: f.write(await voice.read())

    output_name = f"voice_{uuid.uuid4()}.wav"
    output_path = STATIC_DIR / output_name

    try:
        if voice_engine:
            voice_engine.synthesize_advanced(
                text=text,
                output_path=str(output_path),
                speaker_wav=speaker_file,
                language="hi",
                reduce_noise=True # Auto enable for Flutter uploads
            )
            # Cleanup temp speaker file
            if os.path.exists(speaker_file): os.remove(speaker_file)
        else:
            return {"error": "TTS Engine not available"}
    except Exception as e:
        return {"error": str(e)}

    return FileResponse(output_path, filename=output_name)

# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)