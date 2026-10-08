from pycast import *
from browser_control import addon, ydotool, browser

import screeninfo

import browser_control.ydotool

from pydotool import KEY_F
import pydotool

from platforms.assets.npo_icons import *

import time


class Dropout(Platform):
    def __init__(self):
        super().__init__(
            name="Dropout",
            id="dropout",
            actions=[
                (Action.toggleplay, addon.toggleplay),
                (Action.fullscreen, lambda: ydotool.sendkey(KEY_F)),
                (Action.back, addon.backward),
                (Action.forward, addon.forward),
                (Action.refresh, addon.refresh),
                (Action.captions, lambda: addon.unwrap_iframe("#watch-embed")),
            ],
            regex=r".*?(?P<url>https?://(www\.)?watch\.dropout\.tv\/videos/([^\n]+))",
        )

    def _get_primary_monitor(self):
        monitors = screeninfo.get_monitors()

        if len(monitors) == 1:
            return monitors[0]

        output = None
        for monitor in monitors:
            if monitor.is_primary:
                output = monitor
                break
        if output is not None:
            return output

        raise Exception("No primary monitor found.")

    def launch(self, params: dict[str, str]):
        addon.init()
        ydotool.init()

        browser.open(params["url"])
        monitor = self._get_primary_monitor()

        center = (monitor.width // 2, monitor.height // 2)

        # Sleep a bit to give it time to load. It's a bit hacky...
        time.sleep(7)

        # Moving absolute did not work reliably, this hack seems to work?
        pydotool.mouse_move((0,0), True)
        time.sleep(0.1)
        pydotool.mouse_move(center)
        time.sleep(0.1)

        # We click to give the browser a "user event"`giving us the ability to control the video with keyboard shortcuts.
        # The first click pauses the video, by clicking again we go to fullscreen instead to avoid stutters
        pydotool.left_click()
        time.sleep(0.1)
        pydotool.left_click()


    def cleanup(self):
        addon.cleanup()
        browser.close()


def create():
    return [Dropout()]
