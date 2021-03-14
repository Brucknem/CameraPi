#!/bin/bash
ng build --prod --output-path docs --base-href /CameraPi/ 
cp docs/index.html docs/404.html

git add . --all

timestamp=$(date +"%Y-%m-%d %T")
git commit -m="Deploying web UI [$timestamp]"
git push
