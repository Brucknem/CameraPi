#!/bin/bash

source /home/pi/Repositories/CameraPi/venv/bin/activate

python CAMERA=pi RECORDINGS=/mnt/* /home/pi/Repositories/CameraPi/main.py
