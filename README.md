
# 🤖 Discord Bot

A sophisticated Discord bot with multiple commands and logging capabilities. Configurable via a `config.yaml` file.

## ✨ Features

- 📝 **Logging:** Logs all activities to `logs/bot.log`.
- ⚙️ **Configuration:** Easy configuration using `config.yaml`.
- 🧰**Bot Owner Commands:**
  - `/shutdown` - Remotly shut the bot down.
  - `/status` - Check if but is working/online.
  - `/load <cog_name>` - Load a cog, name must be like cogs.fun,cogs.moderation etc.
  - `/unload <cog_name>` - Unload a cog, name must be like cogs.fun,cogs.moderation etc. Note this command will make the commands the cog has unusable.
  - `/reload <cog_name>` - Reload a cog, name must be like cogs.fun,cogs.moderation etc.
- 🛡️ **Moderation Commands:**
  - `/ban <user> <reason>` - Ban a user.
  - `/kick <user> <reason>` - Kick a user.
  - `/mute <user> <duration>` - Mute a user.
  - `/unban <user> <note>` - Unban a user.
- 🎲 **Fun Commands:**
  - `/roll` - Roll a dice.
  - `/8ball <question>` - Get answers from the magic 8-ball.
  - `/fact` - Get a random fact.
  - `/joke` - Get a random joke.
  - `/rps <choice>` - Play rock-paper-scissors with the bot.
  - `/trivia` - Get a random trivia question.
  - `/answer <answer>` - Answer the trivia question. Must use the trivia command first.
- 🔍 **Utility Commands:**
  - `/userinfo <user>` - Get information about a user.
  - `/serverinfo` - Get information about the server.
  - `/avatar <user>` - Get the avatar of a user.
  - `/ping` - Check bot's latency.
  - `/poll <question> <option1> <option2>` - Creates a poll, supports up to 8 options.
  - `/remindme <duration>  <message>` - Reminds a user on a specific time, with a custom message.
  - `/roleinfo <role>` - Get info about a specific role.

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/CodeGuardianSOF/DiscordBot.git
   cd DiscordBot
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**

   Edit the `config.yaml` file to include your bot token and other configurations.

4. **Run the bot:**

   ```bash
   python bot.py
   ```

## 🔧 Commands

### Moderation Commands

- `/ping`: Checks the bot's latency.
- `/ban <user>`: Bans the specified user.
- `/kick <user>`: Kicks the specified user.
- `/mute <user>`: Mutes the specified user.
- `/unban <user>`: Unbans the specified user.
- `/unmute <user>`: Unmutes the specified user.

### Fun Commands

- `/roll`: Rolls a dice and returns a random number between 1 and 6.
- `/8ball <question>`: Provides an answer to a yes/no question using the magic 8-ball.

### Utility Commands

- `/userinfo <user>`: Gets information about a user.
- `/serverinfo`: Gets information about the server.
- `/avatar <user>`: Gets the avatar of a user.
- `/weather <city>`: Gets the current weather for a city.

## 📄 Logging

All bot activities are logged in the `logs/bot.log` file. Make sure to check this file for debugging and monitoring bot activities.

## ⚙️ Configuration

The bot can be configured via the `config.yaml` file. This file includes necessary settings like the bot token, command prefixes, and other configuration options.

## 🐧 Setup Tutorial on Linux

1. **Update your system:**

   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python 3.7+:**

   ```bash
   sudo apt install python3
   sudo apt install python3-pip
   ```

3. **Clone the GitHub repository:**

   ```bash
   git clone https://github.com/CodeGuardianSOF/DiscordBot.git
   cd DiscordBot
   ```

4. **Install dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

5. **Edit the configuration file:**

   Open `config.yaml` and fill in your Discord bot token and other settings.

6. **Run the bot:**

   ```bash
   python3 main.py
   ```

## 🪟 Setup Tutorial on Windows

1. **Update your system:**

   Make sure your Windows is up to date.

2. **Install Python 3.7+:**

   Download and install the latest version of Python from the [official Python website](https://www.python.org/downloads/). Ensure you check the box to add Python to your PATH during installation.

3. **Clone the GitHub repository:**

   Open Command Prompt and run:

   ```bash
   git clone https://github.com/CodeGuardianSOF/DiscordBot.git
   cd DiscordBot
   ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Edit the configuration file:**

   Open `config.yaml` in a text editor and fill in your Discord bot token and other settings.

6. **Run the bot:**

   ```bash
   python main.py
   ```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

