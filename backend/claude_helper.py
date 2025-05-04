import os
from dotenv import load_dotenv
import anthropic
import json
from spotify_helper import parse_songs
import re

load_dotenv()

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=anthropic_api_key)


def query_claude(prompt, system_prompt="", model="claude-3-5-sonnet-20241022", max_tokens=1000, temperature=1):
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return "".join([block.text for block in message.content if block.type == "text"])


def safe_query_playlist_generator(prompt):
    max_attempt = 3
    for attempt in range(max_attempt):
        song_info = query_claude(prompt)
        print(f"/generate->safe_query_playlist_generator: llm response:\n {song_info}\n")

        cleaned = song_info.strip()
        if cleaned.startswith("```json"):
            cleaned = re.sub(r"^```json", "", cleaned)
            cleaned = cleaned.rstrip("```")
        elif cleaned.startswith("```"):
            cleaned = re.sub(r"^```", "", cleaned)
            cleaned = cleaned.rstrip("```")

        try:
            parsed = json.loads(cleaned)
            songs, artists, explanations = parse_songs(parsed)
            return songs, artists, explanations
        except Exception as e:
            print(f"[Retry {attempt + 1}] Invalid format: {e}")
            print("Raw Claude output:\n", cleaned)
            continue

    raise ValueError("Claude failed to return valid JSON after multiple attempts.")
