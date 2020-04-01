#!/bin/sh

sudo cp nightsight.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nightsight.service
sudo systemctl start nightsight.service
sudo systemctl status nightsight.service
