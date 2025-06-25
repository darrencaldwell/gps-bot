"""
Main Application Module

This module ties everything together and implements the main application logic:
- Load configuration
- Initialize Gmail and Discord clients
- Periodically check for new emails
- Parse emails and send to Discord
"""

import os
import sys
import time
import yaml
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

from .gmail_client import GmailClient
from .email_parser import EmailParser
from .discord_client import DiscordClient

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

class GmailDiscordRelay:
    """Main application class for Gmail to Discord relay."""
    
    def __init__(self, config_path: str):
        """
        Initialize the application.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = None
        self.gmail_client = None
        self.discord_client = None
        self.email_parser = None
        self.is_running = False
        self.discord_task = None
        
    def load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading configuration from {self.config_path}")
            
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Update logging level if specified
            if 'logging' in self.config and 'level' in self.config['logging']:
                level = getattr(logging, self.config['logging']['level'], logging.INFO)
                logging.getLogger().setLevel(level)
                logger.info(f"Set logging level to {self.config['logging']['level']}")
            
            # Update log file if specified
            if 'logging' in self.config and 'file' in self.config['logging']:
                file_handler = logging.FileHandler(self.config['logging']['file'])
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logging.getLogger().addHandler(file_handler)
                logger.info(f"Added log file: {self.config['logging']['file']}")
            
            logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize the application components.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Load environment variables
            load_dotenv()
            
            # Get credentials path
            base_dir = Path(self.config_path).parent.parent
            credentials_path = base_dir / "config" / "credentials.json"
            
            # Initialize Gmail client
            logger.info(f"Initializing Gmail client with credentials from {credentials_path}")
            self.gmail_client = GmailClient(str(credentials_path))
            
            # Initialize email parser
            logger.info("Initializing email parser")
            self.email_parser = EmailParser()
            
            # Get Discord token and channel ID
            discord_token = os.getenv("DISCORD_BOT_TOKEN")
            if not discord_token:
                logger.error("DISCORD_BOT_TOKEN environment variable not set")
                return False
            
            discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
            if not discord_channel_id:
                logger.error("DISCORD_CHANNEL_ID environment variable not set")
                return False
            
            # Initialize Discord client with kill callback
            logger.info("Initializing Discord client")
            self.discord_client = DiscordClient(
                discord_token, 
                int(discord_channel_id),
                kill_callback=self.handle_kill_command
            )
            
            logger.info("Initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing application: {str(e)}")
            return False
    
    async def handle_kill_command(self) -> None:
        """Handle the kill command from Discord."""
        logger.info("Kill command received, shutting down application...")
        await self.stop()
        # Exit the application with a dramatic message
        logger.info("🔥 The phoenix will rise again! 🦅✨")
        sys.exit(0)
    
    async def check_emails(self) -> None:
        """Check for new emails and process them."""
        try:
            logger.info("Checking for new emails...")
            
            # Get filter parameters from config
            senders = self.config['gmail']['filter']['senders']
            subject = self.config['gmail']['filter']['subject']
            
            # Check for new emails
            emails = self.gmail_client.check_for_new_emails(senders, subject)
            
            if not emails:
                logger.info("No new emails found")
                return
            
            logger.info(f"Found {len(emails)} new emails")
            
            # Process each email
            for email in emails:
                await self.process_email(email)
                
        except Exception as e:
            logger.error(f"Error checking emails: {str(e)}")
    
    async def process_email(self, email: Dict[str, Any]) -> None:
        """
        Process an email and send it to Discord.
        
        Args:
            email: Dictionary containing email data
        """
        try:
            logger.info(f"Processing email: {email['subject']}")
            
            # Parse the email content
            parsed_data = self.email_parser.parse_email(email['content'])
            
            # Send to Discord
            success = await self.discord_client.send_message(parsed_data)
            
            if success:
                logger.info("Email successfully sent to Discord")
            else:
                logger.error("Failed to send email to Discord")
                
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
    
    async def run_discord_bot(self) -> None:
        """Run the Discord bot."""
        try:
            logger.info("Starting Discord bot...")
            await self.discord_client.start()
        except Exception as e:
            logger.error(f"Error running Discord bot: {str(e)}")
    
    async def start(self) -> None:
        """Start the application."""
        try:
            logger.info("Starting Gmail to Discord relay...")
            
            # Authenticate with Gmail API
            if not self.gmail_client.authenticate():
                logger.error("Failed to authenticate with Gmail API")
                return
            
            # Start Discord bot in the background
            self.discord_task = asyncio.create_task(self.run_discord_bot())
            
            # Wait for Discord bot to be ready
            while not self.discord_client.is_ready:
                logger.info("Waiting for Discord bot to be ready...")
                await asyncio.sleep(1)
            
            # Set running flag
            self.is_running = True
            
            # Schedule email checking
            check_interval = self.config['gmail']['check_interval']
            logger.info(f"Setting up email check every {check_interval} seconds")
            
            # Initial check
            await self.check_emails()
            
            # Run periodic checks
            while self.is_running:
                await asyncio.sleep(check_interval)
                await self.check_emails()
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.is_running = False
        except Exception as e:
            logger.error(f"Error running application: {str(e)}")
            self.is_running = False
    
    async def stop(self) -> None:
        """Stop the application."""
        logger.info("Stopping Gmail to Discord relay...")
        self.is_running = False
        
        # Cancel Discord task if running
        if self.discord_task and not self.discord_task.done():
            self.discord_task.cancel()
            try:
                await self.discord_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Application stopped")


async def main():
    """Main entry point."""
    try:
        # Get the base directory
        base_dir = Path(__file__).parent.parent
        
        # Path to config file
        config_path = base_dir / "config" / "config.yaml"
        
        # Create the application
        app = GmailDiscordRelay(str(config_path))
        
        # Load configuration
        if not app.load_config():
            logger.error("Failed to load configuration")
            return
        
        # Initialize the application
        if not app.initialize():
            logger.error("Failed to initialize application")
            return
        
        # Start the application
        await app.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, exiting...")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    # Run the application
    asyncio.run(main())