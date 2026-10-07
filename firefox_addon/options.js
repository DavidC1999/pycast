const DEFAULT_SERVER_URL = "ws://127.0.0.1:8765";
const form = document.querySelector("#server-form");
const urlInput = document.querySelector("#server-url");
const status = document.querySelector("#status");

browser.storage.local
    .get({ serverUrl: DEFAULT_SERVER_URL })
    .then(({ serverUrl }) => {
        urlInput.value = serverUrl;
    });

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const serverUrl = urlInput.value.trim();

    if (!/^wss?:\/\//i.test(serverUrl)) {
        status.textContent = "Use a ws:// or wss:// URL.";
        return;
    }

    browser.storage.local.set({ serverUrl }).then(() => {
        status.textContent = "WebSocket server saved.";
    });
});