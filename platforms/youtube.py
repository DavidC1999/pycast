from pycast import *

class Youtube(Platform):
    def __init__(self):
        super().__init__(
            "YouTube",
            r".*(https?:\/\/(www\.)?)?youtube\.com\/watch\?v=(?P<id>[^?&#]+).*",
            (Action.toggleplay, lambda: sendkey("k")),
            (Action.fullscreen, lambda: sendkey("f")),
            (Action.bback, lambda: sendkey("j")),
            (Action.back, lambda: sendkey(Keys.ARROW_LEFT)),
            (Action.fforward, lambda: sendkey("l")),
            (Action.forward, lambda: sendkey(Keys.ARROW_RIGHT)),
            (Action.refresh, lambda: session().driver.refresh()),
            (Action.captions, lambda: sendkey("c")),
            (Action.jump, lambda: self._jump_action()),
        )

    def _open_youtube(self, id=None, time=None):
        url = f"https://www.youtube.com/watch?v={id}"

        if time:
            url += "&t=" + time
        
        open_browser(url)

    def _jump_action(self):
        close_browser()
        minutes = get_url_arg('m')
        seconds = get_url_arg('s')

        id = session().user_args
        self._open_youtube(id, f"{minutes}m{seconds}s")

    def launch(self, params: dict[str, str]):
        session().user_args = params["id"]
        self._open_youtube(session().user_args)

def create():
    return Youtube()
