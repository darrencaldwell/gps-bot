# Setting Up Gmail to Discord Relay Bot on Alpine Linux VM

This guide will help you set up the Gmail to Discord Relay Bot on your Alpine Linux VM, including handling authentication without a browser and setting up the bot to run on boot.

## Step 1: Install Dependencies

```bash
# Update package list
apk update

# Install Python and pip
apk add python3 py3-pip

# Install git (if not already installed)
apk add git

# Install development tools (needed for some Python packages)
apk add gcc python3-dev musl-dev
```

## Step 2: Clone the Repository (if you haven't already)

```bash
git clone <your-repository-url> /root/gps-bot
cd /root/gps-bot
```

## Step 3: Set Up a Virtual Environment (Optional but Recommended)

```bash
# Install virtualenv
pip3 install virtualenv

# Create a virtual environment
python3 -m virtualenv .venv

# Activate the virtual environment
source .venv/bin/activate
```

## Step 4: Install Required Packages

```bash
pip install -r requirements.txt
```

## Step 5: Make Scripts Executable

```bash
chmod +x run_bot.sh
chmod +x authenticate.py
```

## Step 6: Authenticate with Gmail API

This step uses the console-based authentication flow, which doesn't require a browser on the VM:

```bash
./authenticate.py
```

Follow the instructions:
1. The script will display a URL
2. Copy this URL and open it in a browser on your local machine (not the VM)
3. Log in with your Google account and grant the requested permissions
4. You'll receive an authorization code
5. Copy this code and paste it back into the console on your VM
6. Press Enter

If successful, a token will be saved to `config/token.json`.

## Step 7: Test the Bot

```bash
./run_bot.sh
```

The bot should start and connect to both Gmail and Discord. Check for any error messages.

## Step 8: Set Up as a Service

### Create an OpenRC Service File

Create a file at `/etc/init.d/gps-bot` with the following content:

```bash
#!/sbin/openrc-run

name="GPS Bot"
description="Gmail to Discord Relay Bot for inReach messages"

# Set the user to run the service
command_user="root"  # Change if needed

# Path to the application
directory="/root/gps-bot"  # Change to your actual path
command="/root/gps-bot/run_bot.sh"  # Change to your actual path

# PID file
pidfile="/var/run/${RC_SVCNAME}.pid"

# Log file
logfile="/var/log/${RC_SVCNAME}.log"

# Dependencies
depend() {
    need net
    after firewall
}

start_pre() {
    # Ensure the log directory exists
    checkpath --directory --owner $command_user:$command_user --mode 0755 /var/log
    
    # Ensure the directory exists
    if [ ! -d "$directory" ]; then
        eerror "Directory $directory does not exist"
        return 1
    fi
    
    # Ensure the run script exists
    if [ ! -f "${command}" ]; then
        eerror "Script ${command} does not exist"
        return 1
    fi
    
    # Make sure the run script is executable
    chmod +x "${command}"
}

start() {
    ebegin "Starting ${name}"
    start-stop-daemon --start \
        --pidfile "${pidfile}" \
        --make-pidfile \
        --background \
        --user "${command_user}" \
        --chdir "${directory}" \
        --stdout "${logfile}" \
        --stderr "${logfile}" \
        --exec "${command}"
    eend $?
}

stop() {
    ebegin "Stopping ${name}"
    start-stop-daemon --stop \
        --pidfile "${pidfile}" \
        --retry TERM/30/KILL/5
    eend $?
}

restart() {
    stop
    sleep 1
    start
}
```

### Make the Service File Executable

```bash
chmod +x /etc/init.d/gps-bot
```

### Add the Service to the Default Runlevel

```bash
rc-update add gps-bot default
```

### Start the Service

```bash
rc-service gps-bot start
```

### Check the Status

```bash
rc-service gps-bot status
```

## Step 9: View Logs

```bash
tail -f /var/log/gps-bot.log
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Delete the existing token:
   ```bash
   rm config/token.json
   ```

2. Run the authentication script again:
   ```bash
   ./authenticate.py
   ```

### Import Errors

If you see import errors:

1. Make sure you're using the run_bot.sh script, which sets the PYTHONPATH correctly
2. If running manually, set the PYTHONPATH:
   ```bash
   export PYTHONPATH="/root/gps-bot:$PYTHONPATH"
   python3 -m src.main
   ```

### Service Startup Issues

If the service fails to start:

1. Check the logs:
   ```bash
   tail -f /var/log/gps-bot.log
   ```

2. Try running the bot manually to see if there are any errors:
   ```bash
   ./run_bot.sh
   ```

### Discord Commands

The bot supports the following commands:

- `/ping` - The bot will respond with "Hello I'm ponging!"
- `/die` - The bot will respond with "You kill me, but I will rise as a phoenix! 🔥🦅✨" and then restart
