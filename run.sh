#!/bin/bash

script_path='/home/pi/Repositories/CameraPi/'
venv_path=$script_path'venv'
virtualenv --python=/usr/bin/python3.7 $venv_path
source $venv_path'/bin/activate'
pip install -r $script_path'requirements.txt'
CAMERA=pi RECORDINGS=/mnt/* gunicorn --worker-class gevent --threads 20 --workers 1 --bind 0.0.0.0:9090 --chdir $script_path lib.api:provider
