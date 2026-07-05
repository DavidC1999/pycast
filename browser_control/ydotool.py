import pydotool
import subprocess
import os
import sys

from pycast import session

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

_initialized = False
_firefox_process = None

def _init():
    global _initialized

    if _initialized:
        return

    if not os.path.exists(f"{SCRIPT_DIR}/../ydotool/build/ydotoold"):
        print("ydotoold not found, please run install.sh")
        sys.exit(1)

    subprocess.Popen(
        [f"{SCRIPT_DIR}/../ydotool/build/ydotoold"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    pydotool.init()

    _initialized = True


def open_browser(url):
    """Open a Firefox browser and navigate to the URL.

    Requires that session().profile_dir is already configured.
    """
    global _firefox_process

    _init()

    _firefox_process = subprocess.Popen(
        ["firefox", "-profile", session().profile_dir, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def close_browser():
    """Close the Firefox browser."""
    global _firefox_process

    if _firefox_process:
        _firefox_process.terminate()
        _firefox_process = None


def sendkey(key):
    """Send a single key to the focused element."""

    pydotool.key(key, True)
    pydotool.key(key, False)
