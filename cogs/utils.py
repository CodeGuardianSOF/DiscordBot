import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio

class UtilsCog(commands.GroupCog, name="utils"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("UtilsCog initialized")

    @app_commands.command(name="remindme", description="Set a reminder")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def remindme(self, interaction: discord.Interaction, time: int, *, message: str):
        """Sets a reminder for the user."""
        try:
            await interaction.response.send_message(f"Reminder set for {time} seconds", ephemeral=True)
            await asyncio.sleep(time)
            await interaction.followup.send(f"Reminder: {message}")
        except Exception as e:
            logging.exception("Failed to set reminder")
            await interaction.followup.send(f"An error occurred while setting the reminder: {e}", ephemeral=True)

    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str):
        """Creates a poll with two options."""
        embed = discord.Embed(title="Poll", description=question, color=discord.Color.blurple())
        embed.add_field(name="Option 1", value=option1, inline=False)
        embed.add_field(name="Option 2", value=option2, inline=False)
        
        try:
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
            if message:
                await message.add_reaction("1️⃣")
                await message.add_reaction("2️⃣")
                await interaction.followup.send("Poll created successfully!", ephemeral=True)
            else:
                await interaction.followup.send("Failed to create poll. Please try again.", ephemeral=True)
        except Exception as e:
            logging.exception("Failed to create poll")
            await interaction.followup.send(f"An error occurred while creating the poll: {e}", ephemeral=True)

    @app_commands.command(name="userinfo", description="Get information about a user")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member):
        """Gets information about a specific user."""
        try:
            embed = discord.Embed(title=f"{member.name}'s Info", color=discord.Color.blue())
            embed.add_field(name="ID", value=member.id, inline=False)
            embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logging.exception("Failed to get user info")
            await interaction.response.send_message(f"An error occurred while retrieving user info: {e}", ephemeral=True)

    @app_commands.command(name="serverinfo", description="Get information about the server")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def serverinfo(self, interaction: discord.Interaction):
        """Gets information about the server."""
        guild = interaction.guild
        try:
            embed = discord.Embed(title=f"{guild.name}'s Info", color=discord.Color.green())
            embed.add_field(name="ID", value=guild.id, inline=False)
            embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
            embed.add_field(name="Member Count", value=guild.member_count, inline=False)
            embed.add_field(name="Roles", value=", ".join([role.name for role in guild.roles if role.name != "@everyone"]), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logging.exception("Failed to get server info")
            await interaction.response.send_message(f"An error occurred while retrieving server info: {e}", ephemeral=True)

    @app_commands.command(name="avatar", description="Get the avatar of a user")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def avatar(self, interaction: discord.Interaction, member: discord.Member):
        """Gets the avatar of a specific user."""
        try:
            embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
            embed.set_image(url=member.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logging.exception("Failed to get avatar")
            await interaction.response.send_message(f"An error occurred while retrieving the avatar: {e}", ephemeral=True)

    @app_commands.command(name="health", description="Check the bot's health status")
    async def health(self, interaction: discord.Interaction):
        """Checks the bot's health status."""
        try:
            await interaction.response.send_message("Bot is up and running!", ephemeral=True)
        except Exception as e:
            logging.exception("Health check failed")
            await interaction.response.send_message(f"An error occurred during the health check: {e}", ephemeral=True)

    @remindme.error
    @poll.error
    @userinfo.error
    @serverinfo.error
    @avatar.error
    async def command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"⏳ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
        else:
            logging.exception("An error occurred")
            await interaction.response.send_message(f"An unexpected error occurred: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(UtilsCog(bot))
    logging.debug("UtilsCog loaded")

# Setup logging
logging.basicConfig(level=logging.DEBUG)
