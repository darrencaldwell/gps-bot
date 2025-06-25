#!/bin/sh

# Wrapper script for Gmail to Discord Relay Bot
# This script activates the virtual environment and runs the bot
# It will always restart the bot, even after a /die command

# Change to the application directory
APP_DIR="/path/to/gmail_discord_relay"
cd "$APP_DIR" || exit 1

# Log file
LOG_FILE="$APP_DIR/bot.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Log startup
log_message "Starting GPS Bot wrapper script"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    log_message "Activating virtual environment"
    # shellcheck disable=SC1091
    . .venv/bin/activate
fi

# Run the bot with automatic restart
while true; do
    log_message "Starting GPS Bot"
    python3 src/main.py
    
    EXIT_CODE=$?
    log_message "Bot exited with code $EXIT_CODE"
    
    # Always restart, even after a clean exit from /die command
    log_message "Restarting bot in 10 seconds..."
    sleep 10
done
