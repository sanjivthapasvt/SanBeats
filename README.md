# 🎵 SanBeats

**SanBeats** is a sleek,minimalist desktop music streaming application built using **Svelte + Electron** for the frontend and **FastAPI** for the backend. It utilizes the **YouTube API** and `yt-dlp` to deliver audio-only music.

> ⚠️ This project is currently **under development**.

---

## 🚀 Features

- 🔥 **Trending Music**: Discover and stream the latest trending tracks.
- 🔍 **Search Music**: Find music using keywords and filter results using tags.
- 🎧 **Audio-Only Playback**: Saves bandwidth by streaming audio-only content using `yt-dlp`.

---

## 🛠️ Tech Stack

### Frontend

- [Svelte](https://svelte.dev/)
- [Electron](https://www.electronjs.org/)
- [Vite](https://vitejs.dev/)
- [TypeScript](https://www.typescriptlang.org/)

### Backend

- [FastAPI](https://fastapi.tiangolo.com/)

---

## 📦 .env Configuration

Create a `.env` file inside the `backend/` directory with the following content:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
```

---

## 💻 Installation & Development

### 🔧 Prerequisites

- Python 3.9+
- Node.js (v18+ recommended)
- npm

---

### 🐍 Backend Setup (FastAPI)

```bash
# Go to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with YouTube API key
touch .env

# Run FastAPI backend
fastapi dev app/main.py
```

---

### ⚡ Frontend Setup (Svelte + Electron + Vite)

```bash
# Go to frontend
cd frontend

# Install dependencies
npm install

# Start the app in development mode
npm run dev
```

---

## 🧪 Testing in Development

Make sure both the backend and frontend are running:

- The **backend** should be available at `http://localhost:8000`
- The **Electron app** will open automatically when you run `npm run dev` in `frontend/`

You can now:

- Browse **Trending** music on the homepage.
- Use the **Search bar** to find tracks.
- Click to **play music** in audio-only mode.

---

## 📦 Build (For Production)

To build the app:

```bash
cd frontend
# For windows
$ npm run build:win

# For macOS
$ npm run build:mac

# For Linux
$ npm run build:linux
```

---

## 📅 Roadmap

- ✅ Implement trending section
- ✅ Search and play music
- 🔲 Playlist support
- 🔲 Favorites and history
- 🔲 Improved UI/UX and animations

---

## 🤝 Contributing

Contributions are welcome!

---