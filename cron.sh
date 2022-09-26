#!/bin/bash

EUID=$(id --real --user)
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$EUID/bus"
echo "DBUS_SESSION_BUS_ADDRESS $DBUS_SESSION_BUS_ADDRESS"

/usr/local/bin/python /home/cedric/.gnome-wallpaper/cron.py