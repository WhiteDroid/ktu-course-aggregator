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

# --- AUTO-ROTATION ENGINE STATE ---
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

# 🕒 AUTO-ROTATE LOGIC (Checks every time the script runs)
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
    st.session_state.last_rotation_time = time.time() # Reset timer on manual switch
    st.rerun()

# --- 🪟 THEME DICTIONARIES (GLASSMORPHISM & PERSONA FONTS) ---
if st.session_state.light_theme:
    idx = st.session_state.theme_cycle_idx
    if idx == 0:
        # 🌸 1. INNOCENT YOUNG GIRL
        t = {"app_bg": "radial-gradient(circle at top left, #FFF8F9, #FFE4E1)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#5D4E52", "hero_grad": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 50%, #FFDAC1 100%)", "hero_shadow": "0 15px 30px -5px rgba(255, 182, 193, 0.3)", "hero_border": "#FFD1DC", "subtitle": "#FFF0F5", "form_bg": "rgba(255, 255, 255, 0.6)", "form_border": "rgba(255, 228, 225, 0.5)", "inp_bg": "rgba(255, 248, 249, 0.8)", "inp_border": "#FFD1DC", "focus": "#FFB6C1", "btn_grad": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 100%)", "btn_shadow": "rgba(255, 182, 193, 0.3)", "btn_h_shadow": "rgba(255, 182, 193, 0.5)", "card_bg": "rgba(255, 255, 255, 0.65)", "card_border": "rgba(255, 228, 225, 0.5)", "card_h_border": "#FFD1DC", "card_h_shadow": "0 15px 35px -5px rgba(255, 182, 193, 0.3)", "pill_bg": "rgba(255, 240, 245, 0.8)", "pill_txt": "#FF69B4", "pill_border": "#FFD1DC", "gauge_bar": "#FF69B4", "radar_fill": "rgba(255, 105, 180, 0.15)", "wc_cmap": "spring", "c_red": "rgba(255, 182, 193, 0.1)", "c_yel": "rgba(255, 182, 193, 0.2)", "c_grn": "rgba(255, 182, 193, 0.3)", "comp_colors": ["#FF69B4", "#FFA9D1", "#FFDAC1"], "font": "'Quicksand', sans-serif"}
    elif idx == 1:
        # 🍷 2. ELEGANT YOUNG LADY
        t = {"app_bg": "radial-gradient(circle at top right, #FCF9F9, #EAD8DC)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#4A4040", "hero_grad": "linear-gradient(135deg, #DCA7B8 0%, #D49BAA 50%, #CE8E9E 100%)", "hero_shadow": "0 15px 30px -5px rgba(212, 155, 170, 0.25)", "hero_border": "#E6BCCD", "subtitle": "#FFF0F2", "form_bg": "rgba(255, 255, 255, 0.6)", "form_border": "rgba(245, 235, 235, 0.5)", "inp_bg": "rgba(252, 249, 249, 0.8)", "inp_border": "#EAD8DC", "focus": "#D49BAA", "btn_grad": "linear-gradient(135deg, #DCA7B8 0%, #CE8E9E 100%)", "btn_shadow": "rgba(212, 155, 170, 0.3)", "btn_h_shadow": "rgba(212, 155, 170, 0.4)", "card_bg": "rgba(255, 255, 255, 0.65)", "card_border": "rgba(245, 235, 235, 0.5)", "card_h_border": "#EAD8DC", "card_h_shadow": "0 15px 35px -5px rgba(212, 155, 170, 0.2)", "pill_bg": "rgba(253, 244, 246, 0.8)", "pill_txt": "#9A7480", "pill_border": "#F5EBEB", "gauge_bar": "#D49BAA", "radar_fill": "rgba(212, 155, 170, 0.15)", "wc_cmap": "PuRd", "c_red": "rgba(226, 176, 192, 0.1)", "c_yel": "rgba(226, 176, 192, 0.2)", "c_grn": "rgba(226, 176, 192, 0.3)", "comp_colors": ["#D49BAA", "#A39BA8", "#E3B5A4"], "font": "'Playfair Display', serif"}
    elif idx == 2:
        # 💋 3. HOT & SEXY LADY
        t = {"app_bg": "radial-gradient(circle at bottom left, #FFF5F7, #FFCCD5)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#4A1525", "hero_grad": "linear-gradient(135deg, #FF0055 0%, #D50032 50%, #8A0030 100%)", "hero_shadow": "0 15px 30px -5px rgba(213, 0, 50, 0.3)", "hero_border": "#FFB3C6", "subtitle": "#FFD1DC", "form_bg": "rgba(255, 255, 255, 0.6)", "form_border": "rgba(255, 228, 232, 0.5)", "inp_bg": "rgba(255, 245, 247, 0.8)", "inp_border": "#FFCCD5", "focus": "#D50032", "btn_grad": "linear-gradient(135deg, #FF0055 0%, #D50032 100%)", "btn_shadow": "rgba(213, 0, 50, 0.3)", "btn_h_shadow": "rgba(213, 0, 50, 0.5)", "card_bg": "rgba(255, 255, 255, 0.7)", "card_border": "rgba(255, 228, 232, 0.5)", "card_h_border": "#FFCCD5", "card_h_shadow": "0 15px 35px -5px rgba(213, 0, 50, 0.25)", "pill_bg": "rgba(255, 240, 243, 0.8)", "pill_txt": "#D50032", "pill_border": "#FFE4E8", "gauge_bar": "#D50032", "radar_fill": "rgba(213, 0, 50, 0.15)", "wc_cmap": "Reds", "c_red": "rgba(213, 0, 50, 0.05)", "c_yel": "rgba(213, 0, 50, 0.15)", "c_grn": "rgba(213, 0, 50, 0.25)", "comp_colors": ["#D50032", "#FF0055", "#8A0030"], "font": "'Montserrat', sans-serif"}
    else:
        # 👑 4. SEXY GODDESS
        t = {"app_bg": "radial-gradient(circle at center, #FFF7F8, #FADADD)", "sidebar_bg": "rgba(255, 255, 255, 0.8)", "text": "#3A101E", "hero_grad": "linear-gradient(135deg, #C70039 0%, #900C3F 50%, #581845 100%)", "hero_shadow": "0 15px 30px -5px rgba(144, 12, 63, 0.35)", "hero_border": "#FFC300", "subtitle": "#FFC300", "form_bg": "rgba(255, 255, 255, 0.6)", "form_border": "rgba(250, 218, 221, 0.5)", "inp_bg": "rgba(255, 247, 248, 0.8)", "inp_border": "#F5C6CB", "focus": "#C70039", "btn_grad": "linear-gradient(135deg, #C70039 0%, #900C3F 100%)", "btn_shadow": "rgba(199, 0, 57, 0.3)", "btn_h_shadow": "rgba(144, 12, 63, 0.5)", "card_bg": "rgba(255, 255, 255, 0.7)", "card_border": "rgba(250, 218, 221, 0.5)", "card_h_border": "#FFC300", "card_h_shadow": "0 15px 35px -5px rgba(144, 12, 63, 0.25)", "pill_bg": "rgba(255, 240, 243, 0.8)", "pill_txt": "#900C3F", "pill_border": "#FFC300", "gauge_bar": "#C70039", "radar_fill": "rgba(199, 0, 57, 0.15)", "wc_cmap": "inferno", "c_red": "rgba(199, 0, 57, 0.05)", "c_yel": "rgba(199, 0, 57, 0.15)", "c_grn": "rgba(199, 0, 57, 0.25)", "comp_colors": ["#C70039", "#FFC300", "#900C3F"], "font": "'Cinzel', serif"}
else:
    d_idx = st.session_state.dark_theme_cycle_idx
    if d_idx == 0:
        # 🕵️‍♂️ 1. THE CYBERPUNK ASSASSIN
        t = {"app_bg": "radial-gradient(circle at top left, #0B0F19, #022C22)", "sidebar_bg": "rgba(17, 24, 39, 0.8)", "text": "#F3F4F6", "hero_grad": "linear-gradient(135deg, #022C22 0%, #0B0F19 50%, #111827 100%)", "hero_shadow": "0 0 40px -10px rgba(16, 185, 129, 0.15), inset 0 0 20px -5px rgba(16, 185, 129, 0.1)", "hero_border": "rgba(16, 185, 129, 0.3)", "subtitle": "#34D399", "form_bg": "rgba(17, 24, 39, 0.6)", "form_border": "rgba(31, 41, 55, 0.5)", "inp_bg": "rgba(11, 15, 25, 0.8)", "inp_border": "#374151", "focus": "#10B981", "btn_grad": "linear-gradient(135deg, #2DD4BF 0%, #10B981 100%)", "btn_shadow": "rgba(16, 185, 129, 0.2)", "btn_h_shadow": "rgba(16, 185, 129, 0.4)", "card_bg": "rgba(17, 24, 39, 0.65)", "card_border": "rgba(31, 41, 55, 0.5)", "card_h_border": "#374151", "card_h_shadow": "0 15px 35px -5px rgba(16, 185, 129, 0.2)", "pill_bg": "rgba(16, 185, 129, 0.1)", "pill_txt": "#34D399", "pill_border": "rgba(16, 185, 129, 0.2)", "gauge_bar": "#10B981", "radar_fill": "rgba(16, 185, 129, 0.15)", "wc_cmap": "viridis", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#10B981", "#3B82F6", "#F43F5E"], "font": "'Orbitron', sans-serif"}
    elif d_idx == 1:
        # 🥃 2. THE STEALTH OPERATIVE
        t = {"app_bg": "radial-gradient(circle at bottom right, #0A0A0A, #451A03)", "sidebar_bg": "rgba(18, 18, 18, 0.8)", "text": "#E5E7EB", "hero_grad": "linear-gradient(135deg, #451A03 0%, #0A0A0A 50%, #121212 100%)", "hero_shadow": "0 0 40px -10px rgba(245, 158, 11, 0.15), inset 0 0 20px -5px rgba(245, 158, 11, 0.1)", "hero_border": "rgba(245, 158, 11, 0.3)", "subtitle": "#FBBF24", "form_bg": "rgba(18, 18, 18, 0.6)", "form_border": "rgba(39, 39, 42, 0.5)", "inp_bg": "rgba(10, 10, 10, 0.8)", "inp_border": "#3F3F46", "focus": "#F59E0B", "btn_grad": "linear-gradient(135deg, #FBBF24 0%, #D97706 100%)", "btn_shadow": "rgba(245, 158, 11, 0.2)", "btn_h_shadow": "rgba(245, 158, 11, 0.4)", "card_bg": "rgba(18, 18, 18, 0.65)", "card_border": "rgba(39, 39, 42, 0.5)", "card_h_border": "#3F3F46", "card_h_shadow": "0 15px 35px -5px rgba(245, 158, 11, 0.2)", "pill_bg": "rgba(245, 158, 11, 0.1)", "pill_txt": "#FBBF24", "pill_border": "rgba(245, 158, 11, 0.2)", "gauge_bar": "#F59E0B", "radar_fill": "rgba(245, 158, 11, 0.15)", "wc_cmap": "copper", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#F59E0B", "#B45309", "#78350F"], "font": "'Rajdhani', sans-serif"}
    elif d_idx == 2:
        # 🌊 3. THE DEEP SEA COMMANDER
        t = {"app_bg": "radial-gradient(circle at center, #020617, #082F49)", "sidebar_bg": "rgba(15, 23, 42, 0.8)", "text": "#E0F2FE", "hero_grad": "linear-gradient(135deg, #082F49 0%, #020617 50%, #0F172A 100%)", "hero_shadow": "0 0 40px -10px rgba(14, 165, 233, 0.15), inset 0 0 20px -5px rgba(14, 165, 233, 0.1)", "hero_border": "rgba(14, 165, 233, 0.3)", "subtitle": "#38BDF8", "form_bg": "rgba(15, 23, 42, 0.6)", "form_border": "rgba(30, 41, 59, 0.5)", "inp_bg": "rgba(2, 6, 23, 0.8)", "inp_border": "#334155", "focus": "#0EA5E9", "btn_grad": "linear-gradient(135deg, #38BDF8 0%, #0284C7 100%)", "btn_shadow": "rgba(14, 165, 233, 0.2)", "btn_h_shadow": "rgba(14, 165, 233, 0.4)", "card_bg": "rgba(15, 23, 42, 0.65)", "card_border": "rgba(30, 41, 59, 0.5)", "card_h_border": "#334155", "card_h_shadow": "0 15px 35px -5px rgba(14, 165, 233, 0.2)", "pill_bg": "rgba(14, 165, 233, 0.1)", "pill_txt": "#38BDF8", "pill_border": "rgba(14, 165, 233, 0.2)", "gauge_bar": "#0EA5E9", "radar_fill": "rgba(14, 165, 233, 0.15)", "wc_cmap": "Blues", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#0EA5E9", "#0284C7", "#0369A1"], "font": "'Exo 2', sans-serif"}
    else:
        # 🔥 4. THE FORGE MASTER
        t = {"app_bg": "radial-gradient(circle at top, #050505, #450A0A)", "sidebar_bg": "rgba(17, 17, 17, 0.8)", "text": "#FECACA", "hero_grad": "linear-gradient(135deg, #450A0A 0%, #050505 50%, #111111 100%)", "hero_shadow": "0 0 40px -10px rgba(220, 38, 38, 0.15), inset 0 0 20px -5px rgba(220, 38, 38, 0.1)", "hero_border": "rgba(220, 38, 38, 0.3)", "subtitle": "#F87171", "form_bg": "rgba(17, 17, 17, 0.6)", "form_border": "rgba(38, 38, 38, 0.5)", "inp_bg": "rgba(5, 5, 5, 0.8)", "inp_border": "#3F3F46", "focus": "#DC2626", "btn_grad": "linear-gradient(135deg, #F87171 0%, #DC2626 100%)", "btn_shadow": "rgba(220, 38, 38, 0.2)", "btn_h_shadow": "rgba(220, 38, 38, 0.4)", "card_bg": "rgba(17, 17, 17, 0.65)", "card_border": "rgba(38, 38, 38, 0.5)", "card_h_border": "#3F3F46", "card_h_shadow": "0 15px 35px -5px rgba(220, 38, 38, 0.2)", "pill_bg": "rgba(220, 38, 38, 0.1)", "pill_txt": "#F87171", "pill_border": "rgba(220, 38, 38, 0.2)", "gauge_bar": "#DC2626", "radar_fill": "rgba(220, 38, 38, 0.15)", "wc_cmap": "Reds", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#DC2626", "#991B1B", "#7F1D1D"], "font": "'Teko', sans-serif"}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Exo+2:wght@400;600&family=Montserrat:wght@400;600&family=Orbitron:wght@400;700&family=Playfair+Display:wght@400;700&family=Quicksand:wght@400;600&family=Rajdhani:wght@400;600&family=Teko:wght@400;600&display=swap');
    .stApp, h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, div {{ font-family: {t['font']} !important; }}
    .stApp {{ background: {t['app_bg']} !important; background-attachment: fixed !important; color: {t['text']} !important; }}
    [data-testid="stSidebar"] {{ background-color: {t['sidebar_bg']} !important; border-right: 1px solid {t['card_border']} !important; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);}}
    .hero-container {{ background: {t['hero_grad']}; color: #FFFFFF !important; padding: 3.5rem 2rem; border-radius: 1rem; text-align: center; margin-bottom: 2.5rem; margin-top: -2rem; box-shadow: {t['hero_shadow']}; border: 1px solid {t['hero_border']}; }}
    .hero-subtitle {{ font-size: 1.15rem; font-weight: 500; margin-top: 1rem; color: {t['subtitle']} !important; letter-spacing: 0.05em; text-transform: uppercase; }}
    div[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {{ background: {t['card_bg']} !important; backdrop-filter: blur(16px) saturate(180%); border: 1px solid {t['card_border']} !important; border-radius: 1rem !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05); padding: 1.5rem !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; padding: 1rem !important; }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{ border-color: {t['card_h_border']} !important; box-shadow: {t['card_h_shadow']} !important; transform: perspective(1000px) rotateX(2deg) rotateY(-2deg) translateY(-5px) scale3d(1.02, 1.02, 1.02) !important; z-index: 10; }}
    div[data-baseweb="select"] > div {{ background-color: {t['inp_bg']} !important; color: {t['text']} !important; border: 1px solid {t['inp_border']} !important; border-radius: 0.5rem; }}
    .stTextArea textarea, .stTextInput input {{ background-color: {t['inp_bg']} !important; color: {t['text']} !important; border: 1px solid {t['inp_border']} !important; border-radius: 0.5rem; }}
    .stTextArea textarea:focus, .stTextInput input:focus {{ border-color: {t['focus']} !important; box-shadow: 0 0 0 1px {t['focus']} !important; }}
    div[data-testid="stForm"] button {{ background: {t['btn_grad']} !important; color: #FFFFFF !important; border: none !important; border-radius: 0.5rem !important; font-weight: 600 !important; letter-spacing: 0.02em !important; padding: 0.6rem 2.5rem !important; box-shadow: 0 4px 10px -1px {t['btn_shadow']} !important; transition: all 0.3s ease !important; }}
    div[data-testid="stForm"] button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 15px -2px {t['btn_h_shadow']} !important; }}
    button[kind="secondary"] {{ background-color: transparent !important; color: {t['pill_txt']} !important; border: 1px solid {t['inp_border']} !important; border-radius: 2rem !important; font-weight: 500 !important;}}
    button[kind="secondary"]:hover {{ border-color: {t['focus']} !important; color: {t['focus']} !important; background-color: {t['pill_bg']} !important; }}
    .tag-pill {{ background-color: {t['pill_bg']}; color: {t['pill_txt']}; padding: 0.25rem 0.8rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin-right: 0.5rem; border: 1px solid {t['pill_border']}; letter-spacing: 0.03em; }}
</style>
""", unsafe_allow_html=True)

chart_text_color, gauge_bar, gauge_bg, step_red, step_yellow, step_green, radar_fill, radar_line, radar_bg, radar_grid, wc_cmap, comp_colors = t['text'], t['gauge_bar'], "rgba(0,0,0,0)", t['c_red'], t['c_yel'], t['c_grn'], t['radar_fill'], t['gauge_bar'], "rgba(255, 255, 255, 0.95)" if st.session_state.light_theme else "rgba(17, 24, 39, 0.8)", t['card_border'], t['wc_cmap'], t['comp_colors']
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
    "University College of Engineering Thodupuzha (UCE)": standard_departments, "Model Engineering College (MEC)": standard_departments, "College of Engineering Trivandrum (CET)": standard_departments, "TKM College of Engineering, Kollam (TKM)": standard_departments, "Rajiv Gandhi Institute of Technology (RIT), Kottayam": standard_departments, "Government Engineering College, Thrissur (GEC)": standard_departments, "Muthoot Institute of Technology and Science (MITS)": standard_departments, "Rajagiri School of Engineering & Technology (RSET)": standard_departments, "Mar Athanasius College of Engineering (MACE)": standard_departments, "Federal Institute of Science and Technology (FISAT)": standard_departments
}
colleges_list = list(ktu_hierarchy.keys())
college_coords = {
    "University College of Engineering Thodupuzha (UCE)": (9.8450, 76.7450), "Model Engineering College (MEC)": (10.0284, 76.3285), "College of Engineering Trivandrum (CET)": (8.5456, 76.9063), "TKM College of Engineering, Kollam (TKM)": (8.9100, 76.6316), "Rajiv Gandhi Institute of Technology (RIT), Kottayam)": (9.5534, 76.6179), "Government Engineering College, Thrissur (GEC)": (10.5540, 76.2230), "Muthoot Institute of Technology and Science (MITS)": (9.9482, 76.3980), "Rajagiri School of Engineering & Technology (RSET)": (10.0102, 76.3653), "Mar Athanasius College of Engineering (MACE)": (10.0543, 76.6186), "Federal Institute of Science and Technology (FISAT)": (10.2312, 76.4087)
}

# --- 2. DATABASE LOGIC ---
DB_NAME = "ktu_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, target_name TEXT, category TEXT, review_text TEXT, upvotes INTEGER DEFAULT 0, tags TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    try: c.execute("ALTER TABLE reviews ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    except: pass 
    c.execute('''CREATE TABLE IF NOT EXISTS replies (id INTEGER PRIMARY KEY AUTOINCREMENT, review_id INTEGER, reply_text TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

def extract_tags(text, category):
    tags = []
    text = text.lower()
    if category == "College":
        for k,v in {"placement":"💼 Placements", "faculty":"👨‍🏫 Faculty", "hostel":"🛏️ Hostel", "campus":"🏛️ Campus"}.items():
            if k in text: tags.append(v)
    else:
        for k,v in {"hard":"⚠️ Tough Syllabus", "easy":"✅ Easy Scoring", "lab":"🧪 Heavy Labs"}.items():
            if k in text: tags.append(v)
    return ", ".join(tags)

def check_spam(text, target_name):
    text = text.strip()
    if len(text) < 10: return True, "Review too short."
    if len(text) > 800: return True, "Review too long."
    if re.search(r'<[^>]*>', text) or re.search(r'(http:\/\/|https:\/\/|www\.)', text): return True, "HTML/Links not allowed."
    profanity = ["fuck", "shit", "bitch", "asshole"]
    if any(bad in text.lower() for bad in profanity): return True, "Inappropriate language."
    return False, ""

def add_review_to_db(target_name, category, review_text):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO reviews (target_name, category, review_text, upvotes, tags) VALUES (?, ?, ?, ?, ?)", (target_name, category, review_text, 0, extract_tags(review_text, category)))
    conn.commit(); conn.close()

def add_reply_to_db(review_id, reply_text):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO replies (review_id, reply_text) VALUES (?, ?)", (review_id, html.escape(reply_text.strip())))
    conn.commit(); conn.close()

def get_reviews_from_db(target_name, sort_by="Most Upvoted"):
    conn = sqlite3.connect(DB_NAME)
    order = "ORDER BY id DESC" if sort_by == "Newest" else "ORDER BY upvotes DESC, id DESC"
    df = pd.read_sql_query(f"SELECT * FROM reviews WHERE target_name=? {order}", conn, params=(target_name,))
    conn.close(); return df.to_dict('records')

def get_replies(review_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM replies WHERE review_id=? ORDER BY id ASC", conn, params=(review_id,))
    conn.close(); return df.to_dict('records')

def upvote_review(review_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("UPDATE reviews SET upvotes = upvotes + 1 WHERE id = ?", (review_id,))
    conn.commit(); conn.close()

def seed_initial_data():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews")
    if c.fetchone()[0] == 0:
        seed_data = []
        for college in colleges_list:
            for _ in range(10):
                text = "Great facilities and supportive faculty." if random.random() > 0.4 else "Strict management but good placements."
                ts = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
                seed_data.append((college, "College", text, random.randint(0, 50), extract_tags(text, "College"), ts))
            for dept, subs in ktu_hierarchy[college].items():
                for sub in subs:
                    for _ in range(3):
                        text = "Labs are heavy but very practical." if random.random() > 0.5 else "Massive syllabus, requires consistent study."
                        ts = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
                        seed_data.append((f"{sub} @ {college}", "Course", text, random.randint(0, 20), extract_tags(text, "Course"), ts))
        c.executemany("INSERT INTO reviews (target_name, category, review_text, upvotes, tags, created_at) VALUES (?, ?, ?, ?, ?, ?)", seed_data)
        conn.commit(); conn.close()

init_db(); seed_initial_data()

# --- 3. AI & RAG LOGIC ---
def generate_rag_response(query, reviews):
    if not reviews: return "No data available."
    keywords = [w.lower() for w in query.split() if len(w) > 3]
    relevant = [r['review_text'] for r in reviews if any(k in r['review_text'].lower() for k in keywords)]
    if not relevant: return f"Students haven't specifically mentioned '{query}' yet."
    avg_s = sum([(TextBlob(t).sentiment.polarity + 1)/2 for t in relevant]) / len(relevant)
    v = "positive" if avg_s > 0.6 else "mixed" if avg_s > 0.4 else "critical"
    return f"**AI RAG Summary:** Reviews regarding your query are generally **{v}**.\n\n> *\"{random.choice(relevant)}\"*"

# --- 4. INTERFACE ---
st.sidebar.divider()
st.sidebar.header("🔍 Filter & Sort")
search_query = st.sidebar.text_input("Search keywords:")
sort_option = st.sidebar.selectbox("Sort:", ["Most Upvoted", "Newest"])

st.sidebar.divider()
st.sidebar.header("📚 Vault")
st.sidebar.download_button("📄 KTU Syllabus", data=b"PDF", file_name="Syllabus.pdf", use_container_width=True)
st.sidebar.download_button("📝 PYQs", data=b"PDF", file_name="PYQs.pdf", use_container_width=True)

st.markdown(f"""<div class="hero-container"><div class="hero-title">⚡ KTU Insight Engine <span style="font-size: 0.35em; font-weight: 600; vertical-align: super; opacity: 0.85; margin-left: 4px;">2.0</span></div><div class="hero-subtitle">Powered by Natural Language Processing & Sentiment Analytics</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🏢 Colleges", "📚 Courses", "⚖️ Versus", "🗺️ Heatmap"])

with tab1:
    c1, c2 = st.columns([1, 2.5])
    with c1:
        sel_col = st.selectbox("College:", colleges_list)
        with st.form("col_form"):
            rev = st.text_area("Review:", max_chars=800)
            if st.form_submit_button("Submit"):
                if time.time() - st.session_state.last_submit_time < 30: st.error("Cooldown active.")
                else:
                    is_s, reas = check_spam(rev, sel_col)
                    if is_s: st.error(reas)
                    else: add_review_to_db(sel_col, "College", rev); st.session_state.last_submit_time = time.time(); st.rerun()
    with c2:
        re_v = get_reviews_from_db(sel_col, sort_option)
        s_score = get_overall_sentiment(re_v, sel_col)
        a_left, a_right = st.columns(2)
        with a_left: plot_gauge(s_score, "Sentiment")
        with a_right: 
            st.markdown("##### 📈 Trend")
            plot_sentiment_timeline(re_v)
        with st.expander("🤖 Chat with Reviews"):
            q = st.text_input("Ask anything:")
            if q: st.success(generate_rag_response(q, re_v))
        for r in [x for x in re_v if search_query.lower() in x['review_text'].lower()][:10]:
            with st.container(border=True):
                av = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed={r['id']}"
                st.markdown(f"<div style='display:flex;align-items:center;margin-bottom:10px;'><img src='{av}' style='width:40px;margin-right:12px;'><b>Insider #{r['id']}</b></div><p><i>\"{r['review_text']}\"</i></p>", unsafe_allow_html=True)
                if st.button(f"👍 {r['upvotes']}", key=f"up_{r['id']}"): upvote_review(r['id']); st.rerun()

with tab2:
    d1, d2, d3 = st.columns(3)
    c_c = d1.selectbox("College:", colleges_list, key="c2")
    c_d = d2.selectbox("Dept:", list(ktu_hierarchy[c_c].keys()))
    c_s = d3.selectbox("Subject:", ktu_hierarchy[c_c][c_d])
    t_name = f"{c_s} @ {c_c}"
    l, r = st.columns([1, 2.5])
    with l:
        with st.form("crs_form"):
            cr = st.text_area("Review:", max_chars=800)
            if st.form_submit_button("Submit"):
                add_review_to_db(t_name, "Course", cr); st.rerun()
    with r:
        cr_v = get_reviews_from_db(t_name, sort_option)
        plot_radar(analyze_course_aspects(cr_v))
        for x in cr_v[:5]:
            with st.container(border=True): st.write(x['review_text'])

with tab3:
    mode = st.radio("Compare:", ["Colleges", "Departments"], horizontal=True)
    if mode == "Colleges":
        picks = st.multiselect("Select 2-3:", colleges_list, max_selections=3)
        if len(picks) >= 2:
            scores = {}
            for p in picks: 
                rvs = get_reviews_from_db(p)
                scores[p] = int(get_overall_sentiment(rvs)*100 + sum(i['upvotes'] for i in rvs))
            st.plotly_chart(px.bar(x=list(scores.keys()), y=list(scores.values()), color=list(scores.keys()), color_discrete_sequence=comp_colors))

with tab4:
    st.markdown("### 🗺️ KTU Heatmap")
    plot_geospatial_heatmap(colleges_list, st.session_state.light_theme)
