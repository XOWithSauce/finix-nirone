#!/bin/bash

sudo apt update && apt upgrade -y

sudo apt install python3-pip -y
# Use default Python 3.9.2 distributed from bullseye
sudo apt install python3-gi


pip install pybluez
pip install pyserial
pip install psutil
pip install dbus-python
pip install PyGObject