import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
from datetime import datetime, timedelta

class ModerationCog(commands.GroupCog, name="moderation"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("ModerationCog initialized")

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        dm_embed = discord.Embed(
            title="⚠️ You have been kicked!",
            description=f'You have been kicked from **{interaction.guild.name}** for: **{reason}**',
            color=discord.Color.red()
        )
        if interaction.guild.icon:
            dm_embed.set_thumbnail(url=interaction.guild.icon.url)
        dm_embed.set_footer(text="Contact an admin if you think this is a mistake.")

        try:
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            logging.warning(f"Failed to send DM to {member}")

        try:
            await member.kick(reason=reason)
            kick_embed = discord.Embed(
                title="🚫 Member Kicked",
                description=f'{member.mention} has been kicked for: **{reason}**',
                color=discord.Color.orange()
            )
            if member.avatar:
                kick_embed.set_thumbnail(url=member.avatar.url)
            kick_embed.set_footer(text="Kick executed successfully.")
            await interaction.response.send_message(embed=kick_embed, ephemeral=True)
        except discord.Forbidden as e:
            logging.error(f"Failed to kick {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to kick {member.mention}: Insufficient permissions.', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to kick {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to kick {member.mention}: An unexpected error occurred.', ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        dm_embed = discord.Embed(
            title="⚠️ You have been banned!",
            description=f'You have been banned from **{interaction.guild.name}** for: **{reason}**',
            color=discord.Color.red()
        )
        if interaction.guild.icon:
            dm_embed.set_thumbnail(url=interaction.guild.icon.url)
        dm_embed.set_footer(text="Contact an admin if you think this is a mistake.")

        try:
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            logging.warning(f"Failed to send DM to {member}")

        try:
            await member.ban(reason=reason)
            ban_embed = discord.Embed(
                title="🚫 Member Banned",
                description=f'{member.mention} has been banned for: **{reason}**',
                color=discord.Color.red()
            )
            if member.avatar:
                ban_embed.set_thumbnail(url=member.avatar.url)
            ban_embed.set_footer(text="Ban executed successfully.")
            await interaction.response.send_message(embed=ban_embed, ephemeral=True)
        except discord.Forbidden as e:
            logging.error(f"Failed to ban {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to ban {member.mention}: Insufficient permissions.', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to ban {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to ban {member.mention}: An unexpected error occurred.', ephemeral=True)

    @app_commands.command(name="unban", description="Unban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def unban(self, interaction: discord.Interaction, user_id: str, *, reason: str = "No reason provided"):
        logging.debug(f"Received unban command for user ID: {user_id}")
        try:
            user_id_int = int(user_id)
            user = await self.bot.fetch_user(user_id_int)
            logging.debug(f"Fetched user: {user}")
            await interaction.guild.unban(user, reason=reason)
            unban_embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f'{user.mention} has been unbanned.',
                color=discord.Color.green()
            )
            if user.avatar:
                unban_embed.set_thumbnail(url=user.avatar.url)
            unban_embed.set_footer(text="Unban executed successfully.")
            await interaction.response.send_message(embed=unban_embed, ephemeral=True)
            try:
                dm_embed = discord.Embed(
                    title="✅ You have been unbanned!",
                    description=f'You have been unbanned from **{interaction.guild.name}**.',
                    color=discord.Color.green()
                )
                if interaction.guild.icon:
                    dm_embed.set_thumbnail(url=interaction.guild.icon.url)
                dm_embed.set_footer(text="Welcome back!")
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                logging.warning(f"Failed to send DM to {user}")
        except ValueError:
            logging.error(f"Invalid user ID: {user_id}")
            await interaction.response.send_message(f'❌ Invalid user ID. Please ensure you entered a valid 18-digit integer.', ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message(f'❌ User with ID {user_id} not found.', ephemeral=True)
        except discord.Forbidden as e:
            logging.error(f"Failed to unban user {user_id}: {e}")
            await interaction.response.send_message(f'❌ Failed to unban user: Insufficient permissions.', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to unban user {user_id}: {e}")
            await interaction.response.send_message(f'❌ Failed to unban user: An unexpected error occurred.', ephemeral=True)

    @app_commands.command(name="mute", description="Mute a member in the server")
    @app_commands.describe(duration="Duration of the mute (e.g., '1h' for 1 hour, '10m' for 10 minutes, etc.)")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            await interaction.response.send_message("❌ Muted role not found.", ephemeral=True)
            return

        try:
            await member.add_roles(mute_role, reason=reason)
            mute_embed = discord.Embed(
                title="🔇 Member Muted",
                description=f'{member.mention} has been muted for: **{reason}**',
                color=discord.Color.dark_gray()
            )
            if member.avatar:
                mute_embed.set_thumbnail(url=member.avatar.url)
            mute_embed.set_footer(text="Mute executed successfully.")
            await interaction.response.send_message(embed=mute_embed, ephemeral=True)

            # Parse duration
            duration_seconds = self.parse_duration(duration)
            if duration_seconds is None:
                await interaction.response.send_message("❌ Invalid duration format. Please use '1h', '10m', etc.", ephemeral=True)
                return

            # Schedule unmute
            await self.schedule_unmute(member, interaction.guild, duration_seconds, reason)

        except discord.Forbidden as e:
            logging.error(f"Failed to mute {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to mute {member.mention}: Insufficient permissions.', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to mute {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to mute {member.mention}: An unexpected error occurred.', ephemeral=True)

    def parse_duration(self, duration: str):
        """Parse duration string and return the duration in seconds."""
        try:
            unit = duration[-1]
            amount = int(duration[:-1])
            if unit == 'h':
                return amount * 3600
            elif unit == 'm':
                return amount * 60
            elif unit == 's':
                return amount
            else:
                return None
        except (ValueError, IndexError):
            return None

    async def schedule_unmute(self, member: discord.Member, guild: discord.Guild, duration_seconds: int, reason: str):
        """Schedule unmute task."""
        await asyncio.sleep(duration_seconds)
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role:
            try:
                await member.remove_roles(mute_role, reason=reason)
                logging.debug(f"Unmuted {member.mention} after duration.")
            except discord.Forbidden as e:
                logging.error(f"Failed to unmute {member.mention}: {e}")
            except Exception as e:
                logging.error(f"Failed to unmute {member.mention}: {e}")

    @app_commands.command(name="unmute", description="Unmute a member in the server")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            await interaction.response.send_message("❌ Muted role not found.", ephemeral=True)
            return

        try:
            await member.remove_roles(mute_role, reason=reason)
            unmute_embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f'{member.mention} has been unmuted.',
                color=discord.Color.green()
            )
            if member.avatar:
                unmute_embed.set_thumbnail(url=member.avatar.url)
            unmute_embed.set_footer(text="Unmute executed successfully.")
            await interaction.response.send_message(embed=unmute_embed, ephemeral=True)
        except discord.Forbidden as e:
            logging.error(f"Failed to unmute {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to unmute {member.mention}: Insufficient permissions.', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to unmute {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to unmute {member.mention}: An unexpected error occurred.', ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))

# Setup logging
logging.basicConfig(level=logging.DEBUG)
