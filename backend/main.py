# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_helper import query_claude
from spotify_helper import get_music_taste, parse_songs, create_playlist
from prompts import build_rant_prompt, build_playlist_generator_prompt, build_explanation
from spotify_auth import get_auth_url, get_tokens
from fastapi.responses import RedirectResponse

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


chat_history = []

class LLMQueryRequest(BaseModel):
    prompt: str


@app.post("/rant")
def rant(req: LLMQueryRequest):
    global chat_history
    prompt = build_rant_prompt(req.prompt, chat_history)
    try:
        response = query_claude(prompt)
        chat_history.append({
            "message": req.prompt,
            "response": response
        })
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
def generate_playlist():
    global chat_history
    music_taste = get_music_taste()
    song_prompt = build_playlist_generator_prompt(chat_history, music_taste)
    try:
        song_info = query_claude(song_prompt)
        songs, explanations = parse_songs(song_info)
        link = create_playlist(songs)

        explanation = build_explanation(songs, explanations, link)
        chat_history = []
        return {"response": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
