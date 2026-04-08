import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("thtwaat.script")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:4b")

def generate(research_data: str, style: str = "educational") -> str:
    logger.info("Generating script with style: %s", style)

    prompt = (
        f"Professional documentary script writer. Style: {style}.\n"
        f"Write a cinematic narration script from these facts (same language as facts):\n"
        f"{research_data}\n"
        f"Use [Visual: ...] cues. Strong hook. Dramatic tone. Be concise."
    )

    try:
        res = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=180,
        )
        res.raise_for_status()
        script = res.json().get("response", "")
        with open("script.txt", "w", encoding="utf-8") as f:
            f.write(script)
        return script
    except Exception as e:
        logger.error("Script generation failed: %s", e)
        return f"Script generation failed: {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(generate(sys.argv[1]))
    else:
        try:
            with open("research.txt", "r", encoding="utf-8") as f:
                print(generate(f.read()))
        except Exception:
            print("No research.txt found.")
