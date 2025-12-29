from flask import Flask, render_template

import subprocess

import x11 as platformspecific

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/youtube/<id>")
def launch_youtube(id=None):
    if id is None:
        return "<p>No ID given</p>"

    subprocess.Popen(["firefox", "-P", "pycast", f"https://www.youtube.com/watch?v={id}"])
    platformspecific.focus_browser()
    return render_template("youtube.html")

@app.route("/youtube/action/<action>")
def youtube_simple_action(action=None):
    if action == "toggleplay":
        platformspecific.keypress("k")
    elif action == "fullscreen":
        platformspecific.keypress("f")
    elif action == "bback":
        platformspecific.keypress("j")
    elif action == "back":
        platformspecific.keypress("Left")
    elif action == "fforward":
        platformspecific.keypress("l")
    elif action == "forward":
        platformspecific.keypress("Right")
    elif action == "refresh":
        platformspecific.keypress("F5")

    return render_template("youtube.html")

@app.route("/close")
def close():
    platformspecific.keypress("ctrl+w")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)