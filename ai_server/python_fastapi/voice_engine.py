from TTS.api import TTS

# Load XTTS model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

def generate_voice(text, speaker_wav="speaker.wav"):
    
    output_file = "output.wav"
    
    tts.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        file_path=output_file
    )
    
    return output_file
