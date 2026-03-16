from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
import shutil
import os
from moviepy.editor import *
from pydub import AudioSegment

app = FastAPI()

SCRIPT_FILE = "script.txt"
VOICE_WAV = "voice.wav"
VOICE_MP3 = "voice.mp3"
FINAL_VIDEO = "final_video.mp4"


# ---------------- DASHBOARD ----------------

@app.get("/", response_class=HTMLResponse)
def dashboard():

    html = f"""
    <html>
    <body style="font-family:Arial">

    <h1>Thtwaat AI Studio</h1>

    <h2>1 Script</h2>

    <form action="/generate_script" method="post">
    <input name="topic" placeholder="Enter topic">
    <button type="submit">Generate Script</button>
    </form>

    <form action="/upload_script" method="post">
    <textarea name="script" rows="6" cols="60"></textarea><br>
    <button type="submit">Use Script</button>
    </form>


    <h2>2 Voice</h2>

    <form action="/upload_voice" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button type="submit">Upload Voice</button>
    </form>

    <form action="/generate_voice" method="post">
    <button type="submit">Convert to MP3</button>
    </form>

    <a href="/download_voice">Download Voice MP3</a>


    <h2>3 Images</h2>

    <form action="/upload_images" method="post" enctype="multipart/form-data">
    <input type="file" name="files" multiple>
    <button type="submit">Upload Images</button>
    </form>


    <h2>4 Generate Video</h2>

    <form action="/generate_video" method="post">
    <button type="submit">Create Video</button>
    </form>


    <h2>5 Final Video</h2>

    <video width="600" controls>
    <source src="/download_video" type="video/mp4">
    </video>

    <br><br>

    <a href="/download_video">
    <button>Download Final Video</button>
    </a>

    </body>
    </html>
    """

    return HTMLResponse(html)



# ---------------- SCRIPT ----------------

@app.post("/generate_script")
def generate_script(topic: str = Form(...)):

    script = f"This is an AI generated script about {topic}"

    with open(SCRIPT_FILE,"w") as f:
        f.write(script)

    return {"script":script}


@app.post("/upload_script")
def upload_script(script: str = Form(...)):

    with open(SCRIPT_FILE,"w") as f:
        f.write(script)

    return {"status":"script saved"}


# ---------------- VOICE ----------------

@app.post("/upload_voice")
async def upload_voice(file: UploadFile = File(...)):

    with open(VOICE_WAV,"wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"status":"voice uploaded"}


@app.post("/generate_voice")
def generate_voice():

    sound = AudioSegment.from_wav(VOICE_WAV)
    sound.export(VOICE_MP3, format="mp3")

    return {"status":"voice converted to mp3"}


@app.get("/download_voice")
def download_voice():
    return FileResponse(VOICE_MP3)


# ---------------- IMAGES ----------------

@app.post("/upload_images")
async def upload_images(files: list[UploadFile] = File(...)):

    os.makedirs("images", exist_ok=True)

    for i,file in enumerate(files):

        with open(f"images/image{i}.png","wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return {"status":"images uploaded"}



# ---------------- VIDEO ----------------

@app.post("/generate_video")
def generate_video():

    images = os.listdir("images")

    clips = []

    for img in images:

        clip = ImageClip(f"images/{img}").set_duration(4)
        clips.append(clip)

    video = concatenate_videoclips(clips)

    audio = AudioFileClip(VOICE_MP3)

    video = video.set_audio(audio)

    video.write_videofile(FINAL_VIDEO, fps=24)

    return {"status":"video created"}


@app.get("/download_video")
def download_video():

    return FileResponse(FINAL_VIDEO)