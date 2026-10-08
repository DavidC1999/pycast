# PyCast

PyCast gives you a cast-like way to start and control online video on a media PC, although in does not actually cast or stream video from your phone. The media PC opens and plays the video itself in Firefox; your phone is a remote control and a convenient way to send it a video link.

## How It Works

- PyCast runs as a Python web app on the media PC.
- A PWA is installed on your phone. A video from a supported platform can be shared from an app on your phone, such as YouTube, to PyCast. The PWA sends the link to the Python app, opens the video in Firefox on the media PC.
- The Firefox add-on communicates with PyCast to control the video playback. PyCast also uses `ydotool` to send keyboard controls where needed.
- You can now use your phone to play/pause the video, jump to a timestamp, and more.

## Supported Platforms

- YouTube videos
- NPO (Dutch public broadcaster) video links
- NPO 1, 2, and 3 livestreams 

Other video services are not currently supported. Pull requests for support of more platforms are welcomed.

## Requirements

- A Linux distribution on the media PC. PyCast should be able to run on any Linux distribution that can provide its dependencies. The convenience install script is Debian-specific for now.
- Firefox installed on the media PC.
- A phone and media PC that can reach each other over the local network.

## Installation

For Debian-based distros there is a convenience install script.

From the project directory, run:

```bash
./install.sh
```

The script requires Debian's `dpkg` and `apt` tools among other dependencies. On another Linux distribution, you can still run PyCast, but you will need to install its dependencies, build and install `ydotool`, and configure Firefox and any desired service manually.

The script updates apt package metadata and installs missing build prerequisites (`python3-venv`, `make`, `cmake`, and `scdoc`) when needed. It initializes the bundled `ydotool` submodule if necessary, builds and installs `ydotool`, creates a Python virtual environment, and installs the packages in `requirements.txt`. It also packages the Firefox add-on and generates Firefox policy configuration to install that add-on.

The script asks whether to run PyCast as a systemd service. If accepted, it generates the service configuration, registers and enables the PyCast and `ydotoold` services, and starts them. This service option requires systemd. The script uses `sudo` for system package installation and system-wide Firefox/systemd configuration; it may also run `git pull --recurse-submodules` when it needs to build `ydotool`.

## Using PyCast

1. Install PyCast using the installation script or manually
2. Install the PWA from [davidc1999.github.io/pycast](https://davidc1999.github.io/pycast/) on your phone
3. Open the PWA and configure the hostname of your media PC
4. Create and setup your desired Firefox profiles. More information in the "Firefox profiles" chapter
5. Share a supported video from an app such as YouTube to PyCast. Firefox on the media PC will open the video, and the PWA will show the available controls.

## Firefox Profiles

PyCast creates its default Firefox profile, named `pycast`, if it does not already exist. Any additional profile you want to use must be created manually in Firefox on the media PC before selecting its name on the phone page.

Open each profile on the media PC and configure it before using it with PyCast:

- Allow DRM-controlled content in Firefox settings so protected video can play.
- Set autoplay permissions to allow audio and video.
- Install any Firefox add-ons you prefer and sign in to supported platforms with your personal accounts.

You can select an existing profile by its name on the phone page. Profiles keep their own settings, add-ons, and account sessions.