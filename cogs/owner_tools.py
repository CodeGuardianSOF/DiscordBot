import discord
from discord import app_commands
from discord.ext import commands
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.DEBUG)

class OwnerCog(commands.GroupCog, name="ownertools"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("OwnerToolsCog initialized")

    def owner_only():
        async def predicate(interaction: discord.Interaction) -> bool:
            is_owner = await interaction.client.is_owner(interaction.user)
            if not is_owner:
                logging.warning(f"User {interaction.user} tried to use an owner command but is not the owner.")
                await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return is_owner
        return app_commands.check(predicate)

    async def send_ephemeral_message(self, interaction, message):
        await interaction.response.send_message(message, ephemeral=True)

    @owner_only()
    @app_commands.command(name="shutdown", description="Shut down the bot")
    async def shutdown(self, interaction: discord.Interaction):
        await self.send_ephemeral_message(interaction, "Shutting down...")
        logging.info("Bot is shutting down by the owner's command")
        await self.bot.close()

    @owner_only()
    @app_commands.command(name="load", description="Load an extension")
    async def load(self, interaction: discord.Interaction, extension_name: str):
        try:
            await self.bot.load_extension(extension_name)
            await self.send_ephemeral_message(interaction, f"Extension {extension_name} loaded")
            logging.info(f"Extension {extension_name} loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load extension {extension_name}: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_message(interaction, f"Failed to load extension {extension_name}: {e}")

    @owner_only()
    @app_commands.command(name="unload", description="Unload an extension")
    async def unload(self, interaction: discord.Interaction, extension_name: str):
        try:
            await self.bot.unload_extension(extension_name)
            await self.send_ephemeral_message(interaction, f"Extension {extension_name} unloaded")
            logging.info(f"Extension {extension_name} unloaded successfully")
        except Exception as e:
            logging.error(f"Failed to unload extension {extension_name}: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_message(interaction, f"Failed to unload extension {extension_name}: {e}")

    @owner_only()
    @app_commands.command(name="reload", description="Reload an extension")
    async def reload(self, interaction: discord.Interaction, extension_name: str):
        try:
            await self.bot.reload_extension(extension_name)
            await self.send_ephemeral_message(interaction, f"Extension {extension_name} reloaded")
            logging.info(f"Extension {extension_name} reloaded successfully")
        except Exception as e:
            logging.error(f"Failed to reload extension {extension_name}: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_message(interaction, f"Failed to reload extension {extension_name}: {e}")

    @owner_only()
    @app_commands.command(name="status", description="Change the bot's status")
    async def status(self, interaction: discord.Interaction, status: str):
        try:
            await self.bot.change_presence(activity=discord.Game(name=status))
            await self.send_ephemeral_message(interaction, f"Status changed to: {status}")
            logging.info(f"Bot status changed to: {status}")
        except Exception as e:
            logging.error(f"Failed to change status: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_message(interaction, f"Failed to change status: {e}")

    @owner_only()
    @app_commands.command(name="list_extensions", description="List all loaded extensions")
    async def list_extensions(self, interaction: discord.Interaction):
        extensions = ', '.join(self.bot.extensions.keys())
        await self.send_ephemeral_message(interaction, f"Loaded extensions: {extensions}")
        logging.info("Listed all loaded extensions")

    @owner_only()
    @app_commands.command(name="broadcast", description="Broadcast a message to specified channels across all servers")
    async def broadcast(self, interaction: discord.Interaction, message: str, channel_name: str):
        embed = discord.Embed(title="Broadcast Message", description=message, color=discord.Color.blue())

        for guild in self.bot.guilds:
            target_channel = None
            for channel in guild.text_channels:
                if channel_name.lower() in channel.name.lower():
                    target_channel = channel
                    break

            if target_channel:
                try:
                    await target_channel.send(embed=embed)
                    logging.info(f"Sent broadcast message to {guild.name} in {target_channel.name}")
                except Exception as e:
                    logging.error(f"Failed to send message to {guild.name} in {target_channel.name}: {e}\n{traceback.format_exc()}")
            else:
                logging.warning(f"Channel {channel_name} not found in {guild.name}")

        await self.send_ephemeral_message(interaction, "Broadcast message sent to all servers")
        logging.info("Broadcast message sent to all servers")

async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))