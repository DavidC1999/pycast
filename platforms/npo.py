from pycast import *
from browser_control import addon, ydotool, browser

from pydotool import KEY_F

from platforms.assets.npo_icons import *


class Npo(Platform):
    def __init__(self, method):
        if method == "share":
            super().__init__(
                name="NPO",
                id="npo",
                actions=[
                    (Action.toggleplay, addon.toggleplay),
                    (Action.fullscreen, lambda: ydotool.sendkey(KEY_F)),
                    (Action.back, addon.backward),
                    (Action.forward, addon.forward),
                    (Action.refresh, addon.refresh),
                    (Action.captions, addon.toggle_captions),
                    (Action.jump, lambda: self._jump()),
                ],
                regex=r".*?(?P<url>https?://(www\.)?npo\.nl/?([^\/\n]+\/)*[^\/\n]+).*",
            )
        elif method == "immediate":
            super().__init__(
                name="NPO",
                id="npo-immediate",
                actions=[
                    (Action.toggleplay, addon.toggleplay),
                    (Action.fullscreen, lambda: ydotool.sendkey(KEY_F)),
                    (Action.back, addon.backward),
                    (Action.forward, addon.forward),
                    (Action.refresh, addon.refresh),
                    (Action.captions, addon.toggle_captions),
                ],
                launch_buttons=[
                    (NPO1_ICON, "npo1"),
                    (NPO2_ICON, "npo2"),
                    (NPO3_ICON, "npo3"),
                ]
            )

    def _jump(self):
        """Only available in share mode"""
        minutes = int(get_url_arg("m") or 0)
        seconds = int(get_url_arg("s") or 0)
        addon.seek(minutes * 60 + seconds)

    def launch_immediate(self, parameter):
        addon.init()
        browser.open(f"https://npo.nl/start/live/{parameter}")

    def launch(self, params: dict[str, str]):
        addon.init()
        browser.open(params["url"])

    def cleanup(self):
        addon.cleanup()
        browser.close()


def create():
    return [Npo("share"), Npo("immediate")]
