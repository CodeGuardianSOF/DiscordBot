import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio

class ModerationCog(commands.GroupCog, name="moderation"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("ModerationCog initialized")

    async def cog_check(self, interaction):
        return interaction.guild is not None

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"This command is on cooldown. Try again after {error.retry_after:.2f} seconds.", ephemeral=True)
        else:
            logging.error(f"An error occurred: {error}")
            await interaction.response.send_message("An unexpected error occurred. Please try again later.", ephemeral=True)

    async def is_authorized(self, interaction, target_member):
        if interaction.user.top_role <= target_member.top_role:
            await interaction.response.send_message(f"❌ You cannot moderate {target_member.mention} due to role hierarchy.", ephemeral=True)
            return False
        if target_member == interaction.user:
            await interaction.response.send_message("❌ You cannot moderate yourself.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not await self.is_authorized(interaction, member):
            return

        if not member.bot:
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
                await interaction.followup.send(f"❌ Could not DM {member.mention} about the kick.", ephemeral=True)

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
        if not await self.is_authorized(interaction, member):
            return

        if not member.bot:
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
                await interaction.followup.send(f"❌ Could not DM {member.mention} about the ban.", ephemeral=True)

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
    async def unban(self, interaction: discord.Interaction, user_id: str, *, note: str = "No note provided"):
        logging.debug(f"Received unban command for user ID: {user_id}")
        try:
            user_id_int = int(user_id)
            user = await self.bot.fetch_user(user_id_int)
            logging.debug(f"Fetched user: {user}")
            await interaction.guild.unban(user, reason=note)
            unban_embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f'{user.mention} has been unbanned.',
                color=discord.Color.green()
            )
            if user.avatar:
                unban_embed.set_thumbnail(url=user.avatar.url)
            unban_embed.set_footer(text="Unban executed successfully.")
            await interaction.response.send_message(embed=unban_embed, ephemeral=True)

            if not user.bot:
                try:
                    dm_embed = discord.Embed(
                        title="✅ You have been unbanned!",
                        description=f'You have been unbanned from **{interaction.guild.name}**. Note: **{note}**.',
                        color=discord.Color.green()
                    )
                    if interaction.guild.icon:
                        dm_embed.set_thumbnail(url=interaction.guild.icon.url)
                    dm_embed.set_footer(text="Welcome back!")
                    await user.send(embed=dm_embed)
                except discord.Forbidden:
                    logging.warning(f"Failed to send DM to {user}")
                    await interaction.followup.send(f"❌ Could not DM {user.mention} about the unban.", ephemeral=True)
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
        if not await self.is_authorized(interaction, member):
            return

        mute_role = await self.create_mute_role(interaction.guild)
        if not mute_role:
            await interaction.response.send_message("❌ Failed to create/find Muted role.", ephemeral=True)
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

            duration_seconds = self.parse_duration(duration)
            await asyncio.sleep(duration_seconds)
            await member.remove_roles(mute_role, reason="Mute duration expired")

            unmute_embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f'{member.mention} has been unmuted.',
                color=discord.Color.green()
            )
            if member.avatar:
                unmute_embed.set_thumbnail(url=member.avatar.url)
            unmute_embed.set_footer(text="Mute duration expired.")
            await interaction.followup.send(embed=unmute_embed, ephemeral=True)
        except discord.Forbidden as e:
            logging.error(f"Failed to mute {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to mute {member.mention}: Insufficient permissions.', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to mute {member.mention}: {e}")
            await interaction.response.send_message(f'❌ Failed to mute {member.mention}: An unexpected error occurred.', ephemeral=True)

    @app_commands.command(name="unmute", description="Unmute a member in the server")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not await self.is_authorized(interaction, member):
            return

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

    def parse_duration(self, duration: str):
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit in units:
            try:
                value = int(duration[:-1])
                return value * units[unit]
            except ValueError:
                return None
        return None

    async def create_mute_role(self, guild):
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role is None:
            try:
                mute_role = await guild.create_role(name="Muted", reason="Mute role created for muting members.")
                for channel in guild.channels:
                    await channel.set_permissions(mute_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)
            except discord.Forbidden as e:
                logging.error(f"Failed to create Muted role in {guild.name}: {e}")
                return None
        return mute_role

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))

# Setup logging
logging.basicConfig(level=logging.DEBUG)
