import os
import yaml
import certifi
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import random
import asyncio
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pydantic import BaseModel, ValidationError
import signal
import sys

# Set the environment variable to use certifi certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

# Configuration loading and validation
class BotConfig(BaseModel):
    token: str
    owner_id: int
    command_prefix: str
    status_update_interval: int

class LoggingConfig(BaseModel):
    file: str
    level: str

class Config(BaseModel):
    bot: BotConfig
    logging: LoggingConfig

def load_config():
        with open('config/config.yaml', 'r') as config_file:
            config_data = yaml.safe_load(config_file)
            return Config(**config_data)
    except FileNotFoundError:
        raise ValueError("Configuration file not found.")
    except ValidationError as e:
        raise ValueError(f"Configuration error: {e}")

config = load_config()

TOKEN = config.bot.token
OWNER_ID = config.bot.owner_id
COMMAND_PREFIX = config.bot.command_prefix
STATUS_UPDATE_INTERVAL = config.bot.status_update_interval
LOG_FILE = config.logging.file
LOG_LEVEL = config.logging.level.upper()

if not TOKEN:
    raise ValueError("No token provided. Please set the DISCORD_BOT_TOKEN variable in the config file.")
if not OWNER_ID:
    raise ValueError("No owner ID provided. Please set the DISCORD_OWNER_ID variable in the config file.")

# Logging setup
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.DEBUG), 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Create the bot and set the intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # For member join/leave events

class MyBot(commands.Bot):
    def __init__(self):
        logger.debug("Initializing MyBot")
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
        self.synced = False

    async def setup_hook(self):
        logger.debug("Running setup_hook")
        # Add sync command
        if "sync" not in [cmd.name for cmd in self.tree.get_commands()]:
            self.tree.add_command(sync)
        await self.tree.sync()
        logger.info("Sync command added and tree synced")
        await self.load_extensions()
        logger.info("Extensions loaded")
    
    @tasks.loop(minutes=STATUS_UPDATE_INTERVAL)
    async def status_task(self):
        if self.is_ready():
            logger.debug("Updating status")
            statuses = [
                "Playing a game",
                "Listening to music",
                "Watching a movie",
                "Coding a bot",
                "Reading a book",
                "Getting repaired",
                "Coding myself",
                "Maintaining Servers",
                "Watching Anime"
            ]
            await self.change_presence(activity=discord.Game(random.choice(statuses)))
            logger.info("Status updated")

    async def load_extensions(self):
        logger.debug("Loading extensions")
        cog_directory = Path('cogs')
        if not cog_directory.exists():
            logger.error(f"Cog directory '{cog_directory}' does not exist.")
            return
        for cog in cog_directory.glob('*.py'):
            if cog.stem != '__init__':
                ext = f'cogs.{cog.stem}'
                try:
                    if ext in self.extensions:
                        logger.debug(f"Reloading extension: {ext}")
                        await self.reload_extension(ext)
                    else:
                        logger.debug(f"Loading extension: {ext}")
                        await self.load_extension(ext)
                except Exception as e:
                    logger.exception(f"Failed to load extension {ext}: {e}")

    async def close(self):
        logger.info("Shutting down bot")
        if self.status_task.is_running():
            self.status_task.cancel()
        await super().close()

bot = MyBot()

# Custom check to verify if the user is the bot owner
def is_owner():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == OWNER_ID
    return app_commands.check(predicate)

# Sync command for syncing application commands
@bot.tree.command(name="sync", description="Sync global commands (bot owner only)")
@is_owner()
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        logger.debug("Loading extensions for sync")
        await bot.load_extensions()
        logger.debug("Extensions loaded")
        synced = await bot.tree.sync()
        synced_command_names = [cmd.name for cmd in synced]
        await interaction.followup.send(f"Successfully synced {len(synced)} cogs globally: {', '.join(synced_command_names)}", ephemeral=True)
        logger.info(f"Successfully synced {len(synced)} cogs globally: {', '.join(synced_command_names)}")
    except discord.errors.HTTPException as e:
        logger.exception("Failed to sync commands due to HTTP exception")
        await interaction.followup.send(f"Failed to sync commands due to HTTP exception: {e}", ephemeral=True)
    except discord.errors.Forbidden as e:
        logger.exception(f"Failed to sync commands due to permission error: {e}")
        await interaction.followup.send(f"Failed to sync commands due to permission error: {e}", ephemeral=True)
    except Exception as e:
        logger.exception(f"Failed to sync commands due to an unexpected error: {e}")
        await interaction.followup.send(f"Failed to sync commands due to an unexpected error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.debug("Bot is ready")
    if not bot.status_task.is_running():
        bot.status_task.start()

# Global error handler for application commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("Command not found.", ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have the necessary permissions to execute this command.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)
    logger.exception(f"Error in command {interaction.command}: {error}")

# Graceful shutdown on SIGTERM and SIGINT
async def graceful_shutdown():
    logger.info("Received shutdown signal")
    await bot.close()

def main():
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *args: asyncio.create_task(graceful_shutdown()))

    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.exception("An unexpected error occurred while running the bot")
        sys.exit(1)

if __name__ == "__main__":
    main()
    
