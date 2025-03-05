import os
from mistralai import Mistral
import discord   

MISTRAL_MODEL = "mistral-large-latest"
#MISTRAL_MODEL = "mental-health-mistral-7b"
SYSTEM_PROMPT = "You are a helpful therapist assistant."

class MistralAgent:
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
                    {"role": "system", "content": "You are a supportive mental health assistant. Provide uplifting and encouraging responses."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error fetching affirmation: {e}")
            return "🌟 **Daily Affirmation:** You are capable and enough!" 
            
    
