# Headless Setup Guide for Gmail to Discord Relay Bot

This guide will help you set up the Gmail to Discord Relay Bot on a headless server (like your Alpine Linux VM) where you don't have access to a browser.

## Step 1: Make the Authentication Script Executable

```bash
chmod +x authenticate.py
```

## Step 2: Run the Authentication Script

```bash
./authenticate.py
```

## Step 3: Follow the Console Authentication Flow

1. The script will display a URL
2. Copy this URL and open it in a browser on your local machine (not the VM)
3. Log in with your Google account and grant the requested permissions
4. You'll receive an authorization code
5. Copy this code and paste it back into the console on your VM
6. Press Enter

## Step 4: Verify Authentication Success

If authentication is successful, you'll see a message confirming that the token has been saved. The token will be stored in `config/token.json`.

## Step 5: Set Up the Bot as a Service

Now that you have authenticated, you can follow the instructions in `INSTALL_SERVICE.md` to set up the bot as a service.

## Troubleshooting

### Token Expiration

If the token expires, you'll need to re-authenticate:

1. Delete the existing token:
   ```bash
   rm config/token.json
   ```

2. Run the authentication script again:
   ```bash
   ./authenticate.py
   ```

### Authentication Errors

If you encounter authentication errors:

1. Make sure your `credentials.json` file is valid and contains the correct client ID and secret
2. Check that you're using the correct Google account
3. Ensure that the Gmail API is enabled for your Google Cloud project

### Service Startup Issues

If the service fails to start after authentication:

1. Check the logs:
   ```bash
   tail -f /var/log/gps-bot.log
   ```

2. Try running the bot manually to see if there are any errors:
   ```bash
   python3 src/main.py
   ```
