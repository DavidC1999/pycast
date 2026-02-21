from pycast import *

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located, visibility_of_element_located
from selenium.webdriver.common.by import By

class Npo(Platform):
    def __init__(self):
        super().__init__(
            "NPO",
            r".*?(?P<url>https?://(www\.)?npo\.nl/?([^\/\n]+\/)*[^\/\n]+).*",
            (Action.toggleplay, lambda: sendkey(Keys.SPACE)),
            (Action.fullscreen, lambda: sendkey("f")),
            (Action.back, lambda: sendkey(Keys.ARROW_LEFT)),
            (Action.forward, lambda: sendkey(Keys.ARROW_RIGHT)),
            (Action.refresh, lambda: session().driver.refresh()),
            (Action.captions, lambda: sendkey("c")),
            (Action.jump, lambda: self._jump()),
        )

    def _focus_player(self):
        WebDriverWait(session().driver, 20)\
            .until(presence_of_element_located((By.ID, "bitmovinplayer-video-null")))
        
        # Focus the video player so keypesses can influence the playback
        session().driver.execute_script("document.getElementById(\"bitmovinplayer-video-null\").focus()")

    def _jump(self):
        minutes = int(get_url_arg('m'))
        jump_seconds = int(get_url_arg('s')) + 60 * minutes

        player_elem = session().driver.find_element(By.CLASS_NAME, "bitmovinplayer-container")
        seek_bar_elem = session().driver.find_element(By.CSS_SELECTOR, ".bmpui-controlbar-seekbar .bmpui-seekbar")
        total_time_elem = session().driver.find_element(By.CLASS_NAME, "bmpui-total-time")

        text = total_time_elem.get_attribute("innerText")
        parts = text.split(":")

        video_length_s = 0
        factor = 1
        for part in reversed(parts):
            video_length_s += int(part) * factor
            factor *= 60
        
        element_width = seek_bar_elem.size["width"]
        target_click = element_width * (jump_seconds / video_length_s) - element_width / 2

        # Get the seek bar to show by moving the mouse:
        action = webdriver.ActionChains(session().driver)
        action.move_to_element(player_elem)
        action.move_by_offset(10, 0)
        action.perform()

        # Wait until the seek bar is visible
        WebDriverWait(session().driver, 10)\
            .until(visibility_of_element_located((By.CSS_SELECTOR, ".bmpui-controlbar-seekbar .bmpui-seekbar")))

        # Click at the correct location to jump to the specified time:
        action = webdriver.ActionChains(session().driver)
        action.move_to_element(seek_bar_elem)
        action.move_by_offset(target_click, 0)
        action.click()
        action.perform()

        # Move the mouse out of the way to the seekbar disappears again:
        action = webdriver.ActionChains(session().driver)
        action.move_to_element(player_elem)
        action.perform()

        

    def launch(self, params: dict[str, str]):
        open_browser(params["url"])

        self._focus_player()

def create():
    return Npo()
