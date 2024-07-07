# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

  - **Added** for new features.
  - **Changed** for changes in existing functionality.
  - **Deprecated** for soon-to-be removed features.
  - **Removed** for now removed features.
  - **Fixed** for any bug fixes.
  - **Security* in case of vulnerabilities.

## [Unreleased]

   ## [1.2.5](https://github.com/CodeGuardianSOF/DiscordBot/releases/tag/v1.2.5) - 2024.07.07

### Changed

 - Improved cog:moderation,utils.
 - The mute command now has a duration and the unmute command is no longer needed.

### Added

 - Added a setup.sh file for Linux and MacOS for automatic installation.
 - Auto create Muted role for mute command if it doesnt exist.
 - Graceful shutdown where the user can tap ctrl + c in the terminal and the bot shuts down gracefully without half stopping operations.

### Removed

 - Some logging messages in main.py.
 - Unmute command.

### Fixed

 - Serverinfo command giving error "NoneType has no object url".
 - Shutdown command not working on Linux.

   ## [1.2.0](https://github.com/CodeGuardianSOF/DiscordBot/releases/tag/v1.2.0) - 2024.07.06
   
### Changed

 - Improved commands: ban,unban,mute,poll,remindme.
 - Changed the way unban command sent dms.
 - Remind me cannot tag roles now to prevent spamming.

### Fixed
 - Unban command not dming users.
