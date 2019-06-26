#!/usr/bin/env bash

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

set -e
app_name='diegoreico/twitter-bot-detector'
git_commit=$(git rev-parse --short HEAD)
build_date=$(date -u +"%Y-%m-%dT%H:%MZ")
tag=${1:-latest}

docker build --build-arg git_commit=${git_commit} \
             --build-arg build_date=${build_date} \
             -t ${app_name}:${tag} .
