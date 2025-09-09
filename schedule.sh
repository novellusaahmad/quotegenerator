#!/bin/bash
# Schedule the application to start on boot via systemd
# Usage: ./schedule.sh

set -e

SERVICE_NAME=novellus-app
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
START_SCRIPT="$APP_DIR/start.sh"

if [ ! -f "$START_SCRIPT" ]; then
    echo "Error: $START_SCRIPT not found"
    exit 1
fi

cat <<SERVICE_EOF | sudo tee "$SERVICE_PATH" > /dev/null
[Unit]
Description=Novellus Loan Management System
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$START_SCRIPT
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE_EOF

sudo chmod 644 "$SERVICE_PATH"
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"

echo "Service '$SERVICE_NAME' installed and enabled to start at boot."
echo "You can start it now with: sudo systemctl start ${SERVICE_NAME}.service"
