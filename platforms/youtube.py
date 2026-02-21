from pycast import *

class Youtube(Platform):
    def __init__(self):
        super().__init__(
            name="YouTube",
            id="youtube",
            actions=[
                (Action.toggleplay, lambda: sendkey("k")),
                (Action.fullscreen, lambda: sendkey("f")),
                (Action.bback, lambda: sendkey("j")),
                (Action.back, lambda: sendkey(Keys.ARROW_LEFT)),
                (Action.fforward, lambda: sendkey("l")),
                (Action.forward, lambda: sendkey(Keys.ARROW_RIGHT)),
                (Action.refresh, lambda: session().driver.refresh()),
                (Action.captions, lambda: sendkey("c")),
                (Action.jump, lambda: self._jump_action()),
            ],
            regex=r".*?(?P<url>(https?:\/\/(www\.)?)?youtube\.com\/watch\?v=(?P<id>[^?&#]+).*)",
        )

    def _jump_action(self):
        minutes = get_url_arg('m')
        seconds = get_url_arg('s')

        id = session().user_args

        session().driver.get(f"https://www.youtube.com/watch?v={id}&t={minutes}m{seconds}s")

    def launch(self, params: dict[str, str]):
        session().user_args = params["id"]
        open_browser(params["url"])

def create():
    return [Youtube()]
