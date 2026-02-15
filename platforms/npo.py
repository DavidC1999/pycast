from pycast import *

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By

class Npo(Platform):
    def __init__(self):
        super().__init__(
            "NPO",
            r".*(?P<url>https?://(www\.)?npo\.nl/?([^\/\n]+\/)*[^\/\n]+).*",
            (Action.toggleplay, lambda: sendkey(Keys.SPACE)),
            (Action.fullscreen, lambda: sendkey("f")),
            (Action.back, lambda: sendkey(Keys.ARROW_LEFT)),
            (Action.forward, lambda: sendkey(Keys.ARROW_RIGHT)),
            (Action.refresh, lambda: session().driver.refresh()),
            (Action.captions, lambda: sendkey("c")),
        )

    def _open_youtube(self, id=None, time=None):
        url = f"https://www.youtube.com/watch?v={id}"

        if time:
            url += "&t=" + time
        
        open_browser(url)

    def _focus_player(self):
        WebDriverWait(session().driver, 20)\
            .until(presence_of_element_located((By.ID, "bitmovinplayer-video-null")))
        
        # Focus the video player so keypesses can influence the playback
        session().driver.execute_script("document.getElementById(\"bitmovinplayer-video-null\").focus()")


    def launch(self, params: dict[str, str]):
        open_browser(params["url"])

        self._focus_player()

def create():
    return Npo()
