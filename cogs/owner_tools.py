import discord
from discord import app_commands
from discord.ext import commands
import logging

class OwnerCog(commands.GroupCog, name="ownertools"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("OwnerToolsCog initialized")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        is_owner = await self.bot.is_owner(interaction.user)
        if not is_owner:
            logging.warning(f"User {interaction.user} tried to use owner command but is not the owner.")
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return is_owner

    @app_commands.command(name="shutdown", description="Shut down the bot")
    async def shutdown(self, interaction: discord.Interaction):
        if not await self.interaction_check(interaction):
            return
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        await self.bot.close()

    @app_commands.command(name="load", description="Load an extension")
    async def load(self, interaction: discord.Interaction, extension_name: str):
        if not await self.interaction_check(interaction):
            return
        try:
            await self.bot.load_extension(extension_name)
            await interaction.response.send_message(f"Extension {extension_name} loaded", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to load extension {extension_name}: {e}", ephemeral=True)

    @app_commands.command(name="unload", description="Unload an extension")
    async def unload(self, interaction: discord.Interaction, extension_name: str):
        if not await self.interaction_check(interaction):
            return
        try:
            await self.bot.unload_extension(extension_name)
            await interaction.response.send_message(f"Extension {extension_name} unloaded", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unload extension {extension_name}: {e}", ephemeral=True)

    @app_commands.command(name="reload", description="Reload an extension")
    async def reload(self, interaction: discord.Interaction, extension_name: str):
        if not await self.interaction_check(interaction):
            return
        try:
            await self.bot.reload_extension(extension_name)
            await interaction.response.send_message(f"Extension {extension_name} reloaded", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to reload extension {extension_name}: {e}", ephemeral=True)

    @app_commands.command(name="status", description="Change the bot's status")
    async def status(self, interaction: discord.Interaction, status: str):
        if not await self.interaction_check(interaction):
            return
        try:
            await self.bot.change_presence(activity=discord.Game(name=status))
            await interaction.response.send_message(f"Status changed to: {status}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to change status: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))

# Setup logging
logging.basicConfig(level=logging.DEBUG)
