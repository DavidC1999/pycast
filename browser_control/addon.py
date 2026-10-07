import math
import json
import threading

from flask import Flask, request
from flask_sock import Sock
from simple_websocket import ConnectionClosed
from werkzeug.serving import make_server

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765

app = Flask(__name__)
sock = Sock(app)

_initialized = False
_server = None
_server_thread = None
_server_lock = threading.Lock()
_connection = None
_connection_lock = threading.Lock()


@sock.route("/ws")
def websocket_route(websocket):
    global _connection

    origin = request.headers.get("Origin", "")
    if not origin.startswith("moz-extension://"):
        websocket.close(reason=1008, message="Firefox extension origin required")
        return

    with _connection_lock:
        if _connection is not None:
            try:
                _connection.close()
            except (ConnectionClosed, OSError):
                pass
        _connection = websocket

    try:
        while websocket.receive() is not None:
            pass
    except ConnectionClosed:
        pass
    finally:
        with _connection_lock:
            if _connection is websocket:
                _connection = None


def _start_socket_server():
    global _server, _server_thread

    with _server_lock:
        if _server_thread is not None:
            return

        _server = make_server(
            SERVER_HOST,
            SERVER_PORT,
            app,
            threaded=True,
        )
        _server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
        _server_thread.start()


def _stop_socket_server():
    global _server, _server_thread, _connection

    with _server_lock:
        server = _server
        server_thread = _server_thread
        _server = None
        _server_thread = None

    with _connection_lock:
        websocket = _connection
        _connection = None
        if websocket is not None:
            try:
                websocket.close()
            except (ConnectionClosed, OSError):
                pass

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


def _send_event(event: str, payload: dict | None = None) -> None:
    global _connection

    message = json.dumps({"event": event, **(payload or {})})
    with _connection_lock:
        if _connection is None:
            return
        try:
            _connection.send(message)
        except (ConnectionClosed, OSError):
            _connection = None


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
    _send_event("toggleplay")


def fullscreen() -> None:
    _send_event("fullscreen")


def backward(seconds: float = 10) -> None:
    _validate_seconds(seconds)
    _send_event("backward", {"seconds": seconds})


def forward(seconds: float = 10) -> None:
    _validate_seconds(seconds)
    _send_event("forward", {"seconds": seconds})


def refresh() -> None:
    _send_event("refresh")


def toggle_captions() -> None:
    _send_event("toggle_captions")


def seek(seconds: float) -> None:
    """Ask the extension to seek HTML5 videos to an absolute time in seconds."""
    _validate_seconds(seconds)
    _send_event("seek", {"time": seconds})