import os
import glob
import logging
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

logger = logging.getLogger("thtwaat.video")

def assemble(script_text: str = "", audio_path: str = "voice.wav", image_paths: list[str] = None) -> str:
    """
    Assemble images and audio into a final MP4 video.
    """
    logger.info("Assembling video with audio: %s", audio_path)
    
    if not image_paths:
        image_pattern = "static/images/img_*.png"
        image_paths = sorted(glob.glob(image_pattern))

    if not image_paths:
        # Check root too
        image_paths = sorted(glob.glob("image*.png"))

    if not image_paths:
        logger.error("No images found for video assembly.")
        return ""

    if not os.path.exists(audio_path):
        logger.error("Audio file not found: %s", audio_path)
        return ""

    try:
        # Load audio
        audio = AudioFileClip(audio_path)
        duration_per_image = audio.duration / len(image_paths)

        clips = []
        for img in image_paths:
            if os.path.exists(img):
                clip = ImageClip(img).set_duration(duration_per_image)
                clips.append(clip)

        if not clips:
            logger.error("Failed to create any image clips.")
            return ""

        # Merge clips
        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio)

        output_path = f"static/final_video_{os.urandom(4).hex()}.mp4"
        os.makedirs("static", exist_ok=True)

        logger.info("Rendering video to %s", output_path)
        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        return f"/{output_path.replace('\\', '/')}" # URL format
    except Exception as e:
        logger.error("Video assembly failed: %s", e)
        return ""

if __name__ == "__main__":
    assemble()