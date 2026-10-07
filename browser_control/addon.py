import math
import subprocess
import threading

from flask import Flask
from flask_socketio import SocketIO
from werkzeug.serving import make_server

from pycast import session

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765

app = Flask(__name__)
socketio = SocketIO(
    app,
    async_mode="threading",
    cors_allowed_origins=lambda origin: origin is not None
    and origin.startswith("moz-extension://"),
)

_initialized = False
_server = None
_server_thread = None
_server_lock = threading.Lock()


def _start_socket_server():
    global _server, _server_thread

    with _server_lock:
        if _server_thread is not None and _server_thread.is_alive():
            return

        _server = make_server(
            SERVER_HOST,
            SERVER_PORT,
            socketio.sockio_mw,
            threaded=True,
        )
        _server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
        _server_thread.start()


def _stop_socket_server():
    global _server, _server_thread

    with _server_lock:
        server = _server
        server_thread = _server_thread
        _server = None
        _server_thread = None

    if server is not None:
        server.shutdown()
        server.server_close()
    if server_thread is not None and server_thread.is_alive():
        server_thread.join(timeout=2)


def _validate_seconds(seconds: float) -> None:
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        raise TypeError("seconds must be a number")
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("seconds must be a finite, non-negative number")

def init():
    global _initialized
    if not _initialized:
        _start_socket_server()
        _initialized = True

def cleanup():
    global _initialized
    if _initialized:
        _stop_socket_server()
        _initialized = False

def toggleplay() -> None:
    socketio.emit("toggleplay")


def fullscreen() -> None:
    socketio.emit("fullscreen")


def backward(seconds: float = 10) -> None:
    _validate_seconds(seconds)
    socketio.emit("backward", {"seconds": seconds})


def forward(seconds: float = 10) -> None:
    _validate_seconds(seconds)
    socketio.emit("forward", {"seconds": seconds})


def refresh() -> None:
    socketio.emit("refresh")


def toggle_captions() -> None:
    socketio.emit("toggle_captions")


def seek(seconds: float) -> None:
    """Ask the extension to seek HTML5 videos to an absolute time in seconds."""
    _validate_seconds(seconds)
    socketio.emit("seek", {"time": seconds})