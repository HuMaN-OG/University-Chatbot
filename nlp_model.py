from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
import requests
from database import get_db

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX", "university-chatbot")
HF_API_KEY = os.environ.get("HF_API_KEY")

_vectorizer = None
_cached_tfidf_matrix = None
_cached_data = None
pinecone_index = None

if PINECONE_API_KEY:
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        print("Pinecone initialization failed:", e)

def get_remote_embedding(text):
    if not HF_API_KEY: return None
    url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    try:
        resp = requests.post(url, headers={"Authorization": f"Bearer {HF_API_KEY}"}, json={"inputs": [text]})
        if resp.status_code == 200:
            return resp.json()[0]
    except Exception:
        pass
    return None

def compute_embeddings():
    global _vectorizer, _cached_tfidf_matrix, _cached_data
    
    conn = get_db()
    # Handle dict-like cursor for pg or standard for sqlite
    c = conn.cursor()
    c.execute("SELECT sentence, intent FROM training_sentences")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None, None
        
    sentences = [r['sentence'] if 'sentence' in r else r[0] for r in rows]
    intents = [r['intent'] if 'intent' in r else r[1] for r in rows]
    
    # Restructure into standard dict format regardless of db driver
    formatted_rows = [{"sentence": sentences[i], "intent": intents[i]} for i in range(len(sentences))]
    
    if pinecone_index and HF_API_KEY:
        print(f"Upserting {len(sentences)} training vectors to Pinecone...")
        vectors = []
        for i, row in enumerate(formatted_rows):
            emb = get_remote_embedding(row['sentence'])
            if emb:
                vectors.append({
                    "id": f"vec_{i}",
                    "values": emb,
                    "metadata": {"intent": row['intent'], "sentence": row['sentence']}
                })
        if vectors:
            # Upsert in batches of 100
            for i in range(0, len(vectors), 100):
                pinecone_index.upsert(vectors=vectors[i:i+100])
        return True, formatted_rows
    else:
        print(f"Computing local TF-IDF vectors for {len(sentences)} sentences (Pinecone disabled)...")
        _vectorizer = TfidfVectorizer(stop_words='english')
        _cached_tfidf_matrix = _vectorizer.fit_transform(sentences)
        _cached_data = formatted_rows
        return _cached_tfidf_matrix, formatted_rows

def train_and_save():
    print("Initiating Semantic Cache Rebuilding Protocol...")
    compute_embeddings()
    print("Successfully re-embedded dynamic database training vectors!")

def keyword_boost(text):
    text = text.lower()
    boosted = set()
    if "fee" in text or "fees" in text: boosted.add("fees")
    if "result" in text or "cgpa" in text or "marks" in text: boosted.add("results")
    if "exam" in text or "schedule" in text: boosted.add("exam")
    if "admission" in text or "apply" in text: boosted.add("admission")
    if "hostel" in text: boosted.add("hostel")
    if "library" in text: boosted.add("library")
    if "placement" in text or "record" in text: boosted.add("placement")
    if "course" in text or "b tech" in text or "btech" in text or "b.tech" in text or "mba" in text or "mca" in text or "bba" in text or "degree" in text or "program" in text: boosted.add("courses")
    if "scholarship" in text: boosted.add("scholarship")
    if "sports" in text: boosted.add("sports")
    if "canteen" in text: boosted.add("canteen")
    if "wifi" in text: boosted.add("wifi")
    if "club" in text: boosted.add("clubs")
    if "event" in text or "fest" in text: boosted.add("events")
    if "transport" in text: boosted.add("transport")
    
    if any(re.search(r'\b' + re.escape(greet) + r'\b', text) for greet in ["hello", "hi", "hey"]): 
        boosted.add("general")
    return boosted

def predict_intents(text, threshold=0.2):
    global _vectorizer, _cached_tfidf_matrix, _cached_data
    
    ml_detected = set()
    
    if pinecone_index and HF_API_KEY:
        # Pinecone Vector Search
        emb = get_remote_embedding(text)
        if emb:
            res = pinecone_index.query(vector=emb, top_k=3, include_metadata=True)
            for match in res['matches']:
                if match['score'] >= threshold:
                    ml_detected.add(match['metadata']['intent'])
    else:
        # Local TF-IDF Search
        if _cached_tfidf_matrix is None or _cached_data is None:
            compute_embeddings()
            
        if _cached_tfidf_matrix is not None:
            query_vec = _vectorizer.transform([text])
            cos_scores = cosine_similarity(query_vec, _cached_tfidf_matrix)[0]
            
            for i, score in enumerate(cos_scores):
                if score >= threshold:
                    ml_detected.add(_cached_data[i]['intent'])
            
    # Merge Keyword Boosts
    boosted = keyword_boost(text)
    final_intents = ml_detected.union(boosted)
    
    EXPLICIT_ONLY = {"scholarship"}
    for intel in list(final_intents):
        if intel in EXPLICIT_ONLY and intel not in text.lower():
            final_intents.remove(intel)
            
    # If no intent matched, return fallback
    if not final_intents:
        return ["fallback"]
        
    return list(final_intents)
