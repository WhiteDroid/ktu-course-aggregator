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
if 'last_submit_time' not in st.session_state:
    st.session_state.last_submit_time = 0.0 

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
    st.session_state.last_rotation_time = time.time() # Reset timer on manual toggle
    st.rerun()

# --- 🪟 THEME DICTIONARIES (GLASSMORPHISM & PERSONA FONTS) ---
if st.session_state.light_theme:
    idx = st.session_state.theme_cycle_idx
    if idx == 0:
        # 🌸 1. INNOCENT YOUNG GIRL
        t = {"app_bg": "radial-gradient(circle at top left, #FFF8F9, #FFE4E1)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#5D4E52", "hero_grad": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 50%, #FFDAC1 100%)", "hero_shadow": "0 15px 30px -5px rgba(255, 182, 193, 0.3)", "hero_border": "#FFD1DC", "subtitle": "#FFF0F5", "card_bg": "rgba(255, 255, 255, 0.65)", "card_border": "rgba(255, 228, 225, 0.5)", "card_h_border": "#FFD1DC", "card_h_shadow": "0 15px 35px -5px rgba(255, 182, 193, 0.3)", "pill_bg": "rgba(255, 240, 245, 0.8)", "pill_txt": "#FF69B4", "gauge_bar": "#FF69B4", "wc_cmap": "spring", "comp_colors": ["#FF69B4", "#FFA9D1", "#FFDAC1"], "font": "'Quicksand', sans-serif"}
    elif idx == 1:
        # 🍷 2. ELEGANT YOUNG LADY
        t = {"app_bg": "radial-gradient(circle at top right, #FCF9F9, #EAD8DC)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#4A4040", "hero_grad": "linear-gradient(135deg, #DCA7B8 0%, #D49BAA 50%, #CE8E9E 100%)", "hero_shadow": "0 15px 30px -5px rgba(212, 155, 170, 0.25)", "hero_border": "#E6BCCD", "subtitle": "#FFF0F2", "card_bg": "rgba(255, 255, 255, 0.65)", "card_border": "rgba(245, 235, 235, 0.5)", "card_h_border": "#EAD8DC", "card_h_shadow": "0 15px 35px -5px rgba(212, 155, 170, 0.2)", "pill_bg": "rgba(253, 244, 246, 0.8)", "pill_txt": "#9A7480", "gauge_bar": "#D49BAA", "wc_cmap": "PuRd", "comp_colors": ["#D49BAA", "#A39BA8", "#E3B5A4"], "font": "'Playfair Display', serif"}
    elif idx == 2:
        # 💋 3. HOT & SEXY LADY
        t = {"app_bg": "radial-gradient(circle at bottom left, #FFF5F7, #FFCCD5)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#4A1525", "hero_grad": "linear-gradient(135deg, #FF0055 0%, #D50032 50%, #8A0030 100%)", "hero_shadow": "0 15px 30px -5px rgba(213, 0, 50, 0.3)", "hero_border": "#FFB3C6", "subtitle": "#FFD1DC", "card_bg": "rgba(255, 255, 255, 0.7)", "card_border": "rgba(255, 228, 232, 0.5)", "card_h_border": "#FFCCD5", "card_h_shadow": "0 15px 35px -5px rgba(213, 0, 50, 0.25)", "pill_bg": "rgba(255, 240, 243, 0.8)", "pill_txt": "#D50032", "gauge_bar": "#D50032", "wc_cmap": "Reds", "comp_colors": ["#D50032", "#FF0055", "#8A0030"], "font": "'Montserrat', sans-serif"}
    else:
        # 👑 4. SEXY GODDESS
        t = {"app_bg": "radial-gradient(circle at center, #FFF7F8, #FADADD)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#3A101E", "hero_grad": "linear-gradient(135deg, #C70039 0%, #900C3F 50%, #581845 100%)", "hero_shadow": "0 15px 30px -5px rgba(144, 12, 63, 0.35)", "hero_border": "#FFC300", "subtitle": "#FFC300", "card_bg": "rgba(255, 255, 255, 0.7)", "card_border": "rgba(250, 218, 221, 0.5)", "card_h_border": "#FFC300", "card_h_shadow": "0 15px 35px -5px rgba(144, 12, 63, 0.25)", "pill_bg": "rgba(255, 240, 243, 0.8)", "pill_txt": "#900C3F", "gauge_bar": "#C70039", "wc_cmap": "inferno", "comp_colors": ["#C70039", "#FFC300", "#900C3F"], "font": "'Cinzel', serif"}
else:
    d_idx = st.session_state.dark_theme_cycle_idx
    if d_idx == 0:
        # 🕵️‍♂️ 1. THE CYBERPUNK ASSASSIN
        t = {"app_bg": "radial-gradient(circle at top left, #0B0F19, #022C22)", "sidebar_bg": "rgba(17, 24, 39, 0.8)", "text": "#F3F4F6", "hero_grad": "linear-gradient(135deg, #022C22 0%, #0B0F19 50%, #111827 100%)", "hero_shadow": "0 0 40px -10px rgba(16, 185, 129, 0.15)", "hero_border": "rgba(16, 185, 129, 0.3)", "subtitle": "#34D399", "card_bg": "rgba(17, 24, 39, 0.65)", "card_border": "rgba(31, 41, 55, 0.5)", "card_h_border": "#374151", "card_h_shadow": "0 15px 35px -5px rgba(16, 185, 129, 0.2)", "pill_bg": "rgba(16, 185, 129, 0.1)", "pill_txt": "#34D399", "gauge_bar": "#10B981", "wc_cmap": "viridis", "comp_colors": ["#10B981", "#3B82F6", "#F43F5E"], "font": "'Orbitron', sans-serif"}
    elif d_idx == 1:
        # 🥃 2. THE STEALTH OPERATIVE
        t = {"app_bg": "radial-gradient(circle at bottom right, #0A0A0A, #451A03)", "sidebar_bg": "rgba(18, 18, 18, 0.8)", "text": "#E5E7EB", "hero_grad": "linear-gradient(135deg, #451A03 0%, #0A0A0A 50%, #121212 100%)", "hero_shadow": "0 0 40px -10px rgba(245, 158, 11, 0.15)", "hero_border": "rgba(245, 158, 11, 0.3)", "subtitle": "#FBBF24", "card_bg": "rgba(18, 18, 18, 0.65)", "card_border": "rgba(39, 39, 42, 0.5)", "card_h_border": "#3F3F46", "card_h_shadow": "0 15px 35px -5px rgba(245, 158, 11, 0.2)", "pill_bg": "rgba(245, 158, 11, 0.1)", "pill_txt": "#FBBF24", "gauge_bar": "#F59E0B", "wc_cmap": "copper", "comp_colors": ["#F59E0B", "#B45309", "#78350F"], "font": "'Rajdhani', sans-serif"}
    elif d_idx == 2:
        # 🌊 3. THE DEEP SEA COMMANDER
        t = {"app_bg": "radial-gradient(circle at center, #020617, #082F49)", "sidebar_bg": "rgba(15, 23, 42, 0.8)", "text": "#E0F2FE", "hero_grad": "linear-gradient(135deg, #082F49 0%, #020617 50%, #0F172A 100%)", "hero_shadow": "0 0 40px -10px rgba(14, 165, 233, 0.15)", "hero_border": "rgba(14, 165, 233, 0.3)", "subtitle": "#38BDF8", "card_bg": "rgba(15, 23, 42, 0.65)", "card_border": "rgba(30, 41, 59, 0.5)", "card_h_border": "#334155", "card_h_shadow": "0 15px 35px -5px rgba(14, 165, 233, 0.2)", "pill_bg": "rgba(14, 165, 233, 0.1)", "pill_txt": "#38BDF8", "gauge_bar": "#0EA5E9", "wc_cmap": "Blues", "comp_colors": ["#0EA5E9", "#0284C7", "#0369A1"], "font": "'Exo 2', sans-serif"}
    else:
        # 🔥 4. THE FORGE MASTER
        t = {"app_bg": "radial-gradient(circle at top, #050505, #450A0A)", "sidebar_bg": "rgba(17, 17, 17, 0.8)", "text": "#FECACA", "hero_grad": "linear-gradient(135deg, #450A0A 0%, #050505 50%, #111111 100%)", "hero_shadow": "0 0 40px -10px rgba(220, 38, 38, 0.15)", "hero_border": "rgba(220, 38, 38, 0.3)", "subtitle": "#F87171", "card_bg": "rgba(17, 17, 17, 0.65)", "card_border": "rgba(38, 38, 38, 0.5)", "card_h_border": "#3F3F46", "card_h_shadow": "0 15px 35px -5px rgba(220, 38, 38, 0.2)", "pill_bg": "rgba(220, 38, 38, 0.1)", "pill_txt": "#F87171", "gauge_bar": "#DC2626", "wc_cmap": "Reds", "comp_colors": ["#DC2626", "#991B1B", "#7F1D1D"], "font": "'Teko', sans-serif"}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Exo+2:wght@400;600&family=Montserrat:wght@400;600&family=Orbitron:wght@400;700&family=Playfair+Display:wght@400;700&family=Quicksand:wght@400;600&family=Rajdhani:wght@400;600&family=Teko:wght@400;600&display=swap');
    .stApp, h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, div {{ font-family: {t['font']} !important; }}
    .stApp {{ background: {t['app_bg']} !important; background-attachment: fixed !important; color: {t['text']} !important; }}
    [data-testid="stSidebar"] {{ background-color: {t['sidebar_bg']} !important; backdrop-filter: blur(20px); }}
    .hero-container {{ background: {t['hero_grad']}; color: #FFFFFF !important; padding: 3.5rem 2rem; border-radius: 1rem; text-align: center; margin-bottom: 2.5rem; margin-top: -2rem; box-shadow: {t['hero_shadow']}; border: 1px solid {t['hero_border']}; }}
    div[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {{ background: {t['card_bg']} !important; backdrop-filter: blur(16px); border: 1px solid {t['card_border']} !important; border-radius: 1rem !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ transition: all 0.4s ease !important; }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{ transform: perspective(1000px) rotateX(2deg) rotateY(-2deg) scale(1.02) !important; box-shadow: {t['card_h_shadow']} !important; }}
    .tag-pill {{ background-color: {t['pill_bg']}; color: {t['pill_txt']}; padding: 0.25rem 0.8rem; border-radius: 9999px; font-size: 0.7rem; border: 1px solid {t['card_border']}; }}
</style>
""", unsafe_allow_html=True)

chart_text_color, gauge_bar, radar_grid, wc_cmap, comp_colors = t['text'], t['gauge_bar'], t['card_border'], t['wc_cmap'], t['comp_colors']
avatar_style = "micah" if st.session_state.light_theme else "bottts"
step_red, step_yellow, step_green = "rgba(200,0,0,0.1)", "rgba(200,200,0,0.1)", "rgba(0,200,0,0.1)"

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
    "University College of Engineering Thodupuzha (UCE)": standard_departments, "Model Engineering College (MEC)": standard_departments, "College of Engineering Trivandrum (CET)": standard_departments, "TKM College of Engineering, Kollam (TKM)": standard_departments, "Rajiv Gandhi Institute of Technology (RIT), Kottayam": standard_departments, "Government Engineering College, Thrissur (GEC)": standard_departments, "Muthoot Institute of Technology and Science (MITS)": standard_departments, "Rajagiri School of Engineering & Technology (RSET)": standard_departments, "Mar Athanasius College of Engineering (MACE)": standard_departments, "Federal Institute of Science and Technology (FISAT)": standard_departments
}
colleges_list = list(ktu_hierarchy.keys())
college_coords = {
    "University College of Engineering Thodupuzha (UCE)": (9.8450, 76.7450), "Model Engineering College (MEC)": (10.0284, 76.3285), "College of Engineering Trivandrum (CET)": (8.5456, 76.9063), "TKM College of Engineering, Kollam (TKM)": (8.9100, 76.6316), "Rajiv Gandhi Institute of Technology (RIT), Kottayam": (9.5534, 76.6179), "Government Engineering College, Thrissur (GEC)": (10.5540, 76.2230), "Muthoot Institute of Technology and Science (MITS)": (9.9482, 76.3980), "Rajagiri School of Engineering & Technology (RSET)": (10.0102, 76.3653), "Mar Athanasius College of Engineering (MACE)": (10.0543, 76.6186), "Federal Institute of Science and Technology (FISAT)": (10.2312, 76.4087)
}

# --- 2. DATABASE ENGINE ---
DB_NAME = "ktu_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, target_name TEXT, category TEXT, review_text TEXT, upvotes INTEGER DEFAULT 0, tags TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS replies (id INTEGER PRIMARY KEY AUTOINCREMENT, review_id INTEGER, reply_text TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

def add_review_to_db(target_name, category, review_text):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    tags = "💼 Placements" if "placement" in review_text.lower() else "✅ Feedback"
    c.execute("INSERT INTO reviews (target_name, category, review_text, upvotes, tags) VALUES (?, ?, ?, ?, ?)", (target_name, category, review_text, 0, tags))
    conn.commit(); conn.close()

def get_reviews_from_db(target_name, sort_by="Most Upvoted"):
    conn = sqlite3.connect(DB_NAME)
    order = "ORDER BY id DESC" if sort_by == "Newest" else "ORDER BY upvotes DESC, id DESC"
    df = pd.read_sql_query(f"SELECT * FROM reviews WHERE target_name=? {order}", conn, params=(target_name,))
    conn.close(); return df.to_dict('records')

def get_replies(review_id):
    conn = sqlite3.connect(DB_NAME); df = pd.read_sql_query("SELECT * FROM replies WHERE review_id=? ORDER BY id ASC", conn, params=(review_id,))
    conn.close(); return df.to_dict('records')

def seed_initial_data():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews")
    if c.fetchone()[0] == 0:
        seed_data = []
        for college in colleges_list:
            for _ in range(10):
                text = "Excellent academics and campus." if random.random() > 0.5 else "Good tech culture but strict."
                ts = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
                seed_data.append((college, "College", text, random.randint(0, 50), "✅ Verified", ts))
        c.executemany("INSERT INTO reviews (target_name, category, review_text, upvotes, tags, created_at) VALUES (?, ?, ?, ?, ?, ?)", seed_data)
        conn.commit(); conn.close()

init_db(); seed_initial_data()

# --- 3. ANALYTICS ---
def get_overall_sentiment(reviews_df):
    if not reviews_df: return 0.5
    texts = [r['review_text'] for r in reviews_df]
    return (TextBlob(" ".join(texts)).sentiment.polarity + 1) / 2

# --- 4. INTERFACE ---
st.sidebar.header("🔍 Controls")
search_query = st.sidebar.text_input("Filter Reviews:")
sort_option = st.sidebar.selectbox("Sort:", ["Most Upvoted", "Newest"])

st.markdown(f"""<div class="hero-container"><div class="hero-title">⚡ KTU Insight Engine <span style="font-size: 0.35em; font-weight: 600; vertical-align: super; opacity: 0.85; margin-left: 4px;">2.0</span></div><div class="hero-subtitle">Interactive AI Dashboard & Geospatial Heatmap</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🏢 Colleges", "📚 Courses", "⚖️ Versus", "🗺️ Heatmap"])

with tab1:
    c1, c2 = st.columns([1, 2.5])
    with c1:
        sel_col = st.selectbox("Select College:", colleges_list)
        with st.form("rev_form"):
            rev_txt = st.text_area("Your Review:", max_chars=800)
            if st.form_submit_button("Submit"):
                add_review_to_db(sel_col, "College", rev_txt); st.rerun()
    with c2:
        reviews = get_reviews_from_db(sel_col, sort_option)
        s_score = get_overall_sentiment(reviews)
        plot_gauge(s_score, f"{sel_col.split()[0]} Sentiment")
        for r in reviews[:10]:
            with st.container(border=True):
                av = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed={r['id']}"
                st.markdown(f"<div style='display:flex;align-items:center;margin-bottom:10px;'><img src='{av}' style='width:45px;margin-right:15px;'><b>Insider #{r['id']}</b></div><i>\"{r['review_text']}\"</i>", unsafe_allow_html=True)

with tab2:
    d1, d2, d3 = st.columns(3)
    c_c = d1.selectbox("College:", colleges_list, key="c2")
    c_d = d2.selectbox("Dept:", list(ktu_hierarchy[c_c].keys()))
    c_s = d3.selectbox("Subject:", ktu_hierarchy[c_c][c_d])
    # Core course logic here...
    st.info(f"Analyzing: {c_s}")

with tab3:
    picks = st.multiselect("Compare Entities:", colleges_list, max_selections=3)
    if len(picks) >= 2:
        scores = {p: int(get_overall_sentiment(get_reviews_from_db(p))*100) for p in picks}
        st.plotly_chart(px.bar(x=list(scores.keys()), y=list(scores.values()), color=list(scores.keys()), color_discrete_sequence=comp_colors))

with tab4:
    plot_geospatial_heatmap(colleges_list, st.session_state.light_theme)

def plot_gauge(score, title):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score*100, title={'text': title, 'font': {'color': chart_text_color}}, number={'font': {'color': chart_text_color}}, gauge={'axis': {'range': [0, 100], 'tickcolor': radar_grid}, 'bar': {'color': gauge_bar}}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': chart_text_color}, height=300)
    st.plotly_chart(fig, use_container_width=True)

def plot_geospatial_heatmap(colleges, is_light):
    map_data = []
    for col in colleges:
        lat, lon = college_coords.get(col, (10, 76))
        score = get_overall_sentiment(get_reviews_from_db(col)) * 100
        map_data.append({"College": col, "Lat": lat, "Lon": lon, "Score": score})
    df = pd.DataFrame(map_data)
    fig = px.scatter_mapbox(df, lat="Lat", lon="Lon", color="Score", size="Score", hover_name="College", color_continuous_scale="Viridis", zoom=6)
    fig.update_layout(mapbox_style="carto-positron" if is_light else "carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
