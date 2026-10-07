import subprocess

from pycast import session

_firefox_process = None

def open(url):
    """Open a Firefox browser and navigate to the URL.

    Requires that session().profile_dir is already configured.
    """
    global _firefox_process

    _firefox_process = subprocess.Popen(
        ["firefox", "-profile", session().profile_dir, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def close():
    """Close the Firefox browser."""
    global _firefox_process

    if _firefox_process:
        _firefox_process.terminate()
        _firefox_process = None