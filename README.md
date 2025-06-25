# Gmail to Discord Relay Bot

A Python bot that relays messages from Gmail to Discord. Specifically designed to forward inReach messages from Garmin to a Discord channel.

## Features

- Checks Gmail inbox every minute for new messages
- Filters emails from "no.reply.inreach@garmin.com" with subject "inReach message from Darren Caldwell"
- Parses message content, tracking link, and location coordinates
- Forwards information as a nicely formatted embed to a Discord channel
- Only processes emails received after the bot starts

## Prerequisites

- Python 3.8 or higher
- A Google Cloud Platform account with Gmail API enabled
- A Discord bot with a token
- A Discord server with a channel for the bot to post in

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd gmail_discord_relay
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Google Cloud Platform

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
   - Application type: Desktop application
   - Download the credentials JSON file
   - Save it as `config/credentials.json`

### 4. Configure environment variables

Create a `.env` file in the root directory with the following variables:

```
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
```

### 5. Run the bot

```bash
python src/main.py
```

On first run, the bot will open a browser window for you to authenticate with your Google account.

## Configuration

You can modify the `config/config.yaml` file to change:

- Email filter parameters
- Check interval
- Logging settings

## License

[MIT](LICENSE)