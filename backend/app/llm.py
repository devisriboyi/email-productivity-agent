# backend/app/llm.py
import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY)


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=1000,
        )

        # ✔ FIXED HERE
        text_output = resp.choices[0].message.content  

        return {
            "success": True,
            "text": text_output
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
