#!/usr/bin/env python3
"""
Discord Music Bot - Main Entry Point
A Discord bot with Lavalink integration for streaming audio in voice channels.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from bot import MusicBot

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging configuration for the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

async def main():
    """Main function to run the Discord music bot."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get bot token from environment
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    # Create and run the bot
    bot = MusicBot()
    
    try:
        logger.info("Starting Discord Music Bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
