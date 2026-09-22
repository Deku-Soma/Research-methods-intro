#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"
if ! command -v "$DOCKER_BIN" &> /dev/null; then
    DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
fi

cd "$(dirname "$0")/../docker"

$DOCKER_BIN compose up -d
$DOCKER_BIN compose exec ros2_sim bash
