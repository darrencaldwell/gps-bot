"""
Headless Authentication Module for Gmail API

This module provides authentication for Gmail API on headless servers
without requiring a browser on the server.
"""

import os
import json
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Configure logger
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_headless(credentials_path):
    """
    Authenticate with Gmail API using a headless approach.
    
    Args:
        credentials_path: Path to the credentials.json file
        
    Returns:
        Credentials object if authentication was successful, None otherwise
    """
    token_path = os.path.join(os.path.dirname(credentials_path), 'token.json')
    credentials = None
    
    # Check if token.json exists
    if os.path.exists(token_path):
        logger.info("Loading existing credentials from token.json")
        try:
            credentials = Credentials.from_authorized_user_info(
                json.loads(open(token_path).read()), SCOPES)
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
    
    # If there are no valid credentials, use the device flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info("Refreshing expired credentials")
            try:
                credentials.refresh(Request())
            except RefreshError as e:
                logger.error(f"Error refreshing credentials: {str(e)}")
                credentials = None
        
        if not credentials:
            logger.info("Getting new credentials using device flow")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                
                # Run the console flow (no browser needed)
                credentials = flow.run_local_server()
                
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(credentials.to_json())
                    logger.info(f"Saved credentials to {token_path}")
            except Exception as e:
                logger.error(f"Error in authentication flow: {str(e)}")
                return None
    
    return credentials
