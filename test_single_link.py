#!/usr/bin/env python3
"""
Test script to verify Discord embed with only one link field
"""

import logging
import sys
import asyncio
import os
from dotenv import load_dotenv
from src.discord_client import DiscordClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get Discord token and channel ID
    token = os.getenv("DISCORD_BOT_TOKEN")
    channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
    
    if not token or channel_id == 0:
        logger.error("DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID must be set in .env file")
        return
    
    # Test data with the exact link from the user's message
    test_data = {
        'message': "Test message - Single Link Field",
        'link': "https://eur.explore.garmin.com/textmessage/txtmsg?extId=08dd417b-5ac1-119e-000d-3aa7bc4d0000&adr=cynicaldead%40gmail.com",
        'latitude': "53.344835",
        'longitude': "-6.276734"
    }
    
    logger.info("Creating Discord client")
    client = DiscordClient(token, channel_id)
    
    # Start the bot in the background
    logger.info("Starting Discord bot")
    bot_task = asyncio.create_task(client.start())
    
    # Wait for the bot to be ready
    while not client.is_ready:
        logger.info("Waiting for Discord bot to be ready...")
        await asyncio.sleep(1)
    
    # Send a test message
    logger.info("Sending test message with embed (single link field)")
    logger.info(f"Using link: {test_data['link']}")
    success = await client.send_message(test_data)
    logger.info(f"Message sent: {success}")
    
    # Keep the bot running for a bit to ensure the message is sent
    await asyncio.sleep(5)
    
    # Cancel the bot task
    logger.info("Stopping Discord bot")
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main())
