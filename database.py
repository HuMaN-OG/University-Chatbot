import sqlite3
import os

DEFAULT_RESPONSES = {
    "fees":        "The semester fee is ₹75,000/-. This includes tuition and lab charges for all enrolled courses. Fee can be paid online via the CU portal or at the finance office by DD/cash.",
    "exam":        "End-semester examinations are conducted twice a year in May and December. Mid-semester tests (MSTs) are held in March and September. The exam schedule is published on the CUIMS portal roughly 3 weeks prior to commencement. A minimum of 75% attendance is strictly required.",
    "admission":   "Admission is based on eligibility criteria and entrance exam score (CUCET). Yes, Diploma holders can apply for direct 2nd year B.E. via lateral entry scheme. Required documents: 10th & 12th marksheets, transfer certificate, Aadhaar, and passport photos.",
    "hostel":      "Hostel facilities are available for both boys and girls with 24x7 security and CCTV. Hostel fee varies by room type. Contact the accommodation office for current pricing. Mess is open for breakfast (7-9 AM), lunch (12-2 PM), and dinner (7-9 PM).",
    "library":     "The Chandigarh University library is open 24x7 for all students. Sectional libraries timings are from 8:00 AM to 8:00 PM on working days. Students can borrow up to 5 books at a time.",
    "placement":   "Chandigarh University has an outstanding placement record. For the 2023-2024 batch, the highest package offered was 54.75 LPA, and overall 9000+ placement offers were generated. Top recruiters include elite companies like TCS, Infosys, Wipro, Capgemini, HCL, Cognizant, Google, Amazon, and Microsoft. Campus recruitment drives typically begin in October.",
    "results":     "Exam results are typically declared within 30-45 days after the completion of the end-semester exams. Students can check their detailed marksheets and SGPA on their CUIMS dashboard under the Academics tab. Re-evaluation requests must be filed within 10 days of result declaration.",
    "courses":     "Chandigarh University offers a wide variety of UG and PG courses including B.Tech, M.Tech, MBA, BBA, BCA, MCA, B.Sc, B.Pharma, and specialized honors degrees with specialization in AI, Cyber Security, and Cloud Computing. You can browse the full curriculum in the University handbook.",
    "scholarship": "CUCET merit scholarship is available. Renewal criteria apply based on SGPA. A minimum SGPA of 7.5 is required to renew the scholarship every year. It is available for the entire duration of the B.Tech program.",
    "transport":   "The University operates a large fleet of modern buses that provide pick and drop facilities to students coming from within a radial distance of 100 Kms, heavily covering Chandigarh, Mohali, Panchkula, and surrounding districts. The exact transport routes and fees can be checked at the transport office.",
    "sports":      "CU boasts state-of-the-art sports facilities including a lush green cricket ground, synthetic basketball courts, a dedicated indoor sports complex for badminton and table tennis, as well as a fully equipped gymnasium. The sports complex is available from 6:00 AM to 8:00 PM.",
    "canteen":     "The university campus has multiple canteens and food courts including major franchises. The standard cafeteria operates from 8:00 AM to 8:00 PM on all working days, offering North Indian, South Indian, and fast food options at subsidized rates.",
    "wifi":        "High-speed Wi-Fi connectivity is available seamlessly across the entire campus, including all academic blocks, libraries, and hostels. Every enrolled student gets a secure login credential via CUIMS which can be used to connect multiple personal devices.",
    "clubs":       "Students can join over 50 dynamic active clubs tailored to multiple disciplines, including technical clubs (like Google Developer Student Club, coding clubs), cultural clubs (dance, dramatics, music), and social clubs. Registration opens at the beginning of each semester.",
    "events":      "The annual youth fest CU Fest and the national-level tech symposium Tech Invent are the major flagship events hosted by Chandigarh University. In addition, the campus regularly hosts hackathons, guest lectures, and cultural nights throughout the academic year.",
    "general":     "Chandigarh University is a leading, NAAC A+ accredited university situated in Punjab, India. It is recognized as one of the fastest-growing private universities in the country, attracting top-tier placements and providing excellent infrastructure.",
    "fallback":    "Sorry, I couldn't understand that. Can you please rephrase?"
}

DEFAULT_TRAINING = [
    ("what is the fee structure", ["fees"]),
    ("semester fee details", ["fees"]),
    ("exam schedule", ["exam"]),
    ("exam date", ["exam"]),
    ("admission process", ["admission"]),
    ("hostel facilities", ["hostel"]),
    ("library timings", ["library"]),
    ("placement record", ["placement"]),
    ("results declaration", ["results"]),
    ("courses offered", ["courses"]),
    ("b tech", ["courses"]),
    ("mba program", ["courses"]),
    ("mca degree", ["courses"]),
    ("scholarship criteria", ["scholarship"]),
    ("fee and exam details", ["fees", "exam"]),
    ("scholarship and placement record", ["scholarship", "placement"]),
    ("fee, exam, scholarship and placement information", ["fees", "exam", "scholarship", "placement"]),
    ("hello", ["general"]),
    ("asdasdasd", ["fallback"]),
    ("what sports facilities are available", ["sports"]),
    ("what are the canteen timings", ["canteen"]),
    ("is there wifi on campus", ["wifi"]),
    ("what clubs are there", ["clubs"]),
    ("what events are held", ["events"]),
    ("what transport facilities are available", ["transport"]),
    ("what are the general queries", ["general", "fallback", "sports", "canteen", "wifi", "clubs", "events", "transport"]),
    ("university bus transport", ["transport"]),
    ("shuttle service timing", ["transport"]),
    ("sports facilities available", ["sports"]),
    ("cricket ground gym", ["sports"]),
    ("canteen food timing", ["canteen"]),
    ("cafeteria menu", ["canteen"]),
    ("wifi internet on campus", ["wifi"]),
    ("network connectivity", ["wifi"]),
    ("student clubs activities", ["clubs"]),
    ("coding club cultural events", ["clubs", "events"])
]

def get_db():
    conn = sqlite3.connect('university.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Create Responses table
    c.execute('''CREATE TABLE IF NOT EXISTS responses (intent TEXT PRIMARY KEY, response TEXT)''')
    # Create Sentences table
    c.execute('''CREATE TABLE IF NOT EXISTS training_sentences (id INTEGER PRIMARY KEY AUTOINCREMENT, intent TEXT, sentence TEXT)''')
    
    # Create Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, intent TEXT, is_helpful INTEGER, query TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create Conversations table
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Seed responses
    c.execute("SELECT COUNT(*) FROM responses")
    if c.fetchone()[0] == 0:
        for intel, res in DEFAULT_RESPONSES.items():
            c.execute("INSERT INTO responses (intent, response) VALUES (?, ?)", (intel, res))
            
    # Seed sentences (flattening multi-intent lists into separate rows for relational DB)
    c.execute("SELECT COUNT(*) FROM training_sentences")
    if c.fetchone()[0] == 0:
        for sentence, intents in DEFAULT_TRAINING:
            for intel in intents:
                c.execute("INSERT INTO training_sentences (sentence, intent) VALUES (?, ?)", (sentence, intel))
                
    conn.commit()
    conn.close()

def get_response(intent):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT response FROM responses WHERE intent=?", (intent,))
    row = cur.fetchone()
    conn.close()
    return row['response'] if row else None

def log_feedback(intent, is_helpful, query):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO feedback (intent, is_helpful, query) VALUES (?, ?, ?)", (intent, int(is_helpful), query))
    conn.commit()
    conn.close()

def get_feedback_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT intent, COUNT(*) as total, SUM(is_helpful) as positive FROM feedback GROUP BY intent")
    stats = []
    for row in cur.fetchall():
        stats.append({'intent': row['intent'], 'total': row['total'], 'positive': row['positive']})
    conn.close()
    return stats

def log_conversation(session_id, role, message):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO conversations (session_id, role, message) VALUES (?, ?, ?)", (session_id, role, message))
    conn.commit()
    conn.close()

def get_conversation_history(session_id, limit=10):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT role, message FROM conversations WHERE session_id=? ORDER BY timestamp DESC LIMIT ?", (session_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [{"role": r['role'], "message": r['message']} for r in reversed(rows)]
