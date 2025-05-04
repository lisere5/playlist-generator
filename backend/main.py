# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_helper import query_claude, safe_query_playlist_generator
from spotify_helper import get_music_taste, create_playlist
from prompts import build_rant_prompt, build_playlist_generator_prompt, build_explanation, generate_playlist_name
from spotify_auth import get_auth_url, get_tokens
from fastapi.responses import RedirectResponse
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


chat_history = []  # only works with single user - should be enough for prototype
access_token_global = None  # also just w/ single user


@app.get("/login")
def login():
    url = get_auth_url()
    return RedirectResponse(url)


@app.get("/callback")
def callback(code: str):
    global access_token_global
    tokens = get_tokens(code)
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to authenticate with Spotify")

    access_token_global = access_token
    return RedirectResponse(f"http://localhost:3000/app?access_token={access_token}")



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
    music_taste = get_music_taste(access_token_global)
    song_prompt = build_playlist_generator_prompt(chat_history, music_taste)
    print(f"/generate: prompt:\n {song_prompt}\n")
    try:
        songs, artists, explanations = safe_query_playlist_generator(song_prompt)
        print(f"/generate: songs:\n {songs}\n")
        print(f"/generate: artists:\n {artists}\n")
        print(f"/generate: explanations:\n {explanations}\n")
        title_prompt = generate_playlist_name(chat_history, songs)
        title = query_claude(title_prompt)
        print(f"/generate: title:\n {title}\n")
        link = create_playlist(songs, artists, title, access_token_global)
        # link = "randomlink.com"
        explanation = build_explanation(songs, artists, explanations, link)
        chat_history = []
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
