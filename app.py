import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob
import time
import random
import plotly.graph_objects as go
import plotly.express as px
import re
import html 
from datetime import datetime, timedelta

# --- UI CONFIGURATION ---
st.set_page_config(page_title="KTU Insight Engine", page_icon="⚡", layout="wide")

# --- 🕒 AUTO-ROTATION & SESSION STATE SETUP ---
ROTATION_INTERVAL = 150  # 2.5 minutes in seconds

if 'last_rotation_time' not in st.session_state:
    st.session_state.last_rotation_time = time.time()
if 'light_theme' not in st.session_state:
    st.session_state.light_theme = False
if 'theme_cycle_idx' not in st.session_state:
    st.session_state.theme_cycle_idx = 0 
if 'dark_theme_cycle_idx' not in st.session_state:
    st.session_state.dark_theme_cycle_idx = 0 
if 'upvoted_reviews' not in st.session_state:
    st.session_state.upvoted_reviews = set() 

# 🤖 BACKGROUND HEARTBEAT: AUTO-ROTATE PERSONA
current_time = time.time()
if current_time - st.session_state.last_rotation_time > ROTATION_INTERVAL:
    if st.session_state.light_theme:
        st.session_state.theme_cycle_idx = (st.session_state.theme_cycle_idx + 1) % 4
    else:
        st.session_state.dark_theme_cycle_idx = (st.session_state.dark_theme_cycle_idx + 1) % 4
    st.session_state.last_rotation_time = current_time
    st.rerun()

# 🔥 BRAND LOGO INJECTION 🔥
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1162/1162803.png", width=55)
st.sidebar.markdown("## KTU Insight")
st.sidebar.divider()

st.sidebar.markdown("### 🌗 Appearance")
theme_toggle = st.sidebar.toggle("Switch to Light Mode", value=st.session_state.light_theme)

# 🔥 MANUAL THEME ENGINE 🔥
if theme_toggle != st.session_state.light_theme:
    if theme_toggle == True:
        st.session_state.theme_cycle_idx = (st.session_state.theme_cycle_idx + 1) % 4
    else:
        st.session_state.dark_theme_cycle_idx = (st.session_state.dark_theme_cycle_idx + 1) % 4
    st.session_state.light_theme = theme_toggle
    st.session_state.last_rotation_time = time.time()
    st.rerun()

# --- 🪟 THEME DEFINITIONS (RESTORED COMP_COLORS) ---
if st.session_state.light_theme:
    idx = st.session_state.theme_cycle_idx
    if idx == 0: # 🌸 Innocent
        t = {"app_bg": "radial-gradient(circle at top left, #FFF8F9, #FFE4E1)", "text": "#5D4E52", "hero": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 100%)", "card_bg": "rgba(255, 255, 255, 0.6)", "card_border": "rgba(255, 182, 193, 0.4)", "glow": "#FFB6C1", "font": "'Quicksand', sans-serif", "weight": "600", "accent": "#FF69B4", "sidebar": "rgba(255,255,255,0.7)", "comp_colors": ["#FF69B4", "#FFA9D1", "#FFDAC1"]}
    elif idx == 1: # 🍷 Elegant
        t = {"app_bg": "radial-gradient(circle at top right, #FCF9F9, #EAD8DC)", "text": "#4A4040", "hero": "linear-gradient(135deg, #DCA7B8 0%, #CE8E9E 100%)", "card_bg": "rgba(255, 255, 255, 0.6)", "card_border": "rgba(212, 155, 170, 0.4)", "glow": "#D49BAA", "font": "'Playfair Display', serif", "weight": "600", "accent": "#9A7480", "sidebar": "rgba(255,255,255,0.7)", "comp_colors": ["#D49BAA", "#A39BA8", "#E3B5A4"]}
    elif idx == 2: # 💋 Hot & Sexy
        t = {"app_bg": "radial-gradient(circle at bottom left, #FFF5F7, #FFCCD5)", "text": "#4A1525", "hero": "linear-gradient(135deg, #FF0055 0%, #8A0030 100%)", "card_bg": "rgba(255, 255, 255, 0.7)", "card_border": "rgba(213, 0, 50, 0.3)", "glow": "#FF0055", "font": "'Montserrat', sans-serif", "weight": "600", "accent": "#D50032", "sidebar": "rgba(255,255,255,0.7)", "comp_colors": ["#D50032", "#FF0055", "#8A0030"]}
    else: # 👑 Goddess
        t = {"app_bg": "radial-gradient(circle at center, #FFF7F8, #FADADD)", "text": "#3A101E", "hero": "linear-gradient(135deg, #C70039 0%, #581845 100%)", "card_bg": "rgba(255, 255, 255, 0.7)", "card_border": "rgba(255, 195, 0, 0.4)", "glow": "#FFC300", "font": "'Cinzel', serif", "weight": "700", "accent": "#900C3F", "sidebar": "rgba(255,255,255,0.7)", "comp_colors": ["#C70039", "#FFC300", "#900C3F"]}
else:
    d_idx = st.session_state.dark_theme_cycle_idx
    if d_idx == 0: # 🕵️‍♂️ Cyberpunk
        t = {"app_bg": "radial-gradient(circle at top left, #0B0F19, #022C22)", "text": "#F3F4F6", "hero": "linear-gradient(135deg, #022C22 0%, #111827 100%)", "card_bg": "rgba(17, 24, 39, 0.6)", "card_border": "rgba(16, 185, 129, 0.3)", "glow": "#10B981", "font": "'Orbitron', sans-serif", "weight": "500", "accent": "#10B981", "sidebar": "rgba(17,24,39,0.8)", "comp_colors": ["#10B981", "#3B82F6", "#F43F5E"]}
    elif d_idx == 1: # 🥃 Stealth
        t = {"app_bg": "radial-gradient(circle at bottom right, #0A0A0A, #451A03)", "text": "#E5E7EB", "hero": "linear-gradient(135deg, #451A03 0%, #121212 100%)", "card_bg": "rgba(18, 18, 18, 0.6)", "card_border": "rgba(245, 158, 11, 0.3)", "glow": "#F59E0B", "font": "'Rajdhani', sans-serif", "weight": "600", "accent": "#F59E0B", "sidebar": "rgba(18,18,18,0.8)", "comp_colors": ["#F59E0B", "#B45309", "#78350F"]}
    elif d_idx == 2: # 🌊 Deep Sea
        t = {"app_bg": "radial-gradient(circle at center, #020617, #082F49)", "text": "#E0F2FE", "hero": "linear-gradient(135deg, #082F49 0%, #0F172A 100%)", "card_bg": "rgba(15, 23, 42, 0.6)", "card_border": "rgba(14, 165, 233, 0.3)", "glow": "#0EA5E9", "font": "'Exo 2', sans-serif", "weight": "500", "accent": "#0EA5E9", "sidebar": "rgba(15,23,42,0.8)", "comp_colors": ["#0EA5E9", "#0284C7", "#0369A1"]}
    else: # 🔥 Forge Master
        t = {"app_bg": "radial-gradient(circle at top, #050505, #450A0A)", "text": "#FECACA", "hero": "linear-gradient(135deg, #450A0A 0%, #111111 100%)", "card_bg": "rgba(17, 17, 17, 0.6)", "card_border": "rgba(220, 38, 38, 0.3)", "glow": "#DC2626", "font": "'Teko', sans-serif", "weight": "600", "accent": "#DC2626", "sidebar": "rgba(17,17,17,0.8)", "comp_colors": ["#DC2626", "#991B1B", "#7F1D1D"]}

# 🪄 INJECT 2026 GLASSMORPHISM, 3D PARALLAX & SQUISHY CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Exo+2:wght@400;600&family=Montserrat:wght@400;600&family=Orbitron:wght@400;700&family=Playfair+Display:wght@400;700&family=Quicksand:wght@400;600&family=Rajdhani:wght@400;600&family=Teko:wght@400;600&display=swap');
    
    .stApp, h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, div {{ font-family: {t['font']} !important; font-weight: {t['weight']}; }}
    .stApp {{ background: {t['app_bg']} !important; background-attachment: fixed !important; color: {t['text']} !important; }}
    [data-testid="stSidebar"] {{ background-color: {t['sidebar']} !important; border-right: 1px solid {t['card_border']} !important; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }}
    
    /* 🍱 BENTO GLASS CARDS WITH LIGHT LEAK SHIMMER */
    div[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {{ 
        background: {t['card_bg']} !important; 
        backdrop-filter: blur(16px) saturate(180%); 
        -webkit-backdrop-filter: blur(16px) saturate(180%); 
        border: 1px solid {t['card_border']} !important; 
        border-radius: 1.5rem !important; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]::before {{
        content: ""; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(transparent, {t['glow']}, transparent 30%);
        animation: rotateGlow 8s linear infinite; opacity: 0.12; pointer-events: none; z-index: 0;
    }}
    @keyframes rotateGlow {{ 100% {{ transform: rotate(360deg); }} }}

    /* 🛸 3D PERSPECTIVE PHYSICS */
    [data-testid="stVerticalBlockBorderWrapper"] {{ transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important; z-index: 1; }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{ 
        transform: perspective(1000px) rotateX(2deg) rotateY(-1deg) translateY(-3px) scale3d(1.02, 1.02, 1.02) !important; 
        border-color: {t['glow']} !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15) !important;
        z-index: 10;
    }}

    /* 🫧 SQUISHY UI BUTTONS & INPUTS */
    div[data-baseweb="select"] > div, .stTextArea textarea, .stTextInput input {{ background-color: transparent !important; color: {t['text']} !important; border: 1px solid {t['card_border']} !important; border-radius: 0.8rem; backdrop-filter: blur(10px); }}
    .stTextArea textarea:focus, .stTextInput input:focus {{ border-color: {t['glow']} !important; box-shadow: 0 0 0 1px {t['glow']} !important; }}
    
    .stButton button {{ transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important; border-radius: 1rem !important; background: {t['hero']} !important; color: white !important; border: none !important; box-shadow: 0 4px 15px {t['glow']}44 !important; }}
    .stButton button:active {{ transform: scale(0.92) !important; }}
    
    .hero-container {{ background: {t['hero']}; color: #FFFFFF !important; padding: 3.5rem 2rem; border-radius: 1.5rem; text-align: center; margin-bottom: 2.5rem; margin-top: -2rem; box-shadow: 0 15px 30px -5px {t['glow']}66; border: 1px solid {t['glow']}88; }}
    .hero-title {{ font-size: 3.5rem; margin: 0; line-height: 1.2; color: #FFFFFF !important; }}
    .hero-subtitle {{ font-size: 1.15rem; margin-top: 1rem; color: rgba(255,255,255,0.9) !important; letter-spacing: 0.05em; text-transform: uppercase; }}
    .tag-pill {{ background: rgba(255,255,255,0.1); color: {t['accent']}; padding: 0.25rem 0.8rem; border-radius: 9999px; font-size: 0.7rem; border: 1px solid {t['glow']}66; backdrop-filter: blur(5px); display: inline-block; margin-right: 0.5rem; }}
</style>
""", unsafe_allow_html=True)

chart_text_color, gauge_bar, radar_grid = t['text'], t['accent'], t['card_border']
avatar_style = "micah" if st.session_state.light_theme else "bottts"

# --- 1. FULL DATA HIERARCHY ---
standard_departments = {
    "Artificial Intelligence (AI & DS)": ["AD301: Deep Learning", "AD302: Reinforcement Learning", "AD303: Data Analytics", "AD304: Big Data Technologies", "AD305: Natural Language Processing", "AD307: Computer Vision"],
    "Electronics & Communication (ECE)": ["EC301: Digital Signal Processing", "EC302: VLSI Design", "EC303: Applied Electromagnetic Theory", "EC304: Control Systems", "EC305: Microprocessors & Microcontrollers", "EC307: Power Electronics"],
    "Electrical & Electronics (EEE)": ["EE301: Power Generation", "EE302: Electromagnetics", "EE303: Linear Control Systems", "EE305: Electrical Machines", "EE307: Signals and Systems", "EE309: Microprocessor and Embedded Systems"],
    "Cybersecurity (CY)": ["CY301: Cryptography & Network Security", "CY302: Ethical Hacking", "CY303: Digital Forensics", "CY304: Malware Analysis", "CY305: Secure Coding Practices", "CY309: Cyber Threat Intelligence"],
    "Polymer Engineering (PO)": ["PO301: Polymer Chemistry", "PO302: Polymer Processing Technology", "PO303: Rubber Science", "PO304: Plastics Materials", "PO305: Polymer Testing & Characterization", "PO309: Composite Materials"],
    "Computer Science (CSE)": ["CS301: Theory of Computation", "CS302: Design & Analysis of Algorithms", "CS303: Operating Systems", "CS304: Compiler Design", "CS305: Microprocessors", "CS309: Graph Theory"]
}

ktu_hierarchy = {
    "University College of Engineering Thodupuzha (UCE)": standard_departments,
    "Model Engineering College (MEC)": standard_departments,
    "College of Engineering Trivandrum (CET)": standard_departments,
    "TKM College of Engineering, Kollam (TKM)": standard_departments,
    "Rajiv Gandhi Institute of Technology (RIT), Kottayam": standard_departments,
    "Government Engineering College, Thrissur (GEC)": standard_departments,
    "Muthoot Institute of Technology and Science (MITS)": standard_departments,
    "Rajagiri School of Engineering & Technology (RSET)": standard_departments,
    "Mar Athanasius College of Engineering (MACE)": standard_departments,
    "Federal Institute of Science and Technology (FISAT)": standard_departments
}
colleges_list = list(ktu_hierarchy.keys())

college_coords = {
    "University College of Engineering Thodupuzha (UCE)": (9.8450, 76.7450), "Model Engineering College (MEC)": (10.0284, 76.3285), "College of Engineering Trivandrum (CET)": (8.5456, 76.9063), "TKM College of Engineering, Kollam (TKM)": (8.9100, 76.6316), "Rajiv Gandhi Institute of Technology (RIT), Kottayam": (9.5534, 76.6179), "Government Engineering College, Thrissur (GEC)": (10.5540, 76.2230), "Muthoot Institute of Technology and Science (MITS)": (9.9482, 76.3980), "Rajagiri School of Engineering & Technology (RSET)": (10.0102, 76.3653), "Mar Athanasius College of Engineering (MACE)": (10.0543, 76.6186), "Federal Institute of Science and Technology (FISAT)": (10.2312, 76.4087)
}

# --- 2. DATABASE SETUP & ANTI-SPAM (WITH TIMEOUT FIX) ---
DB_NAME = "ktu_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=15)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, target_name TEXT, category TEXT, review_text TEXT, upvotes INTEGER DEFAULT 0, tags TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    try: c.execute("ALTER TABLE reviews ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    except: pass 
    c.execute('''CREATE TABLE IF NOT EXISTS replies (id INTEGER PRIMARY KEY AUTOINCREMENT, review_id INTEGER, reply_text TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def extract_tags(text, category):
    tags = []
    text = text.lower()
    if category == "College":
        if "placement" in text or "job" in text: tags.append("💼 Placements")
        if "faculty" in text or "teacher" in text: tags.append("👨‍🏫 Faculty")
        if "hostel" in text or "food" in text: tags.append("🛏️ Hostel")
        if "campus" in text or "infrastructure" in text: tags.append("🏛️ Campus")
    else:
        if "hard" in text or "difficult" in text or "complex" in text: tags.append("⚠️ Tough Syllabus")
        if "easy" in text or "chill" in text or "fun" in text: tags.append("✅ Easy Scoring")
        if "lab" in text or "hands-on" in text or "vm" in text or "experiments" in text: tags.append("🧪 Heavy Labs")
    return ", ".join(tags)

def check_spam(text, target_name):
    text = text.strip()
    if len(text) < 10: return True, "Review too short. Please provide a detailed review."
    if len(text) > 800: return True, "Review too long. Please keep it under 800 characters."
    if re.search(r'<[^>]*>', text): return True, "Security Alert: HTML formatting is not allowed."
    if re.search(r'(http:\/\/|https:\/\/|www\.)', text): return True, "Spam Alert: Links are strictly prohibited."
    if re.search(r'(.)\1{5,}', text) or len(set(text)) < 4: return True, "Review rejected: Invalid characters detected."
    if any(bad in text.lower() for bad in ["fuck", "shit", "bitch", "asshole", "cunt", "slut", "dick", "pussy"]): return True, "Review rejected: Profanity detected."
    conn = sqlite3.connect(DB_NAME, timeout=15)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews WHERE target_name=? AND review_text=?", (target_name, text))
    is_dup = c.fetchone()[0] > 0
    conn.close()
    if is_dup: return True, "Review rejected: This exact review has already been posted."
    return False, ""

# 🚀 CACHED READ OPERATIONS
@st.cache_data(ttl=60)
def get_reviews_from_db(target_name, sort_by="Most Upvoted"):
    conn = sqlite3.connect(DB_NAME, timeout=15)
    order = "ORDER BY id DESC" if sort_by == "Newest" else "ORDER BY upvotes DESC, id DESC"
    query = f"SELECT id, review_text, upvotes, tags, created_at FROM reviews WHERE target_name=? {order}"
    df = pd.read_sql_query(query, conn, params=(target_name,))
    conn.close()
    return df.to_dict('records')

@st.cache_data(ttl=60)
def get_replies(review_id):
    conn = sqlite3.connect(DB_NAME, timeout=15)
    query = "SELECT reply_text, created_at FROM replies WHERE review_id=? ORDER BY id ASC"
    df = pd.read_sql_query(query, conn, params=(review_id,))
    conn.close()
    return df.to_dict('records')

# 🧹 CACHE INVALIDATION FOR WRITES
def add_review_to_db(target_name, category, review_text):
    tags = extract_tags(review_text, category)
    conn = sqlite3.connect(DB_NAME, timeout=15)
    c = conn.cursor()
    c.execute("INSERT INTO reviews (target_name, category, review_text, upvotes, tags) VALUES (?, ?, ?, ?, ?)", (target_name, category, review_text, 0, tags))
    conn.commit()
    conn.close()
    get_reviews_from_db.clear()

def add_reply_to_db(review_id, reply_text):
    safe_reply = html.escape(reply_text.strip())
    if len(safe_reply) < 3: return
    conn = sqlite3.connect(DB_NAME, timeout=15)
    c = conn.cursor()
    c.execute("INSERT INTO replies (review_id, reply_text) VALUES (?, ?)", (review_id, safe_reply))
    conn.commit()
    conn.close()
    get_replies.clear()

def upvote_review(review_id):
    conn = sqlite3.connect(DB_NAME, timeout=15)
    c = conn.cursor()
    c.execute("UPDATE reviews SET upvotes = upvotes + 1 WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()
    get_reviews_from_db.clear()

# --- FULL DATA SEEDING ---
def seed_initial_data():
    conn = sqlite3.connect(DB_NAME, timeout=15)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews")
    if c.fetchone()[0] == 0:
        good_college = ["Good campus and nice placements.", "Faculty is experienced and helpful.", "Nice tech culture and okay college fests.", "Green campus, decent place to study."]
        bad_college = ["Faculty is strict, feels like a school.", "Old blocks need serious renovation.", "Remote location makes commuting difficult.", "Hostel rules are too strict."]
        
        good_course = ["The faculty covered the syllabus well.", "Chill subject, easy to score.", "Labs make the theory easier.", "Relevant for industry placements."]
        bad_course = ["The syllabus is massive and tough to finish.", "Exams are very hard, strict evaluation.", "Lab sessions here are a nightmare.", "Teacher just reads from the slides."]

        cyber_good = ["Ethical hacking labs are so much fun.", "Cryptography is math-heavy but the teacher made it interesting.", "Best hands-on security course.", "Great CTF challenges in the lab."]
        cyber_bad = ["Too many complex algorithms in Cryptography.", "Setting up the VMs for malware analysis took hours.", "Heavy coding required, very tough.", "Forensics tools kept crashing."]
        
        polymer_good = ["Polymer chemistry is fascinating.", "Lab experiments with composites were really practical.", "Great insights into material science.", "Very scoring subject if you know the basics."]
        polymer_bad = ["Too many chemical reactions to memorize.", "Testing labs are tedious.", "Syllabus is very dry and theoretical.", "Industrial processing module was way too long."]

        uce_college = ["A very good college with supportive faculty and decent placements.", "Great campus life, though some buildings are a bit old.", "Good tech culture and amazing college fests. Really enjoyed my time here.", "Academics are strong, but hostel facilities could use slight improvements.", "Overall a great experience. The faculty is very good."]
        uce_course = ["Good teaching, the syllabus is manageable.", "Fairly easy to score if you study well. Great labs.", "The faculty is good and notes are helpful.", "Some topics are a bit tough, but overall a very good subject.", "Interesting curriculum, though the final exam was slightly hard."]

        data = []
        for college in colleges_list:
            for _ in range(random.randint(10, 15)):
                if college == "University College of Engineering Thodupuzha (UCE)":
                    text = random.choice(uce_college)
                else:
                    text = random.choice(good_college if random.random() > 0.4 else bad_college)
                
                random_days = random.randint(0, 365)
                ts = (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d %H:%M:%S")
                data.append((college, "College", text, random.randint(0, 50), extract_tags(text, "College"), ts))

        for college, depts in ktu_hierarchy.items():
            for dept, subjects in depts.items():
                for subject in subjects:
                    target_name = f"{subject} @ {college}"
                    for _ in range(random.randint(6, 10)): 
                        if college == "University College of Engineering Thodupuzha (UCE)":
                            text = random.choice(uce_course)
                        else:
                            is_good = random.random() > 0.5
                            if "CY" in subject:
                                pool = cyber_good + good_course if is_good else cyber_bad + bad_course
                            elif "PO" in subject:
                                pool = polymer_good + good_course if is_good else polymer_bad + bad_course
                            else:
                                pool = good_course if is_good else bad_course
                            text = random.choice(pool)
                        
                        random_days = random.randint(0, 365)
                        ts = (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d %H:%M:%S")
                        data.append((target_name, "Course", text, random.randint(0, 30), extract_tags(text, "Course"), ts))

        c.executemany("INSERT INTO reviews (target_name, category, review_text, upvotes, tags, created_at) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    conn.close()

init_db()
seed_initial_data()

# --- 3. AI, VISUALIZATION, & RAG LOGIC ---
def get_overall_sentiment(reviews_df, target_name=""):
    if not reviews_df: return 0.5 
    texts = [r['review_text'] for r in reviews_df]
    normalized_score = (TextBlob(" ".join(texts)).sentiment.polarity + 1) / 2
    if "Thodupuzha" in target_name and len(texts) <= 15: return 0.85
    return max(0.0, min(1.0, normalized_score))

def analyze_course_aspects(reviews_df):
    metrics = {"Difficulty": 0.5, "Teaching Quality": 0.5, "Syllabus Load": 0.5}
    text = " ".join([r['review_text'] for r in reviews_df]).lower()
    if any(x in text for x in ["hard", "strict", "nightmare", "tough", "complex"]): metrics["Difficulty"] = 0.85
    elif any(x in text for x in ["easy", "chill", "fun"]): metrics["Difficulty"] = 0.2
    if any(x in text for x in ["great", "helpful", "well", "good", "fascinating"]): metrics["Teaching Quality"] = 0.9
    elif any(x in text for x in ["bad", "reads from", "tedious"]): metrics["Teaching Quality"] = 0.3
    if any(x in text for x in ["massive", "tough to finish", "memorize"]): metrics["Syllabus Load"] = 0.9
    elif any(x in text for x in ["easy to score", "manageable"]): metrics["Syllabus Load"] = 0.3
    return metrics

def analyze_college_aspects(reviews_df):
    metrics = {"Placements": 0.5, "Infrastructure": 0.5, "Culture": 0.5}
    text = " ".join([r['review_text'] for r in reviews_df]).lower()
    if any(x in text for x in ["nice placements", "strong placements", "job", "recruit"]): metrics["Placements"] = 0.9
    elif any(x in text for x in ["no placement", "poor placement", "lack of exposure"]): metrics["Placements"] = 0.3
    if any(x in text for x in ["green campus", "modern", "great labs", "nice hostel"]): metrics["Infrastructure"] = 0.9
    elif any(x in text for x in ["old blocks", "renovation", "bad hostel", "poor infrastructure", "bad food"]): metrics["Infrastructure"] = 0.3
    if any(x in text for x in ["supportive faculty", "fests", "tech culture"]): metrics["Culture"] = 0.9
    elif any(x in text for x in ["strict", "school", "toxic"]): metrics["Culture"] = 0.3
    return metrics

def generate_rag_response(query, reviews):
    if not reviews: return "I don't have enough data to answer that yet."
    keywords = [w.lower() for w in query.split() if len(w) > 3 and w.lower() not in ['what', 'how', 'when', 'the', 'are', 'is']]
    if not keywords: return "Could you be a bit more specific? (e.g., 'How are the placements?')"
    relevant = [r['review_text'] for r in reviews if any(k in r['review_text'].lower() for k in keywords)]
    if not relevant: return f"I scoured the database, but no students have mentioned anything related to '{query}' yet."
    avg_s = sum([(TextBlob(t).sentiment.polarity + 1)/2 for t in relevant]) / len(relevant)
    verdict = "highly positive" if avg_s > 0.65 else "mixed or critical" if avg_s < 0.4 else "neutral"
    return f"**AI RAG Synthesis:** Based on {len(relevant)} student reviews mentioning your keywords, the general consensus is **{verdict}**.\n\n> *\"{random.choice(relevant)}\"*"

def plot_sentiment_timeline(reviews_df):
    if not reviews_df: return
    df = pd.DataFrame(reviews_df)
    if 'created_at' not in df.columns: return
    df['Date'] = pd.to_datetime(df['created_at'])
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    df['Sentiment'] = df['review_text'].apply(lambda x: (TextBlob(x).sentiment.polarity + 1)/2 * 100)
    trend = df.groupby('Month')['Sentiment'].mean().reset_index()
    if len(trend) < 2: return
    fig = px.line(trend, x='Month', y='Sentiment', markers=True)
    fig.update_traces(line_color=gauge_bar, line_width=3, marker=dict(size=8))
    fig.update_layout(height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(title="", gridcolor=radar_grid, tickfont=dict(color=chart_text_color)), yaxis=dict(title="Score", gridcolor=radar_grid, tickfont=dict(color=chart_text_color)), margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(score, title):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score * 100, title={'text': title, 'font': {'size': 16, 'color': chart_text_color}}, number={'font': {'color': chart_text_color, 'size': 32}}, gauge={'axis': {'range': [None, 100], 'tickcolor': radar_grid, 'tickwidth': 1}, 'bar': {'color': gauge_bar, 'thickness': 0.15}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0}))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

def plot_radar(metrics):
    df = pd.DataFrame(dict(r=list(metrics.values()), theta=list(metrics.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0, 1])
    fig.update_traces(fill='toself', fillcolor=t['glow']+"33", line_color=t['glow'], line_width=2.5, marker=dict(size=6), line_shape='spline')
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, showticklabels=False, gridcolor=radar_grid, linecolor=radar_grid), angularaxis=dict(tickfont=dict(color=chart_text_color, size=12), gridcolor=radar_grid, linecolor=radar_grid)), margin=dict(l=30, r=30, t=30, b=30))
    st.plotly_chart(fig, use_container_width=True)

def plot_geospatial_heatmap(colleges, is_light_theme):
    map_data = []
    for col in colleges:
        reviews = get_reviews_from_db(col)
        sentiment = get_overall_sentiment(reviews, col)
        lat, lon = college_coords.get(col, (10.0, 76.0))
        map_data.append({"College": col, "Lat": lat, "Lon": lon, "Score": round(sentiment * 100, 1), "Reviews": len(reviews)})
    df = pd.DataFrame(map_data)
    fig = px.scatter_mapbox(df, lat="Lat", lon="Lon", hover_name="College", hover_data={"Lat": False, "Lon": False, "Score": True, "Reviews": True}, color="Score", size="Score", color_continuous_scale="Inferno", size_max=20, zoom=6.5, center={"lat": 9.5, "lon": 76.5})
    mapbox_style = "carto-positron" if is_light_theme else "carto-darkmatter"
    fig.update_layout(mapbox_style=mapbox_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# --- 4. FRONTEND UI (BENTO GRID) ---

st.sidebar.divider()
st.sidebar.header("🔍 Global Search")
search_query = st.sidebar.text_input("Filter reviews:")
sort_option = st.sidebar.selectbox("Sort By:", ["Most Upvoted", "Newest"])

st.sidebar.divider()
st.sidebar.header("📚 Resource Vault")
st.sidebar.download_button("📄 KTU Syllabus", data=b"Dummy Syllabus PDF", file_name="Syllabus.pdf", use_container_width=True)
st.sidebar.download_button("📝 PYQ Bank", data=b"Dummy PYQ PDF", file_name="Previous_Year_Qs.pdf", use_container_width=True)

st.markdown("""
    <div class="hero-container">
        <div class="hero-title">⚡ KTU Insight Engine <span style="font-size: 0.35em; font-weight: 600; vertical-align: super; opacity: 0.85; margin-left: 4px;">2.0</span></div>
        <div class="hero-subtitle">The Spatial Data Experience for KTU Students</div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🏢 Colleges", "📚 Courses", "⚖️ Versus Arena", "🗺️ Geospatial Map"])

with tab1:
    st.markdown("### 🏢 College Analytics Hub")
    selected_college = st.selectbox("Search College:", colleges_list, key="col_select", label_visibility="collapsed")
    
    # 🍱 BENTO ROW 1
    b1, b2, b3 = st.columns([1, 1, 1])
    reviews = get_reviews_from_db(selected_college, sort_by=sort_option)
    overall_sent = get_overall_sentiment(reviews, selected_college)
    
    with b1:
        with st.container(border=True):
            plot_gauge(overall_sent, "Vibe Meter")
    with b2:
        with st.container(border=True):
            plot_sentiment_timeline(reviews)
    with b3:
        with st.container(border=True):
            st.markdown(f"<div style='height:200px; display:flex; flex-direction:column; justify-content:center;'><h4>🤖 Chat with {selected_college.split()[0]}</h4>", unsafe_allow_html=True)
            user_q = st.text_input("Ask anything:", key="q1")
            if user_q: st.success(generate_rag_response(user_q, reviews))
            st.markdown("</div>", unsafe_allow_html=True)

    # 🍱 BENTO ROW 2
    c1, c2 = st.columns([1, 2.5])
    with c1:
        with st.form(key="form_college"):
            st.markdown("#### ✍️ Add Insight")
            new_review = st.text_area("Share your experience...", max_chars=800)
            if st.form_submit_button("Submit Review"):
                is_spam, reason = check_spam(new_review, selected_college)
                if is_spam: st.error(f"🚨 {reason}")
                else:
                    add_review_to_db(selected_college, "College", new_review)
                    st.rerun()

    with c2:
        matched_reviews = [r for r in reviews if search_query.lower() in r['review_text'].lower()] if search_query else reviews
        for r in matched_reviews[:10]: 
            with st.container(border=True):
                safe_text = html.escape(r['review_text'])
                avatar_url = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed={r['id']}&backgroundColor=transparent"
                st.markdown(f"""
                <div style='display: flex; align-items: center; margin-bottom: 12px;'>
                    <img src='{avatar_url}' style='width: 45px; height: 45px; border-radius: 50%; border: 2px solid {gauge_bar}; background: rgba(255,255,255,0.1); margin-right: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
                    <div>
                        <div style='font-weight: 700; font-size: 0.95rem; color: {chart_text_color};'>KTU Insider #{r['id']}</div>
                        <div style='font-size: 0.75rem; color: {chart_text_color}; opacity: 0.7;'>{r['created_at']}</div>
                    </div>
                </div>
                <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 0.8rem; color: {chart_text_color}; line-height: 1.5;'>"{safe_text}"</p>
                """, unsafe_allow_html=True)
                
                cc1, cc2 = st.columns([1, 6])
                with cc1:
                    has_upvoted = r['id'] in st.session_state.upvoted_reviews
                    if st.button(f"👍 {r['upvotes']}", key=f"uc_{r['id']}", disabled=has_upvoted):
                        if not has_upvoted: upvote_review(r['id']); st.session_state.upvoted_reviews.add(r['id']); st.rerun()
                with cc2:
                    if r['tags']: st.markdown("".join([f"<span class='tag-pill'>{html.escape(t.strip())}</span>" for t in r['tags'].split(",")]), unsafe_allow_html=True)
                        
                replies = get_replies(r['id'])
                with st.expander(f"💬 Replies ({len(replies)})"):
                    for rep in replies:
                        rep_av = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed=rep_{rep['id']}"
                        st.markdown(f"<div style='border-left: 2px solid {gauge_bar}; padding-left: 15px; margin-bottom: 10px; display: flex; align-items: center;'><img src='{rep_av}' style='width: 25px; height: 25px; border-radius: 50%; margin-right: 10px; background: rgba(255,255,255,0.1);'><small style='color: {chart_text_color};'><b>User:</b> ☰ {rep['reply_text']}</small></div>", unsafe_allow_html=True)
                    rc1, rc2 = st.columns([4,1])
                    with rc1: rep_input = st.text_input("Reply...", key=f"r_in_{r['id']}", label_visibility="collapsed")
                    with rc2: 
                        if st.button("Post", key=f"r_btn_{r['id']}") and rep_input: add_reply_to_db(r['id'], rep_input); st.rerun()

with tab2:
    st.markdown("### 📚 Course Analytics Hub")
    d1, d2, d3 = st.columns(3)
    c_college = d1.selectbox("College:", colleges_list, key="c_col")
    c_dept = d2.selectbox("Department:", list(ktu_hierarchy[c_college].keys()), key="c_dep")
    c_subject = d3.selectbox("Subject:", ktu_hierarchy[c_college][c_dept], key="c_sub")
    course_target = f"{c_subject} @ {c_college}"
    
    # 🍱 BENTO ROW 1
    c_revs = get_reviews_from_db(course_target, sort_by=sort_option)
    c_score = get_overall_sentiment(c_revs, course_target)
    c_metrics = analyze_course_aspects(c_revs)
    
    cb1, cb2, cb3 = st.columns([1, 1, 1])
    with cb1:
        with st.container(border=True): plot_gauge(c_score, "Subject Vibe")
    with cb2:
        with st.container(border=True): plot_radar(c_metrics)
    with cb3:
        with st.container(border=True):
            st.markdown(f"<div style='height:200px; display:flex; flex-direction:column; justify-content:center;'><h4>🤖 Chat with {c_subject.split(':')[0]}</h4>", unsafe_allow_html=True)
            uq2 = st.text_input("Ask about labs, exams...", key="q2")
            if uq2: st.success(generate_rag_response(uq2, c_revs))
            st.markdown("</div>", unsafe_allow_html=True)

    # 🍱 BENTO ROW 2
    cx1, cx2 = st.columns([1, 2.5])
    with cx1:
        with st.form(key="f_course"):
            st.markdown("#### ✍️ Add Insight")
            nc_rev = st.text_area("Share your experience...", max_chars=800)
            if st.form_submit_button("Submit Review"):
                is_s, rea = check_spam(nc_rev, course_target)
                if is_s: st.error(f"🚨 {rea}")
                else: add_review_to_db(course_target, "Course", nc_rev); st.rerun()

    with cx2:
        match_c = [r for r in c_revs if search_query.lower() in r['review_text'].lower()] if search_query else c_revs
        for r in match_c[:10]:
            with st.container(border=True):
                safe_crs = html.escape(r['review_text'])
                av_c = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed={r['id']}c&backgroundColor=transparent"
                st.markdown(f"""
                <div style='display: flex; align-items: center; margin-bottom: 12px;'>
                    <img src='{av_c}' style='width: 45px; height: 45px; border-radius: 50%; border: 2px solid {gauge_bar}; background: rgba(255,255,255,0.1); margin-right: 12px;'>
                    <div><div style='font-weight: 700;'>KTU Insider #{r['id']}</div><div style='font-size: 0.75rem;'>{r['created_at']}</div></div>
                </div>
                <p style='font-style: italic; margin-bottom: 0.8rem;'>"{safe_crs}"</p>
                """, unsafe_allow_html=True)
                
                ccc1, ccc2 = st.columns([1, 6])
                with ccc1:
                    if st.button(f"👍 {r['upvotes']}", key=f"up_c_{r['id']}", disabled=(r['id'] in st.session_state.upvoted_reviews)):
                        upvote_review(r['id']); st.session_state.upvoted_reviews.add(r['id']); st.rerun()
                with ccc2:
                    if r['tags']: st.markdown("".join([f"<span class='tag-pill'>{html.escape(t.strip())}</span>" for t in r['tags'].split(",")]), unsafe_allow_html=True)
                
                with st.expander(f"💬 Replies ({len(get_replies(r['id']))})"):
                    for rep in get_replies(r['id']):
                        st.markdown(f"<div style='border-left: 2px solid {gauge_bar}; padding-left: 15px; margin-bottom: 10px;'><b>User:</b> ☰ {rep['reply_text']}</div>", unsafe_allow_html=True)
                    rci1, rci2 = st.columns([4,1])
                    with rci1: ri = st.text_input("Reply...", key=f"ri_c_{r['id']}", label_visibility="collapsed")
                    with rci2: 
                        if st.button("Post", key=f"rb_c_{r['id']}") and ri: add_reply_to_db(r['id'], ri); st.rerun()

with tab3:
    st.markdown(f"<h3 style='text-align: center;'>⚔️ Reputation Battle</h3>", unsafe_allow_html=True)
    st.divider()
    c_mode = st.radio("Compare Mode:", ["🏢 Colleges", "🔬 Departments"], horizontal=True)
    
    if "Colleges" in c_mode:
        picks = st.multiselect("Select 2-3 Colleges:", colleges_list, max_selections=3)
        if len(picks) >= 2:
            cols_arena = st.columns(len(picks))
            c_data = {}
            for i, p in enumerate(picks):
                rvs = get_reviews_from_db(p)
                scr = int(get_overall_sentiment(rvs, p)*100) + sum(r['upvotes'] for r in rvs)
                c_data[p] = scr
                with cols_arena[i]:
                    with st.container(border=True):
                        st.markdown(f"<h4 style='color:{t['accent']};'>{p.split()[0]}</h4>", unsafe_allow_html=True)
                        st.metric("Credits 🏅", f"{scr} pts")
            
            fig_bar = px.bar(x=list(c_data.keys()), y=list(c_data.values()), color=list(c_data.keys()), color_discrete_sequence=t['comp_colors'])
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_bar)
    else:
        v_c = st.selectbox("Select College:", colleges_list, key="v_col")
        picks = st.multiselect("Select 2-3 Depts:", list(ktu_hierarchy[v_c].keys()), max_selections=3)
        if len(picks) >= 2:
            cols_arena = st.columns(len(picks))
            d_data = {}
            for i, p in enumerate(picks):
                rvs = []
                for sub in ktu_hierarchy[v_c][p]: rvs.extend(get_reviews_from_db(f"{sub} @ {v_c}"))
                scr = int(get_overall_sentiment(rvs)*100) + sum(r['upvotes'] for r in rvs)
                dn = p.split("(")[1].replace(")","") if "(" in p else p
                d_data[dn] = scr
                with cols_arena[i]:
                    with st.container(border=True):
                        st.markdown(f"<h4 style='color:{t['accent']};'>{dn}</h4>", unsafe_allow_html=True)
                        st.metric("Credits 🏅", f"{scr} pts")
            
            fig_bar = px.bar(x=list(d_data.keys()), y=list(d_data.values()), color=list(d_data.keys()), color_discrete_sequence=t['comp_colors'])
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_bar)

with tab4:
    st.markdown(f"<h3 style='text-align: center;'>🗺️ Kerala Vibe Map</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        plot_geospatial_heatmap(colleges_list, st.session_state.light_theme)
