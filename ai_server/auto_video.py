import re
import subprocess

SCRIPT_FILE = "script.txt"
SCENE_BREAKDOWN_FILE = "scene_breakdown.txt"
PROMPTS_FILE = "scene_prompts.txt"


def split_into_scenes(script_text):
    """Split script text into scenes based on blank lines."""
    raw_scenes = re.split(r"\n\s*\n", script_text.strip())
    scenes = [s.strip() for s in raw_scenes if s.strip()]
    return scenes


def build_prompt_for_scene(scene_text):
    """Build a Stable Diffusion prompt for a scene."""
    # Use the first line or sentence as a seed for the prompt.
    first_line = scene_text.strip().splitlines()[0]
    first_sentence = first_line.split(".")[0][:200]
    prompt = (
        f"{first_sentence}, cinematic documentary style, 8k, dramatic lighting, film grain"
    )
    return prompt


def main():
    print("Step 0: Reading script and generating scene breakdown...")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()

    scenes = split_into_scenes(script_text)
    if not scenes:
        raise ValueError("No scenes detected in script. Please add content to script.txt.")

    with open(SCENE_BREAKDOWN_FILE, "w", encoding="utf-8") as f:
        for idx, scene in enumerate(scenes, start=1):
            f.write(f"Scene {idx}:\n")
            f.write(scene.strip() + "\n\n")

    prompts = [build_prompt_for_scene(scene) for scene in scenes]
    with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
        for prompt in prompts:
            f.write(prompt + "\n")

    print(f"Wrote {len(scenes)} scenes to {SCENE_BREAKDOWN_FILE}")
    print(f"Wrote {len(prompts)} prompts to {PROMPTS_FILE}")

    print("Step 1: Creating voice...")
    subprocess.run(["python", "voice_engine.py"])

    print("Step 2: Generating AI images...")
    subprocess.run(["python", "image_generator.py", "--prompts-file", PROMPTS_FILE])

    print("Step 3: Creating video...")
    subprocess.run(["python", "video_generator.py", "--audio", "voice.wav"])

    print("All done! Video ready.")


if __name__ == "__main__":
    main()