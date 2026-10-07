const SERVER_URL = "ws://127.0.0.1:8765/ws";
const MAX_RECONNECT_DELAY = 30000;
const ACTION_EVENTS = new Set([
    "toggleplay",
    "fullscreen",
    "backward",
    "forward",
    "refresh",
    "toggle_captions",
    "seek",
]);

let reconnectTimer = null;
let reconnectDelay = 1000;

function scheduleReconnect() {
    if (reconnectTimer !== null) {
        return;
    }

    reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        connect();
    }, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
}

function connect() {
    let connection;
    try {
        connection = new WebSocket(SERVER_URL);
    } catch (error) {
        console.error("PyCast: unable to create WebSocket", error);
        scheduleReconnect();
        return;
    }

    connection.addEventListener("open", () => {
        reconnectDelay = 1000;
        console.info(`PyCast: connected to ${SERVER_URL}`);
    });
    connection.addEventListener("message", (event) => {
        handleWebSocketMessage(event.data);
    });
    connection.addEventListener("close", scheduleReconnect);
    connection.addEventListener("error", () => connection.close());
}

function handleWebSocketMessage(message) {
    try {
        const { event: eventName, ...payload } = JSON.parse(message);
        if (ACTION_EVENTS.has(eventName)) {
            handleActionEvent(eventName, payload);
        }
    } catch (error) {
        console.warn("PyCast: ignoring invalid WebSocket message", error);
    }
}

function handleActionEvent(eventName, payload) {
    if (eventName === "seek" && (!Number.isFinite(payload.time) || payload.time < 0)) {
        console.warn("PyCast: ignoring invalid seek time");
        return;
    }

    if (["backward", "forward"].includes(eventName) &&
        (!Number.isFinite(payload.seconds) || payload.seconds < 0)) {
        console.warn(`PyCast: ignoring invalid ${eventName} duration`);
        return;
    }

    browser.tabs
        .query({ active: true, lastFocusedWindow: true })
        .then((tabs) => {
            const activeTab = tabs[0];
            if (!activeTab) {
                return;
            }

            if (eventName === "refresh") {
                return browser.tabs.reload(activeTab.id);
            }

            return browser.webNavigation
                .getAllFrames({ tabId: activeTab.id })
                .then((frames) =>
                    Promise.all(
                        frames.map((frame) =>
                            browser.tabs.sendMessage(
                                activeTab.id,
                                { type: `pycast.${eventName}`, ...payload },
                                { frameId: frame.frameId },
                            ),
                        ),
                    ),
                );
        })
        .catch((error) => console.warn(`PyCast: could not run ${eventName}`, error));
}

connect();