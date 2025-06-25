#!/usr/bin/env python3
"""
Test script to verify link extraction from the specific user content
"""

import logging
import sys
from src.email_parser import EmailParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Exact content provided by the user
    user_content = """View the location or send a reply to Darren Caldwell:
https://eur.explore.garmin.com/textmessage/txtmsg?extId=08dd417b-5ac1-119e-000d-3aa7bc4d0000&adr=cynicaldead%40gmail.com"""
    
    logger.info("Testing link extraction from user-provided content")
    
    # Create parser
    parser = EmailParser()
    
    # Parse the user-provided content
    result = parser.parse_email(user_content)
    
    # Print the results
    logger.info("Parsing results:")
    logger.info(f"Message: {result['message']}")
    logger.info(f"Link: {result['link']}")
    if 'latitude' in result and 'longitude' in result:
        logger.info(f"Coordinates: {result['latitude']}, {result['longitude']}")
    
    # Test if the link was extracted correctly
    if result['link'] == "No tracking link found":
        logger.error("FAILED: Link extraction failed")
    else:
        logger.info("SUCCESS: Link extracted correctly")
        
        # Create a mock email data dictionary for Discord embed
        email_data = {
            'message': "Test message",
            'link': result['link']
        }
        
        # Print the data that would be used for the Discord embed
        logger.info("Data for Discord embed:")
        logger.info(f"Message: {email_data['message']}")
        logger.info(f"Link: {email_data['link']}")
        
        # Verify the link is not empty or "No tracking link found"
        if email_data['link'] and email_data['link'] != "No tracking link found":
            logger.info("Link is valid for Discord embed")
        else:
            logger.error("Link is not valid for Discord embed")

if __name__ == "__main__":
    main()
