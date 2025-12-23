import subprocess

def focus_browser():
    subprocess.call(["xdotool", "search", "\"Mozilla Firefox\"", "windowactivate"])

def keypress(key):
    subprocess.call(["xdotool", "key", key])