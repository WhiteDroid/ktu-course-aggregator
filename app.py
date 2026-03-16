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
ROTATION_INTERVAL = 150  # 2.5 minutes

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

# 🤖 BACKGROUND HEARTBEAT
current_time = time.time()
if current_time - st.session_state.last_rotation_time > ROTATION_INTERVAL:
    if st.session_state.light_theme:
        st.session_state.theme_cycle_idx = (st.session_state.theme_cycle_idx + 1) % 4
    else:
        st.session_state.dark_theme_cycle_idx = (st.session_state.dark_theme_cycle_idx + 1) % 4
    st.session_state.last_rotation_time = current_time
    st.rerun()

# 🔥 BRAND LOGO 🔥
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1162/1162803.png", width=55)
st.sidebar.markdown("## KTU Insight")
st.sidebar.divider()

st.sidebar.markdown("### 🌗 Appearance")
theme_toggle = st.sidebar.toggle("Switch to Light Mode", value=st.session_state.light_theme)

if theme_toggle != st.session_state.light_theme:
    if theme_toggle: st.session_state.theme_cycle_idx = (st.session_state.theme_cycle_idx + 1) % 4
    else: st.session_state.dark_theme_cycle_idx = (st.session_state.dark_theme_cycle_idx + 1) % 4
    st.session_state.light_theme = theme_toggle
    st.session_state.last_rotation_time = time.time()
    st.rerun()

# --- 🪟 THEME DICTIONARIES (WITH ADAPTIVE TYPOGRAPHY) ---
if st.session_state.light_theme:
    idx = st.session_state.theme_cycle_idx
    if idx == 0: # 🌸 Innocent
        t = {"app_bg": "radial-gradient(circle at 10% 20%, #FFF8F9 0%, #FFE4E1 90%)", "sidebar_bg": "rgba(255, 255, 255, 0.7)", "text": "#5D4E52", "hero_grad": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 100%)", "card_bg": "rgba(255, 255, 255, 0.5)", "card_border": "rgba(255, 182, 193, 0.3)", "glow": "#FFB6C1", "font": "'Quicksand', sans-serif", "weight": "300", "btn": "#FF69B4"}
    elif idx == 1: # 🍷 Elegant
        t = {"app_bg": "radial-gradient(circle at 50% 50%, #FCF9F9 0%, #EAD8DC 100%)", "sidebar_bg": "rgba(255, 255, 255, 0.7)", "text": "#4A4040", "hero_grad": "linear-gradient(135deg, #DCA7B8 0%, #CE8E9E 100%)", "card_bg": "rgba(255, 255, 255, 0.5)", "card_border": "rgba(212, 155, 170, 0.3)", "glow": "#D49BAA", "font": "'Playfair Display', serif", "weight": "400", "btn": "#9A7480"}
    elif idx == 2: # 💋 Hot & Sexy
        t = {"app_bg": "radial-gradient(circle at bottom left, #FFF5F7 0%, #FFCCD5 100%)", "sidebar_bg": "rgba(255, 255, 255, 0.7)", "text": "#4A1525", "hero_grad": "linear-gradient(135deg, #FF0055 0%, #8A0030 100%)", "card_bg": "rgba(255, 255, 255, 0.5)", "card_border": "rgba(213, 0, 50, 0.2)", "glow": "#FF0055", "font": "'Montserrat', sans-serif", "weight": "600", "btn": "#D50032"}
    else: # 👑 Goddess
        t = {"app_bg": "radial-gradient(circle at center, #FFF7F8 0%, #FADADD 100%)", "sidebar_bg": "rgba(255, 255, 255, 0.7)", "text": "#3A101E", "hero_grad": "linear-gradient(135deg, #C70039 0%, #581845 100%)", "card_bg": "rgba(255, 255, 255, 0.5)", "card_border": "rgba(255, 195, 0, 0.3)", "glow": "#FFC300", "font": "'Cinzel', serif", "weight": "700", "btn": "#900C3F"}
else:
    d_idx = st.session_state.dark_theme_cycle_idx
    if d_idx == 0: # 🕵️‍♂️ Cyberpunk
        t = {"app_bg": "radial-gradient(circle at top left, #0B0F19, #022C22)", "sidebar_bg": "rgba(17, 24, 39, 0.7)", "text": "#F3F4F6", "hero_grad": "linear-gradient(135deg, #022C22 0%, #111827 100%)", "card_bg": "rgba(17, 24, 39, 0.5)", "card_border": "rgba(16, 185, 129, 0.3)", "glow": "#10B981", "font": "'Orbitron', sans-serif", "weight": "400", "btn": "#10B981"}
    elif d_idx == 1: # 🥃 Stealth
        t = {"app_bg": "radial-gradient(circle at bottom right, #0A0A0A, #451A03)", "sidebar_bg": "rgba(18, 18, 18, 0.7)", "text": "#E5E7EB", "hero_grad": "linear-gradient(135deg, #451A03 0%, #121212 100%)", "card_bg": "rgba(18, 18, 18, 0.5)", "card_border": "rgba(245, 158, 11, 0.3)", "glow": "#F59E0B", "font": "'Rajdhani', sans-serif", "weight": "600", "btn": "#F59E0B"}
    elif d_idx == 2: # 🌊 Deep Sea
        t = {"app_bg": "radial-gradient(circle at center, #020617, #082F49)", "sidebar_bg": "rgba(15, 23, 42, 0.7)", "text": "#E0F2FE", "hero_grad": "linear-gradient(135deg, #082F49 0%, #0F172A 100%)", "card_bg": "rgba(15, 23, 42, 0.5)", "card_border": "rgba(14, 165, 233, 0.3)", "glow": "#0EA5E9", "font": "'Exo 2', sans-serif", "weight": "500", "btn": "#0EA5E9"}
    else: # 🔥 Forge Master
        t = {"app_bg": "radial-gradient(circle at top, #050505, #450A0A)", "sidebar_bg": "rgba(17, 17, 17, 0.7)", "text": "#FECACA", "hero_grad": "linear-gradient(135deg, #450A0A 0%, #111111 100%)", "card_bg": "rgba(17, 17, 17, 0.5)", "card_border": "rgba(220, 38, 38, 0.3)", "glow": "#DC2626", "font": "'Teko', sans-serif", "weight": "800", "btn": "#DC2626"}

# 🫧 ✨ 🍱 DYNAMIC CSS INJECTION
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Exo+2:wght@400;600&family=Montserrat:wght@400;600&family=Orbitron:wght@400;700&family=Playfair+Display:wght@400;700&family=Quicksand:wght@300;600&family=Rajdhani:wght@400;600&family=Teko:wght@400;800&display=swap');
    
    .stApp, h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{ font-family: {t['font']} !important; font-weight: {t['weight']} !important; }}
    .stApp {{ background: {t['app_bg']} !important; background-attachment: fixed !important; color: {t['text']} !important; }}
    
    /* 🍱 BENTO GLASS CARDS WITH SHIMMER */
    div[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"], .bento-tile {{ 
        background: {t['card_bg']} !important; 
        backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid {t['card_border']} !important; 
        border-radius: 1.5rem !important; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }}

    /* ✨ LIGHT LEAK ANIMATION */
    [data-testid="stVerticalBlockBorderWrapper"]::before {{
        content: ""; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(transparent, {t['glow']}, transparent 30%);
        animation: rotateGlow 6s linear infinite; opacity: 0.15;
    }}
    @keyframes rotateGlow {{ 100% {{ transform: rotate(360deg); }} }}

    /* 🫧 SQUISHY BUTTONS */
    .stButton button {{
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 1rem !important;
    }}
    .stButton button:active {{ transform: scale(0.92) !important; }}
    
    .hero-container {{ background: {t['hero_grad']}; color: #FFFFFF !important; padding: 3rem 2rem; border-radius: 1.5rem; text-align: center; margin-bottom: 2rem; box-shadow: 0 10px 40px -10px {t['glow']}55; border: 1px solid {t['glow']}44; }}
</style>
""", unsafe_allow_html=True)

# --- 1. DATA & DB (RESTORED) ---
DB_NAME = "ktu_reviews.db"
def init_db():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, target_name TEXT, category TEXT, review_text TEXT, upvotes INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

init_db()

standard_departments = {
    "Artificial Intelligence (AI & DS)": ["AD301: Deep Learning", "AD305: NLP"],
    "Computer Science (CSE)": ["CS301: TOC", "CS302: Algorithms"]
}
ktu_hierarchy = {
    "University College of Engineering Thodupuzha (UCE)": standard_departments,
    "Model Engineering College (MEC)": standard_departments,
    "College of Engineering Trivandrum (CET)": standard_departments
}
colleges_list = list(ktu_hierarchy.keys())
college_coords = {"UCE": (9.84, 76.74), "MEC": (10.02, 76.32), "CET": (8.54, 76.90)}

# --- 2. LOGIC ---
def get_sentiment(texts):
    if not texts: return 0.5
    return (TextBlob(" ".join(texts)).sentiment.polarity + 1) / 2

# --- 3. THE INTERFACE (BENTO LAYOUT) ---
st.sidebar.header("🔍 Controls")
search = st.sidebar.text_input("Filter Reviews:")

st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">
            ⚡ KTU Insight Engine <span style="font-size: 0.35em; font-weight: 600; vertical-align: super; opacity: 0.85; margin-left: 4px;">2.0</span>
        </div>
        <div class="hero-subtitle">The Spatial Data Experience for KTU Students</div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏢 Analytics Hub", "⚖️ Battle Arena", "🗺️ Heatmap"])

with tab1:
    # 🍱 BENTO GRID ROW 1
    sel = st.selectbox("Select Target:", colleges_list)
    
    b1, b2 = st.columns([1.5, 2.5])
    with b1:
        # TILE: Sentiment Gauge
        with st.container(border=True):
            st.markdown("#### 🌡️ Live Vibe")
            score = 0.85 # Placeholder
            fig = go.Figure(go.Indicator(mode="gauge+number", value=score*100, gauge={'bar':{'color':t['btn']}, 'axis':{'range':[0,100]}}))
            fig.update_layout(height=200, paper_bgcolor="rgba(0,0,0,0)", font={'color':t['text']})
            st.plotly_chart(fig, use_container_width=True)
            
    with b2:
        # TILE: Sentiment Trend
        with st.container(border=True):
            st.markdown("#### 📈 Reputation Pulse")
            df_trend = pd.DataFrame({'Date': pd.date_range(start='1/1/2025', periods=5, freq='M'), 'Score': [70, 75, 72, 85, 88]})
            fig2 = px.line(df_trend, x='Date', y='Score')
            fig2.update_traces(line_color=t['btn'], line_width=4)
            fig2.update_layout(height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig2, use_container_width=True)

    # 🍱 BENTO GRID ROW 2
    st.markdown("#### 📖 Student Voices")
    v1, v2, v3 = st.columns([1,1,1])
    # Mapping avatars & reviews into Bento Columns
    for i in range(3):
        with [v1, v2, v3][i]:
            with st.container(border=True):
                av = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed={i+10}"
                st.markdown(f"<img src='{av}' style='width:50px; margin-bottom:10px;'>", unsafe_allow_html=True)
                st.write("The faculty here is top-notch and placements are peak!")
                st.button(f"👍 {random.randint(1,50)}", key=f"b_{i}")

with tab2:
    st.markdown("### ⚔️ Reputation Battle")
    picks = st.multiselect("Select 2-3 Colleges:", colleges_list, max_selections=3)
    if len(picks) >= 2:
        with st.container(border=True):
            scores = {p: random.randint(60, 95) for p in picks}
            st.plotly_chart(px.bar(x=list(scores.keys()), y=list(scores.values()), color_discrete_sequence=t['comp_colors']))

with tab3:
    st.markdown("### 🗺️ Geospatial Pulse")
    with st.container(border=True):
        df_map = pd.DataFrame({'lat': [9.84, 10.02, 8.54], 'lon': [76.74, 76.32, 76.90], 'score': [85, 90, 70]})
        fig_map = px.scatter_mapbox(df_map, lat="lat", lon="lon", color="score", size="score", size_max=20, zoom=6)
        fig_map.update_layout(mapbox_style="carto-positron" if st.session_state.light_theme else "carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
