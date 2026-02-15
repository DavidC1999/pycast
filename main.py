from flask import Flask, render_template, current_app, request

import subprocess
import os
import os.path
import time

import x11 as platformspecific

app = Flask(__name__)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROFILES_DIR = f"{SCRIPT_DIR}/firefox_profiles"
DEFAULT_PROFILE_NAME = "pycast"
DEFAULT_PROFILE = f"{PROFILES_DIR}/{DEFAULT_PROFILE_NAME}"

def create_firefox_profile(profile_name):
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)

    profile_dir = f"{PROFILES_DIR}/{profile_name}"
    cmd = subprocess.Popen(["firefox", "-CreateProfile", f"{profile_name} {profile_dir}"])
    # waits for command to exit to make sure the profile exists before returning from function
    cmd.communicate()

def get_profiles():
    return [a for a in os.listdir(PROFILES_DIR) if os.path.isdir(f"{PROFILES_DIR}/{a}")]

@app.route("/")
def index():
    return render_template("index.html")

def close_tab():
    platformspecific.keypress("ctrl+w")

def launch_website(url):
    profile = request.args.get("profile") if "profile" in request.args else DEFAULT_PROFILE_NAME

    existing_profiles = get_profiles()

    if not profile in existing_profiles:
        create_firefox_profile(profile)
    
    subprocess.Popen(["firefox", "-P", profile, url])

    platformspecific.focus_browser()

def launch_youtube(id=None, time=None):
    url = f"https://www.youtube.com/watch?v={id}"

    if time:
        url += "&t=" + time
    
    launch_website(url)

def focus_npo_player():
    # Hacky solution to focus the video player:
    time.sleep(8)
    platformspecific.keypress("Tab")

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

@app.route("/npo")
@app.route("/npo/<path:url>")
def route_npo(url=None):
    if url is not None:
        launch_website(url)
        focus_npo_player()
    
    return render_template("npo.html")

@app.route("/npo_action/<action>")
def route_npo_action(action=None):
    if action == "toggleplay":
        platformspecific.keypress("space")
    elif action == "fullscreen":
        platformspecific.keypress("f")
    elif action == "back":
        platformspecific.keypress("Left")
    elif action == "forward":
        platformspecific.keypress("Right")
    elif action == "refresh":
        platformspecific.keypress("F5")
        focus_npo_player()
    
    return render_template("npo.html")

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
    if not os.path.exists(DEFAULT_PROFILE):
        create_firefox_profile(DEFAULT_PROFILE_NAME)

    app.run(host="0.0.0.0", port=8080)
