#!/bin/bash
source camerapiEnv/bin/activate
pytest -v --cov --cov-config=.coveragerc
curl --request POST --user coverage:arT3O0ylAHCsr0qevI8c9BPbpzKVPBNr --form "report=@coverage.xml" "http://marcelbruckner.spdns.de:8080/api/projects/camera-pi/external-analysis/session/auto-create/report?format=Cobertura&partition=Unit%20Tests&message=Unit%20Test%20Coverage"
