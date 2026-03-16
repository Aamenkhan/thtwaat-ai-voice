from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/generate")
def generate(topic: str):

    subprocess.run([
        "python",
        "auto_documentary_engine.py",
        topic
    ])

    return {"status": "video generated"}