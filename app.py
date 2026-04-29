from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from database import init_db, get_db, get_response, log_feedback, get_feedback_stats, log_conversation, get_conversation_history
from nlp_model import train_and_save, predict_intents
from scraper import run_scraper
import os
import re
import datetime
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"],
    storage_uri="memory://",
)

# Initialize DB on bootup
init_db()

GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "howdy"]
FAREWELLS  = ["bye", "goodbye", "thanks", "thank you", "ok bye", "see you", "great thanks"]

# ---- AUTHENTICATION CONFIG ---- #
JWT_SECRET = os.environ.get("JWT_SECRET", "super-secure-chatbot-secret-key")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

def is_auth(req):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ")[1]
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return data.get('user') == 'admin'
    except Exception:
        return False

# ---- FRONTEND ROUTES ---- #
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/admin.html')
def admin_page():
    return send_file('admin.html')

# ---- ADMIN LOGIN & SECURE ENDPOINTS ---- #

@app.route('/api/admin/login', methods=['POST'])
@limiter.limit("10 per minute")
def admin_login():
    data = request.get_json() or {}
    password = data.get("password")
    if password == ADMIN_PASSWORD:
        token = jwt.encode({
            'user': 'admin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Unauthorized: Invalid credentials'}), 401

@app.route('/api/responses', methods=['GET'])
def get_all_responses():
    if not is_auth(request): return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT intent, response FROM responses")
    rows = c.fetchall()
    conn.close()
    return jsonify([{'intent': r['intent'], 'response': r['response']} for r in rows])

@app.route('/api/responses', methods=['POST'])
def update_response():
    if not is_auth(request): return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    intent, resp = data.get('intent'), data.get('response')
    if not intent or not resp: return jsonify({'error': 'Malformed'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT intent FROM responses WHERE intent=?", (intent,))
    if c.fetchone():
        c.execute("UPDATE responses SET response=? WHERE intent=?", (resp, intent))
    else:
        c.execute("INSERT INTO responses (intent, response) VALUES (?, ?)", (intent, resp))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/admin/retrain', methods=['POST'])
def handle_retrain():
    if not is_auth(request): return jsonify({'error': 'Unauthorized'}), 401
    try:
        train_and_save()
        return jsonify({'status': 'Semantic vectors successfully rebuilt on dynamic datasets!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/scrape', methods=['POST'])
def handle_scrape():
    if not is_auth(request): return jsonify({'error': 'Unauthorized'}), 401
    try:
        run_scraper()
        return jsonify({'status': 'Scraping executed successfully. Live website info loaded into Database!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    if not is_auth(request): return jsonify({'error': 'Unauthorized'}), 401
    stats = get_feedback_stats()
    return jsonify(stats)

@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    data = request.get_json()
    intent = data.get('intent')
    is_helpful = data.get('is_helpful', 1)
    query = data.get('query', '')
    if intent:
        log_feedback(intent, is_helpful, query)
    return jsonify({'status': 'success'})

import os
from groq import Groq

def generate_rag_response(query, context, history):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return f"To generate unique and specific answers to your questions, please set your GROQ_API_KEY securely. Here is what I found loosely: {context[:150]}..."
    try:
        client = Groq(api_key=api_key)
        
        messages = [
            {"role": "system", "content": "You are a specialized Chandigarh University chatbot. Provide concise, direct, and conversational answers using ONLY the provided Context Information and past history. DO NOT ever use phrases like 'Based on the provided context'. Just answer naturally. If the exact answer isn't in the context, give the most relevant information. Context: " + context}
        ]
        
        for h in history:
            if h['role'] == 'user' and h['message'] == query:
                continue
            messages.append({"role": h['role'], "content": h['message']})
            
        messages.append({"role": "user", "content": query})
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Generation Error (Check your API settings): {e}"

# ---- PUBLIC BOT API ---- #

@app.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    data = request.get_json() or {}
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default-session')
    if not user_msg: return jsonify({'error': 'Empty message'}), 400
    
    log_conversation(session_id, 'user', user_msg)
    
    # Rule based Overrides
    if any(re.search(r'\b' + re.escape(word) + r'\b', user_msg.lower()) for word in GREETINGS):
        resp = "Hello! How can I help you today?"
        log_conversation(session_id, 'assistant', resp)
        return jsonify({'responses': [resp], 'intents': ['greeting']})
        
    if any(re.search(r'\b' + re.escape(word) + r'\b', user_msg.lower()) for word in FAREWELLS):
        resp = "Goodbye! Feel free to ask anytime."
        log_conversation(session_id, 'assistant', resp)
        return jsonify({'responses': [resp], 'intents': ['farewell']})

    # AI Retrieval
    final_intents = predict_intents(user_msg)
    
    if not final_intents:
        fallback_resp = get_response("fallback") or "Sorry, I didn't understand that. You can ask me about: fees, exams, admission, hostel, library, placement, results, courses, scholarships, transport, sports, canteen, wifi, or clubs."
        log_conversation(session_id, 'assistant', fallback_resp)
        return jsonify({'responses': [fallback_resp], 'intents': ['fallback']})
        
    context_blocks = []
    for intel in final_intents:
        resp = get_response(intel)
        if resp and resp not in ["Sorry, I couldn't understand that. Can you please rephrase?"]:
            context_blocks.append(resp)
            
    if not context_blocks:
        fallback_resp = get_response("fallback") or "Sorry, no relevant information found."
        log_conversation(session_id, 'assistant', fallback_resp)
        return jsonify({'responses': [fallback_resp], 'intents': list(final_intents)})

    full_context = " | ".join(context_blocks)
    
    # Gather multi-turn logs
    history = get_conversation_history(session_id, limit=6)
    
    # RAG Generation
    final_answer = generate_rag_response(user_msg, full_context, history)
    
    log_conversation(session_id, 'assistant', final_answer)
    
    return jsonify({'responses': [final_answer], 'intents': list(final_intents)})

if __name__ == '__main__':
    app.run(debug=True)
