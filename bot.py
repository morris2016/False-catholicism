import discord
import json
import random
import os
import re
from discord.ext import tasks
from dotenv import load_dotenv
from openai_handler import generate_commentary

load_dotenv()
POST_INTERVAL_HOURS = float(os.getenv("POST_INTERVAL_HOURS", 3))  # default = 3

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    post_hadith.start()

@tasks.loop(hours=POST_INTERVAL_HOURS)
async def post_hadith():

    with open("hadiths.json", "r", encoding="utf-8") as f:
        hadiths = json.load(f)["hadiths"]

    hadith = random.choice(hadiths)

    raw_text = hadith["english"]["text"]

    # Smart truncate: keep only sentences with 20–40 words
    sentences = re.split(r'(?<=[.?!])\s+', raw_text.strip())
    interesting = [s for s in sentences if 20 <= len(s.split()) <= 40]

    # Fallback if no interesting sentence found
    if not interesting:
        interesting = [sentences[0]]

    text = " ".join(interesting[:2])  # use 1–2 most relevant sentences

    number = hadith["id"]
    narrator = hadith["english"].get("narrator", "Unknown")

    # Build prompt for GPT
    prompt = f"""
You are analyzing the most logically absurd or ironic part of this hadith. 
Focus only on what makes it unbelievable, bizarre, or comical from a theological or rational perspective. 
Keep your commentary sharp, brief, and clever (max 5 sentences). End with a rhetorical question that exposes the flaw.
Then give a contrast showing how God's revelation was clearer or more direct through previous prophets or what prophets said on the contrary.
In two sentences, contrast it with a reason why they should believe in Jesus Christ.

Hadith #{number} – Narrated {narrator}:
\"{text}\"
"""

    # Get commentary
    commentary = generate_commentary(prompt)

    # Format message for Discord
    message = (
        f"📜 **Hadith #{number} – Narrated {narrator}:**\n\n{text}\n\n"
        f"🧠 **Commentary:**\n{commentary}"
    )

    if len(message) > 2000:
        message = message[:1997] + "..."

    channel = client.get_channel(CHANNEL_ID)
    await channel.send("@everyone")  # Ping separately for visibility
    await channel.send(message)

# Start bot
client.run(TOKEN)
