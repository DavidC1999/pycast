import json
import subprocess
import json
from flask import request, render_template, current_app
from flask_sock import Sock
from pycast import session
from flask_app import app

# Global state for YouTube iframe control
_connected_clients = set()
_firefox_process = None
_sock = Sock(app)

_is_fullscreen = True

_player_status = ""

def cleanup():
    """Close the Firefox browser and clean up state."""
    global  _firefox_process
    
    if _firefox_process is not None:
        try:
            _firefox_process.terminate()
            _firefox_process.wait(timeout=5)
        except (subprocess.TimeoutExpired, Exception):
            try:
                _firefox_process.kill()
            except Exception:
                pass
        _firefox_process = None


def open_video(video_id, start_at=None, autoplay=None, cc_enabled=None, fullscreen=True):
    """Open a YouTube video in Firefox using the configured profile.
    
    Starts Firefox with the user's profile and opens the local iframe page.
    """
    global _firefox_process, _is_fullscreen

    cleanup()
    
    profile_dir = session().profile_dir
    
    # Get base URL from Flask request context if available, else use config
    try:
        base_url = request.url_root.rstrip('/')
    except RuntimeError:
        # No request context available, use config
        base_url = current_app.config.get('BASE_URL', 'http://localhost:8080')
    
    firefox_url = f"{base_url}/youtube-iframe?video_id={video_id}"

    if start_at is not None:
        firefox_url += f"&start_at={start_at}"

    if autoplay is not None:
        firefox_url += f"&autoplay={autoplay}"
    
    if cc_enabled is not None:
        firefox_url += f"&cc={cc_enabled}"
    
    _is_fullscreen = fullscreen

    try:
        command = ["firefox", "-profile", profile_dir]
        if _is_fullscreen:
            command.append("--kiosk")
        command.append(firefox_url)
        _firefox_process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        raise RuntimeError("Firefox not found in PATH")


@app.route("/youtube-iframe")
def youtube_iframe_page():
    return render_template("youtube_iframe.html")

@_sock.route("/youtube-commands")
def handle_ws(ws):
    """WebSocket endpoint for command delivery."""
    global _player_status
    
    _connected_clients.add(ws)
    try:
        # Keep the connection alive and listen (though we don't need incoming messages)
        while True:
            try:
                data = ws.receive(timeout=30)
                _player_status = data
            except Exception:
                break
    finally:
        _connected_clients.discard(ws)

def get_status():
    if not _player_status:
        return None
    
    output = json.loads(_player_status)

    output["is_fullscreen"] = _is_fullscreen

    return output

def send_command(command: str, payload: dict = None):
    global _waiting_for_fullscreen_toggle

    """Send a command to the YouTube player via WebSocket.
    
    Sends to all connected clients. If no clients are connected, queues the command.
    
    Args:
        command: Command name (e.g., "play", "pause", "seek")
        payload: Optional dict with command parameters
    """

    cmd_obj = {"command": command}
    if payload:
        cmd_obj.update(payload)
    
    cmd_json = json.dumps(cmd_obj)
    
    # Send to all connected clients
    for client in list(_connected_clients):
        try:
            client.send(cmd_json)
        except Exception:
            _connected_clients.discard(client)
