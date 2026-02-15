from flask import Flask, render_template, current_app, request

import os, glob
import os.path
import importlib

from pycast import *

app = Flask(__name__)
platforms: dict[str, Platform] = {}
    
def render_index():
    return render_template("index.html", active_control=session() is not None)

def render_platform():
    return render_template(session().active_platform.template)

@app.route("/")
def index():
    return render_index()


@app.route("/launch/<platform_name>")
def route_launch(platform_name=None):
    if platform_name not in platforms:
        return render_index()
    
    open_session(platforms[platform_name])
    session().active_platform.launch()

    return render_platform()

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
            platforms[module_name] = module.create()

    app.run(host="0.0.0.0", port=8080)
