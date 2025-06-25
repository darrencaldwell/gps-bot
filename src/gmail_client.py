"""
Gmail Client Module

This module handles:
- Authenticating with Gmail API using OAuth2
- Searching for specific emails
- Extracting email content
- Tracking email timestamps to only process new emails
"""

import os
import json
import base64
import logging
import datetime
from typing import Dict, List, Optional, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logger
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self, credentials_path: str):
        """
        Initialize the Gmail client.
        
        Args:
            credentials_path: Path to the credentials.json file
        """
        self.credentials_path = credentials_path
        self.credentials = None
        self.service = None
        self.last_check_time = datetime.datetime.utcnow().isoformat()
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # Import the headless authentication module
            from src.headless_auth import authenticate_headless
            
            # Use headless authentication
            logger.info("Using headless authentication for Gmail API")
            self.credentials = authenticate_headless(self.credentials_path)
            
            if not self.credentials:
                logger.error("Failed to authenticate with Gmail API")
                return False
            
            # Build the Gmail API service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            logger.error(f"Error authenticating with Gmail API: {str(e)}")
            return False
    
    def check_for_new_emails(self, senders: List[str], subject: str) -> List[Dict[str, Any]]:
        """
        Check for new emails from specific senders with a specific subject.
        
        Args:
            senders: List of email addresses of allowed senders
            subject: Subject of the email
            
        Returns:
            List of dictionaries containing email data:
            [
                {
                    'id': str,           # Email ID
                    'subject': str,      # Email subject
                    'sender': str,       # Email sender
                    'date': str,         # Email date
                    'content': str       # Email content (plain text)
                },
                ...
            ]
        """
        try:
            if not self.service:
                logger.error("Gmail API service not initialized. Call authenticate() first.")
                return []
            
            # Debug: Print current time
            current_time = datetime.datetime.utcnow()
            logger.info(f"Current UTC time: {current_time}")
            
            # For Gmail API, use YYYY/MM/DD format for date filtering
            # For testing, let's look back 7 days to ensure we catch recent emails
            seven_days_ago = (current_time - datetime.timedelta(days=7)).strftime('%Y/%m/%d')
            
            all_email_data = []
            
            # Process each sender
            for sender in senders:
                # Create the query with configurable filtering
                # Start with the sender filter
                query = f"from:{sender}"
                
                # Add subject filter if provided
                if subject:
                    query += f" subject:\"{subject}\""
                
                query += f" after:{seven_days_ago}"
                
                logger.info(f"Searching for emails with query: {query}")
                
                # Search for messages
                results = self.service.users().messages().list(
                    userId='me', q=query).execute()
                
                messages = results.get('messages', [])
                
                if not messages:
                    logger.info(f"No new emails found from {sender}")
                    continue
                
                # Process messages from this sender
                email_data = self._process_messages(messages)
                all_email_data.extend(email_data)
            
            # Update the last check time
            self.last_check_time = datetime.datetime.utcnow().isoformat()
            logger.info(f"Updated last check time to {self.last_check_time}")
            
            return all_email_data
            
        except Exception as e:
            logger.error(f"Error checking for new emails: {str(e)}")
            return []
    
    def _process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of messages and extract relevant data.
        
        Args:
            messages: List of message dictionaries from Gmail API
            
        Returns:
            List of dictionaries containing email data
        """
        email_data = []
        processed_ids_file = os.path.join(os.path.dirname(self.credentials_path), 'processed_emails.txt')
        
        # Load existing processed IDs
        processed_ids = set()
        if os.path.exists(processed_ids_file):
            try:
                with open(processed_ids_file, 'r') as f:
                    processed_ids = set(line.strip() for line in f)
                logger.info(f"Loaded {len(processed_ids)} previously processed email IDs")
            except Exception as e:
                logger.error(f"Error loading processed email IDs: {str(e)}")
        
        # Track newly processed IDs
        newly_processed_ids = []
        
        for message in messages:
            msg_id = message['id']
            
            # Skip already processed emails
            if msg_id in processed_ids:
                logger.info(f"Skipping already processed email: {msg_id}")
                continue
            
            logger.info(f"Processing email with ID: {msg_id}")
            newly_processed_ids.append(msg_id)
            
            # Get the message details
            msg = self.service.users().messages().get(
                userId='me', id=msg_id, format='full').execute()
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Debug: Print the email date
            logger.info(f"Email date: {date}")
            
            # Extract internal timestamp
            internal_date = msg.get('internalDate')
            if internal_date:
                # Convert from milliseconds since epoch to datetime
                # Use timezone aware datetime to properly handle UTC
                email_timestamp_ms = int(internal_date)
                email_timestamp_sec = email_timestamp_ms / 1000
                email_datetime = datetime.datetime.fromtimestamp(email_timestamp_sec)
                email_datetime_utc = datetime.datetime.utcfromtimestamp(email_timestamp_sec)
                
                logger.info(f"Email internal date (local): {email_datetime}")
                logger.info(f"Email internal date (UTC): {email_datetime_utc}")
                logger.info(f"Raw internal timestamp: {internal_date} ms")
            
            # Extract content
            content = self._get_email_content(msg)
            
            # Add to the list
            email_data.append({
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'content': content
            })
        
        # Save newly processed IDs
        if newly_processed_ids:
            try:
                with open(processed_ids_file, 'a') as f:
                    for msg_id in newly_processed_ids:
                        f.write(f"{msg_id}\n")
                logger.info(f"Saved {len(newly_processed_ids)} new email IDs to processed list")
            except Exception as e:
                logger.error(f"Error saving processed email IDs: {str(e)}")
        
        return email_data
    
    def _get_email_content(self, message: Dict[str, Any]) -> str:
        """
        Extract plain text content from a Gmail message.
        
        Args:
            message: Gmail message object
            
        Returns:
            str: Plain text content of the email
        """
        try:
            # Check if the message has parts
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        # Get the data
                        if 'data' in part['body']:
                            data = part['body']['data']
                            # Decode the data
                            text = base64.urlsafe_b64decode(data).decode('utf-8')
                            return text
            
            # If no parts or no text/plain part, try to get the body directly
            if 'body' in message['payload'] and 'data' in message['payload']['body']:
                data = message['payload']['body']['data']
                text = base64.urlsafe_b64decode(data).decode('utf-8')
                return text
            
            return "No content found in email"
            
        except Exception as e:
            logger.error(f"Error extracting email content: {str(e)}")
            return f"Error extracting email content: {str(e)}"


# Example usage (not executed when imported)
if __name__ == "__main__":
    import json
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Path to credentials file
    credentials_path = "../config/credentials.json"
    
    # Create Gmail client
    client = GmailClient(credentials_path)
    
    # Authenticate
    if client.authenticate():
        # Check for new emails
        emails = client.check_for_new_emails(
            senders=["no.reply.inreach@garmin.com", "cynicaldead@gmail.com"],
            subject="inReach message from Darren Caldwell"
        )
        
        # Print the results
        print(f"Found {len(emails)} new emails:")
        for email in emails:
            print(f"Subject: {email['subject']}")
            print(f"From: {email['sender']}")
            print(f"Date: {email['date']}")
            print(f"Content: {email['content'][:100]}...")  # Show first 100 chars
            print("-" * 50)
