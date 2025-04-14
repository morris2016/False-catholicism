import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🧠 Generate the main commentary response
def generate_commentary(prompt_text):
    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

# 🔍 Ask GPT if this hadith is critique-worthy
def should_critique(hadith_text):
    review_prompt = f"""
You are a critical theological reviewer.
Analyze the following hadith and answer ONLY with "yes" or "no":
Does it contain anything that is morally problematic, logically inconsistent, absurd, or theologically questionable?

Hadith:
\"{hadith_text}\"
"""

    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": review_prompt}],
        temperature=0,
        max_tokens=2
    )
    return response.choices[0].message.content.strip().lower() == "yes"
