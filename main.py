from flask import Flask, render_template, current_app, request

import os
import importlib

from pycast import *

app = Flask(__name__)
platforms: list[Platform] = []
    
def render_index():
    return render_template("index.html", active_control=session() is not None)


def render_platform():
    return render_template(session().active_platform.template)


def launch(platform, params):
    close_session()
    
    open_session(platform)
    session().active_platform.launch(params)

    return render_platform()

def get_possible_urls_to_check():
    to_check = []
    if "link" in request.args:
        to_check.append(request.args["link"])
    if "description" in request.args:
        to_check.append(request.args["description"])
    if "name" in request.args:
        to_check.append(request.args["name"])
    
    return to_check

@app.route("/launch")
def route_launch():
    global platforms

    to_check = get_possible_urls_to_check()
    
    if len(to_check) == 0:
        return render_index()
    
    for possible_url in to_check:
        for platform in platforms:
            vars = platform.check_url(possible_url)
            if vars is not None:
                return launch(platform, vars)
    return render_index()

@app.route("/")
def index():
    to_check = get_possible_urls_to_check()
    
    if len(to_check) == 0:
        return render_index()
    
    # We should also get the profile from local storage
    # The get_profile page will redirect to /launch
    return render_template("get_profile.html")


@app.route("/action/<action_name>")
def route_action(action_name=None):
    action = Action.to_action(action_name)
    if action is None:
        return render_platform()
    
    if action not in session().active_platform.actions:
        return render_platform()
    
    session().active_platform.actions[action]()
    return render_platform()


@app.route("/close")
def route_close():
    close_session()
    return render_index()


@app.route("/active-control")
def route_active_control():
    return session().render_active_control()


if __name__ == "__main__":
    for file in os.listdir("platforms"):
        if file.endswith(".py"):
            module_name = file[:len(file) - len(".py")]
            module = importlib.import_module(f"platforms.{module_name}")
            platforms.append(module.create())

    app.run(host="0.0.0.0", port=8080)
