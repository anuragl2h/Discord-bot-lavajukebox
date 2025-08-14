"""
Discord Music Bot - Main Bot Class
Handles bot initialization, events, and command loading.
"""

import discord
from discord.ext import commands
import wavelink
import logging
import os
from config import Config

class MusicBot(commands.Bot):
    """Main bot class with music functionality."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            description="A Discord music bot with Lavalink integration"
        )
        
        self.logger = logging.getLogger(__name__)
        
    async def setup_hook(self):
        """Setup hook called when bot is ready."""
        # Setup Wavelink nodes
        protocol = "https" if Config.LAVALINK_PORT == 443 else "http"
        nodes = [wavelink.Node(
            uri=f"{protocol}://{Config.LAVALINK_HOST}:{Config.LAVALINK_PORT}",
            password=Config.LAVALINK_PASSWORD,
            identifier=Config.LAVALINK_NAME
        )]
        
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)
        self.logger.info(f"Wavelink connected to {Config.LAVALINK_HOST}:{Config.LAVALINK_PORT}")
        
        # Load music cog
        await self.load_extension('music_cog')
        self.logger.info("Music cog loaded successfully")
        
    async def on_ready(self):
        """Event triggered when bot is ready."""
        self.logger.info(f'{self.user} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{Config.COMMAND_PREFIX}help | Music Bot"
            )
        )
        
    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ Command on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            self.logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send("❌ An error occurred while processing the command.")
            
    async def close(self):
        """Clean up resources when bot shuts down."""
        # Disconnect from Wavelink
        await wavelink.Pool.close()
        await super().close()
