from pycast import *
from browser_control.ydotool import *
from urllib.parse import urlparse, parse_qs

from pydotool import KEY_K, KEY_F, KEY_LEFT, KEY_RIGHT, KEY_J, KEY_L, KEY_F5, KEY_C


class Youtube(Platform):
    def __init__(self):
        super().__init__(
            name="YouTube",
            id="youtube",
            actions=[
                (Action.toggleplay, lambda: sendkey(KEY_K)),
                (Action.fullscreen, lambda: sendkey(KEY_F)),
                (Action.bback, lambda: sendkey(KEY_J)),
                (Action.back, lambda:sendkey(KEY_LEFT)),
                (Action.fforward, lambda: sendkey(KEY_L)),
                (Action.forward, lambda: sendkey(KEY_RIGHT)),
                (Action.refresh, lambda: sendkey(KEY_F5)),
                (Action.captions, lambda: sendkey(KEY_C)),
                (Action.jump, lambda: self._jump_action()),
            ],
            regex=r".*?(?P<url>(https?:\/\/(www\.)?)?youtube\.com\/watch\?v=(?P<id>[^?&#]+).*)",
        )

    def _open_video(self, video_id, start_at=None):
        url = f"https://www.youtube.com/watch?v={video_id}"
        if start_at is not None:
            url += f"&t={start_at}s"

        print(f"Opening YouTube video: {url}")
        open_browser(url)

    def _jump_action(self):
        minutes = int(get_url_arg('m')) if get_url_arg('m') else 0
        seconds = int(get_url_arg('s')) if get_url_arg('s') else 0
        total_seconds = minutes * 60 + seconds
        close_browser()
        self._open_video(session().user_args, start_at=total_seconds)

    def launch(self, params: dict[str, str]):
        session().user_args = params["id"]

        parsed_url = urlparse(params["url"])
        parsed_query = parse_qs(parsed_url.query)

        start_at = None
        if 't' in parsed_query:
            start_at = parse_qs(parsed_url.query)['t'][0]

        self._open_video(params["id"], start_at)

    def cleanup(self):
        close_browser()


def create():
    return [Youtube()]
