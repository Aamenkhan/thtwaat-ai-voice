from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Thtwaat AI Voice Server Running"}

@app.get("/health")
def health():
    return {"status": "ok"}
