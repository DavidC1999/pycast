from flask import Flask, render_template, request

import subprocess

import x11 as platformspecific

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def close_tab():
    platformspecific.keypress("ctrl+w")

def launch_youtube(id=None, time=None):
    url = f"https://www.youtube.com/watch?v={id}"

    if time:
        url += "&t=" + time

    subprocess.Popen(["firefox", "-P", "pycast", url])
    platformspecific.focus_browser()

@app.route("/youtube/<id>")
def route_launch_youtube(id=None):
    if id is None:
        return "<p>No ID given</p>"

    launch_youtube(id)
    return render_template("youtube.html", id=id)

@app.route("/youtube/<id>/<action>")
def route_youtube_simple_action(id=None, action=None):
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
    elif action == "jump":
        close_tab()
        minutes = request.args.get('m')
        seconds = request.args.get('s')
        launch_youtube(id, f"{minutes}m{seconds}s")


    return render_template("youtube.html", id=id)

@app.route("/close")
def route_close():
    close_tab()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)