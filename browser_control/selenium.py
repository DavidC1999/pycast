from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.firefox.service import Service
import os

from pycast import session

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def open_browser(url):
    """Open a Firefox browser and navigate to the URL.

    Requires that session().profile_dir is already configured.
    Assigns the driver to session().driver.
    """

    options = Options()
    options.add_argument("-profile")
    options.add_argument(session().profile_dir)

    driver = webdriver.Firefox(
        service=Service(f"{SCRIPT_DIR}/../thirdparty/geckodriver"),
        options=options
    )

    driver.get(url)
    driver.maximize_window()

    session().driver = driver


def close_browser():
    """Close the Firefox browser."""
    from pycast import session

    if session().driver is not None:
        session().driver.quit()
        session().driver = None


def sendkey(key):
    """Send a single key to the focused element."""

    ActionChains(session().driver)\
        .key_down(key)\
        .key_up(key)\
        .perform()
