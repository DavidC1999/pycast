from flask import Flask, Response, render_template

import webbrowser

import x11 as platformspecific

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/youtube/<id>")
def launch_youtube(id=None):
    if id is None:
        return "<p>No ID given</p>"
    
    webbrowser.open_new(f"https://www.youtube.com/watch?v={id}")
    platformspecific.focus_browser()
    return render_template("youtube.html")

@app.route("/youtube/toggleplay")
def toggle_play(id=None):
    platformspecific.keypress("k")
    return render_template("youtube.html")

if __name__ == "__main__":
    app.run(host="192.168.1.201", port=8080)