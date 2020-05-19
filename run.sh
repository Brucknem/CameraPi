#!/bin/bash

source /home/pi/Repositories/Raspberry-Pi/camerapiEnv/bin/activate

/usr/bin/python3 /home/pi/Repositories/Raspberry-Pi/main.py -c 300 -o "/mnt/harddrive/recordings/"
