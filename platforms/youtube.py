from pycast import *

class Youtube(Platform):
    def __init__(self):
        super().__init__(
            "youtube.html",
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

    def launch(self):
        session().user_args = get_url_arg("id")
        self._open_youtube(session().user_args)

def create():
    return Youtube()