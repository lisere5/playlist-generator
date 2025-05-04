'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

export default function ChatApp() {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState<{ user: string; bot: string }[]>([]);
  const [playlistInfo, setPlaylistInfo] = useState<{
    link: string;
    explanations: { song: string; artist: string; summary: string }[];
  } | null>(null);

  const [loading, setLoading] = useState(false);

  // Extract access token from query param, store in localStorage
  useEffect(() => {
    const url = new URL(window.location.href);
    const token = url.searchParams.get('access_token');

    if (token) {
      localStorage.setItem('access_token', token);
      // Remove token from URL
      window.history.replaceState({}, document.title, '/app');
    }

    // If token still missing, force user back to login
    if (!localStorage.getItem('access_token')) {
      alert('Please log in first.');
      window.location.href = '/';
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const newChat = [...chat, { user: input, bot: '...' }];
    setChat(newChat);
    setInput('');

    try {
      const res = await axios.post('http://127.0.0.1:8000/rant', { prompt: input });
      newChat[newChat.length - 1].bot = res.data.response;
      setChat([...newChat]);
    } catch (err) {
      console.error(err);
      newChat[newChat.length - 1].bot = '⚠️ Failed to get response.';
      setChat([...newChat]);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/generate');
      setPlaylistInfo(res.data);
    } catch (err) {
      console.error(err);
      setGenerated('⚠️ Failed to generate playlist.');
    }
    setLoading(false);
  };

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🎵 Spotify Ranter</h1>

      <div style={{ border: '1px solid #ccc', padding: '1rem', height: '300px', overflowY: 'auto' }}>
        {chat.map((msg, idx) => (
          <div key={idx}>
            <b>You:</b> {msg.user} <br />
            <b>Bot:</b> {msg.bot}
            <hr />
          </div>
        ))}
      </div>

      <input
        type="text"
        placeholder="Type your rant..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        style={{ width: '100%', marginTop: '1rem' }}
      />

      <button onClick={handleGenerate} disabled={loading} style={{ marginTop: '1rem' }}>
        {loading ? 'Generating...' : '🎧 Generate Playlist'}
      </button>

      {playlistInfo && (
        <div style={{ marginTop: '2rem' }}>
          <h3>📝 Playlist Explanation</h3>
          <div style={{ marginBottom: '1rem' }}>
            📎 Access it here:{" "}
            <a href={playlistInfo.link} target="_blank" rel="noopener noreferrer">
              Open in Spotify
            </a>
          </div>
          <ul style={{ paddingLeft: '1.5rem', lineHeight: '1.6' }}>
            {playlistInfo.explanations.map((track, idx) => (
              <li key={idx} style={{ marginBottom: '1rem' }}>
                <strong>🎧 {track.song} – {track.artist}</strong>
                <div style={{ marginTop: '0.3rem' }}>➤ {track.summary}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}
