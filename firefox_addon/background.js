const DEFAULT_SERVER_URL = "ws://127.0.0.1:8765";
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

let socket = null;
let reconnectTimer = null;
let reconnectDelay = 1000;
let connectionGeneration = 0;

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

async function connect() {
    const generation = ++connectionGeneration;
    const { serverUrl } = await browser.storage.local.get({
        serverUrl: DEFAULT_SERVER_URL,
    });

    if (generation !== connectionGeneration) {
        return;
    }

    let connection;
    try {
        const socketUrl = new URL(serverUrl);
        socketUrl.pathname = "/socket.io/";
        socketUrl.search = "?EIO=4&transport=websocket";
        connection = new WebSocket(socketUrl);
    } catch (error) {
        console.error("PyCast: unable to create WebSocket", error);
        scheduleReconnect();
        return;
    }

    socket = connection;
    connection.addEventListener("open", () => {
        if (socket === connection) {
            reconnectDelay = 1000;
            console.info(`PyCast: connected to ${serverUrl}`);
        }
    });
    connection.addEventListener("message", (event) => {
        if (socket === connection) {
            handleSocketIoPacket(connection, event.data);
        }
    });
    connection.addEventListener("close", () => {
        if (socket === connection) {
            socket = null;
            scheduleReconnect();
        }
    });
    connection.addEventListener("error", () => connection.close());
}

function handleSocketIoPacket(connection, packet) {
    if (packet.startsWith("0")) {
        connection.send("40");
        return;
    }

    if (packet === "2") {
        connection.send("3");
        return;
    }

    if (!packet.startsWith("42")) {
        return;
    }

    try {
        const [eventName, payload = {}] = JSON.parse(packet.slice(2));
        if (ACTION_EVENTS.has(eventName)) {
            handleActionEvent(eventName, payload);
        }
    } catch (error) {
        console.warn("PyCast: ignoring invalid Socket.IO event", error);
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

browser.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== "local" || !changes.serverUrl) {
        return;
    }

    if (reconnectTimer !== null) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
    }
    if (socket !== null) {
        const previousSocket = socket;
        socket = null;
        previousSocket.close();
    }
    connect();
});

connect();