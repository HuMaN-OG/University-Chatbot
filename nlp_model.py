from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
from database import get_db

_vectorizer = None
_cached_tfidf_matrix = None
_cached_data = None

def compute_embeddings():
    global _vectorizer, _cached_tfidf_matrix, _cached_data
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT sentence, intent FROM training_sentences")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None, None
        
    sentences = [r['sentence'] for r in rows]
    print(f"Computing TF-IDF vectors for {len(sentences)} sentences...")
    
    # TF-IDF Vectorizer to convert text to numerical vectors
    _vectorizer = TfidfVectorizer(stop_words='english')
    _cached_tfidf_matrix = _vectorizer.fit_transform(sentences)
    
    _cached_data = rows
    return _cached_tfidf_matrix, rows

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

def predict_intents(text, threshold=0.2):
    """Parses text via TF-IDF embeddings to compute cosine similarities"""
    global _vectorizer, _cached_tfidf_matrix, _cached_data
    
    if _cached_tfidf_matrix is None or _cached_data is None:
        compute_embeddings()
        
    if _cached_tfidf_matrix is None:
        return ["fallback"]
        
    query_vec = _vectorizer.transform([text])
    cos_scores = cosine_similarity(query_vec, _cached_tfidf_matrix)[0]
    
    ml_detected = set()
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
            
    return list(final_intents)
