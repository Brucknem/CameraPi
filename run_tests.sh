#!/bin/bash
sudo systemctl stop camerapi.service

source camerapiEnv/bin/activate

flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=camerapiEnv
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=camerapiEnv

verbose=false
for arg in "$@"; do
  if [ "$arg" == "-s" ]; then
    verbose=true
  break
  fi
done

if [ "$verbose" = true ]; then
  pytest -v -s --cov --cov-config=.coveragerc --cov-report=xml
else
  pytest -v --cov --cov-config=.coveragerc --cov-report=xml
fi

for arg in "$@"; do
  if [ "$arg" == "-u" ]; then
    echo "Uploading coverage"
    curl --request POST --user coverage:arT3O0ylAHCsr0qevI8c9BPbpzKVPBNr --form "report=@coverage.xml" "http://marcelbruckner.spdns.de:8080/api/projects/camera-pi/external-analysis/session/auto-create/report?format=Cobertura&partition=Unit%20Tests&message=Unit%20Test%20Coverage"
    break
  fi
done

sudo systemctl start camerapi.service

