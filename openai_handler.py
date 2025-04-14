import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_commentary(prompt_text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

def should_critique(doctrine_text):
    review_prompt = f"""
You are a theological reviewer.
Does the following Catholic doctrine contain anything logically inconsistent, unbiblical, or questionable compared to Scripture?

Doctrine: "{doctrine_text}"

Answer only "yes" or "no".
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": review_prompt}],
        temperature=0,
        max_tokens=2
    )
    return response.choices[0].message.content.strip().lower() == "yes"
