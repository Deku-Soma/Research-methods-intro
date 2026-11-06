#!/bin/bash
set -e

if [ "$USE_HOST_DISPLAY" = "1" ] || [ "$USE_HOST_DISPLAY" = "true" ]; then
    echo "==============================================================="
    echo "  Host Display Mode Active (Hardware Acceleration Enabled)"
    echo "  Rendering directly to host display: ${DISPLAY:-:0}"
    echo "  noVNC service skipped."
    echo "==============================================================="
    if [ $# -gt 0 ]; then
        exec "$@"
    else
        tail -f /dev/null
    fi
fi

echo "Starting Xvfb display on :1 (1920x1080x24)..."
Xvfb :1 -screen 0 1920x1080x24 &
export DISPLAY=:1
sleep 1

echo "Starting Fluxbox window manager..."
fluxbox &
sleep 1

echo "Starting x11vnc server on port 5901..."
x11vnc -display :1 -forever -nopw -shared -rfbport 5901 -bg

echo "Starting noVNC web interface on port 6080..."
websockify --web=/usr/share/novnc 6080 localhost:5901 &

echo "noVNC running! Open http://localhost:6080/vnc.html in your browser."

# Keep alive or run command passed in
if [ $# -gt 0 ]; then
    exec "$@"
else
    tail -f /dev/null
fi
