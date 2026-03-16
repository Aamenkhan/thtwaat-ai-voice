﻿from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

import subprocess
import shutil
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Dashboard
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Generate Script
@app.post("/generate_script")
def generate_script(topic: str = Form(...)):

    subprocess.run(["python", "ai_server/research_engine.py", topic])
    subprocess.run(["python", "ai_server/deep_script.py"])

    return {"status": "script generated"}


# Upload Voice
@app.post("/upload_voice")
def upload_voice(file: UploadFile = File(...)):

    with open("speaker.wav", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"status": "voice uploaded"}


# Generate Voice
@app.post("/generate_voice")
def generate_voice():

    subprocess.run(["python", "ai_server/voice_engine.py"])

    return {"status": "voice generated"}


# Generate Images
@app.post("/generate_images")
def generate_images():

    subprocess.run(["python", "ai_server/image_generator.py"])

    return {"status": "images generated"}


# Generate Video
@app.post("/generate_video")
def generate_video():

    subprocess.run(["python", "ai_server/video_generator.py"])

    return {"status": "video generated"}


# Download Video
@app.get("/download_video")
def download_video():

    return FileResponse(
        "final_video.mp4",
        media_type="video/mp4",
        filename="documentary.mp4"
    )


# Full AI Video Pipeline
@app.post("/generate_full_video")
def generate_full_video(topic: str = Form(...)):

    generate_script(topic)
    generate_voice()
    generate_images()
    generate_video()

    return {"status": "AI video generated"}


# Start Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)