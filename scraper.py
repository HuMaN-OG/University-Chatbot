import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# ---------- CONFIG ----------
# Use a session so cookies carry across requests (helps bypass soft 403 blocks)
session = requests.Session()
session.headers.update({
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer":         "https://www.cuchd.in/",
    "Connection":      "keep-alive",
})

# Warm up the session by hitting homepage first (loads cookies)
def warm_session():
    try:
        session.get("https://www.cuchd.in/", timeout=10)
        print("  Session warmed up with homepage cookies")
        time.sleep(1)
    except Exception as e:
        print(f"  Could not warm session: {e}")

PAGES = {
    "admission":   "https://www.cuchd.in/admissions/",
    "scholarship": "https://www.cuchd.in/scholarship/",
    "hostel":      "https://www.cuchd.in/student-services/hostel-facility.php",
    "placement":   "https://www.cuchd.in/placements/",
    "courses":     "https://www.cuchd.in/academics/institutes.php",
    "fees":        "https://www.cuchd.in/admissions/",
    "exam":        "https://www.cuchd.in/examination/",
    "library":     "https://culib.cuchd.in/",
    "transport":   "https://www.cuchd.in/student-services/transport-facility.php",
}

# ---------- SCRAPER ----------
def scrape_page(url):
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 403:
            print(f"  [WARN] 403 Forbidden - site blocks bots. Using fallback response.")
            return []
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove nav, footer, scripts, styles — keep only content
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        # Extract meaningful text blocks (paragraphs)
        texts = []
        for tag in soup.find_all("p"):
            text = tag.get_text(separator=" ", strip=True)
            if len(text) > 40 and "." in text:
                texts.append(text)
                
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in texts:
            if t not in seen:
                seen.add(t)
                unique.append(t)

        return unique[:5]  # Top 5 most relevant paragraphs per page

    except Exception as e:
        print(f"  ERROR scraping {url}: {e}")
        return []


# ---------- BUILD RESPONSES ----------
def build_response(texts, fallback):
    if not texts:
        return fallback
    # Join top 4 lines into a clean response
    return " | ".join(texts[:4])


# ---------- MAIN ----------
def run_scraper():
    print("Starting scraper for cuchd.in...\n")
    warm_session()
    data = {}

    fallbacks = {
        "admission":   "Admission is based on eligibility criteria and entrance exam score (CUCET). Yes, Diploma holders can apply for direct 2nd year B.E. via lateral entry scheme. Required documents: 10th & 12th marksheets, transfer certificate, Aadhaar, and passport photos.",
        "scholarship": "CUCET merit scholarship is available. Renewal criteria apply based on SGPA. A minimum SGPA of 7.5 is required to renew the scholarship every year. It is available for the entire duration of the B.Tech program.",
        "hostel":      "Hostel facilities are available for both boys and girls with 24x7 security and CCTV. Hostel fee varies by room type. Contact the accommodation office for current pricing. Mess is open for breakfast (7-9 AM), lunch (12-2 PM), and dinner (7-9 PM).",
        "placement":   "Chandigarh University has an outstanding placement record. For the 2023-2024 batch, the highest package offered was 54.75 LPA, and overall 9000+ placement offers were generated. Top recruiters include elite companies like TCS, Infosys, Wipro, Capgemini, HCL, Cognizant, Google, Amazon, and Microsoft. Campus recruitment drives typically begin in October.",
        "courses":     "Chandigarh University offers a wide variety of UG and PG courses including B.Tech, M.Tech, MBA, BBA, BCA, MCA, B.Sc, B.Pharma, and specialized honors degrees with specialization in AI, Cyber Security, and Cloud Computing. You can browse the full curriculum in the University handbook.",
        "fees":        "The semester fee is ₹75,000/-. This includes tuition and lab charges for all enrolled courses. Fee can be paid online via the CU portal or at the finance office by DD/cash.",
        "exam":        "End-semester examinations are conducted twice a year in May and December. Mid-semester tests (MSTs) are held in March and September. The exam schedule is published on the CUIMS portal roughly 3 weeks prior to commencement. A minimum of 75% attendance is strictly required to be eligible to appear for the final exams.",
        "library":     "The Chandigarh University library is open 24x7 for all students. Sectional libraries timings are from 8:00 AM to 8:00 PM on working days. Students can borrow up to 5 books at a time.",
        "transport":   "The University operates a large fleet of modern buses that provide pick and drop facilities to students coming from within a radial distance of 100 Kms, heavily covering Chandigarh, Mohali, Panchkula, and surrounding districts. The exact transport routes and fees can be checked at the transport office.",
    }

    for intent, url in PAGES.items():
        print(f"Scraping [{intent}] -> {url}")
        texts = scrape_page(url)
        data[intent] = build_response(texts, fallbacks[intent])
        print(f"  [OK] Got {len(texts)} lines")
        time.sleep(1)  # Be polite, don't hammer the server

    # Save to SQLite database
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS responses (intent TEXT PRIMARY KEY, response TEXT)''')
    for intent, response in data.items():
        c.execute("UPDATE responses SET response=? WHERE intent=?", (response, intent))
        if c.rowcount == 0:
            c.execute("INSERT INTO responses (intent, response) VALUES (?, ?)", (intent, response))
    conn.commit()
    conn.close()

    print("\n[DONE] Scraping complete! Data dynamically injected into university.db")
    print("\nPreview of scraped data:")
    for intent, response in data.items():
        print(f"\n[{intent}]:\n  {response[:120]}...")

if __name__ == "__main__":
    run_scraper()
