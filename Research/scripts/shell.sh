#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"

cd "$(dirname "$0")/../docker"

$DOCKER_BIN compose up -d
$DOCKER_BIN compose exec ros2_sim bash
