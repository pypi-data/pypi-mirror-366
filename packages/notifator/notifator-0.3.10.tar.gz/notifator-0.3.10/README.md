``` example
This is verbatim text

apt install libdbus-1-dev   python3-dev
# this heslp on ubuntu 24.04
sudo apt install libglib2.0-dev
```

# Project: notifator

*in development*

Initially, it was showing a text/number on raspberry HAT display matrix.
Other things were added later...

## Prerequisites

``` bash
sudo apt install libglib2.0-dev  # dbus-python problem
sudo -H apt install libdbus-1-dev # dbus-python problem
```

## Description:

The code provides CMD interface to different notifications. Currently
supported:

-   rpihat running text (test even without RPi) **h**
-   DBUS message for desktop **b**
-   terminal wall (problems appeared recently...)
-   myservice2 (? deprecated)
-   telegram **t**
-   ntfy.sh **n**
-   speak the message (TTS) via audio locally **s**
-   TTS multicast audio message /server **m** (in development)
-   TTS multicast audio message /client **c** (in development)

## Installation

``` {.bash org-language="sh"}
sudo -H apt install python3-dbus
pip3 install dbus-python
```
