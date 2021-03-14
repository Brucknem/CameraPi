#!/bin/bash

source /home/pi/Repositories/CameraPi/venv/bin/activate

CAMERA=pi RECORDINGS=/mnt/* python /home/pi/Repositories/CameraPi/main.py
