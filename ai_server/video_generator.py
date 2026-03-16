# video_generator.py
# Create video from generated images and AI voice

import argparse
import glob
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def generate_video(audio_file, image_pattern="image*.png", output="final_video.mp4", fps=24):

    # Check audio
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Find images
    images = sorted(glob.glob(image_pattern))

    if not images:
        raise FileNotFoundError(f"No images found for pattern: {image_pattern}")

    print("Images found:", images)

    # Load audio
    audio = AudioFileClip(audio_file)

    duration_per_image = audio.duration / len(images)

    clips = []

    for img in images:
        clip = ImageClip(img).set_duration(duration_per_image)
        clips.append(clip)

    # Merge clips
    video = concatenate_videoclips(clips, method="compose")

    # Add audio
    video = video.set_audio(audio)

    print("Rendering video...")

    video.write_videofile(
        output,
        fps=fps,
        codec="libx264",
        audio_codec="aac"
    )

    print("Video created:", output)

    return output


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--audio", default="voice.wav")
    parser.add_argument("--images", default="image*.png")
    parser.add_argument("--output", default="final_video.mp4")
    parser.add_argument("--fps", type=int, default=24)

    args = parser.parse_args()

    generate_video(
        audio_file=args.audio,
        image_pattern=args.images,
        output=args.output,
        fps=args.fps
    )


if __name__ == "__main__":
    main()