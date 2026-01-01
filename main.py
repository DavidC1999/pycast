from flask import Flask, render_template, current_app, request

import subprocess, os.path

import x11 as platformspecific

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def close_tab():
    platformspecific.keypress("ctrl+w")

def launch_website(url):
    subprocess.Popen(["firefox", "-P", "pycast", url])
    platformspecific.focus_browser()

def launch_youtube(id=None, time=None):
    url = f"https://www.youtube.com/watch?v={id}"

    if time:
        url += "&t=" + time
    
    launch_website(url)

@app.route("/website")
@app.route("/website/<path:url>")
def route_launch_website(url=None):
    if url is not None:
        launch_website(url)

    return render_template("website.html")

@app.route("/youtube")
@app.route("/youtube/<id>")
def route_launch_youtube(id=None):
    if id is not None:
        launch_youtube(id)

    return render_template("youtube.html", id=id or "")

@app.route("/youtube_action/<action>")
@app.route("/youtube_action/<action>/<id>")
def route_youtube_action(action=None, id=None):
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
    elif action == "captions":
        platformspecific.keypress("c")
    elif action == "jump" and id is not None:
        close_tab()
        minutes = request.args.get('m')
        seconds = request.args.get('s')
        launch_youtube(id, f"{minutes}m{seconds}s")


    return render_template("youtube.html", id=id or "")

@app.route("/close")
def route_close():
    close_tab()
    return render_template("index.html")

@app.route("/asset/<asset>")
def route_asset(asset=None):
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(f"{BASE_DIR}/static/{asset}"):
        return current_app.send_static_file(asset)
    return current_app.send_static_file("notfound.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)