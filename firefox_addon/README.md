# PyCast Firefox Controls

This Firefox extension connects to the Flask-SocketIO server started by
`browser_control/addon.py` and controls HTML5 videos in the active tab.

## Install for testing

1. Open `about:debugging#/runtime/this-firefox` in Firefox.
2. Choose **Load Temporary Add-on...** and select `manifest.json` from this folder.
3. Open the extension's settings and enter the WebSocket server URL. The default
   is `ws://127.0.0.1:8765`.

## Commands

Python methods emit named Socket.IO events. For example, `addon.seek(42)` emits:

```json
42["seek",{"time":42}]
```

`toggleplay`, `fullscreen`, `refresh`, and `toggle_captions` are payload-free events. `forward(seconds=10)` and
`backward(seconds=10)` emit a `seconds` payload.

The extension reconnects with an increasing delay if the server is unavailable
and applies media commands to HTML5 videos in the active tab and its frames.