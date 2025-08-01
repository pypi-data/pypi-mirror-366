#!/bin/bash

sudo apt-get install python3 python3-pip pipx -y


# Tested with a Ubuntu 24.04 Termux Proot container.
# On some Debian-based distributions, these package can be installed with ONLY dpkg, not pip.
# Solution, use pipx
pipx install fg-mobileJoystick

# Ensure ~/.local/bin/ is in $PATH
pipx ensurepath


# Restart Bash to activate new PATH
exec bash

mobileJoystick

