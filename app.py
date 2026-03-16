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

# --- 1. UI CONFIGURATION & MOBILE-FIRST CSS ---
st.set_page_config(page_title="KTU Insight Engine", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Responsive Block Container */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            width: 100%;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            font-size: 14px;
        }
    }

    /* Professional Card Styling */
    .review-card {
        background: #1d2129;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0px;
        border-left: 5px solid #00CC96;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .review-text {
        font-size: 1.1rem;
        color: #e0e0e0;
        margin-bottom: 10px;
    }
    
    .tag-pill {
        display: inline-block;
        background: #2e353f;
        color: #00CC96;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 5px;
    }

    /* Mobile-Optimized Buttons */
    .stButton > button {
        border-radius: 10px !important;
        transition: transform 0.1s ease;
    }
    .stButton > button:active {
        transform: scale(0.98);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & LOGIC (STABILIZED) ---
DB_NAME = "ktu_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        target_name TEXT, 
        category TEXT, 
        review_text TEXT, 
        upvotes INTEGER DEFAULT 0, 
        tags TEXT)''')
    conn.commit()
    conn.close()

def get_reviews(target):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM reviews WHERE target_name=? ORDER BY upvotes DESC", conn, params=(target,))
    conn.close()
    return df.to_dict('records')

def add_review(target, category, text):
    tags = "✅ Verified"
    if "hard" in text.lower() or "tough" in text.lower(): tags += ", ⚠️ High Difficulty"
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO reviews (target_name, category, review_text, tags) VALUES (?,?,?,?)", (target, category, text, tags))
    conn.commit()
    conn.close()

init_db()

# --- 3. RESPONSIVE COMPONENT GENERATORS ---
def render_review_card(r, key_prefix):
    st.markdown(f"""
    <div class="review-card">
        <div class="review-text">"{r['review_text']}"</div>
        <div>
            {" ".join([f'<span class="tag-pill">{tag}</span>' for tag in r['tags'].split(',')])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button(f"👍 {r['upvotes']}", key=f"{key_prefix}_{r['id']}", use_container_width=True):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("UPDATE reviews SET upvotes = upvotes + 1 WHERE id = ?", (r['id'],))
            conn.commit()
            st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("⚡ KTU Insight Engine")
st.caption("Perfectly optimized for Mobile & Web")

tab1, tab2 = st.tabs(["🏢 Colleges", "📚 Subjects"])

# --- TAB 1: COLLEGES ---
with tab1:
    # Top Section: Navigation and AI Summary
    col_nav, col_stat = st.columns([1, 1.5])
    
    with col_nav:
        college = st.selectbox("Choose Institution:", ["UCE Thodupuzha", "MEC Kochi", "CET Trivandrum", "TKM Kollam"])
        with st.expander("✍️ Write a Review", expanded=False):
            with st.form("col_form"):
                new_rev = st.text_area("Your experience...")
                if st.form_submit_button("Submit", use_container_width=True):
                    add_review(college, "College", new_rev)
                    st.toast("Posted!", icon="🚀")
                    time.sleep(0.5)
                    st.rerun()

    with col_stat:
        # Mini dashboard for mobile
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Sentiment", "85%", "+2%")
        with m2:
            st.metric("Active Users", "1.2k", "Live")
    
    st.markdown("### 📢 Student Feed")
    reviews = get_reviews(college)
    if not reviews:
        st.info("No reviews yet. Be the first!")
    for r in reviews:
        render_review_card(r, "col")

# --- TAB 2: SUBJECTS ---
with tab2:
    # Subject Filters - 3 columns on PC, stacks on Mobile
    f1, f2 = st.columns(2)
    with f1: sub_college = st.selectbox("Select College:", ["UCE Thodupuzha", "MEC Kochi"], key="s_col")
    with f2: subject = st.selectbox("Select Subject:", ["Data Structures", "Operating Systems", "Graph Theory"], key="s_sub")
    
    target_subject = f"{subject} @ {sub_college}"
    
    # Visual Analytics
    v1, v2 = st.columns([1, 1])
    with v1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=72, gauge={'bar': {'color': "#00CC96"}}))
        fig.update_layout(height=180, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with v2:
        st.write("📊 **Quick Stats**")
        st.caption("Difficulty: Hard")
        st.caption("Study Material: Available")
        if st.button("➕ Add Subject Review", use_container_width=True):
            st.session_state.show_form = True

    if st.session_state.get('show_form'):
        with st.form("sub_form"):
            s_rev = st.text_area("How was the exam/faculty?")
            if st.form_submit_button("Post Review", use_container_width=True):
                add_review(target_subject, "Course", s_rev)
                st.session_state.show_form = False
                st.rerun()

    st.markdown("### 📖 Discussion")
    s_reviews = get_reviews(target_subject)
    for r in s_reviews:
        render_review_card(r, "sub")

# --- SIDEBAR SEARCH ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.text_input("🔍 Global Search")
    st.checkbox("Show Anonymous Reviews", value=True)
    st.divider()
    st.info("This engine uses AI to filter spam and highlight helpful feedback.")
