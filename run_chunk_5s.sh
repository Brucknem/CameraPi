#!/bin/bash

sudo systemctl stop camerapi.service

source /home/pi/Repositories/Raspberry-Pi/camerapiEnv/bin/activate

/usr/bin/python3 /home/pi/Repositories/Raspberry-Pi/main.py -c 5

sudo systemctl start camerapi.service
