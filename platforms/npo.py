from pycast import *

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located, visibility_of_element_located
from selenium.webdriver.common.by import By

from platforms.assets.npo_icons import *

class Npo(Platform):
    def __init__(self, method):
        if method == "share":
            super().__init__(
                name="NPO",
                id="npo",
                actions=[
                    (Action.toggleplay, lambda: self._sendkey(Keys.SPACE)),
                    (Action.fullscreen, lambda: self._sendkey("f")),
                    (Action.back, lambda: self._sendkey(Keys.ARROW_LEFT)),
                    (Action.forward, lambda: self._sendkey(Keys.ARROW_RIGHT)),
                    (Action.refresh, lambda: session().driver.refresh()),
                    (Action.captions, lambda: self._sendkey("c")),
                    (Action.jump, lambda: self._jump()),
                ],
                regex=r".*?(?P<url>https?://(www\.)?npo\.nl/?([^\/\n]+\/)*[^\/\n]+).*",
            )
        elif method == "immediate":
            super().__init__(
                name="NPO",
                id="npo-immediate",
                actions=[
                    (Action.toggleplay, lambda: self._sendkey(Keys.SPACE)),
                    (Action.fullscreen, lambda: self._sendkey("f")),
                    (Action.back, lambda: self._sendkey(Keys.ARROW_LEFT)),
                    (Action.forward, lambda: self._sendkey(Keys.ARROW_RIGHT)),
                    (Action.fforward, lambda: self._go_to_live()),
                    (Action.refresh, lambda: session().driver.refresh()),
                    (Action.captions, lambda: self._sendkey("c")),
                ],
                launch_buttons=[
                    (NPO1_ICON, "npo1"),
                    (NPO2_ICON, "npo2"),
                    (NPO3_ICON, "npo3"),
                ]
            )

    def _focus_player(self):
        WebDriverWait(session().driver, 20)\
            .until(presence_of_element_located((By.ID, "bitmovinplayer-video-null")))
        
        # Focus the video player so keypesses can influence the playback
        session().driver.execute_script("document.getElementById(\"bitmovinplayer-video-null\").focus()")
    
    def _sendkey(self, key):
        self._focus_player()
        sendkey(key)
    
    def _show_seek_bar(self):
        """Get the seek bar to show by moving the mouse"""
        player_elem = session().driver.find_element(By.CLASS_NAME, "bitmovinplayer-container")
        action = webdriver.ActionChains(session().driver)
        action.move_to_element(player_elem)
        action.move_by_offset(10, 0)
        action.perform()

        WebDriverWait(session().driver, 10)\
            .until(visibility_of_element_located((By.CSS_SELECTOR, ".bmpui-controlbar-seekbar .bmpui-seekbar")))
    
    def _hide_seek_bar(self):
        """Hide the seek bar by moving the mouse to the middle and keeping it still"""
        player_elem = session().driver.find_element(By.CLASS_NAME, "bitmovinplayer-container")
        action = webdriver.ActionChains(session().driver)
        action.move_to_element(player_elem)
        action.perform()
    
    def _go_to_live(self):
        """Only available in immediate mode."""
        self._show_seek_bar()

        session().driver.execute_script("document.getElementsByClassName(\"bmpui-ui-playbacktimelabel-live\")[0].click()")

        self._hide_seek_bar()

    def _jump(self):
        """Only available in share mode"""
        minutes = int(get_url_arg('m'))
        jump_seconds = int(get_url_arg('s')) + 60 * minutes

        seek_bar_elem = session().driver.find_element(By.CSS_SELECTOR, ".bmpui-controlbar-seekbar .bmpui-seekbar")
        total_time_elem = session().driver.find_element(By.CLASS_NAME, "bmpui-total-time")

        text = total_time_elem.get_attribute("innerText")
        parts = text.split(":")

        video_length_s = 0
        factor = 1
        for part in reversed(parts):
            video_length_s += int(part) * factor
            factor *= 60
        
        if jump_seconds < 0 or jump_seconds > video_length_s:
            return
        
        element_width = seek_bar_elem.size["width"]
        # Add one to make sure we always click inside the element if the user jumps to 0
        # This can happen due to floating point shenanigans
        target_click = (element_width * (jump_seconds / video_length_s) - element_width / 2) + 1

        self._show_seek_bar()

        # Click at the correct location to jump to the specified time:
        action = webdriver.ActionChains(session().driver)
        action.move_to_element(seek_bar_elem)
        action.move_by_offset(target_click, 0)
        action.click()
        action.perform()

        self._hide_seek_bar()

    def launch_immediate(self, parameter):
        open_browser(f"https://npo.nl/start/live/{parameter}")
        self._focus_player()

    def launch(self, params: dict[str, str]):
        open_browser(params["url"])
        self._focus_player()

def create():
    return [Npo("share"), Npo("immediate")]
