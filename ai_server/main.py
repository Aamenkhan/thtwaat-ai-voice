from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import subprocess
import shutil
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ✅ Dashboard
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ✅ Generate Script
@app.post("/generate_script")
def generate_script(topic: str = Form(...)):
    try:
        subprocess.run(["python", "research_engine.py", topic], check=True, cwd=BASE_DIR)
        subprocess.run(["python", "deep_script.py"], check=True, cwd=BASE_DIR)
        return {"status": "script generated"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Upload Script
@app.post("/upload_script")
def upload_script(script: str = Form(...)):
    try:
        with open(os.path.join(BASE_DIR, "script.txt"), "w") as f:
            f.write(script)
        return {"status": "custom script uploaded"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Upload Voice
@app.post("/upload_voice")
def upload_voice(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(BASE_DIR, "speaker.wav")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"status": "voice uploaded"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Generate Voice
@app.post("/generate_voice")
def generate_voice():
    try:
        subprocess.run(["python", "voice_engine.py"], check=True, cwd=BASE_DIR)
        return {"status": "voice generated"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Improve Quality
@app.post("/improve_quality")
def improve_quality():
    try:
        subprocess.run(["python", "voice_engine.py", "--quality", "high"], check=True, cwd=BASE_DIR)
        return {"status": "quality improved"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Pitch / Volume controls (same pattern)
@app.post("/pitch_up")
def pitch_up():
    subprocess.run(["python", "voice_engine.py", "--pitch", "+1"], cwd=BASE_DIR)
    return {"status": "pitch up"}


@app.post("/pitch_down")
def pitch_down():
    subprocess.run(["python", "voice_engine.py", "--pitch", "-1"], cwd=BASE_DIR)
    return {"status": "pitch down"}


@app.post("/volume_up")
def volume_up():
    subprocess.run(["python", "voice_engine.py", "--volume", "+10"], cwd=BASE_DIR)
    return {"status": "volume up"}


@app.post("/volume_down")
def volume_down():
    subprocess.run(["python", "voice_engine.py", "--volume", "-10"], cwd=BASE_DIR)
    return {"status": "volume down"}


# ✅ Generate Images
@app.post("/generate_images")
def generate_images():
    try:
        subprocess.run(["python", "image_generator.py"], check=True, cwd=BASE_DIR)
        return {"status": "images generated"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Generate Video
@app.post("/generate_video")
def generate_video():
    try:
        subprocess.run(["python", "video_generator.py"], check=True, cwd=BASE_DIR)
        return {"status": "video generated"}
    except Exception as e:
        return {"error": str(e)}


# ✅ Download Video
@app.get("/download_video")
def download_video():
    path = os.path.join(BASE_DIR, "final_video.mp4")
    if not os.path.exists(path):
        return {"error": "Video not found"}
    return FileResponse(path, media_type="video/mp4", filename="video.mp4")


# ✅ Download Voice
@app.get("/download_voice")
def download_voice():
    path = os.path.join(BASE_DIR, "generated_voice.mp3")
    if not os.path.exists(path):
        return {"error": "Voice not found"}
    return FileResponse(path, media_type="audio/mpeg", filename="voice.mp3")


# ✅ Full Pipeline
@app.post("/generate_full_video")
def generate_full_video(topic: str = Form(...)):
    generate_script(topic)
    generate_voice()
    generate_images()
    generate_video()
    return {"status": "AI video generated 🚀"}