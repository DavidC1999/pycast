import pydotool
import subprocess
import os
import sys

from pycast import session

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

_initialized = False

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


def sendkey(key):
    """Send a single key to the focused element."""

    _init()

    pydotool.key(key, True)
    pydotool.key(key, False)
