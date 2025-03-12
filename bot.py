import os
import discord
import logging
import random
import platform

from discord.ext import commands
from discord.ui import View, Button, Select
from discord import ButtonStyle
from dotenv import load_dotenv
from agent import TherapyAgent
from agent import UserManager
from agent import OnboardingManager
from agent import ButtonManager

import asyncio
import matplotlib.pyplot as plt
from datetime import datetime

#import certifi
#os.environ['SSL_CERT_FILE'] = certifi.where()

intents = discord.Intents.all()
# Enable message content intent so the bot can read messages.
# The message content intent must be enabled in the Discord Developer Portal as well.
intents.message_content = True

logger = logging.getLogger("discord")

PREFIX = "!"
CUSTOM_STATUS = "therapy chats 🤗"
# Define Button View Class
class FeatureButtons(View):
    def __init__(self):
        super().__init__()
        # Add buttons for different features with separate callbacks
        self.add_item(AffirmationButton())
        self.add_item(SelfCareButton())
        self.add_item(BreatheButton())
        self.add_item(MusicButton())
        self.add_item(ArtButton())
        self.add_item(MindfulButton())
        self.add_item(GratitudeButton())
        self.add_item(GroundButton())

class AffirmationButton(Button):
    def __init__(self):
        super().__init__(label="Affirmation", style=discord.ButtonStyle.primary, custom_id="affirmation")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        affirmation = await button_manager.get_mistral_response("Give me a short, positive daily affirmation.")
        await interaction.followup.send(f"🌟 **Daily Affirmation:** {affirmation}", ephemeral=True)

class SelfCareButton(Button):
    def __init__(self):
        super().__init__(label="Self Care", style=discord.ButtonStyle.primary, custom_id="selfcare")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selfcare = await button_manager.get_mistral_response("Give me a self-care tip.")
        await interaction.followup.send(f"🌟 **Self-Care Tip:** {selfcare}", ephemeral=True)

class BreatheButton(Button):
    def __init__(self):
        super().__init__(label="Breathing", style=discord.ButtonStyle.primary, custom_id="breathe")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("🌿 **Breathing Exercise Started!**", ephemeral=True)
        await asyncio.sleep(1)
        # Inhale (6 seconds)
        await interaction.followup.send("🌿 **Inhale...** Take a deep breath in.", ephemeral=True)
        for i in range(6, 0, -1):
            await asyncio.sleep(1)
            await interaction.followup.send(f"**{i} seconds left to inhale**", ephemeral=True)
        # Hold (3 seconds)
        await interaction.followup.send("🌿 **Hold your breath...**", ephemeral=True)
        for i in range(3, 0, -1):
            await asyncio.sleep(1)
            await interaction.followup.send(f"**{i} seconds left to hold**", ephemeral=True)
        # Exhale (6 seconds)
        await interaction.followup.send("🌿 **Exhale...** Slowly breathe out.", ephemeral=True)
        for i in range(6, 0, -1):
            await asyncio.sleep(1)
            await interaction.followup.send(f"**{i} seconds left to exhale**", ephemeral=True)
        await interaction.followup.send("🌟 **Fantastic! You completed the breathing exercise.**", ephemeral=True)

class MusicButton(Button):
    def __init__(self):
        super().__init__(label="Sounds of Music", style=discord.ButtonStyle.primary, custom_id="music")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        musics = await button_manager.get_mistral_response("Give me two therapy music links.")
        await interaction.followup.send(f"🎼 **Sounds of music:** {musics}", ephemeral=True)

class ArtButton(Button):
    def __init__(self):
        super().__init__(label="Peaceful Art", style=discord.ButtonStyle.primary, custom_id="art")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        arts = await button_manager.get_mistral_response("Give me two peaceful art links.")
        await interaction.followup.send(f"🎼 **Peaceful art:** {arts}", ephemeral=True)

class MindfulButton(Button):
    def __init__(self):
        super().__init__(label="Mindfulness Practice", style=discord.ButtonStyle.primary, custom_id="mindful")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        minds = await button_manager.get_mistral_response("Give me simple mindful tips (not about he breathing and five sense).")
        await interaction.followup.send(f"🎼 **Mindfulness practice:** {minds}", ephemeral=True)

gratitude_prompts = [
    "🌿 What is one thing you appreciate about yourself today? Take a moment to reflect on your strengths and how they empower you.",
    "🌿 Think of someone who has made a positive impact in your life. Write down **one thing** that you are grateful for about them.",
    "🌿 Pause and appreciate **three things** in your surroundings right now. It could be as simple as the sun shining, the air you breathe, or the company you have.",
    "🌿 Reflect on a recent challenge. How did you grow from it? Write down at least one lesson you learned.",
    "🌿 What made you smile today? Take a moment to **appreciate** those little joyful moments."
    "🌿 Write down **three things** you are grateful for today. No matter how big or small, focus on the positives in your life.",
    "🌿 Think of **one person** who has positively impacted your life. Send them a message of appreciation or simply reflect on their kindness.",
    "🌿 Pause for a moment. Take three deep breaths and focus on something beautiful around you. What about it makes you feel grateful?",
    "🌿 What is something that made you smile recently? Write about it and how it made you feel.",
    "🌿 What is one challenge that helped you grow? Gratitude is also about appreciating the lessons we learn from difficulties."
]

class GratitudeButton(Button):
    def __init__(self):
        super().__init__(label="Gratitude and Appreciation", style=discord.ButtonStyle.primary, custom_id="gratitude")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # Select a random gratitude and appreciation prompt from the above list
        gratitude_prompt = random.choice(gratitude_prompts)
        await interaction.followup.send(f"**Gratitude and Appreciation:** {gratitude_prompt}", ephemeral=True)

class GroundButton(Button):
    def __init__(self):
        super().__init__(label="Five Senses Grounding ", style=discord.ButtonStyle.primary, custom_id="ground")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        grounds = await button_manager.get_mistral_response("Give me five-sense grounding technique.")
        await interaction.followup.send(f"🎼 **Five sense grounding:** {grounds}", ephemeral=True)

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents
        )
        self.logger = logger

        # Set up managers and agents
        self.user_manager = UserManager()
        self.therapy_agent = TherapyAgent(self.user_manager)
        self.onboarding_manager = OnboardingManager(self.user_manager, self.therapy_agent)



    async def on_ready(self):
        self.logger.info("-------------------")
        self.logger.info(f"Logged in as {self.user}")
        self.logger.info(f"Discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("-------------------")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=CUSTOM_STATUS
            )
        )

    async def on_message(self, message: discord.Message):
        await self.process_commands(message)

        # Ignore messages from self or other bots
        if (
            message.author == self.user
            or message.author.bot
            or message.content.startswith("!")
        ):
            return

        self.logger.info(f"Message from {message.author}: {message.content}")
        user_id = str(message.author.id)

        # Check if user needs onboarding
        if self.onboarding_manager.needs_onboarding(user_id):
            await self.onboarding_manager.handle_onboarding(message)
            return

        # Get profile and state
        profile = self.user_manager.user_profiles.get(user_id)
        state = self.user_manager.user_states[user_id]

        # Handle journaling
        if state.get("awaiting_mood_journal", False):
            if message.content.lower() in ["yes", "y"]:
                mood = await self.user_manager.get_mood(user_id)
                profile = self.user_manager.user_profiles[user_id]
                synthesis = await self.user_manager.summarize_conversation(user_id)
                name = profile.get("name")
                age = profile.get("age")
                location = profile.get("location")

                self.user_manager.log_mood(user_id, mood, synthesis)
                await message.reply(f"📓 Mood logged! \n User: {name} | {age} | {location} \n Mood: {mood} \n Summary: {synthesis}")

                if mood in ["Sad", "Stressed", "Anxious", "Frustrated", "Angry"]:
                    await message.reply("Would you like to try some exercises? (yes/no)")
                    state["awaiting_exercise_decision"] = True
                else:
                    await message.reply(
                        "Would you like to continue our conversation or try exercises? (continue/exercises)")
                    state["awaiting_exercise_decision"] = True

                state["awaiting_mood_journal"] = False
            return

        elif state.get("awaiting_exercise_decision", False):
            if message.content.lower() in ["yes", "exercises"]:
                await message.reply("Here's a menu of helpful exercises 🌸", view=FeatureButtons())
            else:
                await message.reply("No problem! I'm here whenever you need me 😊")
            state["awaiting_exercise_decision"] = False
            return

        # Normal conversation flow
        message_count = self.user_manager.increment_message_count(user_id)
        # Mood journaling offer
        if message_count % 3 == 0:
            await message.reply("Would you like to log your mood in the journal? (yes/no)")
            state["awaiting_mood_journal"] = True
            state["awaiting_exercise_decision"] = False
            return

        response = await self.therapy_agent.run(message, user_id)
        # Run the therapy agent
        await message.reply(response)

        self.user_manager.add_to_conversation(user_id, message.content, response)



if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    bot = DiscordBot()

    button_manager = ButtonManager()

    # Command to Show Feature Buttons
    @bot.command(name="menu")
    async def show_menu(ctx):
        """Displays interactive buttons for features."""
        await ctx.send("**🌸 **This is your quiet corner to relax and refresh; and to reconnect with yourself.** 🌸\n\n"
                       "**Click the button to access a feature:", view=FeatureButtons())


    # Bot Ready Event
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    bot.run(token)


