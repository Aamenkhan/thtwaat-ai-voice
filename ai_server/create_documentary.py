"""Create a cinematic documentary video from a script.

This script ties together the existing pieces in the repo:
  1) scene_breakdown.py (breaks a script into scene descriptions)
  2) image_generator.py (generates images from prompts)
  3) video_generator.py (creates a video from images + audio)

Usage:
    python create_documentary.py --script script.txt --audio voice.wav

You can also run the steps manually if you want more control.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List


def scenes_to_prompts(scenes_text: str) -> List[str]:
    """Convert a scene breakdown into one prompt per scene."""

    # Split on one or more blank lines.
    blocks = [b.strip() for b in scenes_text.split("\n\n") if b.strip()]

    # Keep each block as a prompt, trimming any leading scene header.
    prompts: List[str] = []
    for block in blocks:
        # If a block starts with "Scene" or similar, keep it but remove the prefix.
        lines = block.splitlines()
        if lines:
            first = lines[0].strip()
            if first.lower().startswith("scene") or first.lower().startswith("sc"):
                # Keep the entire block as context but prefer the first line as the prompt.
                prompts.append(first)
                continue
        prompts.append(block)

    return prompts


def write_prompts(prompts: List[str], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for prompt in prompts:
            if prompt:
                f.write(prompt.strip() + "\n")


def run_command(args: List[str]) -> None:
    print("Running:", " ".join(args))
    subprocess.check_call(args)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a documentary-style video from a script.")
    parser.add_argument("--script", default="script.txt", help="Input script file to break into scenes.")
    parser.add_argument("--scenes", default="scenes.txt", help="Path to write scene breakdown output.")
    parser.add_argument("--prompts", default="scene_prompts.txt", help="Path to write image prompts.")
    parser.add_argument("--images-dir", default="images", help="Directory where generated images will be written.")
    parser.add_argument("--audio", default="voice.wav", help="Path to the audio file to use in the video.")
    parser.add_argument("--output", default="final_video.mp4", help="Output video file path.")
    parser.add_argument("--openai-api-key", default=None, help="OpenAI API key (or set OPENAI_API_KEY).")
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation step.")
    parser.add_argument("--skip-video", action="store_true", help="Skip video generation step.")

    args = parser.parse_args(argv)

    # 1) Scene breakdown
    print("==> Breaking script into scenes")
    scene_cmd = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "scene_breakdown.py"),
        "--script",
        args.script,
        "--output",
        args.scenes,
    ]
    if args.openai_api_key:
        scene_cmd += ["--api-key", args.openai_api_key]

    run_command(scene_cmd)

    # 2) Convert scenes to prompts
    print("==> Converting scenes into image prompts")
    with open(args.scenes, "r", encoding="utf-8") as f:
        scenes_text = f.read()

    prompts = scenes_to_prompts(scenes_text)
    write_prompts(prompts, args.prompts)

    # 3) Image generation
    if not args.skip_images:
        print("==> Generating images")
        img_cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), "image_generator.py"),
            "--prompts-file",
            args.prompts,
            "--output-dir",
            args.images_dir,
        ]
        run_command(img_cmd)

    # 4) Video generation
    if not args.skip_video:
        print("==> Generating video")
        image_pattern = os.path.join(args.images_dir, "image*.png")
        vid_cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), "video_generator.py"),
            "--audio",
            args.audio,
            "--images",
            image_pattern,
            "--output",
            args.output,
        ]
        run_command(vid_cmd)

    print("Done! Output video:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
