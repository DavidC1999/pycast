function getSeekBounds(video) {
    if (video.seekable.length > 0) {
        return [
            video.seekable.start(0),
            video.seekable.end(video.seekable.length - 1),
        ];
    }

    if (Number.isFinite(video.duration)) {
        return [0, video.duration];
    }
    return null;
}

function seekVideo(video, targetTime) {
    const bounds = getSeekBounds(video);
    if (bounds !== null) {
        targetTime = Math.max(bounds[0], Math.min(targetTime, bounds[1]));
    }
    video.currentTime = targetTime;
}

function getCaptionTracks(video) {
    return Array.from(video.textTracks).filter((track) =>
        track.kind === "captions" || track.kind === "subtitles",
    );
}

function showCaptions(video) {
    const tracks = getCaptionTracks(video);
    const selectedTrack = tracks.find((track) => track.mode === "showing") || tracks[0];
    for (const track of tracks) {
        track.mode = track === selectedTrack ? "showing" : "disabled";
    }
}

function toggleCaptions(video) {
    const tracks = getCaptionTracks(video);
    const hasShowingCaptions = tracks.some((track) => track.mode === "showing");

    if (hasShowingCaptions) {
        for (const track of tracks) {
            track.mode = "disabled";
        }
    } else {
        showCaptions(video);
    }
}

browser.runtime.onMessage.addListener((message) => {
    const video = document.querySelector("video");
    if (!video) {
        return;
    }

    try {
        switch (message.type) {
            case "pycast.seek":
                if (!Number.isFinite(message.time) || message.time < 0) {
                    return;
                }
                seekVideo(video, message.time);
                break;
            case "pycast.backward":
            case "pycast.forward": {
                const direction = message.type === "pycast.forward" ? 1 : -1;
                const seconds = Number.isFinite(message.seconds) && message.seconds >= 0
                    ? message.seconds
                    : 10;
                seekVideo(video, video.currentTime + direction * seconds);
                break;
            }
            case "pycast.toggleplay":
                if (video.paused) {
                    video.play().catch((error) =>
                        console.warn("PyCast: video playback was blocked", error),
                    );
                } else {
                    video.pause();
                }
                break;
            case "pycast.fullscreen":
                if (document.fullscreenElement) {
                    document.exitFullscreen().catch((error) =>
                        console.warn("PyCast: could not exit fullscreen", error),
                    );
                } else if (video.requestFullscreen) {
                    video.requestFullscreen().catch((error) =>
                        console.warn("PyCast: fullscreen was blocked", error),
                    );
                }
                break;
            case "pycast.toggle_captions":
                toggleCaptions(video);
                break;
            default:
                return;
        }
    } catch (error) {
        console.warn(`PyCast: could not run ${message.type}`, error);
    }

    return { videoFound: true };
});