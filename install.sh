#!/usr/bin/env bash

BASE_DIR=$(dirname $(realpath $BASH_SOURCE))

if ! command -v dpkg >/dev/null 2>&1
then
    echo "This script only works on debian with dpkg"
    exit 1
fi

if ! command -v apt >/dev/null 2>&1
then
    echo "This script only works on debian with apt"
    exit 1
fi

if ! command -v firefox >/dev/null 2>&1
then
    echo "PyCast only works with Firefox installed"
    exit 1
fi

if [ "$XDG_SESSION_TYPE" != "x11" ]
then
    echo "PyCast only works on x11"
fi


if ! dpkg -s xdotool > /dev/null 2>&1
then
    echo xdotool not found
    read -p "Do you wish to install it right now? [yn]" yn
    case $yn in
        [Yy]* ) sudo apt install xdotool; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
fi

if ! dpkg -s python3-venv > /dev/null 2>&1
then
    echo python3-venv not found
    read -p "Do you wish to install it right now? [yn]" yn
    case $yn in
        [Yy]* ) sudo apt install python3-venv; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
fi

if command -v deactivate >/dev/null 2>&1
then
    echo "Already in Python virtual environment. Deactivating..."
    deactivate
fi

if [ ! -f ".venv/bin/activate" ]
then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install -r requirements.txt

echo Creating firefox profile...
firefox -CreateProfile pycast

read -p "Do you wish to start PyCast as a systemd daemon? [yn]" yn
case $yn in
    [Yy]* ) ;;
    * ) exit 0;;
esac

if ! command -v systemctl >/dev/null 2>&1
then
    echo "Running PyCast as a daemon only works with systemd as the init system"
    exit 1
fi

echo Creating service file locally...
sed -e "s|@basedir@|$BASE_DIR|g" \
    -e "s|@user@|$USER|g"\
    -e "s|@userid@|$(id -u)|g"\
    pycast.service.template > pycast.service

link_dir=/etc/systemd/system
link_name=pycast.service
link_path=$link_dir/$link_name
if [ -L ${link_path} ] ; then
    echo "Symlink already exists. Removing..."
    sudo rm ${link_path}
fi

echo Creating symlink in /etc/systemd/system...
sudo ln -s $(pwd)/pycast.service /etc/systemd/system

echo Enabling the pycast service
sudo systemctl enable pycast