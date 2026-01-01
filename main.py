from flask import Flask, render_template, current_app, request

import subprocess
import os
import os.path

import x11 as platformspecific

app = Flask(__name__)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROFILES_DIR = f"{SCRIPT_DIR}/firefox_profiles"
DEFAULT_PROFILE_NAME = "pycast"
DEFAULT_PROFILE = f"{PROFILES_DIR}/{DEFAULT_PROFILE_NAME}"

def create_firefox_profile(profile_name):
    profile_dir = f"{PROFILES_DIR}/{profile_name}"
    subprocess.Popen(["firefox", "-CreateProfile", f"{profile_name} {profile_dir}"])

def get_profiles():
    return [a for a in os.listdir(PROFILES_DIR) if os.path.isdir(f"{PROFILES_DIR}/{a}")]

def close_tab():
    platformspecific.keypress("ctrl+w")

def launch_website(url):
    profile = request.args.get("profile") if "profile" in request.args else DEFAULT_PROFILE_NAME
    
    subprocess.Popen(["firefox", "-P", profile, url])
    platformspecific.focus_browser()

def launch_youtube(id=None, time=None):
    url = f"https://www.youtube.com/watch?v={id}"

    if time:
        url += "&t=" + time
    
    launch_website(url)

def render_index():
    return render_template("index.html", profiles=get_profiles())

@app.route("/")
def index():
    return render_index()

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
    return render_index()

@app.route("/asset/<asset>")
def route_asset(asset=None):
    if os.path.exists(f"{SCRIPT_DIR}/static/{asset}"):
        return current_app.send_static_file(asset)
    return current_app.send_static_file("notfound.png")

@app.route("/create_profile/<name>")
def route_create_profile(name=None):
    create_firefox_profile(f"pycast-{name}")
    return render_index()

if __name__ == "__main__":
    if not os.path.exists(DEFAULT_PROFILE):
        create_firefox_profile(DEFAULT_PROFILE_NAME)
    
    app.run(host="0.0.0.0", port=8080)