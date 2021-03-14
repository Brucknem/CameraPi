#!/bin/sh

sudo systemctl stop camerapi.service
sudo cp camerapi.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable camerapi.service
sudo systemctl start camerapi.service
sudo systemctl status camerapi.service
