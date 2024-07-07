import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
import re

class UtilsCog(commands.GroupCog, name="utils"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("UtilsCog initialized")

    def parse_time(self, time_str: str) -> int:
        match = re.match(r"(\d+)([smhd])", time_str)
        if not match:
            return None
        value, unit = match.groups()
        value = int(value)
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        return None

    @app_commands.command(name="remindme", description="Set a reminder")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def remindme(self, interaction: discord.Interaction, time: str, *, message: str):
        """Sets a reminder for the user."""
        if any(re.findall(r"@everyone|@here|<@&\d+>|<@!\d+>", message)):
            await interaction.response.send_message("Reminders cannot contain user or role mentions.", ephemeral=True)
            logging.warning(f"User {interaction.user} tried to set a reminder with mentions.")
            return

        seconds = self.parse_time(time)
        if seconds is None:
            await interaction.response.send_message("Invalid time format. Use numbers followed by s, m, h, or d (e.g., 10s, 5m, 1h, 2d).", ephemeral=True)
            return

        try:
            await interaction.response.send_message(f"Reminder set for {time}.", ephemeral=True)
            await asyncio.sleep(seconds)
            await interaction.followup.send(f"Reminder: {message}")
        except Exception as e:
            logging.exception("Failed to set reminder")
            await interaction.followup.send(f"An error occurred while setting the reminder: {e}", ephemeral=True)

    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None, option6: str = None, option7: str = None, option8: str = None, option9: str = None, option10: str = None):
        """Creates a poll with up to 10 options."""
        options = [option for option in [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10] if option is not None]
        if len(options) < 2:
            await interaction.response.send_message("Poll must have at least 2 options.", ephemeral=True)
            return

        embed = discord.Embed(title="Poll", description=question, color=discord.Color.blurple())
        for idx, option in enumerate(options, start=1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        try:
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
            if message:
                reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
                for reaction in reactions[:len(options)]:
                    await message.add_reaction(reaction)
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
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="ID", value=member.id, inline=False)
            embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=False)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
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
            icon_url = str(guild.icon.url) if guild.icon else ""
            embed.set_thumbnail(url=icon_url)
            embed.add_field(name="ID", value=guild.id, inline=False)
            embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
            embed.add_field(name="Member Count", value=guild.member_count, inline=False)
            embed.add_field(name="Roles", value=", ".join([role.name for role in guild.roles if role.name != "@everyone"]), inline=False)
            embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            user_avatar_url = str(interaction.user.avatar.url) if interaction.user.avatar else str(interaction.user.default_avatar.url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=user_avatar_url)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.exception("Failed to get server info")
            await interaction.response.send_message(f"An error occurred while retrieving server info: {e}", ephemeral=True)

    @app_commands.command(name="avatar", description="Get the avatar of a user")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def avatar(self, interaction: discord.Interaction, member: discord.Member):
        """Gets the avatar of a specific user."""
        try:
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
            embed.set_image(url=avatar_url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logging.exception("Failed to get avatar")
            await interaction.response.send_message(f"An error occurred while retrieving the avatar: {e}", ephemeral=True)

    @app_commands.command(name="ping", description="Check the bot's latency")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def ping(self, interaction: discord.Interaction):
        """Checks the bot's latency."""
        latency = self.bot.latency * 1000  # Convert to milliseconds
        await interaction.response.send_message(f"Pong! Latency is {latency:.2f}ms", ephemeral=True)

    @app_commands.command(name="serverstats", description="Get server statistics")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def serverstats(self, interaction: discord.Interaction):
        """Gets server statistics."""
        guild = interaction.guild
        try:
            embed = discord.Embed(title=f"{guild.name}'s Statistics", color=discord.Color.orange())
            embed.add_field(name="Total Members", value=guild.member_count, inline=False)
            online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
            embed.add_field(name="Online Members", value=online_members, inline=False)
            embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=False)
            embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=False)
            embed.add_field(name="Roles", value=len(guild.roles), inline=False)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.exception("Failed to get server stats")
            await interaction.response.send_message(f"An error occurred while retrieving server stats: {e}", ephemeral=True)

    @app_commands.command(name="roleinfo", description="Get information about a role")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Gets information about a specific role."""
        try:
            embed = discord.Embed(title=f"{role.name} Role Info", color=role.color)
            embed.add_field(name="ID", value=role.id, inline=False)
            embed.add_field(name="Color", value=str(role.color), inline=False)
            embed.add_field(name="Position", value=role.position, inline=False)
            embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
            embed.add_field(name="Members", value=len(role.members), inline=False)
            user_avatar_url = str(interaction.user.avatar.url) if interaction.user.avatar else str(interaction.user.default_avatar.url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=user_avatar_url)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.exception("Failed to get role info")
            await interaction.response.send_message(f"An error occurred while retrieving role info: {e}", ephemeral=True)
    @remindme.error
    @poll.error
    @userinfo.error
    @serverinfo.error
    @avatar.error
    @ping.error
    @serverstats.error
    @roleinfo.error
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
