import discord
import json
import random
import os
import re
from discord.ext import tasks
from dotenv import load_dotenv
from openai_handler import generate_commentary, should_critique

# Load env variables
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
    print(f"✅ Logged in as {client.user}")
    print("🚀 Starting post_catholic task loop...")
    post_catholic.start()
    await post_catholic()  # <-- this will run once immediately


@tasks.loop(hours=POST_INTERVAL_HOURS)
async def post_catholic():
    with open("Catholic.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        doctrines = data["doctrines"] if isinstance(data, dict) else data

    skipped_ids = load_skipped_ids()
    doctrine = None

    for _ in range(50):  # Max 50 tries to find a doctrine worth critiquing
        candidate = random.choice(doctrines)
        doctrine_id = candidate.get("id")
        if doctrine_id in skipped_ids:
            continue

        summary = candidate.get("text", "")
        print(f"🧪 Reviewing Doctrine #{doctrine_id}: {summary[:80]}...")

        try:
            if should_critique(summary):
                doctrine = candidate
                print(f"✅ Critique-worthy: Doctrine #{doctrine_id}")
                break
            else:
                print(f"⏩ Skipped Doctrine #{doctrine_id}")
                skipped_ids.add(doctrine_id)
        except Exception as e:
            print(f"❌ Error checking doctrine #{doctrine_id}: {e}")
            skipped_ids.add(doctrine_id)

    save_skipped_ids(skipped_ids)

    if not doctrine:
        print("⚠️ No flagged doctrines found, posting a random one.")
        doctrine = random.choice(doctrines)

    doctrine_id = doctrine.get("id")
    title = doctrine.get("title", "Untitled")
    text = doctrine.get("text", "")
    evidence_data = doctrine.get("evidence", [{}])[0]
    source = evidence_data.get("source", "Unknown Source")
    quote = evidence_data.get("quote", "No citation found.")

    # 🧠 Build prompt for OpenAI
    prompt = f"""
You are a biblical scholar critiquing Catholic doctrine.
Find flaws, contradictions with the Bible, or theological issues.
Explain clearly in 4–6 sentences. Use logic and reference Scripture.
End with a rhetorical or thought-provoking question. Then provide one-sentence contrast showing clarity in biblical truth through Christ.

Doctrine #{doctrine_id}: "{title}"
Summary: "{text}"
Source: "{source}"
Quote: "{quote}"
"""

    # 🧠 Get critique
    try:
        commentary = generate_commentary(prompt)
    except Exception as e:
        commentary = f"⚠️ OpenAI error: {e}"

    # 📬 Compose message
    doctrine_msg = f"📜 **Doctrine #{doctrine_id}: {title}**\n\n\"{text}\"\n\n📖 *{source}*:\n> {quote}"
    commentary_msg = f"--------------------------------------------------------------------\n   Heresy Detector detecting....\n----------------------------------------------------------------------\n🧠 **Commentary:**\n{commentary}"

    channel = client.get_channel(CHANNEL_ID)
    await channel.send(doctrine_msg[:2000])
    await channel.send(commentary_msg[:2000])

client.run(TOKEN)
