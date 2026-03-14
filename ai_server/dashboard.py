from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Thtwaat AI Studio</title>
</head>
<body style="font-family:Arial;text-align:center">

<h2>Thtwaat AI Video Studio</h2>

<form method="post">
<textarea name="script" rows="10" cols="50"
placeholder="Paste your script here"></textarea><br><br>

<button type="submit">Generate Video</button>
</form>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():

    if request.method == "POST":

        script_text = request.form["script"]

        with open("script.txt","w",encoding="utf-8") as f:
            f.write(script_text)

        subprocess.run(["python","auto_video.py"])

        return "Video Created! Check final_video.mp4"

    return render_template_string(HTML)


app.run(host="0.0.0.0",port=5000)