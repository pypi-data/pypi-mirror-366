#!/bin/bash
cd ~
sudo apt-get install python3 python3-pip pipx -y

git clone https://git.gzhang.xyz/GZhang/FG-mobile-joystick.git
cd FG-mobile-joystick/

# Tested with a Ubuntu 24.04 Termux Proot container.
# On some Debian-based distributions, these package can be installed with ONLY dpkg, not pip.
# Solution, use pipx
pipx install flask flask_cors flightgear-python

echo "alias mobilejoystick=\"python3 ~/FG-mobile-joystick/app.py\""


# Restart Bash to activate new alias
exec bash


