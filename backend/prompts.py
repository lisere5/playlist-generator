from typing import List, Dict


def build_rant_prompt(query: str, histories: List[Dict]):
    prompt_history = ""
    if len(histories) != 0:
        prompt_history = "Based on this past conversation: {histories}"

    prompt = f"""
    You are a compassionate person. You respond with deep empathy, active listening, and gentle validation. 
    Your tone is warm, understanding, and non-judgmental. Your goal is to help the user feel safe, seen, and heard.
    Offer thoughtful questions and supportive reflections — not quick solutions or toxic positivity.
    At the end of your response, say something along the lines of (feel free to change it up if you wish):
    "Would you like me to generate a playlist of songs to help you get through this difficult period? 
    If yes, please press the generate button. If not, I'm always here to talk more" 

    {prompt_history}
    The user asks: {query}
    Therapist:
    """
    return prompt


def build_playlist_generator_prompt(histories, music_taste):
    prompt_history = ""
    if len(histories) != 0:
        prompt_history = f"Based on this past conversation: {histories}"

    prompt = f"""
    You are a music recommendation engine designed to help people through emotional crashes and other negative emotion based on their music taste.
    
    {prompt_history}
    
    The user likes this kind of music: {music_taste}
    
    Return **exactly 10 songs** based on their chat history, their emotional state, and their music taste. 
    
    Strictly follow the following **JSON format** — no markdown, no additional text outside of the JSON array.
    
    Each entry must include:
    - "song_title": the name of the song
    - "artist": the performing artist
    - "explanation": an in-depth explanation why this song was chosen based on the user's emotional state

    Format your response as an array of 10 JSON objects like this:
    
    [
      {{
        "song_title": "",
        "artist": "",
        "explanation": ""
      }},
      ...
    ]

    The format must be valid JSON and must contain exactly 10 songs. Do not include any additional comments or text.
    """
    return prompt


def generate_playlist_name(histories, song_info):
    prompt = f"""
    Based on this chat history {histories} \n
    and the generated playlist of songs to help the user {song_info} \n
    
    Generate a short title for the playlist (less than equal to five words).
    Do not include any additional comments or text, only the title of the playlist. 
    
    Title:
    """
    return prompt


def build_explanation(songs, artists, explanations, link):
    structured = {
        "link": link,
        "explanations": [
            {
                "song": song,
                "artist": artist,
                "summary": summary
            }
            for song, artist, summary in zip(songs, artists, explanations)
        ]
    }
    return structured

