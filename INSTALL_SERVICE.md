# Installing GPS Bot as a Service on Alpine Linux

This guide will help you set up the Gmail to Discord Relay Bot as a service that starts automatically on boot and restarts if it crashes.

## Prerequisites

- Alpine Linux VM
- Python 3.8 or higher installed
- Bot code already set up and working

## Installation Steps

### 1. Edit Configuration Files

First, edit the service files to match your environment:

1. Edit `run_bot.sh`:
   ```sh
   # Change this to your actual installation path
   APP_DIR="/path/to/gmail_discord_relay"
   ```

2. Edit `gps-bot.initd`:
   ```sh
   # Change to your VM username
   command_user="yourusername"
   
   # Change to your actual installation path
   directory="/path/to/gmail_discord_relay"
   ```

### 2. Make the Run Script Executable

```sh
chmod +x run_bot.sh
```

### 3. Install the Service

1. Copy the service file to the init.d directory:
   ```sh
   sudo cp gps-bot.initd /etc/init.d/gps-bot
   ```

2. Make it executable:
   ```sh
   sudo chmod +x /etc/init.d/gps-bot
   ```

3. Add the service to the default runlevel:
   ```sh
   sudo rc-update add gps-bot default
   ```

### 4. Start the Service

```sh
sudo rc-service gps-bot start
```

### 5. Check the Status

```sh
sudo rc-service gps-bot status
```

### 6. View Logs

```sh
tail -f /var/log/gps-bot.log
```

## Managing the Service

- **Start the service:**
  ```sh
  sudo rc-service gps-bot start
  ```

- **Stop the service:**
  ```sh
  sudo rc-service gps-bot stop
  ```

- **Restart the service:**
  ```sh
  sudo rc-service gps-bot restart
  ```

## Troubleshooting

If the service fails to start:

1. Check the logs:
   ```sh
   tail -f /var/log/gps-bot.log
   ```

2. Verify the paths in the service files are correct.

3. Make sure the bot's dependencies are installed:
   ```sh
   cd /path/to/gmail_discord_relay
   pip install -r requirements.txt
   ```

4. Test running the bot manually:
   ```sh
   cd /path/to/gmail_discord_relay
   python3 src/main.py
   ```

## Notes

- The bot will automatically restart if it crashes or if it's stopped using the `/die` command in Discord.
- There will be a 10-second delay between restarts to prevent rapid cycling if there's a persistent error.
