import discord
from discord import app_commands
from discord.ext import commands
import random
import logging

class FunCog(commands.GroupCog, name="fun"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        logging.debug("FunCog initialized")

    @app_commands.command(name="roll", description="Roll a dice")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        result = random.randint(1, sides)
        await interaction.response.send_message(f'You rolled a {result}', ephemeral=True)

    @app_commands.command(name="fact", description="Get a random fact")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def fact(self, interaction: discord.Interaction):
        facts = [
            "Honey never spoils.",
            "A flock of crows is known as a murder.",
            "Bananas are berries but strawberries aren't."
        ]
        await interaction.response.send_message(random.choice(facts), ephemeral=True)

    @app_commands.command(name="joke", description="Get a random joke")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def joke(self, interaction: discord.Interaction):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "How does a penguin build its house? Igloos it together!",
            "Why was the math book sad? Because it had too many problems."
        ]
        await interaction.response.send_message(random.choice(jokes), ephemeral=True)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = ["Yes", "No", "Maybe", "Definitely", "Absolutely not"]
        await interaction.response.send_message(f'🎱 {random.choice(responses)}', ephemeral=True)

    @app_commands.command(name="rps", description="Play rock-paper-scissors with the bot")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def rps(self, interaction: discord.Interaction, choice: str):
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)
        result = "It's a tie!"
        if (choice == "rock" and bot_choice == "scissors") or \
           (choice == "paper" and bot_choice == "rock") or \
           (choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
        elif choice != bot_choice:
            result = "You lose!"
        await interaction.response.send_message(f'I chose {bot_choice}. {result}', ephemeral=True)

    @app_commands.command(name="trivia", description="Answer a trivia question")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def trivia(self, interaction: discord.Interaction):
        # Example questions; in a real scenario, fetch from a trivia API
        questions = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "Who wrote 'To Kill a Mockingbird'?", "answer": "Harper Lee"},
            {"question": "What is the largest planet in our Solar System?", "answer": "Jupiter"}
        ]
        question = random.choice(questions)
        await interaction.response.send_message(question["question"], ephemeral=True)
        self.bot.trivia_answer = question["answer"]

    @app_commands.command(name="answer", description="Answer the trivia question")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def answer(self, interaction: discord.Interaction, answer: str):
        correct_answer = getattr(self.bot, 'trivia_answer', None)
        if correct_answer is None:
            await interaction.response.send_message("No trivia question has been asked!", ephemeral=True)
        elif answer.lower() == correct_answer.lower():
            await interaction.response.send_message("Correct!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Incorrect! The correct answer was {correct_answer}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))

