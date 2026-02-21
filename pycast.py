from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.firefox.service import Service
import os

from flask import request

import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_PROFILE_DIR = f"{SCRIPT_DIR}/firefox_profile"
DEFAULT_PROFILE_NAME = "pycast"

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


class Platform:
    def __init__(
            self,
            name: str,
            id: str,
            actions: list[tuple],
            regex: str | list[str] | None = None,
            launch_buttons: list[tuple] | None = None):
        self.name = name
        self.id = id

        if regex is None:
            self.regexes = []
        elif isinstance(regex,
        list):
            self.regexes = [re.compile(x, re.MULTILINE) for x in regex]
        else:
            self.regexes = [re.compile(regex, re.MULTILINE)]
        
        self.actions = {}

        for action in actions:
            if not isinstance(action, tuple):
                raise Exception("action must be a tuple")
            
            if not isinstance(action[0], int) or action[0] >= Action.count():
                raise Exception("invalid action")
            
            if not callable(action[1]):
                raise Exception("action must be callable")
            
            self.actions[action[0]] = action[1]
        
        self.launch_buttons = launch_buttons
    
    def launch_immediate(self, parameter):
        _ = parameter
        raise NotImplementedError()
    
    def launch(self, params: dict[str, str]):
        _ = params
        raise NotImplementedError()

    def check_url(self, text: str) -> dict[str, str] | None:
        for regex in self.regexes:
            # Python seems to struggle with matching text with newlines:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            
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

def open_session(platform: Platform, profiles_dir):
    global _session
    if _session is not None:
        close_session()
    
    _session = Session()

    profile = request.args.get("profile") if "profile" in request.args else DEFAULT_PROFILE_NAME

    profile_dir = DEFAULT_PROFILE_DIR
    dir_items = os.listdir(profiles_dir)
    for item in dir_items:
        if re.match((r"[a-zA-Z0-9]+." + profile), item):
            profile_dir = f"{profiles_dir}/{item}"
            break

    _session.driver_options = Options()
    _session.driver_options.add_argument("-profile")
    _session.driver_options.add_argument(f"{profile_dir}")
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
