import sys
import requests

# topic receive from auto_documentary_engine
topic = sys.argv[1]

print("Researching topic:", topic)

url = f"https://api.duckduckgo.com/?q={topic}&format=json"

data = requests.get(url).json()

research = data.get("AbstractText", "")

with open("research.txt", "w", encoding="utf-8") as f:
    f.write(research)

print("Research collected")