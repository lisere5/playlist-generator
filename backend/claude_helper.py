import os
from dotenv import load_dotenv
import anthropic

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

    return message.content
