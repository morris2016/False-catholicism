import discord
import json
import random
import os
import re
from discord.ext import tasks
from dotenv import load_dotenv
from openai_handler import generate_commentary, should_critique

# Load config
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
POST_INTERVAL_HOURS = float(os.getenv("POST_INTERVAL_HOURS", 3))
SKIPPED_LOG_PATH = "skipped_catholic.json"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def load_skipped_ids():
    if not os.path.exists(SKIPPED_LOG_PATH):
        return set()
    with open(SKIPPED_LOG_PATH, "r") as f:
        return set(json.load(f))

def save_skipped_ids(skipped_ids):
    with open(SKIPPED_LOG_PATH, "w") as f:
        json.dump(list(skipped_ids), f, indent=2)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    post_catholic.start()

@tasks.loop(hours=POST_INTERVAL_HOURS)
async def post_catholic():
    with open("catholic.json", "r", encoding="utf-8") as f:
        doctrines = json.load(f)

    skipped_ids = load_skipped_ids()
    doctrine = None

    for _ in range(50):
        candidate = random.choice(doctrines)
        doctrine_id = candidate["id"]
        if doctrine_id in skipped_ids:
            continue

        summary = candidate["text"]
        if should_critique(summary):
            doctrine = candidate
            break
        else:
            print(f"⏩ Skipped Doctrine #{doctrine_id}")
            skipped_ids.add(doctrine_id)

    save_skipped_ids(skipped_ids)

    if not doctrine:
        print("❌ No critique-worthy doctrine found.")
        return

    doctrine_id = doctrine["id"]
    title = doctrine["title"]
    text = doctrine["text"]
    evidence = doctrine["evidence"][0]["quote"]
    source = doctrine["evidence"][0]["source"]

    prompt = f"""
You are critiquing Catholic doctrine using logic and Scripture.
Point out what is inconsistent, man-made, or theologically troubling about this doctrine.
Be sharp, brief (5 sentences), and end with a rhetorical question.
Then, contrast it with a short example of truth from Scripture.
Finally, suggest why trusting Christ directly is more reasonable.

Doctrine #{doctrine_id}: "{title}"
Summary: "{text}"
Catholic Source: "{source}"
Quote: "{evidence}"
"""

    commentary = generate_commentary(prompt)

    doctrine_msg = f"📜 **Doctrine #{doctrine_id}: {title}**\n\n\"{text}\"\n\n📖 *{source}*:\n> {evidence}"
    commentary_msg = f"🧠 **Commentary:**\n{commentary}"

    channel = client.get_channel(CHANNEL_ID)
    await channel.send(doctrine_msg[:2000])
    await channel.send(commentary_msg[:2000])

client.run(TOKEN)
