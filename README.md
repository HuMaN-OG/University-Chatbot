# Sem-Pro — University Chatbot

> A full-stack AI chatbot for Chandigarh University built with Flask, Scikit-learn TF-IDF, and Groq's LLaMA 3.1 — featuring a hybrid RAG architecture, context-aware multi-turn history, admin dashboard, and live web scraper.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey) ![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-orange) ![License](https://img.shields.io/badge/License-MIT-green)

---

## What it does

Students can ask the chatbot anything about Chandigarh University — fees, exams, hostels, placements, scholarships, transport, clubs, and more. The bot uses a multi-intent semantic classifier to understand the query, retrieves relevant context and past conversation history from a SQLite database, and generates a natural, context-aware response via Groq's LLaMA 3.1 API.

---

## Features

### Chat Interface
- **Multi-intent detection** — understands combined queries like "fees and exam schedule" in one message using semantic search.
- **Context-aware multi-turn responses** — remembers the conversation history for seamless follow-up questions.
- **Voice input** — speak your question using the Web Speech API microphone button.
- **Text-to-speech** — have responses read aloud via the speaker button.
- **Quick action chips** — one-click buttons for common topics (Fees, Admission, Hostel).
- **Typing animation** — realistic animated dots before each response.
- **Chat persistence** — conversation saved across page refreshes.
- **Chat export** — download the full conversation as `chat_log.txt`.
- **Feedback buttons** — 👍 / 👎 on every response, logged for quality analysis.
- **Intent tags** — shows detected intents (e.g. `[fees]` `[exam]`) below each response.

### Backend & ML
- **Hybrid RAG architecture** — Scikit-learn TF-IDF for semantic intent classification, then Groq LLaMA 3.1 for response generation.
- **Keyword boosting** — rule-based fallback layer on top of ML predictions for reliability.
- **Auto-seeding** — `university.db` is created automatically on first boot, no manual setup needed.
- **Live web scraper** — `scraper.py` crawls the CU website to keep the database updated.
- **Rate Limiting & JWT Auth** — robust API security preventing spam and unauthorized admin access.

### Admin Dashboard (`/admin.html`)
- Edit any bot response directly from the UI.
- View live feedback analytics per intent.
- Trigger the web scraper to refresh live data.
- Retrain the semantic vectors after making changes.
- Protected by a configurable JWT token and password login.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask, Gunicorn, Flask-Limiter |
| ML / NLP | Scikit-learn TF-IDF |
| AI Generation | Groq API — LLaMA 3.1 8B Instant |
| Database | SQLite (via `database.py`) |
| Scraping | BeautifulSoup4, Requests |
| Frontend | Vanilla HTML, CSS, JavaScript |

---

## Project Structure

```text
Sem-Pro/
├── app.py                        # Flask server — routes, auth, RAG pipeline
├── database.py                   # SQLite handler — init, seed, multi-turn history
├── nlp_model.py                  # ML core — TF-IDF, semantic search
├── scraper.py                    # Web scraper — crawls CU website
├── index.html                    # Chat frontend
├── admin.html                    # Admin dashboard
├── Procfile                      # Gunicorn start command for Render
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore
└── system_architecture_overview.svg

# Auto-generated at runtime (not in repo):
# university.db   — SQLite database
```

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/sem-pro-chatbot.git
cd sem-pro-chatbot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
```
Open `.env` and fill in:
```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET=your_jwt_secret_key_here
ADMIN_PASSWORD=admin123
```
Get a free Groq API key at [console.groq.com](https://console.groq.com).

**4. Run the server**
```bash
python app.py
```
The app will be live at `http://localhost:5000`. The database and TF-IDF model are initialized automatically on first boot.

**5. Access the admin panel**
Go to `http://localhost:5000/admin.html` and use your `ADMIN_PASSWORD` to log in.

---

## Deployment (Render — free tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Use these settings:

| Field | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

5. Add environment variables on Render:
   - `GROQ_API_KEY` — your Groq API key
   - `JWT_SECRET` — a strong random secret key for authentication
   - `ADMIN_PASSWORD` — a strong password for the admin panel

> **Note:** Render's free tier spins down after 15 minutes of inactivity. The first request after a cold start may take ~10 seconds as it initializes the backend. The database is re-seeded automatically on each startup.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Error connecting to server` | Flask is not running — run `python app.py` first |
| `flask_cors not found` | Run `pip install -r requirements.txt` |
| Port conflict | Change `port=5001` in `app.py` and update `BACKEND_URL` in `index.html` |
| Admin panel says Unauthorized | Check your `ADMIN_PASSWORD` in `.env` matches what you're entering |

---

## Supported Topics

The chatbot can answer questions about: fees, exams, admission, hostel, library, placements, results, courses, scholarships, transport, sports, canteen, WiFi, clubs, and university events.

---

## License

MIT