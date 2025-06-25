#!/usr/bin/env python3
"""
Test script to verify link extraction from inReach emails
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
    # Sample email content from the user
    sample_email = """
I'm checking in. Everything is OK.

View the location or send a reply to Darren Caldwell:
https://eur.explore.garmin.com/textmessage/txtmsg?extId=08dd417b-5ac1-119e-000d-3aa7bc4d0000&adr=cynicaldead%40gmail.com

Darren Caldwell sent this message from: Lat 53.344835 Lon -6.276734

Do not reply directly to this message.

This message was sent to you using the inReach two-way satellite communicator with GPS. To learn more, visit http://explore.garmin.com/inreach.
    """
    
    # Exact content provided by the user
    user_content = """View the location or send a reply to Darren Caldwell:
https://eur.explore.garmin.com/textmessage/txtmsg?extId=08dd417b-5ac1-119e-000d-3aa7bc4d0000&adr=cynicaldead%40gmail.com"""
    
    logger.info("Testing link extraction from inReach email")
    
    # Create parser
    parser = EmailParser()
    
    # Parse the full sample email
    logger.info("Testing with full sample email:")
    result1 = parser.parse_email(sample_email)
    
    # Print the results
    logger.info("Parsing results for full sample:")
    logger.info(f"Message: {result1['message']}")
    logger.info(f"Link: {result1['link']}")
    if 'latitude' in result1 and 'longitude' in result1:
        logger.info(f"Coordinates: {result1['latitude']}, {result1['longitude']}")
    
    # Test if the link was extracted correctly
    if result1['link'] == "No tracking link found":
        logger.error("FAILED: Link extraction failed for full sample")
    else:
        logger.info("SUCCESS: Link extracted correctly from full sample")
    
    # Parse the user-provided content
    logger.info("\nTesting with user-provided content:")
    result2 = parser.parse_email(user_content)
    
    # Print the results
    logger.info("Parsing results for user content:")
    logger.info(f"Message: {result2['message']}")
    logger.info(f"Link: {result2['link']}")
    if 'latitude' in result2 and 'longitude' in result2:
        logger.info(f"Coordinates: {result2['latitude']}, {result2['longitude']}")
    
    # Test if the link was extracted correctly
    if result2['link'] == "No tracking link found":
        logger.error("FAILED: Link extraction failed for user content")
    else:
        logger.info("SUCCESS: Link extracted correctly from user content")

if __name__ == "__main__":
    main()
