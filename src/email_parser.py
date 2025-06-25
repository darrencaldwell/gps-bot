"""
Email Parser Module

This module handles parsing of emails from Garmin inReach to extract:
- Message content
- Tracking link
- Location coordinates (if available)
"""

import re
import logging
from typing import Dict, Optional, Tuple

# Configure logger
logger = logging.getLogger(__name__)

class EmailParser:
    """Parser for Garmin inReach emails."""
    
    def __init__(self):
        # Regular expressions for extracting information
        # Even more flexible pattern for the Garmin link
        self.link_pattern = re.compile(r'https?://[^\s\n]+garmin\.com/textmessage/txtmsg\?[^\s\n]+')
        self.location_pattern = re.compile(r'Lat\s+(-?\d+\.\d+)\s+Lon\s+(-?\d+\.\d+)')
        
    def parse_email(self, email_content: str) -> Dict[str, str]:
        """
        Parse the email content to extract message, link, and coordinates.
        
        Args:
            email_content: The plain text content of the email
            
        Returns:
            Dictionary containing extracted information:
            {
                'message': str,  # The main message content
                'link': str,     # The tracking/reply link
                'latitude': str, # Latitude (if available)
                'longitude': str # Longitude (if available)
            }
        """
        try:
            logger.info("Parsing email content")
            logger.info(f"Email content length: {len(email_content)} characters")
            
            # Debug: Print the first 500 characters of the email content
            content_preview = email_content.replace('\n', '\\n')[:500]
            logger.info(f"Email content preview: {content_preview}")
            
            # Extract the message (first paragraph before the link)
            message = self._extract_message(email_content)
            
            # Extract the tracking link
            link = self._extract_link(email_content)
            
            # If link extraction failed, try a direct search for the URL
            if link == "No tracking link found":
                logger.info("Attempting alternative link extraction method")
                # Look for specific patterns in the email content
                if "eur.explore.garmin.com/textmessage/txtmsg" in email_content:
                    logger.info("Found garmin.com URL in content, extracting manually")
                    start_idx = email_content.find("https://eur.explore.garmin.com/textmessage/txtmsg")
                    if start_idx != -1:
                        end_idx = email_content.find("\n", start_idx)
                        if end_idx == -1:  # If no newline, take the rest of the string
                            end_idx = len(email_content)
                        link = email_content[start_idx:end_idx].strip()
                        logger.info(f"Manually extracted link: {link}")
            
            # Extract coordinates if available
            latitude, longitude = self._extract_coordinates(email_content)
            
            result = {
                'message': message,
                'link': link
            }
            
            # Add coordinates if available
            if latitude and longitude:
                result['latitude'] = latitude
                result['longitude'] = longitude
                
            logger.info(f"Parsed email data: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}", exc_info=True)
            # Return a minimal result with error information
            return {
                'message': 'Error parsing email content',
                'link': '',
                'error': str(e)
            }
    
    def _extract_message(self, content: str) -> str:
        """Extract the main message from the email content."""
        # The message is typically the first paragraph(s) before the tracking link
        lines = content.strip().split('\n')
        message_lines = []
        
        for line in lines:
            line = line.strip()
            # Stop when we reach the line with "View the location" as it marks the end of the message
            if line.startswith("View the location"):
                break
            # Skip empty lines at the beginning
            if not message_lines and not line:
                continue
            # Add non-empty lines to the message
            if line:
                message_lines.append(line)
        
        # Join the message lines
        return '\n'.join(message_lines) if message_lines else "No message content found"
    
    def _extract_link(self, content: str) -> str:
        """Extract the tracking/reply link from the email content."""
        logger.info("Extracting link from email content")
        
        # Try to find the link using regex
        match = self.link_pattern.search(content)
        if match:
            link = match.group(0)
            logger.info(f"Found link using regex: {link}")
            return link
        
        # If regex fails, try to find the link by looking for specific text
        try:
            # Look for the line that typically contains the link
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "View the location or send a reply" in line:
                    logger.info(f"Found 'View the location' line: {line}")
                    # Check the next line for the URL
                    if i + 1 < len(lines) and "garmin.com" in lines[i + 1]:
                        link = lines[i + 1].strip()
                        logger.info(f"Found link in next line: {link}")
                        return link
        except Exception as e:
            logger.error(f"Error in alternative link extraction: {str(e)}")
        
        logger.warning("No tracking link found in email content")
        return "No tracking link found"
    
    def _extract_coordinates(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract latitude and longitude coordinates if available."""
        match = self.location_pattern.search(content)
        if match:
            lat = match.group(1)
            lon = match.group(2)
            logger.info(f"Found coordinates: Lat {lat}, Lon {lon}")
            return lat, lon
        
        logger.warning("No coordinates found in email content")
        return None, None


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample email content for testing
    sample_email = """
I'm checking in. Everything is OK.

View the location or send a reply to Darren Caldwell:
https://eur.explore.garmin.com/textmessage/txtmsg?extId=08dd417b-5ac1-119e-000d-3aa7bc4d0000&adr=cynicaldead%40gmail.com

Darren Caldwell sent this message from: Lat 53.344835 Lon -6.276734

Do not reply directly to this message.

This message was sent to you using the inReach two-way satellite communicator with GPS. To learn more, visit http://explore.garmin.com/inreach.
    """
    
    parser = EmailParser()
    result = parser.parse_email(sample_email)
    
    print("Parsed Email:")
    print(f"Message: {result['message']}")
    print(f"Link: {result['link']}")
    if 'latitude' in result and 'longitude' in result:
        print(f"Coordinates: {result['latitude']}, {result['longitude']}")
