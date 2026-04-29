from sentence_transformers import SentenceTransformer, util
import os
import re
from database import get_db

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None
_cached_embeddings = None
_cached_data = None

def load_sentence_model():
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        # Using a small, fast semantic similarity model
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def compute_embeddings():
    global _cached_embeddings, _cached_data
    model = load_sentence_model()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT sentence, intent FROM training_sentences")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None, None
        
    sentences = [r['sentence'] for r in rows]
    print(f"Computing semantic embeddings for {len(sentences)} sentences...")
    embeddings = model.encode(sentences, convert_to_tensor=True)
    
    _cached_embeddings = embeddings
    _cached_data = rows
    return embeddings, rows

def train_and_save():
    """Retrain hook clears the memory cache and re-computes vectors dynamically"""
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

def predict_intents(text, threshold=0.45):
    """Parses text via SentenceTransformer embeddings to compute cosine similarities"""
    global _cached_embeddings, _cached_data
    
    model = load_sentence_model()
    
    if _cached_embeddings is None or _cached_data is None:
        compute_embeddings()
        
    if _cached_embeddings is None:
        return ["fallback"]
        
    query_emb = model.encode(text, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, _cached_embeddings)[0]
    
    ml_detected = set()
    for i, score in enumerate(cos_scores):
        if score.item() >= threshold:
            ml_detected.add(_cached_data[i]['intent'])
            
    # Merge Keyword Boosts
    boosted = keyword_boost(text)
    final_intents = ml_detected.union(boosted)
    
    EXPLICIT_ONLY = {"scholarship"}
    for intel in list(final_intents):
        if intel in EXPLICIT_ONLY and intel not in text.lower():
            final_intents.remove(intel)
            
    return list(final_intents)
