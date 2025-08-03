#!/bin/zsh

# ---------------------------------------------------------
# shell script -- to automate generichelpers streamlit app
# Make executable with: chmod +x run_streamlit.sh
# ---------------------------------------------------------
# CONFIG: Customized all configs
PORT=8503
INTERFACE="Wi-Fi"
STATIC_IP="192.168.31.22"
SUBNET_MASK="255.255.255.0"
ROUTER_IP="192.168.31.1"

HOME_DIR="/Users/ratnadipadhikari/Library/CloudStorage/OneDrive-TIGERANALYTICS"
VENV_PATH="$HOME_DIR/.venv_ratnadip_p3.11/bin/activate"
APP_DIR="$HOME_DIR/TigerAnalytics/generic-helpers/src/generichelpers"
LOG_FILE="$HOME_DIR/streamlit-app.log"

# Set static IP
echo "🌐 Setting static IP to $STATIC_IP on $INTERFACE..."
sudo networksetup -setmanual "$INTERFACE" $STATIC_IP $SUBNET_MASK $ROUTER_IP
sudo networksetup -setdnsservers "$INTERFACE" 8.8.8.8 8.8.4.4
# networksetup -setdhcp "Wi-Fi"  [for reverting to DHCP]

# Check if venev exists and then activate
if [ ! -f "$VENV_PATH" ]; then
  echo "❌ Virtual environment not found at: $VENV_PATH"
  exit 1
fi
source "$VENV_PATH"
cd "$APP_DIR" || exit 1

# Prevent system sleep while this script is running
caffeinate -s -w $$ &

# Run the streamlit app
streamlit run appst.py \
    --server.port "$PORT" \
    --server.address 0.0.0.0 \
    --server.runOnSave true \
    >> "$LOG_FILE" 2>&1

<< //
# Start ngrok tunnel
STREAMLIT_PID=$!
sleep 5

echo "🌍 Starting ngrok tunnel for port $PORT..."
ngrok http $PORT >> "$LOG_FILE" 2>&1 &
NGROK_PID=$!

sleep 5

# Print public URL
PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o "https://[a-zA-Z0-9.-]*\.ngrok\.io" | head -n 1)
echo "✅ Public ngrok URL: $PUBLIC_URL"

# Show final status
echo "📡 Your app is live at: $PUBLIC_URL"
echo "📝 Logs: $LOG_FILE"
echo "🛑 Press Ctrl+C to stop"

# Keep the script alive while Streamlit is running
wait $STREAMLIT_PID
//
