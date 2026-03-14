import subprocess

print("Step 1: Creating voice...")
subprocess.run(["python", "voice_engine.py"])

print("Step 2: Generating AI images...")
subprocess.run(["python", "image_generator.py"])

print("Step 3: Creating video...")
subprocess.run(["python", "video_generator.py"])

print("All done! Video ready.")