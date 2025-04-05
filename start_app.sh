#!/bin/bash
# Enhanced startup for Caelum's Neurodivergent Assistant

APP_PORT=5000
NGROK_DOMAIN="duck-healthy-easily.ngrok-free.app"

# Load .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "✅ Loaded environment variables from .env"
fi

# Create required folders if missing
mkdir -p app/static/audio uploads exports

# Start ngrok if not already running
if ! pgrep -x "ngrok" > /dev/null; then
  echo "🌀 Starting ngrok tunnel on port $APP_PORT..."
  ngrok http --domain=$NGROK_DOMAIN $APP_PORT --log=stdout > ngrok.log 2>&1 &
  sleep 5
else
  echo "🌀 ngrok already running."
fi

# Display current tunnel status
echo "🌐 ngrok tunnels:"
curl --silent http://127.0.0.1:4040/api/tunnels | python3 -m json.tool

# Optional: Run Python DB initializer
if [ -f "init_system.py" ]; then
  echo "🛠️ Initializing database tables..."
  python3 init_system.py
fi

# Start Docker Compose
echo "🐳 Starting Docker Compose..."
docker compose up --build
