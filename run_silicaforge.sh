#!/usr/bin/env bash
# ==============================================================================
# SilicaForge-RL - 1-Click Desktop Launcher
# 28.5 MW Submerged Arc Furnace 3D Digital Twin & Autonomous SCADA
# ==============================================================================

PROJECT_DIR="/home/piet/Desktop/harsh /rl project"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="$PROJECT_DIR/logs"
ICON_PATH="$PROJECT_DIR/silicaforge_logo.png"
PORT=5173
URL="http://localhost:${PORT}/"

mkdir -p "$LOG_DIR"
exec >> "$LOG_DIR/launcher.log" 2>&1
echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Launching SilicaForge-RL ==="

# 1. Desktop Notification
if command -v notify-send >/dev/null 2>&1; then
    notify-send -i "$ICON_PATH" "SilicaForge-RL" "Starting 28.5 MW Submerged Arc Furnace Digital Twin on port $PORT..."
fi

# 2. Check if Vite dev server is already running
CHECK_HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")

if [ "$CHECK_HTTP" = "200" ]; then
    echo "Server already running on $URL."
else
    echo "Starting Vite dev server on $PORT..."
    cd "$FRONTEND_DIR" || exit 1
    # Run detached in a new session via setsid & disown
    setsid npx vite --port "$PORT" --host 0.0.0.0 > "$LOG_DIR/vite_server.log" 2>&1 &
    SERVER_PID=$!
    disown $SERVER_PID 2>/dev/null || true
    echo "Vite server process PID: $SERVER_PID"

    # Wait for server to become responsive (up to 12 seconds)
    READY=0
    for i in $(seq 1 24); do
        sleep 0.5
        CHECK_HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")
        if [ "$CHECK_HTTP" = "200" ]; then
            READY=1
            echo "Server became healthy after $((i * 500)) ms."
            break
        fi
    done

    if [ "$READY" -eq 0 ]; then
        echo "Warning: Server took longer than expected to report HTTP 200, proceeding to open browser."
    fi
fi

# 3. Open Browser
echo "Opening browser at $URL"
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v google-chrome >/dev/null 2>&1; then
    google-chrome "$URL" >/dev/null 2>&1 &
elif command -v firefox >/dev/null 2>&1; then
    firefox "$URL" >/dev/null 2>&1 &
fi

if command -v notify-send >/dev/null 2>&1; then
    notify-send -i "$ICON_PATH" "SilicaForge-RL Ready" "Digital Twin running live at $URL"
fi

echo "Launcher completed successfully."
exit 0
