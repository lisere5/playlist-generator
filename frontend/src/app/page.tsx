'use client';

export default function Home() {
  const handleLogin = () => {
    window.location.href = 'http://127.0.0.1:8000/login'; // FastAPI login route
  };

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🎧 Welcome to Spotify Ranter</h1>
      <p>Log in to get started.</p>
      <button onClick={handleLogin} style={{ marginTop: '1rem' }}>
        Log in with Spotify
      </button>
    </main>
  );
}
