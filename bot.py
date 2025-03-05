import os
import discord
import logging
import random   

from discord.ext import commands
from discord.ui import View, Button, Select
from discord import ButtonStyle
from dotenv import load_dotenv
from agent import MistralAgent

import asyncio
import matplotlib.pyplot as plt
from datetime import datetime

#import certifi
#os.environ['SSL_CERT_FILE'] = certifi.where()

PREFIX = "!"

# Setup logging
logger = logging.getLogger("discord")

# Load the environment variables
load_dotenv()

# Create the bot with all intents
# The message content and members intent must be enabled in the Discord Developer Portal for the bot to work.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Import the Mistral agent from the agent.py file
agent = MistralAgent()

# Get the token from the environment variables
token = os.getenv("DISCORD_TOKEN")

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
        affirmation = await agent.get_mistral_response("Give me a short, positive daily affirmation.")
        await interaction.followup.send(f"🌟 **Daily Affirmation:** {affirmation}", ephemeral=True)

class SelfCareButton(Button):
    def __init__(self):
        super().__init__(label="Self Care", style=discord.ButtonStyle.primary, custom_id="selfcare")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selfcare = await agent.get_mistral_response("Give me a self-care tip.")
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
        musics = await agent.get_mistral_response("Give me two therapy music links.")
        await interaction.followup.send(f"🎼 **Sounds of music:** {musics}", ephemeral=True)

class ArtButton(Button):
    def __init__(self):
        super().__init__(label="Peaceful Art", style=discord.ButtonStyle.primary, custom_id="art")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        arts = await agent.get_mistral_response("Give me two peaceful art links.")
        await interaction.followup.send(f"🎼 **Peaceful art:** {arts}", ephemeral=True)

class MindfulButton(Button):
    def __init__(self):
        super().__init__(label="Mindfulness Practice", style=discord.ButtonStyle.primary, custom_id="mindful")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        minds = await agent.get_mistral_response("Give me simple mindful tips (not about he breathing and five sense).")
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
        grounds = await agent.get_mistral_response("Give me five-sense grounding technique.")
        await interaction.followup.send(f"🎼 **Five sense grounding:** {grounds}", ephemeral=True)

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

# Start the bot, connecting it to the gateway
bot.run(token) 
