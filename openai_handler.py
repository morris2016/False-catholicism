import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_commentary(prompt_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        max_tokens=250  # keep this short to avoid Discord 2K limit
    )
    return response.choices[0].message.content.strip()
