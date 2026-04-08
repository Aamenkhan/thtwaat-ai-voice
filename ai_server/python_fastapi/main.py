import asyncio, logging, os, sys, uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("thtwaat")

BASE   = Path(__file__).resolve().parent.parent
STATIC = BASE / "static"
TMPL   = BASE.parent / "templates"

STATIC.mkdir(parents=True, exist_ok=True)
(STATIC / "images").mkdir(exist_ok=True)

if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

def _load(n):
    try:
        m = __import__(n); log.info("ok: %s", n); return m
    except Exception as e:
        log.warning("skip: %s — %s", n, e); return None

re_mod = _load("research_engine")
ds_mod = _load("deep_script")
vo_mod = _load("voice_engine")
ig_mod = _load("image_generator")
vg_mod = _load("video_generator")
ai_mod = _load("ai_recommendation")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting…"); yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

try:
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
except Exception as e:
    log.warning("static skip: %s", e)

_tpl = None
try:
    if TMPL.exists():
        from fastapi.templating import Jinja2Templates
        _tpl = Jinja2Templates(directory=str(TMPL))
except Exception:
    pass

class RR(BaseModel):
    topic: str     = Field(..., min_length=1, max_length=500)
    language: str  = Field(default="ar")

class SR(BaseModel):
    research_data: str = Field(..., min_length=1)
    style: str         = Field(default="educational")

class VoR(BaseModel):
    script: str        = Field(..., min_length=1)
    age: str           = Field(default="young_adult")
    gender: str        = Field(default="neutral")
    reduce_noise: bool = Field(default=True)

class ViR(BaseModel):
    script: str            = Field(..., min_length=1)
    voice_path: str        = Field(...)
    image_urls: List[str]  = Field(default_factory=list)

@app.get("/")
def home():
    return {"message": "API working 🚀"}

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "modules": {
        "research": re_mod is not None, "script": ds_mod is not None,
        "voice":    vo_mod is not None, "image":  ig_mod is not None,
        "video":    vg_mod is not None, "ai":     ai_mod is not None,
    }})

def _page(req, tpl):
    if _tpl:
        return _tpl.TemplateResponse(tpl, {"request": req})
    return JSONResponse({"page": tpl})

@app.get("/dashboard")
async def dashboard(request: Request): return _page(request, "dashboard.html")
@app.get("/analytics")
async def analytics(request: Request): return _page(request, "analytics.html")
@app.get("/marketplace")
async def marketplace(request: Request): return _page(request, "marketplace.html")

@app.post("/api/research")
async def api_research(req: RR):
    if not re_mod: raise HTTPException(503, "research_engine unavailable")
    try:
        data = await asyncio.to_thread(re_mod.run, req.topic, req.language)
        return JSONResponse({"status": "ok", "data": data})
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/script")
async def api_script(req: SR):
    if not ds_mod: raise HTTPException(503, "deep_script unavailable")
    try:
        s = await asyncio.to_thread(ds_mod.generate, req.research_data, req.style)
        return JSONResponse({"status": "ok", "script": s})
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/voice")
async def api_voice(req: VoR):
    if not vo_mod: raise HTTPException(503, "voice_engine unavailable")
    try:
        n = f"voice_{uuid.uuid4().hex}.wav"
        await asyncio.to_thread(vo_mod.synthesize_advanced, text=req.script,
            output_path=str(STATIC/n), language="hi",
            age=req.age, gender=req.gender, reduce_noise=req.reduce_noise)
        return JSONResponse({"status": "ok", "output_path": f"/static/{n}"})
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/generate-video")
async def api_video(req: ViR):
    if not vg_mod: raise HTTPException(503, "video_generator unavailable")
    try:
        audio = str(STATIC / Path(req.voice_path).name)
        imgs: List[str] = []
        if req.image_urls:
            import requests as _r
            for i, url in enumerate(req.image_urls):
                dest = str(STATIC/"images"/f"img_{uuid.uuid4().hex[:6]}_{i}.jpg")
                try:
                    r = _r.get(url, timeout=10); r.raise_for_status()
                    Path(dest).write_bytes(r.content); imgs.append(dest)
                except Exception: pass
        vp = await asyncio.to_thread(vg_mod.assemble, req.script, audio, imgs or None)
        if not vp: raise HTTPException(500, "assembly failed")
        return JSONResponse({"status": "ok", "video_path": vp})
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@app.get("/api/recommendations")
async def api_recs(context: str = "general"):
    if not ai_mod: raise HTTPException(503, "ai_recommendation unavailable")
    try:
        r = await asyncio.to_thread(ai_mod.get_recommendations, context)
        return JSONResponse({"status": "ok", "recommendations": r})
    except Exception as e: raise HTTPException(500, str(e))

_jobs: Dict[str, Dict[str, Any]] = {}

def _pipeline(job_id: str, topic: str, lang: str):
    _jobs[job_id]["status"] = "running"
    try:
        _jobs[job_id]["step"] = "research"
        rd = re_mod.run(topic, lang) if re_mod else f"Placeholder: {topic}"
        _jobs[job_id]["step"] = "script"
        sc = ds_mod.generate(rd) if ds_mod else rd
        _jobs[job_id]["step"] = "voice"
        vn = f"voice_{job_id}.wav"
        if vo_mod:
            vo_mod.synthesize_advanced(sc, language=lang,
                output_path=str(STATIC/vn), reduce_noise=True)
        _jobs[job_id]["step"] = "images"
        imgs = ig_mod.generate(sc, 3) if ig_mod else []
        _jobs[job_id].update({"status": "done", "step": "complete", "script": sc,
                               "images": imgs, "voice_path": f"/static/{vn}"})
    except Exception as e:
        _jobs[job_id].update({"status": "error", "detail": str(e)})

@app.post("/api/pipeline")
async def api_pipeline(req: RR, bg: BackgroundTasks):
    jid = str(uuid.uuid4())
    _jobs[jid] = {"status": "queued", "step": "starting", "topic": req.topic}
    bg.add_task(_pipeline, jid, req.topic, req.language)
    return JSONResponse({"job_id": jid, "status": "queued"})

@app.get("/api/pipeline/{job_id}")
async def api_status(job_id: str):
    j = _jobs.get(job_id)
    if not j: raise HTTPException(404, "not found")
    return JSONResponse(j)

@app.post("/api/generate")
async def api_generate(text: str = Form(None), voice: UploadFile = File(None)):
    if not text or not voice:
        return JSONResponse({"error": "missing text or voice"}, status_code=400)
    if not vo_mod:
        return JSONResponse({"error": "TTS unavailable"}, status_code=503)
    spk = str(STATIC / f"spk_{uuid.uuid4().hex}.wav")
    out = str(STATIC / f"voice_{uuid.uuid4().hex}.wav")
    try:
        Path(spk).write_bytes(await voice.read())
        vo_mod.synthesize_advanced(text=text, output_path=out,
            speaker_wav=spk, language="hi", reduce_noise=True)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        if os.path.exists(spk): os.remove(spk)
    return FileResponse(out, filename=Path(out).name, media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
