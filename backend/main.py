# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_helper import query_claude, safe_query_playlist_generator
from spotify_helper import get_music_taste, parse_songs, create_playlist
from prompts import build_rant_prompt, build_playlist_generator_prompt, build_explanation
from spotify_auth import get_auth_url, get_tokens
from fastapi.responses import RedirectResponse
import json

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/login")
def login():
    url = get_auth_url()
    return RedirectResponse(url)


@app.get("/callback")
def callback(code: str):
    tokens = get_tokens(code)
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to authenticate with Spotify")

    # Optionally store token in session or DB
    return {"access_token": access_token, "refresh_token": refresh_token}


chat_history = [] # only works with single user - should be enough for prototype :D


class LLMQueryRequest(BaseModel):
    prompt: str


@app.post("/rant")
def rant(req: LLMQueryRequest):
    global chat_history
    prompt = build_rant_prompt(req.prompt, chat_history)
    try:
        response = query_claude(prompt)
        print(f"/rant: prompt:\n {prompt}\n")
        chat_history.append({
            "message": req.prompt,
            "response": response
        })
        print(f"/rant: chat_history:\n {chat_history}\n")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
def generate_playlist():
    global chat_history
    music_taste = get_music_taste()
    song_prompt = build_playlist_generator_prompt(chat_history, music_taste)
    print(f"/generate: prompt:\n {song_prompt}\n")
    try:
        songs, artists, explanations = safe_query_playlist_generator(song_prompt)
        print(f"/generate: songs:\n {songs}\n")
        print(f"/generate: artists:\n {artists}\n")
        print(f"/generate: explanations:\n {explanations}\n")
        # link = create_playlist(songs)
        link = "randomlink.com"
        explanation = build_explanation(songs, artists, explanations, link)
        chat_history = []
        return {"response": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
