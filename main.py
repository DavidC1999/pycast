from flask import Flask, render_template, current_app, request

import subprocess
import os
import os.path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

app = Flask(__name__)

class Session:
    driver: webdriver.Firefox = None
    driver_options: Options = None
    render_active_control: callable = None
    profile: str
    
    platform_specific = None

    def render_control(self, render_control: callable):
        self.render_active_control = render_control
        return render_control()

session: Session = None

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

def sendkey(key):
    global session
    ActionChains(session.driver)\
        .key_down(key)\
        .key_up(key)\
        .perform()
    
def render_index():
    global session
    return render_template("index.html", active_control=session is not None)

@app.route("/")
def index():
    return render_index()

def close_browser():
    global session

    if session.driver is not None:
        session.driver.quit()
        session.driver = None

def close_session():
    global session
    close_browser()
    session = None

def open_session():
    global session
    if session is not None:
        close_session()
    
    session = Session()

    profile = request.args.get("profile") if "profile" in request.args else DEFAULT_PROFILE_NAME

    existing_profiles = get_profiles()

    if not profile in existing_profiles:
        create_firefox_profile(profile)

    session.driver_options = Options()
    session.driver_options.add_argument("-profile")
    session.driver_options.add_argument(f"{PROFILES_DIR}/{profile}")


def open_browser(url):
    global session

    close_browser()

    session.driver = webdriver.Firefox(
        service=Service(f"{SCRIPT_DIR}/thirdparty/geckodriver"),
        options=session.driver_options
    )

    session.driver.get(url)
    session.driver.maximize_window()

def open_youtube(id=None, time=None):
    url = f"https://www.youtube.com/watch?v={id}"

    if time:
        url += "&t=" + time
    
    open_browser(url)

def focus_npo_player():
    global session
    WebDriverWait(session.driver, 20)\
        .until(presence_of_element_located((By.ID, "bitmovinplayer-video-null")))
    
    session.driver.execute_script("document.getElementById(\"bitmovinplayer-video-null\").focus()")

@app.route("/website")
@app.route("/website/<path:url>")
def route_launch_website(url=None):
    global session

    open_session()

    if url is not None:
        open_browser(url)

    return session.render_control(lambda: render_template("website.html"))

@app.route("/youtube")
@app.route("/youtube/<id>")
def route_launch_youtube(id=None):
    global session
    
    open_session()

    if id is not None:
        session.platform_specific = id
        open_youtube(id)
    

    return session.render_control(lambda: render_template("youtube.html"))

@app.route("/youtube_action/<action>")
def route_youtube_action(action=None):
    global session
    if action == "toggleplay":
        sendkey("k")
    elif action == "fullscreen":
        sendkey("f")
    elif action == "bback":
        sendkey("j")
    elif action == "back":
        sendkey(Keys.ARROW_LEFT)
    elif action == "fforward":
        sendkey("l")
    elif action == "forward":
        sendkey(Keys.ARROW_RIGHT)
    elif action == "refresh":
        session.driver.refresh()
    elif action == "captions":
        sendkey("c")
    elif action == "jump":
        close_browser()
        minutes = request.args.get('m')
        seconds = request.args.get('s')

        id = session.platform_specific
        open_youtube(id, f"{minutes}m{seconds}s")


    return session.render_active_control()

@app.route("/npo")
@app.route("/npo/<path:url>")
def route_launch_npo(url=None):
    global session

    open_session()

    if url is not None:
        open_browser(url)
        focus_npo_player()
    
    return session.render_control(lambda: render_template("npo.html"))

@app.route("/npo_action/<action>")
def route_npo_action(action=None):
    global session
    if action == "toggleplay":
        sendkey(Keys.SPACE)
    elif action == "fullscreen":
        sendkey("f")
    elif action == "back":
        sendkey(Keys.ARROW_LEFT)
    elif action == "forward":
        sendkey(Keys.ARROW_RIGHT)
    elif action == "refresh":
        session.driver.refresh()
        focus_npo_player()
    
    return session.render_active_control()

@app.route("/close")
def route_close():
    close_session()
    return render_index()

@app.route("/active-control")
def route_active_control():
    global session
    return session.render_active_control()


if __name__ == "__main__":
    if not os.path.exists(DEFAULT_PROFILE):
        create_firefox_profile(DEFAULT_PROFILE_NAME)

    app.run(host="0.0.0.0", port=8080)
