#!/usr/bin/env python3
"""
Entry point script for the Gmail to Discord Relay Bot.
This script makes it easier to run the bot from the command line.
"""

import asyncio
import sys
from src.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)