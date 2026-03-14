# video_generator.py
# This module handles video generation functionality for the AI server.

import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def generate_video_from_images_and_audio(audio_file, image_files, output_file="final_video.mp4", fps=24):
    """
    Generate a video by combining images with audio.

    Args:
        audio_file (str): Path to the audio file.
        image_files (list): List of paths to image files.
        output_file (str): Path for the output video file.
        fps (int): Frames per second for the video.

    Returns:
        str: Path to the generated video file.
    """

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file {audio_file} not found.")

    for img in image_files:
        if not os.path.exists(img):
            raise FileNotFoundError(f"Image file {img} not found.")

    # Load audio
    audio = AudioFileClip(audio_file)

    # Calculate duration per image
    duration = audio.duration / len(image_files)

    clips = []

    for img in image_files:
        clip = ImageClip(img).set_duration(duration)
        clips.append(clip)

    # Combine clips
    video = concatenate_videoclips(clips)

    # Add audio
    video = video.set_audio(audio)

    # Export video
    video.write_videofile(output_file, fps=fps)

    return output_file


# ---- Example Run ----
if __name__ == "__main__":

    audio_file = "voice_791236c9-4c45-4ffa-9b73-6febd0939bba.wav"

    image_files = [
        "image1.png",
        "image2.png",
        "image3.png"
    ]

    generate_video_from_images_and_audio(audio_file, image_files)