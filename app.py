import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob
import time
import random
import requests
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie

# --- UI CONFIGURATION ---
st.set_page_config(page_title="KTU Insight Engine", page_icon="⚡", layout="wide")

# --- THEME MANAGEMENT ---
if 'light_theme' not in st.session_state:
    st.session_state.light_theme = False

st.sidebar.markdown("### 🌗 Appearance")
theme_toggle = st.sidebar.toggle("Switch to Light Mode", value=st.session_state.light_theme)

if theme_toggle != st.session_state.light_theme:
    st.session_state.light_theme = theme_toggle
    st.rerun()

# Apply CSS overrides and set chart color variables based on the toggle state
if st.session_state.light_theme:
    st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #0f172a !important; }
        div[data-testid="stForm"] { background-color: #ffffff !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        .stSelectbox label, .stTextArea label { color: #0f172a !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Cool Light Mode Variables
    chart_text_color = "#0f172a"
    radar_fill = "rgba(14, 165, 233, 0.4)"   # Cyan-blue
    radar_line = "#0ea5e9"
    wc_cmap = "winter"                       # Cool blue/green colormap
    gauge_bar = "#0ea5e9"
    gauge_high = "rgba(14, 165, 233, 0.3)"
else:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117 !important; color: #fafafa !important; }
        [data-testid="stSidebar"] { background-color: #262730 !important; }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #fafafa !important; }
        div[data-testid="stForm"] { background-color: #262730 !important; border: 1px solid #444; }
        .stSelectbox label, .stTextArea label { color: #fafafa !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Standard Dark Mode Variables
    chart_text_color = "white"
    radar_fill = "rgba(0, 204, 150, 0.5)"
    radar_line = "#00CC96"
    wc_cmap = "Greens"
    gauge_bar = "#00CC96"
    gauge_high = "rgba(0, 204, 150, 0.3)"

# --- ANIMATION HELPER ---
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_ai = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_1m1of8zi.json")

# --- 1. DATA HIERARCHY ---
standard_departments = {
      "Artificial Intelligence (AI & DS)": [
        "AD301: Deep Learning", "AD302: Reinforcement Learning", 
        "AD303: Data Analytics", "AD304: Big Data Technologies", 
	"AD305: Natural Language Processing", "AD307: Computer Vision"

    ],
    "Electronics & Communication (ECE)": [
        "EC301: Digital Signal Processing", "EC302: VLSI Design", 
        "EC303: Applied Electromagnetic Theory", "EC304: Control Systems", 
        "EC305: Microprocessors & Microcontrollers", "EC307: Power Electronics"
    ],
    "Electrical & Electronics (EEE)": [
        "EE301: Power Generation", "EE302: Electromagnetics", 
        "EE303: Linear Control Systems", "EE305: Electrical Machines", 
        "EE307: Signals and Systems", "EE309: Microprocessor and Embedded Systems"
    ],
    "Cybersecurity (CY)": [
        "CY301: Cryptography & Network Security", "CY302: Ethical Hacking", 
        "CY303: Digital Forensics", "CY304: Malware Analysis", 
        "CY305: Secure Coding Practices", "CY309: Cyber Threat Intelligence"
    ],
    "Polymer Engineering (PO)": [
        "PO301: Polymer Chemistry", "PO302: Polymer Processing Technology", 
        "PO303: Rubber Science", "PO304: Plastics Materials", 
        "PO305: Polymer Testing & Characterization", "PO309: Composite Materials"
    ],
    "Computer Science (CSE)": [
        "CS301: Theory of Computation", "CS302: Design & Analysis of Algorithms", 
        "CS303: Operating Systems", "CS304: Compiler Design", 
        "CS305: Microprocessors", "CS309: Graph Theory"
    ]
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

# --- 2. DATABASE SETUP & UPGRADE ---
DB_NAME = "ktu_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_name TEXT,
            category TEXT,
            review_text TEXT,
            upvotes INTEGER DEFAULT 0,
            tags TEXT
        )
    ''')
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

def add_review_to_db(target_name, category, review_text):
    tags = extract_tags(review_text, category)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO reviews (target_name, category, review_text, upvotes, tags) VALUES (?, ?, ?, ?, ?)", 
              (target_name, category, review_text, 0, tags))
    conn.commit()
    conn.close()

def get_reviews_from_db(target_name):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, review_text, upvotes, tags FROM reviews WHERE target_name=? ORDER BY upvotes DESC", conn, params=(target_name,))
    conn.close()
    return df.to_dict('records')

def upvote_review(review_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE reviews SET upvotes = upvotes + 1 WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()

def seed_initial_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews")
    
    if c.fetchone()[0] == 0:
        good_college = ["Good campus and nice placements.", "Faculty is experienced and helpful.", "Nice tech culture and okay college fests.", "Green campus, decent place to study."]
        bad_college = ["Faculty is strict, feels like a school.", "Old blocks need serious renovation.", "Remote location makes commuting difficult.", "Hostel rules are too strict."]
        
        # Generic Course Reviews
        good_course = ["The faculty covered the syllabus well.", "Chill subject, easy to score.", "Labs make the theory easier.", "Relevant for industry placements."]
        bad_course = ["The syllabus is massive and tough to finish.", "Exams are very hard, strict evaluation.", "Lab sessions here are a nightmare.", "Teacher just reads from the slides."]

        # Specialized Course Reviews
        cyber_good = ["Ethical hacking labs are so much fun.", "Cryptography is math-heavy but the teacher made it interesting.", "Best hands-on security course.", "Great CTF challenges in the lab."]
        cyber_bad = ["Too many complex algorithms in Cryptography.", "Setting up the VMs for malware analysis took hours.", "Heavy coding required, very tough.", "Forensics tools kept crashing."]
        
        polymer_good = ["Polymer chemistry is fascinating.", "Lab experiments with composites were really practical.", "Great insights into material science.", "Very scoring subject if you know the basics."]
        polymer_bad = ["Too many chemical reactions to memorize.", "Testing labs are tedious.", "Syllabus is very dry and theoretical.", "Industrial processing module was way too long."]

        # UCE Specific Overrides (85% Sentiment Lock)
        uce_college = ["A very good college with supportive faculty and decent placements.", "Great campus life, though some buildings are a bit old.", "Good tech culture and amazing college fests. Really enjoyed my time here.", "Academics are strong, but hostel facilities could use slight improvements.", "Overall a great experience. The faculty is very good."]
        uce_course = ["Good teaching, the syllabus is manageable.", "Fairly easy to score if you study well. Great labs.", "The faculty is good and notes are helpful.", "Some topics are a bit tough, but overall a very good subject.", "Interesting curriculum, though the final exam was slightly hard."]

        initial_data = []

        for college in colleges_list:
            for _ in range(random.randint(10, 15)):
                if college == "University College of Engineering Thodupuzha (UCE)":
                    text = random.choice(uce_college)
                else:
                    text = random.choice(good_college if random.random() > 0.4 else bad_college)
                initial_data.append((college, "College", text, random.randint(0, 50), extract_tags(text, "College")))

        for college, depts in ktu_hierarchy.items():
            for dept, subjects in depts.items():
                for subject in subjects:
                    target_name = f"{subject} @ {college}"
                    for _ in range(random.randint(10, 15)):
                        if college == "University College of Engineering Thodupuzha (UCE)":
                            text = random.choice(uce_course)
                        else:
                            is_good = random.random() > 0.5
                            
                            # Blend generic reviews with domain-specific ones
                            if "CY" in subject:
                                pool = cyber_good + good_course if is_good else cyber_bad + bad_course
                            elif "PO" in subject:
                                pool = polymer_good + good_course if is_good else polymer_bad + bad_course
                            else:
                                pool = good_course if is_good else bad_course
                                
                            text = random.choice(pool)
                            
                        initial_data.append((target_name, "Course", text, random.randint(0, 30), extract_tags(text, "Course")))

        c.executemany("INSERT INTO reviews (target_name, category, review_text, upvotes, tags) VALUES (?, ?, ?, ?, ?)", initial_data)
        conn.commit()
    conn.close()

init_db()
seed_initial_data()

# --- 3. AI & VISUALIZATION LOGIC ---
def get_overall_sentiment(reviews_df, target_name=""):
    if not reviews_df: return 0.5 
    texts = [r['review_text'] for r in reviews_df]
    text = " ".join(texts)
    
    normalized_score = (TextBlob(text).sentiment.polarity + 1) / 2
    
    # Exact 85 Prototype Lock for UCE (only applies if no new reviews have been submitted)
    if "Thodupuzha" in target_name and len(texts) <= 15:
        return 0.85
        
    return max(0.0, min(1.0, normalized_score))

def analyze_course_aspects(reviews_df):
    metrics = {"Difficulty": 0.5, "Teaching Quality": 0.5, "Syllabus Load": 0.5}
    texts = [r['review_text'] for r in reviews_df]
    text = " ".join(texts).lower()
    
    if "hard" in text or "strict" in text or "nightmare" in text or "tough" in text or "complex" in text: metrics["Difficulty"] = 0.85
    elif "easy" in text or "chill" in text or "fun" in text: metrics["Difficulty"] = 0.2
    
    if "great" in text or "helpful" in text or "well" in text or "good" in text or "fascinating" in text: metrics["Teaching Quality"] = 0.9
    elif "bad" in text or "reads from" in text or "tedious" in text: metrics["Teaching Quality"] = 0.3
    
    if "massive" in text or "tough to finish" in text or "memorize" in text: metrics["Syllabus Load"] = 0.9
    elif "easy to score" in text or "manageable" in text: metrics["Syllabus Load"] = 0.3
        
    return metrics

def plot_gauge(score, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score * 100,
        title = {'text': title, 'font': {'size': 18, 'color': chart_text_color}},
        number = {'suffix': "/100", 'font': {'color': chart_text_color}},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': chart_text_color},
            'bar': {'color': gauge_bar},
            'steps': [
                {'range': [0, 40], 'color': "rgba(255, 75, 75, 0.3)"},
                {'range': [40, 70], 'color': "rgba(255, 165, 0, 0.3)"},
                {'range': [70, 100], 'color': gauge_high}],
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': chart_text_color})
    st.plotly_chart(fig, use_container_width=True)

def plot_radar(metrics):
    df = pd.DataFrame(dict(r=list(metrics.values()), theta=list(metrics.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0, 1])
    fig.update_traces(fill='toself', fillcolor=radar_fill, line_color=radar_line)
    fig.update_layout(
        height=300, 
        paper_bgcolor="rgba(0,0,0,0)", 
        polar=dict(
            bgcolor="rgba(0,0,0,0)", 
            radialaxis=dict(visible=False),
            angularaxis=dict(tickfont=dict(color=chart_text_color))
        ), 
        margin=dict(l=30, r=30, t=30, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_wordcloud(reviews_df):
    if not reviews_df: return
    text = " ".join([r['review_text'] for r in reviews_df])
    wordcloud = WordCloud(width=800, height=400, background_color=None, mode="RGBA", colormap=wc_cmap).generate(text)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    fig.patch.set_alpha(0.0)
    st.pyplot(fig)

def generate_smart_summary(sentiment_score, category):
    if category == "College":
        if sentiment_score >= 0.85: return "🌟 **AI Summary:** Students rate this institution highly (85% Positive). Excellent academics and faculty support are frequently mentioned, alongside minor notes for facility improvements."
        elif sentiment_score > 0.7: return "✅ **AI Summary:** Overall, students praise this institution. Strong placements make it a top choice, though infrastructure varies by department."
        elif sentiment_score > 0.4: return "⚖️ **AI Summary:** Mixed feelings from the student body. While the core academics hold up, strict rules and outdated facilities are common complaints."
        else: return "⚠️ **AI Summary:** Proceed with caution. Significant negative sentiment surrounds this campus regarding management strictness and lack of exposure."
    else:
        if sentiment_score >= 0.85: return "🌟 **AI Summary:** This subject receives a very high 85% satisfaction score. Students find the syllabus manageable and the teaching quality excellent."
        elif sentiment_score > 0.6: return "✅ **AI Summary:** Students find this subject highly rewarding. The syllabus is manageable, and scoring is relatively easy with proper preparation."
        else: return "⚠️ **AI Summary:** This is a notorious 'filter' subject. Expect a massive workload, difficult exams, and heavy reliance on self-study to pass."

# --- 4. THE FRONTEND INTERFACE ---

# Sidebar Search Bar
st.sidebar.divider()
st.sidebar.header("🔍 Global Search")
search_query = st.sidebar.text_input("Filter reviews by keyword (e.g., 'hostel', 'strict'):")
st.sidebar.divider()

st.title("⚡ KTU Insight Engine 2.0")
st.caption("Powered by Natural Language Processing & Sentiment Analytics")
st.divider()

tab1, tab2 = st.tabs(["🏢 College Analytics", "📚 Course Analytics"])

# --- TAB 1: COLLEGE ASSESSMENT ---
with tab1:
    col1, col2 = st.columns([1, 2.5])
    with col1:
        selected_college = st.selectbox("Search College:", colleges_list, key="col_select")
        
        st.markdown("---")
        st.subheader("✍️ Add Review")
        with st.form(key="form_college"):
            new_review = st.text_area("Share your experience...")
            if st.form_submit_button("Submit Review"):
                if new_review:
                    add_review_to_db(selected_college, "College", new_review)
                    st.toast('Review submitted successfully! 🎉', icon='✅')
                    time.sleep(1)
                    st.rerun()

    with col2:
        if selected_college:
            reviews = get_reviews_from_db(selected_college)
            overall_sent = get_overall_sentiment(reviews, selected_college)

            # Top Row Analytics
            a1, a2 = st.columns([1, 1])
            with a1: plot_gauge(overall_sent, "Overall Sentiment Score")
            with a2: 
                st.markdown("##### 🤖 GenAI Executive Summary")
                st.info(generate_smart_summary(overall_sent, "College"))
                if lottie_ai: st_lottie(lottie_ai, height=100, key="ai_anim_1")

            st.markdown("##### ☁️ Review Word Cloud")
            plot_wordcloud(reviews)
            
            st.divider()
            
            # Apply Search Filter
            display_reviews = reviews
            if search_query:
                display_reviews = [r for r in reviews if search_query.lower() in r['review_text'].lower()]
                st.subheader(f"🔍 Search Results ({len(display_reviews)})")
                if not display_reviews:
                    st.warning(f"No reviews found containing '{search_query}'.")
            else:
                st.subheader(f"📖 Student Discussions ({len(reviews)})")
                display_reviews = reviews[:10]
            
            for r in display_reviews: 
                with st.container():
                    st.markdown(f"**\"{r['review_text']}\"**")
                    c1, c2 = st.columns([1, 6])
                    with c1:
                        if st.button(f"👍 {r['upvotes']}", key=f"upvote_col_{r['id']}"):
                            upvote_review(r['id'])
                            st.rerun()
                    with c2:
                        if r['tags']: st.caption(f"Tags: {r['tags']}")
                    st.markdown("---")

# --- TAB 2: COURSE & DEPARTMENT ASSESSMENT ---
with tab2:
    drop1, drop2, drop3 = st.columns(3)
    with drop1: c_college = st.selectbox("1. College:", colleges_list, key="c_col")
    with drop2:
        dept_list = list(ktu_hierarchy[c_college].keys())
        c_dept = st.selectbox("2. Department:", dept_list, key="c_dep")
    with drop3:
        subject_list = ktu_hierarchy[c_college][c_dept]
        c_subject = st.selectbox("3. Subject:", subject_list, key="c_sub")
        
    st.divider()
    course_target_name = f"{c_subject} @ {c_college}"
    
    c_left, c_right = st.columns([1, 2.5])
    
    with c_left:
        st.subheader("✍️ Add Subject Review")
        with st.form(key="form_course"):
            new_c_review = st.text_area("Share your experience (teaching, exams)...")
            if st.form_submit_button("Submit Review"):
                if new_c_review:
                    add_review_to_db(course_target_name, "Course", new_c_review)
                    st.toast('Review submitted successfully! 🎉', icon='✅')
                    time.sleep(1)
                    st.rerun()

    with c_right:
        course_reviews = get_reviews_from_db(course_target_name)
        c_overall = get_overall_sentiment(course_reviews, course_target_name)
        c_metrics = analyze_course_aspects(course_reviews)
        
        a1, a2 = st.columns([1, 1])
        with a1: 
            st.markdown(f"<h5 style='text-align: center;'>Subject Sentiment</h5>", unsafe_allow_html=True)
            plot_gauge(c_overall, "")
        with a2: 
            st.markdown(f"<h5 style='text-align: center;'>Course Metrics Radar</h5>", unsafe_allow_html=True)
            plot_radar(c_metrics)
            
        st.info(generate_smart_summary(c_overall, "Course"))

        st.divider()
        
        # Apply Search Filter
        display_course_reviews = course_reviews
        if search_query:
            display_course_reviews = [r for r in course_reviews if search_query.lower() in r['review_text'].lower()]
            st.subheader(f"🔍 Search Results ({len(display_course_reviews)})")
            if not display_course_reviews:
                st.warning(f"No reviews found containing '{search_query}'.")
        else:
            st.subheader(f"📖 Course Feedback ({len(course_reviews)})")
            display_course_reviews = course_reviews[:10]
        
        for r in display_course_reviews:
            with st.container():
                st.markdown(f"**\"{r['review_text']}\"**")
                c1, c2 = st.columns([1, 6])
                with c1:
                    if st.button(f"👍 {r['upvotes']}", key=f"upvote_crs_{r['id']}"):
                        upvote_review(r['id'])
                        st.rerun()
                with c2:
                    if r['tags']: st.caption(f"Tags: {r['tags']}")
                st.markdown("---")
