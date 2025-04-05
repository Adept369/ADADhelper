#!/bin/bash
# start_app.sh
# This script starts ngrok and then launches Docker Compose

# Define the port your Flask app runs on
APP_PORT=5000
ngrok http --url=duck-healthy-easily.ngrok-free.app 5000
# Check if ngrok is already running
if ! pgrep -x "ngrok" > /dev/null; then
  echo "Starting ngrok tunnel on port $APP_PORT..."
  # Start ngrok in the background and log output to ngrok.log
  ngrok http $APP_PORT --log=stdout > ngrok.log 2>&1 &
  # Wait a few seconds for ngrok to initialize
  sleep 5
else
  echo "ngrok is already running."
fi

# Optionally, display the current ngrok tunnel status
echo "ngrok tunnels:"
curl --silent http://127.0.0.1:4040/api/tunnels | python3 -m json.tool

# Start Docker Compose to run your application containers
echo "Starting Docker Compose..."
docker compose up --build
