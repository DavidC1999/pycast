from pycast import *
from browser_control.youtube_iframe import *
from urllib.parse import urlparse, parse_qs

class Youtube(Platform):
    def __init__(self):
        super().__init__(
            name="YouTube",
            id="youtube",
            actions=[
                (Action.toggleplay, lambda: send_command("togglePlay")),
                (Action.fullscreen, lambda: self._toggle_fullscreen_action()),
                (Action.bback, lambda: send_command("seek", {"seconds": -10})),
                (Action.back, lambda: send_command("seek", {"seconds": -5})),
                (Action.fforward, lambda: send_command("seek", {"seconds": 10})),
                (Action.forward, lambda: send_command("seek", {"seconds": 5})),
                (Action.refresh, lambda: send_command("reload")),
                (Action.captions, lambda: send_command("toggleCaptions")),
                (Action.jump, lambda: self._jump_action()),
            ],
            regex=r".*?(?P<url>(https?:\/\/(www\.)?)?youtube\.com\/watch\?v=(?P<id>[^?&#]+).*)",
        )

    def _jump_action(self):
        minutes = int(get_url_arg('m')) if get_url_arg('m') else 0
        seconds = int(get_url_arg('s')) if get_url_arg('s') else 0
        total_seconds = minutes * 60 + seconds
        send_command("jump", {"seconds": total_seconds})
    
    def _toggle_fullscreen_action(self):
        status = get_status()

        if status is None:
            return
        
        cleanup()  # Close the current video and reset state
        open_video(
            session().user_args,
            start_at=status["current_time"],
            autoplay=status["is_playing"],
            cc_enabled=status["cc_enabled"],
            fullscreen=not status["is_fullscreen"])

    def launch(self, params: dict[str, str]):
        session().user_args = params["id"]

        parsed_url = urlparse(params["url"])
        parsed_query = parse_qs(parsed_url.query)

        start_at = None
        if 't' in parsed_query:
            start_at = parse_qs(parsed_url.query)['t'][0]

        open_video(params["id"], start_at=start_at)

    def cleanup(self):
        cleanup()

def create():
    return [Youtube()]
