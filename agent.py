# This is a basic agent to have a therapy conversation

import os
import json
import logging
import discord
import datetime
import requests

from mistralai import Mistral

logger = logging.getLogger("discord")

MISTRAL_MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
You are a compassionate therapist that is named Therabot. 
Your role is to provide empathetic, non-judgemental, and supportive advice with a casual and approachable tone.
Be less stiff in your language and talk more like a real person. Include at least one emojis per response. 
Use diverse and varied response structures each time. Don't start with "hey there." 
Focus on psychonalaysis. 
Ask short follow up questions that are reflective and try to look into the root causes of the user's feelings and get them to understand themself. 
Don't ask basic follow up questions like How are You or tell me more? 
Do not provide medical advice or diagnoses. 

If a user seems extreme, tell to them to contact a hotline. 
"""

EXTRACT_INFO_PROMPT = """
The response will either include a response with a name, age, or location. 

Return the name, age, or location in a JSON format. 

Example:
Message: My name is Sophie
Response: {"name": "Sophie"}

Message: Mark
Response: {"name": "Mark"}

Message: I am 20
Response: {"age": 20}

Message: twenty one
Response :{"age": 21}

Message: sf
Response: {"location": "San Francisco, CA"}

Message: I live in nyc
Response: {"location": "New York City, NY"}

"""
MOOD_PROMPT = """
Analyze the emotional tone of this message and classify it into one of the following moods: 
["Happy", "Sad", "Stressed", "Anxious", "Frustrated", "Angry", "Calm", "Excited", "Neutral"].
Return only the mood in JSON format.

Examples:
User: "I had an amazing day! I got a promotion."
Response: {"mood": "Happy"}

User: "I feel really anxious about tomorrow’s meeting."
Response: {"mood": "Anxious"}

User: "I'm feeling completely overwhelmed with work."
Response: {"mood": "Stressed"}
"""

SYNTHESIS_PROMPT = """
Analyze this conversation using the user's responses and summarize in 2 sentences very matter-of-factly. 
"""

class ButtonManager:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)

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

# Manages user profiles, state tracking, and mood journal entries
class UserManager:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)

        self.user_profiles = {}  # user_id -> profile (name, age, location)
        self.user_states = {}  # user_id -> message count, onboarding status
        self.mood_journal = {}  # user_id -> list of mood entries
        self.user_conversations = {}

    def is_onboarded(self, user_id):
        return user_id in self.user_profiles

    def onboard_user(self, user_id, name, age, location):
        self.user_profiles[user_id] = {
            "name": name,
            "age": age,
            "location": location
        }
        self.user_states[user_id] = {
            "message_count": 0,
            "awaiting_mood_journal": False,
            "awaiting_exercise_decision": False
        }

        # Initialize an empty conversation
        self.user_conversations[user_id] = {"conversation": []}

    def increment_message_count(self, user_id):
        state = self.user_states.setdefault(user_id, {"message_count": 0})
        state["message_count"] += 1
        return state["message_count"]

    def log_mood(self, user_id, mood, synthesis):
        profile = self.user_profiles.get(user_id, {})
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "name": profile.get("name"),
            "age": profile.get("age"),
            "location": profile.get("location"),
            "mood": mood,
            "synthesis": synthesis
        }
        self.mood_journal.setdefault(user_id, []).append(entry)
        logger.info(f"Logged mood for user {user_id}: {entry}")

    async def get_mood(self, user_id):
        convo_pairs = self.user_conversations[user_id]["conversation"]
        # Convert list of tuples into a readable conversation
        convo = "\n".join([f"User: {u}\nBot: {b}" for u, b in convo_pairs])

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=[{"role": "system", "content": MOOD_PROMPT},
                      {"role": "user", "content": convo}],
            response_format={"type": "json_object"},
        )
        mood_data = json.loads(response.choices[0].message.content)
        return mood_data["mood"]

    async def get_conversation(self,user_id):
        convo_pairs = self.user_conversations[user_id]["conversation"]
        # Convert list of tuples into a readable conversation
        convo = "\n".join([f"User: {u}\nBot: {b}" for u, b in convo_pairs])
        return convo
    async def summarize_conversation(self, user_id):
        convo_pairs = self.user_conversations[user_id]["conversation"]
        # Convert list of tuples into a readable conversation
        convo = "\n".join([f"User: {u}\nBot: {b}" for u, b in convo_pairs])
        synthesis = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": SYNTHESIS_PROMPT},
                    {"role": "user", "content": convo},
                ],
            )
        return synthesis.choices[0].message.content

    def add_to_conversation(self, user_id, user_msg, bot_msg):
        convo = self.user_conversations.setdefault(user_id, {"conversation": []})
        convo["conversation"].append((user_msg, bot_msg))


class OnboardingManager:

    def __init__(self, user_manager, therapy_agent):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)

        self.user_manager = user_manager
        self.therapy_agent = therapy_agent
        self.pending_onboarding = {} # user_id -> current_stage (intro, name, age, location)

    def needs_onboarding(self, user_id):
        # Return True if they are not onboarded, or if they're partway through onboarding
        return not self.user_manager.is_onboarded(user_id) or user_id in self.pending_onboarding

    async def handle_onboarding(self, message: discord.Message):

        user_id = str(message.author.id)
        content = message.content.strip()
        # Initialize user profile if not already there
        if user_id not in self.user_manager.user_profiles:
            self.user_manager.user_profiles[user_id] = {}

        # Get current stage or start onboarding
        current_stage = self.pending_onboarding.get(user_id, "intro")
        profile = self.user_manager.user_profiles[user_id]
        if current_stage == "intro":
            await message.reply(
                "👋 Hi! I'm your personal therapy bot.\n\n"
                "I can track your mood, offer mindfulness exercises, and be here when you need someone to talk to!\n\n"
                "Let's get to know each other. What's your name?"
            )
            self.pending_onboarding[user_id] = "name"
            return

        # Name step
        if current_stage == "name":
            response = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": EXTRACT_INFO_PROMPT},
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
            )
            obj = json.loads(response.choices[0].message.content)
            name = obj.get("name")

            if not name:
                await message.reply("Sorry, I didn't catch your name. Could you try again?")
                return

            # Save partial profile
            profile["name"] = name
            self.pending_onboarding[user_id] = "age"

            await message.reply(f"Nice to meet you, {name}! How old are you?")
            return

        # Age step
        if current_stage == "age":
            response = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": EXTRACT_INFO_PROMPT},
                    {"role": "user", "content":content},
                ],
                response_format={"type": "json_object"},
            )

            obj = json.loads(response.choices[0].message.content)
            age = obj.get("age")

            if not age:
                await message.reply("Hmm, could you tell me your age again?")
                return

            # Save partial profile
            profile["age"] = age
            self.pending_onboarding[user_id] = "location"

            await message.reply("Thanks! And where are you located?")
            return

        # Location step
        if current_stage == "location":
            response = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": EXTRACT_INFO_PROMPT},
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
            )
            obj = json.loads(response.choices[0].message.content)
            location = obj.get("location")

            if not location:
                await message.reply("Could you share your location one more time?")
                return

            # Save partial profile
            profile["location"] = location

            # Finish onboarding
            self.user_manager.onboard_user(
                user_id,
                profile["name"],
                profile["age"],
                profile["location"]
            )
            # After finishing onboarding
            del self.pending_onboarding[user_id]

            await message.reply(
                f"Thanks {profile["name"]}! 😊 I'm your personal therapy bot.\n"
                "You can talk to me about anything.\n"
                "**Features available:** Mood journaling, breathing exercises, affirmations & more! 🌸\n\n"
                "Type `!menu` anytime to explore!\n\n"
                "So, how are you doing today?"
            )

class TherapyAgent:
    def __init__(self, user_manager):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.user_manager = user_manager  # Pass in user manager

    async def run(self, message: discord.Message, user_id):
        # The simplest form of an agent
        # Send the message's content to Mistral's API and return Mistral's response

        convo = await self.user_manager.get_conversation(user_id)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            #{"role": "user", "content": convo},
            {"role": "user", "content": message.content},
        ]

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        return response.choices[0].message.content
