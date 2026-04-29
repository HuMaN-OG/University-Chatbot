# Multi-Intent University Chatbot (Advanced Architecture)

An end-to-end, full-stack NLP chatbot built with Python, Flask, Scikit-Learn, SQLite, and vanilla web technologies. It is designed to act as an automated assistant for university queries (exam schedules, fees, hostel info, etc.) utilizing a dynamic Machine Learning intent classifier.

> Built with: Python · Flask · Scikit-Learn · SQLite · HTML/CSS/JS

## 🚀 Key Features

### Frontend & UI Experience 
* **Deep Black Aesthetic:** Both the chat application and the admin dashboard feature a stunning, premium dark mode aesthetic with animated ambient blurs, gradient message bubbles, and smooth css styling.
* **Visual Intent Tags:** When the AI responds, it dynamically displays the detected intents (e.g. `[fees]`, `[exam]`) in the chat footer to visually demonstrate the NLP classification occurring behind the scenes.
* **Conversational Persistence:** The application hooks into browser `localStorage`, ensuring that the chat history does not disappear if the user refreshes or temporarily closes the page. 
* **Organic Typing Animations:** Configured with an asynchronous delay to display animated "typing dots" before delivering responses, adding behavioral realism to the bot.
* **Voice & Accessibility:** Users can interact hands-free using the native Web Speech API (Microphone icon) and can have responses read aloud using the **Text-To-Speech (TTS)** speaker icon.
* **Quick Action Chips:** Features one-click suggestion buttons for common queries like Fees, Admission, and Hostels to streamline the user experience.
* **Chat Export:** Users can download the full conversation as `chat_log.txt` using the floppy disk icon.
* **Interactive Feedback:** Integrated 👍/👎 buttons allow users to rate responses, which are then logged for quality analysis.

### Backend & ML Architecture
* **Hybrid RAG Architecture:** Combines traditional NLP classification with **Retrieval-Augmented Generation (RAG)**. It uses the Groq API and **Llama 3.1** to generate intelligent, context-aware responses based on database content.
* **Modular Codebase:** Cleanly engineered separation of concerns containing the database connector (`database.py`), the routing framework (`app.py`), and the computational ML core (`nlp_model.py`).
* **Multi-Intent Processing:** Capable of detecting and responding to multiple user intents within a single query (e.g., "fees and exam schedule").
* **Live Web Scraper:** Includes a specialized `scraper.py` that can actively crawl the university website to keep the local database synchronized with live data.
* **SQLite Database Engine:** AI response definitions and training sentences are retrieved and written natively to a dynamic `university.db`.
* **Pickled ML Kernel Cache:** The application intelligently serializes the trained `LogisticRegression` and `TfidfVectorizer` states to a disk file named `model.pkl` for instant bootups.
* **Secure Admin Control Panel:** A password-protected interface (`admin.html`) where administrators can edit responses, view **live feedback analytics**, trigger the web scraper, and retrain the AI kernel.
* **Auto Model Generation:** `model.pkl` and `university.db` are automatically created and seeded on first boot — no manual setup required.

---

## 📁 File Structure

* **`app.py`** — The central Flask router and gateway. Initiates the server, checks auth tokens, and exposes `/chat` and `/api/responses` mechanisms.
* **`database.py`** — Handles SQLite connections utilizing context-pooling and builds the `university.db` tables upon first boot.
* **`nlp_model.py`** — The brain of the project. Contains `train_and_save()` and `predict_intents()` utilizing Scikit-learn to handle TF-IDF mapping and intent classification mathematically.
* **`index.html`** — The primary client-side web application interface the user interacts with securely.
* **`admin.html`** — The administrative dashboard protected by keyword algorithms designed for dynamic GUI-based database manipulation.

## ⚙️ How to Run

1. Open your terminal in this directory.
2. Ensure you have the required packages by `pip install -r requirement.txt).
3. Execute the server:
   ```bash
   python app.py
   ```
4. Double-click `index.html` via your browser to converse with the bot.
5. In your browser access `admin.html`. Use the password **admin123** to modify the parameters!
