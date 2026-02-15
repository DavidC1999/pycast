from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.firefox.service import Service
import os
import subprocess

from flask import request

import abc
import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROFILES_DIR = f"{SCRIPT_DIR}/firefox_profiles"
DEFAULT_PROFILE_NAME = "pycast"
DEFAULT_PROFILE = f"{PROFILES_DIR}/{DEFAULT_PROFILE_NAME}"

class Action:
    toggleplay = 0
    fullscreen = 1
    bback = 2
    back = 3
    fforward = 4
    forward = 5
    refresh = 6
    captions = 7
    jump = 8

    @staticmethod
    def action_names():
        return [x for x in vars(Action) if not x.startswith("_") and not callable(getattr(Action, x))]
    
    @staticmethod
    def action_values():
        return [getattr(Action, x) for x in Action.action_names()]

    @staticmethod
    def count():
        return len(Action.action_names())
    
    @staticmethod
    def is_action(value):
        return value in Action.action_names() or value in Action.action_values()

    @staticmethod
    def str_to_int(text):
        if not Action.is_action(text):
            return None
        return getattr(Action, text)
    
    @staticmethod
    def int_to_str(nr):
        for action_name in Action.action_names():
            if Action.str_to_int(action_name) == nr:
                return action_name
        
        return None


class Platform(abc.ABC):
    def __init__(self, name: str, regex: str | list[str], *actions):
        self.name = name

        if isinstance(regex, list):
            self.regexes = [re.compile(x) for x in regex]
        else:
            self.regexes = [re.compile(regex)]
        
        self.actions = {}

        for action in actions:
            if not isinstance(action, tuple):
                raise Exception("action must be a tuple")
            
            if not isinstance(action[0], int) or action[0] >= Action.count():
                raise Exception("invalid action")
            
            if not callable(action[1]):
                raise Exception("action must be callable")
            
            self.actions[action[0]] = action[1]
    
    @abc.abstractmethod
    def launch(self, params: dict[str, str]):
        pass

    def check_url(self, text) -> dict[str, str] | None:
        for regex in self.regexes:
            matches = regex.match(text)

            if matches is not None:
                return matches.groupdict()
        
        return None



class Session:
    driver: webdriver.Firefox = None
    driver_options: Options = None
    render_active_control: callable = None
    profile: str
    active_platform: Platform = None
    
    user_args = None

    def render_control(self, render_control: callable):
        self.render_active_control = render_control
        return render_control()

def _create_firefox_profile(profile_name):
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)

    profile_dir = f"{PROFILES_DIR}/{profile_name}"
    cmd = subprocess.Popen(["firefox", "-CreateProfile", f"{profile_name} {profile_dir}"])
    # waits for command to exit to make sure the profile exists before returning from function
    cmd.communicate()

def _get_profiles():
    return [a for a in os.listdir(PROFILES_DIR) if os.path.isdir(f"{PROFILES_DIR}/{a}")]

_session: Session = None

def session():
    global _session
    return _session

def sendkey(key):
    global _session
    ActionChains(_session.driver)\
        .key_down(key)\
        .key_up(key)\
        .perform()

def close_browser():
    global _session
    if _session.driver is not None:
        _session.driver.quit()
        _session.driver = None

def close_session():
    global _session
    if _session is not None:
        close_browser()
        _session = None

def open_session(platform: Platform):
    global _session
    if _session is not None:
        close_session()
    
    _session = Session()

    profile = request.args.get("profile") if "profile" in request.args else DEFAULT_PROFILE_NAME

    existing_profiles = _get_profiles()

    if not profile in existing_profiles:
        _create_firefox_profile(profile)

    _session.driver_options = Options()
    _session.driver_options.add_argument("-profile")
    _session.driver_options.add_argument(f"{PROFILES_DIR}/{profile}")

    _session.active_platform = platform


def open_browser(url):
    global _session

    close_browser()

    _session.driver = webdriver.Firefox(
        service=Service(f"{SCRIPT_DIR}/thirdparty/geckodriver"),
        options=_session.driver_options
    )

    _session.driver.get(url)
    _session.driver.maximize_window()

def get_url_arg(name):
    return request.args.get(name)
