#!/usr/bin/env python3
"""
Authentication script for Gmail to Discord Relay Bot

This script performs the initial authentication with Gmail API
and saves the token for future use. Run this script once before
setting up the bot as a service.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import the headless auth module
from src.headless_auth import authenticate_headless

def main():
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to credentials file
    credentials_path = os.path.join(base_dir, "config", "credentials.json")
    
    if not os.path.exists(credentials_path):
        logger.error(f"Credentials file not found: {credentials_path}")
        logger.error("Please create a credentials.json file in the config directory")
        return 1
    
    print("\n=== Gmail to Discord Relay Bot Authentication ===\n")
    print("This script will authenticate with Gmail API and save the token for future use.")
    print("You will need to follow the instructions to complete the authentication process.")
    print("\nPress Enter to continue...")
    input()
    
    print("\nAuthenticating with Gmail API...")
    credentials = authenticate_headless(credentials_path)
    
    if credentials:
        token_path = os.path.join(os.path.dirname(credentials_path), 'token.json')
        print("\n=== Authentication Successful! ===")
        print(f"Token saved to: {token_path}")
        print("\nYou can now set up the bot as a service.")
        return 0
    else:
        print("\n=== Authentication Failed! ===")
        print("Please check the error messages above and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
