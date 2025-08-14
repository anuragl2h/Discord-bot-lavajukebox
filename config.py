"""
Discord Music Bot - Configuration
Contains all configuration settings for the bot.
"""

import os

class Config:
    """Configuration class for bot settings."""
    
    # Bot settings
    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
    
    # Lavalink settings for Wavelink
    LAVALINK_HOST = os.getenv("LAVALINK_HOST", "lavalink.devxcode.in")
    LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "80"))
    LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "DevamOP")
    LAVALINK_REGION = os.getenv("LAVALINK_REGION", "us")
    LAVALINK_NAME = os.getenv("LAVALINK_NAME", "main-node")
    
    # Bot behavior settings
    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "100"))
    DEFAULT_VOLUME = int(os.getenv("DEFAULT_VOLUME", "50"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
