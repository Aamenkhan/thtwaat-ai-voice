import sys
import subprocess

# topic receive from API
if len(sys.argv) > 1:
    topic = sys.argv[1]
else:
    topic = "Default Topic"

print("Generating documentary about:", topic)

subprocess.run(["python", "ai_server/research_engine.py", topic])
subprocess.run(["python", "ai_server/fact_extractor.py"])
subprocess.run(["python", "ai_server/deep_script.py"])
subprocess.run(["python", "ai_server/scene_breakdown.py"])
subprocess.run(["python", "ai_server/image_generator.py"])
subprocess.run(["python", "ai_server/voice_engine.py"])
subprocess.run(["python", "ai_server/video_generator.py"])

print("Cinematic documentary video ready")