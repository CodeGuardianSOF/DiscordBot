import discord
from discord import app_commands
from discord.ext import commands
import logging
import traceback
import os
from datetime import datetime, timedelta
import psutil

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
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Permission Denied",
                        description="You do not have permission to use this command.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
            return is_owner
        return app_commands.check(predicate)

    async def send_ephemeral_embed(self, interaction, title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @owner_only()
    @app_commands.command(name="shutdown", description="Shut down the bot")
    async def shutdown(self, interaction: discord.Interaction):
        await self.send_ephemeral_embed(interaction, "Shutting Down", "The bot is shutting down...")
        logging.info("Bot is shutting down by the owner's command")
        await self.bot.close()

    @owner_only()
    @app_commands.command(name="load", description="Load an extension")
    async def load(self, interaction: discord.Interaction, extension_name: str):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.load_extension(extension_name)
            await self.send_ephemeral_embed(interaction, "Extension Loaded", f"Extension `{extension_name}` has been loaded successfully.")
            logging.info(f"Extension {extension_name} loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load extension {extension_name}: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_embed(interaction, "Load Failed", f"Failed to load extension `{extension_name}`: {e}", discord.Color.red())
    @owner_only()
    @app_commands.command(name="unload", description="Unload an extension")
    async def unload(self, interaction: discord.Interaction, extension_name: str):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.unload_extension(extension_name)
            await self.send_ephemeral_embed(interaction, "Extension Unloaded", f"Extension `{extension_name}` has been unloaded successfully.")
            logging.info(f"Extension {extension_name} unloaded successfully")
        except Exception as e:
            logging.error(f"Failed to unload extension {extension_name}: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_embed(interaction, "Unload Failed", f"Failed to unload extension `{extension_name}`: {e}", discord.Color.red())

    @owner_only()
    @app_commands.command(name="reload", description="Reload an extension")
    async def reload(self, interaction: discord.Interaction, extension_name: str):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(extension_name)
            await self.send_ephemeral_embed(interaction, "Extension Reloaded", f"Extension `{extension_name}` has been reloaded successfully.")
            logging.info(f"Extension {extension_name} reloaded successfully")
        except Exception as e:
            logging.error(f"Failed to reload extension {extension_name}: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_embed(interaction, "Reload Failed", f"Failed to reload extension `{extension_name}`: {e}", discord.Color.red())

    @owner_only()
    @app_commands.command(name="status", description="Change the bot's status")
    async def status(self, interaction: discord.Interaction, status: str):
        try:
            await self.bot.change_presence(activity=discord.Game(name=status))
            await self.send_ephemeral_embed(interaction, "Status Changed", f"Bot status changed to: `{status}`")
            logging.info(f"Bot status changed to: {status}")
        except Exception as e:
            logging.error(f"Failed to change status: {e}\n{traceback.format_exc()}")
            await self.send_ephemeral_embed(interaction, "Status Change Failed", f"Failed to change status: {e}", discord.Color.red())

    @owner_only()
    @app_commands.command(name="broadcast", description="Broadcast a message to specified channels across all servers")
    async def broadcast(self, interaction: discord.Interaction, message: str, channel_name: str):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="Broadcast Message", description=message, color=discord.Color.blue())
        failed_guilds = []

        for guild in self.bot.guilds:
            target_channel = discord.utils.get(guild.text_channels, name=channel_name)
            if target_channel:
                try:
                    await target_channel.send(embed=embed)
                    logging.info(f"Sent broadcast message to {guild.name} in {target_channel.name}")
                except Exception as e:
                    logging.error(f"Failed to send message to {guild.name} in {target_channel.name}: {e}\n{traceback.format_exc()}")
                    failed_guilds.append(guild.name)
            else:
                logging.warning(f"Channel {channel_name} not found in {guild.name}")
                failed_guilds.append(guild.name)

        if failed_guilds:
            failed_guilds_str = ', '.join(failed_guilds)
            await self.send_ephemeral_embed(interaction, "Broadcast Partially Failed", f"Failed to send message to the following guilds: {failed_guilds_str}", discord.Color.orange())
        else:
            await self.send_ephemeral_embed(interaction, "Broadcast Sent", "Broadcast message sent to all servers")
            logging.info("Broadcast message sent to all servers")

    @owner_only()
    @app_commands.command(name="list_guilds", description="List all guilds the bot is in")
    async def list_guilds(self, interaction: discord.Interaction):
        guilds = '\n'.join([f"{guild.name} (ID: {guild.id}, Members: {guild.member_count})" for guild in self.bot.guilds])
        await self.send_ephemeral_embed(interaction, "Guilds List", f"**Guilds:**\n{guilds}")
        logging.info("Listed all guilds")

    @owner_only()
    @app_commands.command(name="guild_info", description="Get information about a specific guild")
    async def guild_info(self, interaction: discord.Interaction, guild_id: str):
        try:
            guild_id = int(guild_id)
            guild = self.bot.get_guild(guild_id)
            if guild:
                info = (f"**Guild Name:** {guild.name}\n"
                        f"**ID:** {guild.id}\n"
                        f"**Members:** {guild.member_count}\n"
                        f"**Owner:** {guild.owner}\n"
                        f"**Created At:** {guild.created_at}")
                await self.send_ephemeral_embed(interaction, "Guild Information", info)
                logging.info(f"Retrieved info for guild {guild.name}")
            else:
                await self.send_ephemeral_embed(interaction, "Guild Not Found", f"Guild with ID `{guild_id}` not found", discord.Color.red())
                logging.warning(f"Guild with ID {guild_id} not found")
        except ValueError:
            await self.send_ephemeral_embed(interaction, "Invalid ID", "The provided guild ID is not a valid integer.", discord.Color.red())

    @owner_only()
    @app_commands.command(name="send_dm", description="Send a direct message to a user")
    async def send_dm(self, interaction: discord.Interaction, user_id: str, message: str):
        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
            if user:
                embed = discord.Embed(
                    title="Message from Server",
                    description=f"Message from server **{interaction.guild.name}** by user **{interaction.user.name}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Message", value=message)

                await user.send(embed=embed)
                await self.send_ephemeral_embed(interaction, "Message Sent", f"Message sent to user `{user.name}`", discord.Color.green())
                logging.info(f"Sent DM to user {user.name} from server {interaction.guild.name}")
            else:
                await self.send_ephemeral_embed(interaction, "User Not Found", f"User with ID `{user_id}` not found", discord.Color.red())
                logging.warning(f"User with ID {user_id} not found")
        except ValueError:
            await self.send_ephemeral_embed(interaction, "Invalid ID", "The provided user ID is not a valid integer.", discord.Color.red())
        except discord.Forbidden:
            await self.send_ephemeral_embed(interaction, "DM Failed", f"Failed to send DM to user. They may have blocked DMs from this server.", discord.Color.red())

    @owner_only()
    @app_commands.command(name="prune_messages", description="Prune messages from a text channel")
    async def prune_messages(self, interaction: discord.Interaction, channel_id: str, limit: int):
        await interaction.response.defer(ephemeral=True)
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                deleted = await channel.purge(limit=limit)
                await self.send_ephemeral_embed(interaction, "Messages Pruned", f"Deleted {len(deleted)} messages from {channel.mention}", discord.Color.green())
                logging.info(f"Pruned {len(deleted)} messages from {channel.name}")
            else:
                await self.send_ephemeral_embed(interaction, "Channel Not Found", f"Text channel with ID `{channel_id}` not found", discord.Color.red())
                logging.warning(f"Text channel with ID {channel_id} not found")
        except ValueError:
            await self.send_ephemeral_embed(interaction, "Invalid ID", "The provided channel ID is not a valid integer.", discord.Color.red())

    @app_commands.command(name="list_issues", description="List issues with the bot's script or dependencies")
    async def list_issues(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        issues = []
        status_messages = []

        # Helper function to summarize error messages
        def summarize_error(error_message):
            words = error_message.split()
            if len(words) < 100:
                return error_message
            else:
                return ' '.join(words[:70]) + '...'

        # Check for specific files or directories
        required_files = ['main.py', 'cogs', 'config/config.yaml', 'logs']
        missing_files = [file for file in required_files if not os.path.exists(file)]
        if missing_files:
            issues.append(f"**Missing Files or Directories:**\n{', '.join(missing_files)[:1000]}")
        else:
            status_messages.append("All required files and directories are present.")

        # Basic health check
        try:
            await self.bot.application_info()
            status_messages.append("Basic health check passed.")
        except Exception as e:
            error_message = str(e)
            issues.append(f"Basic health check failed: {summarize_error(error_message)}")
            issues.append(f"Full error: {error_message}")

        # Check recent errors in log file
        log_file_path = 'logs/bot.log'  # Change this to the actual path of your log file
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as log_file:
                    log_lines = log_file.readlines()
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    recent_errors = []
                    for line in log_lines:
                        if "ERROR" in line:
                            try:
                                log_time_str = line.split(' ')[0] + ' ' + line.split(' ')[1]
                                log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S,%f")
                                if log_time > one_hour_ago:
                                    recent_errors.append(line[:100])
                            except ValueError as e:
                                issues.append(f"Error parsing log time: {log_time_str} - {str(e)}")
                    if recent_errors:
                        issues.append(f"**Recent Errors in Last Hour:**\n```\n{''.join(recent_errors)}\n```")
                    else:
                        status_messages.append("No recent errors in the last hour.")
            else:
                issues.append("Log file not found.")
        except Exception as e:
            error_message = str(e)
            issues.append(f"Error checking log file: {summarize_error(error_message)}")
            issues.append(f"Full error: {error_message}")

        # Advanced checks

        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 80:
            issues.append(f"High CPU usage detected: {cpu_usage}%")
        else:
            status_messages.append(f"CPU usage is within acceptable limits: {cpu_usage}%")

        # Check memory usage
        memory_info = psutil.virtual_memory()
        if memory_info.percent > 80:
            issues.append(f"High memory usage detected: {memory_info.percent}%")
        else:
            status_messages.append(f"Memory usage is within acceptable limits: {memory_info.percent}%")

        # Check disk space
        disk_info = psutil.disk_usage('/')
        if disk_info.percent > 80:
            issues.append(f"Low disk space detected: {disk_info.percent}% used")
        else:
            status_messages.append(f"Disk space is within acceptable limits: {disk_info.percent}% used")

        # Check active connections
        connections = psutil.net_connections()
        if not connections:
            issues.append("No active network connections found.")
        else:
            status_messages.append(f"Active network connections found: {len(connections)}")

        # Check uptime
        uptime_seconds = (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
        uptime_str = str(timedelta(seconds=uptime_seconds))
        status_messages.append(f"System uptime: {uptime_str}")

        # Determine embed color based on issues
        embed_color = discord.Color.green() if not issues else discord.Color.red()

        # Create and send the embed
        embed = discord.Embed(title="Bot Issues", color=embed_color)
        if not issues:  # No issues found
            embed.add_field(name="Status", value="Everything is good.", inline=False)
        else:
            for issue in issues:
                embed.add_field(name="Issue", value=issue, inline=False)

        for status in status_messages:
            embed.add_field(name="Status", value=status, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)
        logging.info("Listed bot issues")

async def setup(bot):
    await bot.add_cog(OwnerCog(bot))