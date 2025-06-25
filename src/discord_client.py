"""
Discord Client Module

This module handles:
- Connecting to Discord using a bot token
- Creating formatted embeds for inReach messages
- Sending messages to a specified Discord channel
- Handling commands like ping and kill
"""

import logging
import discord
import asyncio
import sys
from discord.ext import commands
from typing import Dict, Optional, Callable

# Configure logger
logger = logging.getLogger(__name__)

class DiscordClient:
    """Client for interacting with Discord."""
    
    def __init__(self, token: str, channel_id: int, kill_callback: Callable = None):
        """
        Initialize the Discord client.
        
        Args:
            token: Discord bot token
            channel_id: ID of the channel to send messages to
            kill_callback: Optional callback function to call when the kill command is used
        """
        self.token = token
        self.channel_id = channel_id
        self.kill_callback = kill_callback
        
        # Create intents with message content intent enabled
        intents = discord.Intents.default()
        intents.voice_states = False  # Disable voice functionality
        intents.message_content = True  # Enable message content intent for commands
        
        self.bot = commands.Bot(command_prefix="/", intents=intents)
        self.is_ready = False
        
        # Set up event handlers
        @self.bot.event
        async def on_ready():
            logger.info(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
            # Sync slash commands with Discord
            try:
                logger.info("Syncing application commands with Discord...")
                await self.bot.tree.sync()
                logger.info("Application commands synced successfully")
            except Exception as e:
                logger.error(f"Error syncing application commands: {str(e)}")
            self.is_ready = True
        
        # Set up traditional prefix commands
        @self.bot.command(name="ping")
        async def ping_prefix(ctx):
            """Respond to ping command with a pong message."""
            logger.info(f"Received ping command from {ctx.author}")
            await ctx.send("Hello I'm ponging!")
        
        @self.bot.command(name="die")
        async def die_prefix(ctx):
            """Kill the bot with a dramatic message."""
            logger.info(f"Received die command from {ctx.author}")
            await ctx.send("You kill me, but I will rise as a phoenix! 🔥🦅✨")
            
            # Call the kill callback if provided
            if self.kill_callback:
                logger.info("Executing kill callback")
                await self.kill_callback()
        
        # Set up slash commands
        @self.bot.tree.command(name="ping", description="Check if the bot is alive")
        async def ping_slash(interaction: discord.Interaction):
            """Respond to ping slash command with a pong message."""
            logger.info(f"Received ping slash command from {interaction.user}")
            await interaction.response.send_message("Hello I'm ponging!")
        
        @self.bot.tree.command(name="die", description="Shut down the bot")
        async def die_slash(interaction: discord.Interaction):
            """Kill the bot with a dramatic message."""
            logger.info(f"Received die slash command from {interaction.user}")
            await interaction.response.send_message("You kill me, but I will rise as a phoenix! 🔥🦅✨")
            
            # Call the kill callback if provided
            if self.kill_callback:
                logger.info("Executing kill callback")
                await self.kill_callback()
    
    async def start(self):
        """Start the Discord bot."""
        try:
            logger.info("Starting Discord bot...")
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"Error starting Discord bot: {str(e)}")
            raise
    
    async def send_message(self, email_data: Dict[str, str]) -> bool:
        """
        Send a message to the specified Discord channel.
        
        Args:
            email_data: Dictionary containing parsed email data:
                {
                    'message': str,  # The main message content
                    'link': str,     # The tracking/reply link
                    'latitude': str, # Latitude (if available)
                    'longitude': str # Longitude (if available)
                }
                
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Log the email data for debugging
            logger.info(f"Email data received: {email_data}")
            
            # Get the channel
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Channel with ID {self.channel_id} not found")
                return False
            
            # Create embed
            embed = self._create_embed(email_data)
            
            # Send the message
            await channel.send(embed=embed)
            logger.info("Message sent to Discord successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to Discord: {str(e)}")
            return False
    
    def _create_embed(self, email_data: Dict[str, str]) -> discord.Embed:
        """
        Create a formatted embed for the inReach message.
        
        Args:
            email_data: Dictionary containing parsed email data
            
        Returns:
            discord.Embed: Formatted embed for Discord
        """
        # Create the embed
        embed = discord.Embed(
            title="inReach Message from Darren Caldwell",
            description=email_data['message'],
            color=0x00FF00  # Green color
        )
        
        # Add tracking link - only include this one field for the link
        if email_data['link'] and email_data['link'] != "No tracking link found":
            logger.info(f"Adding tracking link to embed: {email_data['link']}")
            
            # Add tracking link
            embed.add_field(
                name="Tracking Link",
                value=f"[View Location or Reply]({email_data['link']})",
                inline=False
            )
        
        # Add coordinates if available
        if 'latitude' in email_data and 'longitude' in email_data:
            lat = email_data['latitude']
            lon = email_data['longitude']
            
            # Add coordinates as a field
            embed.add_field(
                name="Location",
                value=f"Lat: {lat}, Lon: {lon}",
                inline=True
            )
            
            # Add Google Maps link
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            embed.add_field(
                name="Google Maps",
                value=f"[Open in Maps]({maps_url})",
                inline=True
            )
        
        # Add timestamp
        embed.timestamp = discord.utils.utcnow()
        
        # Add footer
        embed.set_footer(text="inReach Satellite Communicator")
        
        return embed


# Example usage (not executed when imported)
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample email data
    email_data = {
        'message': "I'm checking in. Everything is OK.",
        'link': "https://eur.explore.garmin.com/textmessage/txtmsg?extId=08dd417b-5ac1-119e-000d-3aa7bc4d0000&adr=cynicaldead%40gmail.com",
        'latitude': "53.344835",
        'longitude': "-6.276734"
    }
    
    # Get token and channel ID from environment variables
    token = os.getenv("DISCORD_BOT_TOKEN")
    channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
    
    if not token or channel_id == 0:
        print("Error: DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID must be set in .env file")
        exit(1)
    
    # Create Discord client
    client = DiscordClient(token, channel_id)
    
    # Run the example
    async def main():
        # Start the bot in the background
        asyncio.create_task(client.start())
        
        # Wait for the bot to be ready
        while not client.is_ready:
            await asyncio.sleep(1)
        
        # Send a test message
        success = await client.send_message(email_data)
        print(f"Message sent: {success}")
        
        # Keep the bot running for a bit to ensure the message is sent
        await asyncio.sleep(5)
    
    # Run the example
    asyncio.run(main())
