from flask import Flask, request, send_file, render_template_string
from TTS.api import TTS
import uuid
import os

app = Flask(__name__)

# XTTS model load
print("Loading XTTS model...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

HTML_PAGE = """
<html>
<head>
<title>Thtwaat AI Voice Studio</title>
</head>
<body style="text-align:center;font-family:Arial">

<h1>Thtwaat AI Voice Studio</h1>

<form action="/generate" method="post" enctype="multipart/form-data">

<p>Paste your Script</p>

<textarea name="text" rows="10" cols="60"></textarea>

<br><br>

<p>Upload your Voice Sample</p>

<input type="file" name="voice">

<br><br>

<button type="submit">Generate MP3 Voice</button>

</form>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/generate", methods=["POST"])
def generate():

    text = request.form.get("text")
    voice = request.files["voice"]

    # save voice sample
    speaker_path = "speaker.wav"
    voice.save(speaker_path)

    # output file
    output_file = f"voice_{uuid.uuid4()}.wav"

    print("Generating voice...")

    tts.tts_to_file(
        text=text,
        speaker_wav=speaker_path,
        language="en",
        file_path=output_file
    )

    print("Voice generated:", output_file)

    return send_file(output_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)