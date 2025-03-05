# This is a basic agent to have a therapy conversation

import os
import json
import logging
import discord

from mistralai import Mistral

logger = logging.getLogger("discord")

MISTRAL_MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
You are a compassionate therapist. 
Your role is to provide empathetic, non-judgemental, and supportive responses.
Focus on active listening, validation, and encouragement.
Do not provide medical advice or diagnoses. 

Examples:
User: "I had a really bad day. Everything went wrong."
Response: "I'm really sorry to hear that. It sounds like today was really tough for you. Would you like to talk more about what happened?"

User: "I feel so stressed with work."
Response: "That sounds overwhelming. Work stress can be really difficult to manage. Have you had a chance to take a break or do something that helps you relax?"

User: "I'm so happy today! I finally got a promotion."
Response: "That's amazing! Congratulations on your promotion! You must be feeling really proud. How are you planning to celebrate?"
"""

class TherapyAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
    async def run(self, message: discord.Message):
        # The simplest form of an agent
        # Send the message's content to Mistral's API and return Mistral's response

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message.content},
        ]

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        return response.choices[0].message.content

    async def get_mistral_response(self, prompt: str):
        """Fetch AI-generated responses from Mistral AI."""
        try:
            response = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a supportive mental health assistant. Provide uplifting and encouraging responses."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error fetching affirmation: {e}")
            return "🌟 **Daily Affirmation:** You are capable and enough!"