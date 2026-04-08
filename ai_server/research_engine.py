import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("thtwaat.research")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:4b")

def run(topic: str, language: str = "en") -> str:
    logger.info("Researching topic: %s in %s", topic, language)

    prompt = (
        f"Research expert. Respond in {language}. Topic: {topic}\n"
        f"Cover: overview, key facts, emotional/dramatic points, 5 visual scene descriptions. Be concise."
    )

    try:
        res = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )
        res.raise_for_status()
        research_data = res.json().get("response", "")
        with open("research.txt", "w", encoding="utf-8") as f:
            f.write(research_data)
        return research_data
    except Exception as e:
        logger.error("Research failed: %s", e)
        return f"Research failed: {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
