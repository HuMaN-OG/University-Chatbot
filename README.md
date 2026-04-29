# 🎓 University ChatBot

> An AI-powered chatbot for **Chandigarh University** — answers student queries on fees, exams, placements, hostel, library, and more using a hybrid NLP + RAG (Retrieval-Augmented Generation) pipeline.

🔗 **Live Demo:** [university-chatbot-k8fx.onrender.com](https://university-chatbot-k8fx.onrender.com)

---

## ✨ Features

- 🤖 **Hybrid NLP Engine** — TF-IDF cosine similarity + keyword boosting for intent detection
- 🔍 **RAG Pipeline** — Relevant context is retrieved from the database and passed to Groq LLaMA 3.1 for natural, conversational answers
- 🌐 **Web Scraper** — Admin can trigger live scraping of the official CU website to keep data fresh
- 💬 **Multi-turn Conversations** — Session-aware conversation history for contextual follow-ups
- 👍 **Feedback System** — Users can rate responses; feedback stats are visible in the admin panel
- 🔐 **Secure Admin Panel** — JWT-authenticated admin dashboard to manage intents, responses, scraping, and retraining
- ⚡ **Rate Limiting** — Flask-Limiter protects endpoints (30/min for chat, 10/min for login)
- 🚀 **Deployed on Render** — Production-ready with Gunicorn

---

## 🧠 System Architecture

```
User Query
    │
    ▼
Rule-Based Override (greetings / farewells)
    │
    ▼
NLP Intent Detection (TF-IDF + Keyword Boost)
    │
    ▼
Context Retrieval from SQLite DB
    │
    ▼
RAG: Groq LLaMA 3.1 (llama-3.1-8b-instant)
    │
    ▼
Response → Logged → Returned to User
```

---

## 🗂️ Project Structure

```
University_ChatBot/
├── app.py               # Flask app — all routes, auth, RAG logic
├── database.py          # SQLite init, seeding, CRUD helpers
├── nlp_model.py         # TF-IDF vectorizer, cosine similarity, keyword boost
├── scraper.py           # BeautifulSoup web scraper for CU website
├── index.html           # Student-facing chat UI
├── admin.html           # Admin dashboard (JWT-protected)
├── requirements.txt     # Python dependencies
├── Procfile             # Gunicorn entry point for Render/Heroku
├── runtime.txt          # Python version pin (3.11.9)
├── .env.example         # Environment variable template
└── university.db        # SQLite database (auto-created on first run)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A free [Groq API Key](https://console.groq.com/)

### 1. Clone the repository

```bash
git clone https://github.com/HuMaN-OG/University-Chatbot.git
cd University-Chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET=your_strong_random_secret_here
ADMIN_PASSWORD=your_secure_password_here
```

### 5. Run the application

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

---

## 🔑 Admin Panel

Navigate to `/admin.html` and log in with your `ADMIN_PASSWORD`.

| Feature | Description |
|---|---|
| 📋 View Responses | See all intent–response pairs in the database |
| ✏️ Edit Responses | Update any response in real-time |
| 🔄 Retrain Model | Re-compute TF-IDF vectors after adding new data |
| 🌐 Run Scraper | Fetch fresh data from the official CU website |
| 📊 Feedback Stats | View helpful/unhelpful ratings per intent |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| NLP | Scikit-learn (TF-IDF + Cosine Similarity) |
| LLM | Groq API — LLaMA 3.1 8B Instant |
| Database | SQLite |
| Auth | PyJWT |
| Scraping | BeautifulSoup4, Requests |
| Rate Limiting | Flask-Limiter |
| Deployment | Render (Gunicorn) |
| Frontend | Vanilla HTML, CSS, JavaScript |

---

## 🌍 Deployment (Render)

This project is configured for one-click deployment on Render.

1. Fork/push the repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `gunicorn app:app`
5. Add the following **Environment Variables** in the Render dashboard:

```
GROQ_API_KEY=...
JWT_SECRET=...
ADMIN_PASSWORD=...
```

> ⚠️ **Note:** Render's free tier uses an ephemeral filesystem. The SQLite database will reset on each redeploy. For a persistent setup, migrate to PostgreSQL or use a persistent disk.

---

## 📡 API Reference

### `POST /chat`
Send a user message and receive a chatbot response.

**Body:**
```json
{
  "message": "What is the fee structure?",
  "session_id": "user-abc-123"
}
```

**Response:**
```json
{
  "responses": ["The semester fee is ₹75,000/-..."],
  "intents": ["fees"]
}
```

---

### `POST /api/admin/login`
Authenticate as admin and receive a JWT token.

**Body:**
```json
{ "password": "your_admin_password" }
```

---

### `POST /api/admin/retrain`
Rebuild TF-IDF vectors from current database data. *(Requires Bearer token)*

### `POST /api/admin/scrape`
Scrape the CU website for fresh information. *(Requires Bearer token)*

### `GET /api/admin/stats`
Get feedback statistics per intent. *(Requires Bearer token)*

### `GET /api/responses`
List all intent–response pairs. *(Requires Bearer token)*

### `POST /api/responses`
Add or update an intent–response pair. *(Requires Bearer token)*

---

## 🙋 Supported Topics

The chatbot can answer questions about:

`fees` · `exams` · `admission` · `hostel` · `library` · `placement` · `results` · `courses` · `scholarship` · `transport` · `sports` · `canteen` · `wifi` · `clubs` · `events`

---

## 📄 License

This project is built for academic purposes as a semester project for Chandigarh University.

---