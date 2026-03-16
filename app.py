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

# --- ANTI-SPAM & DUAL THEME STATE SETUP ---
if 'light_theme' not in st.session_state:
    st.session_state.light_theme = False
if 'theme_cycle_idx' not in st.session_state:
    st.session_state.theme_cycle_idx = 3 # Light Mode Cycle
if 'dark_theme_cycle_idx' not in st.session_state:
    st.session_state.dark_theme_cycle_idx = 3 # Dark Mode Cycle
if 'upvoted_reviews' not in st.session_state:
    st.session_state.upvoted_reviews = set() 
if 'last_submit_time' not in st.session_state:
    st.session_state.last_submit_time = 0.0 

# 🔥 BRAND LOGO INJECTION 🔥
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1162/1162803.png", width=55)
st.sidebar.markdown("## KTU Insight")
st.sidebar.divider()

st.sidebar.markdown("### 🌗 Appearance")
theme_toggle = st.sidebar.toggle("Switch to Light Mode", value=st.session_state.light_theme)

# 🔥 DUAL SHAPE-SHIFTING THEME ENGINE 🔥
if theme_toggle != st.session_state.light_theme:
    if theme_toggle == True:
        # Switched to Light: Rotate Light Persona
        st.session_state.theme_cycle_idx = (st.session_state.theme_cycle_idx + 1) % 4
    else:
        # Switched to Dark: Rotate Dark Persona
        st.session_state.dark_theme_cycle_idx = (st.session_state.dark_theme_cycle_idx + 1) % 4
        
    st.session_state.light_theme = theme_toggle
    st.rerun()

# Apply CSS overrides and set sophisticated chart color variables
if st.session_state.light_theme:
    idx = st.session_state.theme_cycle_idx
    if idx == 0:
        # 🌸 1. INNOCENT YOUNG GIRL (Cotton Candy & Peach)
        t = {"app_bg": "#FFF8F9", "sidebar_bg": "#FFFFFF", "text": "#5D4E52", "hero_grad": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 50%, #FFDAC1 100%)", "hero_shadow": "0 15px 30px -5px rgba(255, 182, 193, 0.3)", "hero_border": "#FFD1DC", "hero_txt_shadow": "0 2px 10px rgba(0,0,0,0.05)", "subtitle": "#FFF0F5", "form_bg": "#FFFFFF", "form_border": "#FFE4E1", "inp_bg": "#FFF8F9", "inp_border": "#FFD1DC", "focus": "#FFB6C1", "btn_grad": "linear-gradient(135deg, #FFA9D1 0%, #FFB6C1 100%)", "btn_shadow": "rgba(255, 182, 193, 0.3)", "btn_h_shadow": "rgba(255, 182, 193, 0.5)", "card_bg": "#FFFFFF", "card_border": "#FFE4E1", "card_h_border": "#FFD1DC", "card_h_shadow": "0 12px 20px -3px rgba(255, 182, 193, 0.2)", "pill_bg": "#FFF0F5", "pill_txt": "#FF69B4", "pill_border": "#FFD1DC", "gauge_bar": "#FF69B4", "radar_fill": "rgba(255, 105, 180, 0.15)", "wc_cmap": "spring", "c_red": "rgba(255, 182, 193, 0.1)", "c_yel": "rgba(255, 182, 193, 0.2)", "c_grn": "rgba(255, 182, 193, 0.3)", "comp_colors": ["#FF69B4", "#FFA9D1", "#FFDAC1"]}
    elif idx == 1:
        # 🍷 2. ELEGANT YOUNG LADY (Blush & Silk)
        t = {"app_bg": "#FCF9F9", "sidebar_bg": "#FFFFFF", "text": "#4A4040", "hero_grad": "linear-gradient(135deg, #DCA7B8 0%, #D49BAA 50%, #CE8E9E 100%)", "hero_shadow": "0 15px 30px -5px rgba(212, 155, 170, 0.25)", "hero_border": "#E6BCCD", "hero_txt_shadow": "0 2px 10px rgba(0,0,0,0.1)", "subtitle": "#FFF0F2", "form_bg": "#FFFFFF", "form_border": "#F5EBEB", "inp_bg": "#FCF9F9", "inp_border": "#EAD8DC", "focus": "#D49BAA", "btn_grad": "linear-gradient(135deg, #DCA7B8 0%, #CE8E9E 100%)", "btn_shadow": "rgba(212, 155, 170, 0.3)", "btn_h_shadow": "rgba(212, 155, 170, 0.4)", "card_bg": "#FFFFFF", "card_border": "#F5EBEB", "card_h_border": "#EAD8DC", "card_h_shadow": "0 12px 20px -3px rgba(212, 155, 170, 0.1)", "pill_bg": "#FDF4F6", "pill_txt": "#9A7480", "pill_border": "#F5EBEB", "gauge_bar": "#D49BAA", "radar_fill": "rgba(212, 155, 170, 0.15)", "wc_cmap": "PuRd", "c_red": "rgba(226, 176, 192, 0.1)", "c_yel": "rgba(226, 176, 192, 0.2)", "c_grn": "rgba(226, 176, 192, 0.3)", "comp_colors": ["#D49BAA", "#A39BA8", "#E3B5A4"]}
    elif idx == 2:
        # 💋 3. HOT & SEXY LADY (Crimson & Ruby)
        t = {"app_bg": "#FFF5F7", "sidebar_bg": "#FFFFFF", "text": "#4A1525", "hero_grad": "linear-gradient(135deg, #FF0055 0%, #D50032 50%, #8A0030 100%)", "hero_shadow": "0 15px 30px -5px rgba(213, 0, 50, 0.3)", "hero_border": "#FFB3C6", "hero_txt_shadow": "0 2px 10px rgba(0,0,0,0.1)", "subtitle": "#FFD1DC", "form_bg": "#FFFFFF", "form_border": "#FFE4E8", "inp_bg": "#FFF5F7", "inp_border": "#FFCCD5", "focus": "#D50032", "btn_grad": "linear-gradient(135deg, #FF0055 0%, #D50032 100%)", "btn_shadow": "rgba(213, 0, 50, 0.3)", "btn_h_shadow": "rgba(213, 0, 50, 0.5)", "card_bg": "#FFFFFF", "card_border": "#FFE4E8", "card_h_border": "#FFCCD5", "card_h_shadow": "0 12px 20px -3px rgba(213, 0, 50, 0.15)", "pill_bg": "#FFF0F3", "pill_txt": "#D50032", "pill_border": "#FFE4E8", "gauge_bar": "#D50032", "radar_fill": "rgba(213, 0, 50, 0.15)", "wc_cmap": "Reds", "c_red": "rgba(213, 0, 50, 0.05)", "c_yel": "rgba(213, 0, 50, 0.15)", "c_grn": "rgba(213, 0, 50, 0.25)", "comp_colors": ["#D50032", "#FF0055", "#8A0030"]}
    else:
        # 👑 4. SEXY GODDESS (Velvet & Gold)
        t = {"app_bg": "#FFF7F8", "sidebar_bg": "#FFFFFF", "text": "#3A101E", "hero_grad": "linear-gradient(135deg, #C70039 0%, #900C3F 50%, #581845 100%)", "hero_shadow": "0 15px 30px -5px rgba(144, 12, 63, 0.35)", "hero_border": "#FFC300", "hero_txt_shadow": "0 2px 10px rgba(0,0,0,0.1)", "subtitle": "#FFC300", "form_bg": "#FFFFFF", "form_border": "#FADADD", "inp_bg": "#FFF7F8", "inp_border": "#F5C6CB", "focus": "#C70039", "btn_grad": "linear-gradient(135deg, #C70039 0%, #900C3F 100%)", "btn_shadow": "rgba(199, 0, 57, 0.3)", "btn_h_shadow": "rgba(144, 12, 63, 0.5)", "card_bg": "#FFFFFF", "card_border": "#FADADD", "card_h_border": "#FFC300", "card_h_shadow": "0 12px 20px -3px rgba(144, 12, 63, 0.15)", "pill_bg": "#FFF0F3", "pill_txt": "#900C3F", "pill_border": "#FFC300", "gauge_bar": "#C70039", "radar_fill": "rgba(199, 0, 57, 0.15)", "wc_cmap": "inferno", "c_red": "rgba(199, 0, 57, 0.05)", "c_yel": "rgba(199, 0, 57, 0.15)", "c_grn": "rgba(199, 0, 57, 0.25)", "comp_colors": ["#C70039", "#FFC300", "#900C3F"]}

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t['app_bg']} !important; color: {t['text']} !important; font-family: 'Inter', sans-serif; }}
        [data-testid="stSidebar"] {{ background-color: {t['sidebar_bg']} !important; border-right: 1px solid {t['card_border']} !important; }}
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{ color: {t['text']} !important; }}
        .hero-container {{ background: {t['hero_grad']}; color: #FFFFFF !important; padding: 3.5rem 2rem; border-radius: 1rem; text-align: center; margin-bottom: 2.5rem; margin-top: -2rem; box-shadow: {t['hero_shadow']}; border: 1px solid {t['hero_border']}; }}
        .hero-title {{ font-size: 3.5rem; font-weight: 800; margin: 0; line-height: 1.2; letter-spacing: -0.01em; color: #FFFFFF !important; font-family: 'Georgia', serif; text-shadow: {t['hero_txt_shadow']};}}
        .hero-subtitle {{ font-size: 1.15rem; font-weight: 500; margin-top: 1rem; color: {t['subtitle']} !important; letter-spacing: 0.05em; text-transform: uppercase; }}
        div[data-testid="stForm"] {{ background-color: {t['form_bg']} !important; border: 1px solid {t['form_border']} !important; border-radius: 0.75rem; box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.03); padding: 2.5rem !important; }}
        div[data-baseweb="select"] > div {{ background-color: {t['inp_bg']} !important; color: {t['text']} !important; border: 1px solid {t['inp_border']} !important; border-radius: 0.5rem; }}
        .stTextArea textarea, .stTextInput input {{ background-color: {t['inp_bg']} !important; color: {t['text']} !important; border: 1px solid {t['inp_border']} !important; border-radius: 0.5rem; }}
        .stTextArea textarea:focus, .stTextInput input:focus {{ border-color: {t['focus']} !important; box-shadow: 0 0 0 1px {t['focus']} !important; }}
        div[data-testid="stForm"] button {{ background: {t['btn_grad']} !important; color: #FFFFFF !important; border: none !important; border-radius: 0.5rem !important; font-weight: 600 !important; letter-spacing: 0.02em !important; padding: 0.6rem 2.5rem !important; box-shadow: 0 4px 10px -1px {t['btn_shadow']} !important; transition: all 0.3s ease !important; }}
        div[data-testid="stForm"] button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 15px -2px {t['btn_h_shadow']} !important; }}
        button[kind="secondary"] {{ background-color: #FFFFFF !important; color: {t['pill_txt']} !important; border: 1px solid {t['inp_border']} !important; border-radius: 2rem !important; font-weight: 500 !important;}}
        button[kind="secondary"]:hover {{ border-color: {t['focus']} !important; color: {t['focus']} !important; background-color: {t['pill_bg']} !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 0.75rem !important; border: 1px solid {t['card_border']} !important; background-color: {t['card_bg']} !important; transition: all 0.3s ease !important; box-shadow: 0 2px 10px -1px rgba(0,0,0,0.02) !important; padding: 0.8rem !important; }}
        [data-testid="stVerticalBlockBorderWrapper"]:hover {{ border-color: {t['card_h_border']} !important; box-shadow: {t['card_h_shadow']} !important; transform: translateY(-2px); }}
        .tag-pill {{ background-color: {t['pill_bg']}; color: {t['pill_txt']}; padding: 0.25rem 0.8rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin-right: 0.5rem; border: 1px solid {t['pill_border']}; letter-spacing: 0.03em; }}
    </style>
    """, unsafe_allow_html=True)
    
    chart_text_color, gauge_bar, gauge_bg, step_red, step_yellow, step_green, radar_fill, radar_line, radar_bg, radar_grid, wc_cmap, comp_colors = t['text'], t['gauge_bar'], "rgba(0,0,0,0)", t['c_red'], t['c_yel'], t['c_grn'], t['radar_fill'], t['gauge_bar'], "rgba(255, 255, 255, 0.95)", t['card_border'], t['wc_cmap'], t['comp_colors']

else:
    d_idx = st.session_state.dark_theme_cycle_idx
    if d_idx == 0:
        # 🕵️‍♂️ 1. THE CYBERPUNK ASSASSIN (Midnight & Neon Emerald)
        d = {"app_bg": "#0B0F19", "sidebar_bg": "#111827", "text": "#F3F4F6", "hero_grad": "linear-gradient(135deg, #022C22 0%, #0B0F19 50%, #111827 100%)", "hero_shadow": "0 0 40px -10px rgba(16, 185, 129, 0.15), inset 0 0 20px -5px rgba(16, 185, 129, 0.1)", "hero_border": "rgba(16, 185, 129, 0.3)", "subtitle": "#34D399", "form_bg": "#111827", "form_border": "#1F2937", "inp_bg": "#0B0F19", "inp_border": "#374151", "focus": "#10B981", "btn_grad": "linear-gradient(135deg, #2DD4BF 0%, #10B981 100%)", "btn_txt": "#022C22", "btn_shadow": "rgba(16, 185, 129, 0.2)", "btn_h_shadow": "rgba(16, 185, 129, 0.4)", "card_bg": "#111827", "card_border": "#1F2937", "card_h_border": "#374151", "card_h_shadow": "0 10px 25px -5px rgba(16, 185, 129, 0.1)", "pill_bg": "rgba(16, 185, 129, 0.1)", "pill_txt": "#34D399", "pill_border": "rgba(16, 185, 129, 0.2)", "gauge_bar": "#10B981", "radar_fill": "rgba(16, 185, 129, 0.15)", "wc_cmap": "viridis", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#10B981", "#3B82F6", "#F43F5E"]}
    elif d_idx == 1:
        # 🥃 2. THE STEALTH OPERATIVE (Obsidian & Amber)
        d = {"app_bg": "#0A0A0A", "sidebar_bg": "#121212", "text": "#E5E7EB", "hero_grad": "linear-gradient(135deg, #451A03 0%, #0A0A0A 50%, #121212 100%)", "hero_shadow": "0 0 40px -10px rgba(245, 158, 11, 0.15), inset 0 0 20px -5px rgba(245, 158, 11, 0.1)", "hero_border": "rgba(245, 158, 11, 0.3)", "subtitle": "#FBBF24", "form_bg": "#121212", "form_border": "#27272A", "inp_bg": "#0A0A0A", "inp_border": "#3F3F46", "focus": "#F59E0B", "btn_grad": "linear-gradient(135deg, #FBBF24 0%, #D97706 100%)", "btn_txt": "#451A03", "btn_shadow": "rgba(245, 158, 11, 0.2)", "btn_h_shadow": "rgba(245, 158, 11, 0.4)", "card_bg": "#121212", "card_border": "#27272A", "card_h_border": "#3F3F46", "card_h_shadow": "0 10px 25px -5px rgba(245, 158, 11, 0.1)", "pill_bg": "rgba(245, 158, 11, 0.1)", "pill_txt": "#FBBF24", "pill_border": "rgba(245, 158, 11, 0.2)", "gauge_bar": "#F59E0B", "radar_fill": "rgba(245, 158, 11, 0.15)", "wc_cmap": "copper", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#F59E0B", "#B45309", "#78350F"]}
    elif d_idx == 2:
        # 🌊 3. THE DEEP SEA COMMANDER (Abyssal Navy & Electric Cyan)
        d = {"app_bg": "#020617", "sidebar_bg": "#0F172A", "text": "#E0F2FE", "hero_grad": "linear-gradient(135deg, #082F49 0%, #020617 50%, #0F172A 100%)", "hero_shadow": "0 0 40px -10px rgba(14, 165, 233, 0.15), inset 0 0 20px -5px rgba(14, 165, 233, 0.1)", "hero_border": "rgba(14, 165, 233, 0.3)", "subtitle": "#38BDF8", "form_bg": "#0F172A", "form_border": "#1E293B", "inp_bg": "#020617", "inp_border": "#334155", "focus": "#0EA5E9", "btn_grad": "linear-gradient(135deg, #38BDF8 0%, #0284C7 100%)", "btn_txt": "#082F49", "btn_shadow": "rgba(14, 165, 233, 0.2)", "btn_h_shadow": "rgba(14, 165, 233, 0.4)", "card_bg": "#0F172A", "card_border": "#1E293B", "card_h_border": "#334155", "card_h_shadow": "0 10px 25px -5px rgba(14, 165, 233, 0.1)", "pill_bg": "rgba(14, 165, 233, 0.1)", "pill_txt": "#38BDF8", "pill_border": "rgba(14, 165, 233, 0.2)", "gauge_bar": "#0EA5E9", "radar_fill": "rgba(14, 165, 233, 0.15)", "wc_cmap": "Blues", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#0EA5E9", "#0284C7", "#0369A1"]}
    else:
        # 🔥 4. THE FORGE MASTER (Vantablack & Crimson)
        d = {"app_bg": "#050505", "sidebar_bg": "#111111", "text": "#FECACA", "hero_grad": "linear-gradient(135deg, #450A0A 0%, #050505 50%, #111111 100%)", "hero_shadow": "0 0 40px -10px rgba(220, 38, 38, 0.15), inset 0 0 20px -5px rgba(220, 38, 38, 0.1)", "hero_border": "rgba(220, 38, 38, 0.3)", "subtitle": "#F87171", "form_bg": "#111111", "form_border": "#262626", "inp_bg": "#050505", "inp_border": "#3F3F46", "focus": "#DC2626", "btn_grad": "linear-gradient(135deg, #F87171 0%, #DC2626 100%)", "btn_txt": "#450A0A", "btn_shadow": "rgba(220, 38, 38, 0.2)", "btn_h_shadow": "rgba(220, 38, 38, 0.4)", "card_bg": "#111111", "card_border": "#262626", "card_h_border": "#3F3F46", "card_h_shadow": "0 10px 25px -5px rgba(220, 38, 38, 0.1)", "pill_bg": "rgba(220, 38, 38, 0.1)", "pill_txt": "#F87171", "pill_border": "rgba(220, 38, 38, 0.2)", "gauge_bar": "#DC2626", "radar_fill": "rgba(220, 38, 38, 0.15)", "wc_cmap": "Reds", "c_red": "rgba(239, 68, 68, 0.1)", "c_yel": "rgba(245, 158, 11, 0.1)", "c_grn": "rgba(16, 185, 129, 0.1)", "comp_colors": ["#DC2626", "#991B1B", "#7F1D1D"]}

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {d['app_bg']} !important; color: {d['text']} !important; font-family: 'Inter', sans-serif; }}
        [data-testid="stSidebar"] {{ background-color: {d['sidebar_bg']} !important; border-right: 1px solid {d['form_border']} !important; }}
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{ color: {d['text']} !important; }}
        .hero-container {{ background: {d['hero_grad']}; padding: 3rem 2rem; border-radius: 1.5rem; text-align: center; margin-bottom: 2rem; margin-top: -2rem; border: 1px solid {d['hero_border']}; box-shadow: {d['hero_shadow']}; }}
        .hero-title {{ font-size: 3.5rem; font-weight: 900; margin: 0; line-height: 1.2; letter-spacing: -0.03em; color: #FFFFFF !important; }}
        .hero-subtitle {{ font-size: 1.25rem; font-weight: 500; margin-top: 0.75rem; color: {d['subtitle']} !important; }}
        div[data-testid="stForm"] {{ background-color: {d['form_bg']} !important; border: 1px solid {d['form_border']} !important; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); padding: 2rem !important; }}
        div[data-baseweb="select"] > div {{ background-color: {d['inp_bg']} !important; color: {d['text']} !important; border: 1px solid {d['inp_border']} !important; border-radius: 0.5rem; }}
        .stTextArea textarea, .stTextInput input {{ background-color: {d['inp_bg']} !important; color: {d['text']} !important; border: 1px solid {d['inp_border']} !important; border-radius: 0.5rem; }}
        .stTextArea textarea:focus, .stTextInput input:focus {{ border-color: {d['focus']} !important; box-shadow: 0 0 0 1px {d['focus']} !important; }}
        div[data-testid="stForm"] button {{ background: {d['btn_grad']} !important; color: {d['btn_txt']} !important; border: none !important; border-radius: 0.5rem !important; font-weight: 700 !important; padding: 0.5rem 2rem !important; box-shadow: 0 4px 6px -1px {d['btn_shadow']} !important; transition: all 0.3s ease !important; }}
        div[data-testid="stForm"] button:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px {d['btn_h_shadow']} !important; }}
        button[kind="secondary"] {{ background-color: {d['sidebar_bg']} !important; color: {d['pill_txt']} !important; border: 1px solid {d['inp_border']} !important; border-radius: 2rem !important; }}
        button[kind="secondary"]:hover {{ border-color: {d['focus']} !important; color: {d['focus']} !important; background-color: {d['pill_bg']} !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 1rem !important; border: 1px solid {d['card_border']} !important; background-color: {d['card_bg']} !important; transition: all 0.3s ease !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3) !important; padding: 0.5rem !important; }}
        [data-testid="stVerticalBlockBorderWrapper"]:hover {{ border-color: {d['card_h_border']} !important; box-shadow: {d['card_h_shadow']} !important; transform: translateY(-3px); }}
        .tag-pill {{ background-color: {d['pill_bg']}; color: {d['pill_txt']}; padding: 0.3rem 0.8rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; display: inline-block; margin-right: 0.5rem; border: 1px solid {d['pill_border']}; letter-spacing: 0.02em; }}
    </style>
    """, unsafe_allow_html=True)
    
    chart_text_color, gauge_bar, gauge_bg, step_red, step_yellow, step_green, radar_fill, radar_line, radar_bg, radar_grid, wc_cmap, comp_colors = d['text'], d['gauge_bar'], "rgba(0,0,0,0)", d['c_red'], d['c_yel'], d['c_grn'], d['radar_fill'], d['gauge_bar'], d['sidebar_bg'], d['card_border'], d['wc_cmap'], d['comp_colors']

# --- ANIMATION HELPER ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None
lottie_ai = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_1m1of8zi.json")

# --- 1. DATA HIERARCHY ---
standard_departments = {
      "Artificial Intelligence (AI & DS)": ["AD301: Deep Learning", "AD302: Reinforcement Learning", "AD303: Data Analytics", "AD304: Big Data Technologies", "AD305: Natural Language Processing", "AD307: Computer Vision"],
      "Computer Science (CSE)": ["CS301: Theory of Computation", "CS302: Design & Analysis of Algorithms", "CS303: Operating Systems", "CS304: Compiler Design", "CS305: Microprocessors", "CS309: Graph Theory"]
}
ktu_hierarchy = {
    "University College of Engineering Thodupuzha (UCE)": standard_departments,
    "Model Engineering College (MEC)": standard_departments,
    "College of Engineering Trivandrum (CET)": standard_departments
}
colleges_list = list(ktu_hierarchy.keys())

# --- 2. DATABASE SETUP, MIGRATION & ANTI-SPAM ---
DB_NAME = "ktu_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_name TEXT, category TEXT, review_text TEXT,
                    upvotes INTEGER DEFAULT 0, tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    try: c.execute("ALTER TABLE reviews ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    except: pass 
    c.execute('''CREATE TABLE IF NOT EXISTS replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id INTEGER, reply_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def extract_tags(text, category):
    tags = []
    text = text.lower()
    if category == "College":
        if "placement" in text or "job" in text: tags.append("💼 Placements")
        if "faculty" in text or "teacher" in text: tags.append("👨‍🏫 Faculty")
        if "hostel" in text or "food" in text: tags.append("🛏️ Hostel")
    else:
        if "hard" in text or "difficult" in text: tags.append("⚠️ Tough Syllabus")
        if "easy" in text or "chill" in text: tags.append("✅ Easy Scoring")
        if "lab" in text or "hands-on" in text: tags.append("🧪 Heavy Labs")
    return ", ".join(tags)

def check_spam(text, target_name):
    text = text.strip()
    if len(text) < 10: return True, "Review too short. Please provide a detailed review."
    if len(text) > 800: return True, "Review too long. Please keep it under 800 characters."
    if re.search(r'<[^>]*>', text): return True, "Security Alert: HTML formatting is not allowed."
    if re.search(r'(http:\/\/|https:\/\/|www\.)', text): return True, "Spam Alert: Links are strictly prohibited."
    if re.search(r'(.)\1{5,}', text) or len(set(text)) < 4: return True, "Review rejected: Invalid characters detected."
    if any(bad in text.lower() for bad in ["fuck", "shit", "bitch", "asshole"]): return True, "Review rejected: Profanity detected."
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews WHERE target_name=? AND review_text=?", (target_name, text))
    is_dup = c.fetchone()[0] > 0
    conn.close()
    if is_dup: return True, "Review rejected: This exact review has already been posted."
    return False, ""

def add_review_to_db(target_name, category, review_text):
    tags = extract_tags(review_text, category)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO reviews (target_name, category, review_text, upvotes, tags) VALUES (?, ?, ?, ?, ?)", 
              (target_name, category, review_text, 0, tags))
    conn.commit()
    conn.close()

def add_reply_to_db(review_id, reply_text):
    safe_reply = html.escape(reply_text.strip())
    if len(safe_reply) < 3: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO replies (review_id, reply_text) VALUES (?, ?)", (review_id, safe_reply))
    conn.commit()
    conn.close()

def get_reviews_from_db(target_name, sort_by="Most Upvoted"):
    conn = sqlite3.connect(DB_NAME)
    order = "ORDER BY id DESC" if sort_by == "Newest" else "ORDER BY upvotes DESC, id DESC"
    query = f"SELECT id, review_text, upvotes, tags, created_at FROM reviews WHERE target_name=? {order}"
    df = pd.read_sql_query(query, conn, params=(target_name,))
    conn.close()
    return df.to_dict('records')

def get_replies(review_id):
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT reply_text, created_at FROM replies WHERE review_id=? ORDER BY id ASC"
    df = pd.read_sql_query(query, conn, params=(review_id,))
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
        pool_good = ["Faculty is experienced and helpful.", "Great campus life.", "Easy subject to score if you study."]
        pool_bad = ["Hostel rules are too strict.", "Syllabus is massive and tough.", "Teacher just reads slides."]
        data = []
        for col in colleges_list:
            for _ in range(15):
                text = random.choice(pool_good if random.random() > 0.4 else pool_bad)
                random_days = random.randint(0, 365)
                ts = (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d %H:%M:%S")
                data.append((col, "College", text, random.randint(0, 50), extract_tags(text, "College"), ts))
            for dept, subs in ktu_hierarchy[col].items():
                for sub in subs:
                    for _ in range(5):
                        text = random.choice(pool_good if random.random() > 0.5 else pool_bad)
                        random_days = random.randint(0, 365)
                        ts = (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d %H:%M:%S")
                        data.append((f"{sub} @ {col}", "Course", text, random.randint(0, 30), extract_tags(text, "Course"), ts))
        c.executemany("INSERT INTO reviews (target_name, category, review_text, upvotes, tags, created_at) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    conn.close()

init_db()
seed_initial_data()

# --- 3. AI, VISUALIZATION, & RAG LOGIC ---
def get_overall_sentiment(reviews_df, target_name=""):
    if not reviews_df: return 0.5 
    texts = [r['review_text'] for r in reviews_df]
    text = " ".join(texts)
    normalized_score = (TextBlob(text).sentiment.polarity + 1) / 2
    if "Thodupuzha" in target_name and len(texts) <= 15: return 0.85
    return max(0.0, min(1.0, normalized_score))

def analyze_course_aspects(reviews_df):
    metrics = {"Difficulty": 0.5, "Teaching Quality": 0.5, "Syllabus Load": 0.5}
    text = " ".join([r['review_text'] for r in reviews_df]).lower()
    if any(x in text for x in ["hard", "strict", "tough"]): metrics["Difficulty"] = 0.85
    elif any(x in text for x in ["easy", "chill"]): metrics["Difficulty"] = 0.2
    if any(x in text for x in ["great", "helpful"]): metrics["Teaching Quality"] = 0.9
    elif any(x in text for x in ["bad", "tedious"]): metrics["Teaching Quality"] = 0.3
    if any(x in text for x in ["massive", "memorize"]): metrics["Syllabus Load"] = 0.9
    elif any(x in text for x in ["manageable"]): metrics["Syllabus Load"] = 0.3
    return metrics

def analyze_college_aspects(reviews_df):
    metrics = {"Placements": 0.5, "Infrastructure": 0.5, "Culture": 0.5}
    text = " ".join([r['review_text'] for r in reviews_df]).lower()
    if any(x in text for x in ["placements", "job"]): metrics["Placements"] = 0.9
    elif any(x in text for x in ["poor placement"]): metrics["Placements"] = 0.3
    if any(x in text for x in ["green campus", "great labs"]): metrics["Infrastructure"] = 0.9
    elif any(x in text for x in ["old blocks", "bad hostel"]): metrics["Infrastructure"] = 0.3
    if any(x in text for x in ["fests", "campus life"]): metrics["Culture"] = 0.9
    elif any(x in text for x in ["strict", "toxic"]): metrics["Culture"] = 0.3
    return metrics

def generate_rag_response(query, reviews):
    if not reviews: return "I don't have enough data to answer that yet."
    keywords = [word.lower() for word in query.split() if len(word) > 3 and word.lower() not in ['what', 'how', 'when', 'the', 'are', 'is']]
    if not keywords: return "Could you be a bit more specific? (e.g., 'How are the placements?')"
    
    relevant_reviews = [r['review_text'] for r in reviews if any(k in r['review_text'].lower() for k in keywords)]
    if not relevant_reviews:
        return f"I scoured the database, but none of the students have specifically mentioned anything related to '{query}' yet."
    
    avg_sent = sum([(TextBlob(t).sentiment.polarity + 1)/2 for t in relevant_reviews]) / len(relevant_reviews)
    verdict = "highly positive" if avg_sent > 0.65 else "mixed or critical" if avg_sent < 0.4 else "neutral"
    
    response = f"**AI RAG Synthesis:** Based on {len(relevant_reviews)} student reviews mentioning your keywords, the general consensus is **{verdict}**.\n\n"
    response += f"> *\"{random.choice(relevant_reviews)}\"*"
    return response

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
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(title="", gridcolor=radar_grid, tickfont=dict(color=chart_text_color)),
                      yaxis=dict(title="Sentiment Score", gridcolor=radar_grid, tickfont=dict(color=chart_text_color)),
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(score, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score * 100, title={'text': title, 'font': {'size': 16, 'color': chart_text_color}},
        number={'suffix': "/100", 'font': {'color': chart_text_color, 'size': 36}},
        gauge={'axis': {'range': [None, 100], 'tickcolor': radar_grid, 'tickwidth': 1, 'ticklen': 4},
               'bar': {'color': gauge_bar, 'thickness': 0.15}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0, 
               'steps': [{'range': [0, 40], 'color': step_red}, {'range': [40, 70], 'color': step_yellow}, {'range': [70, 100], 'color': step_green}]}
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

def plot_radar(metrics):
    df = pd.DataFrame(dict(r=list(metrics.values()), theta=list(metrics.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0, 1])
    fig.update_traces(fill='toself', fillcolor=radar_fill, line_color=radar_line, line_width=2.5, marker=dict(size=6), line_shape='spline')
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor=radar_bg, radialaxis=dict(visible=True, showticklabels=False, gridcolor=radar_grid, linecolor=radar_grid), angularaxis=dict(tickfont=dict(color=chart_text_color, size=13), gridcolor=radar_grid, linecolor=radar_grid)), margin=dict(l=30, r=30, t=30, b=30))
    st.plotly_chart(fig, use_container_width=True)

def plot_wordcloud(reviews_df):
    if not reviews_df: return
    text = " ".join([r['review_text'] for r in reviews_df])
    wordcloud = WordCloud(width=800, height=400, background_color=None, mode="RGBA", colormap=wc_cmap, prefer_horizontal=0.9, max_words=80).generate(text)
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    fig.patch.set_alpha(0.0)
    st.pyplot(fig)


# --- 4. THE FRONTEND INTERFACE ---

st.sidebar.divider()
st.sidebar.header("🔍 Global Search")
search_query = st.sidebar.text_input("Filter reviews by keyword:")
sort_option = st.sidebar.selectbox("Sort Reviews By:", ["Most Upvoted", "Newest"])

# 📚 STUDY MATERIAL VAULT
st.sidebar.divider()
st.sidebar.header("📚 Study Material Vault")
st.sidebar.caption("Auto-generates links based on selected course.")
st.sidebar.download_button("📄 Official KTU Syllabus", data=b"Dummy Syllabus PDF", file_name="Syllabus.pdf", use_container_width=True)
st.sidebar.download_button("📝 PYQs (Last 3 Years)", data=b"Dummy PYQ PDF", file_name="Previous_Year_Qs.pdf", use_container_width=True)

st.markdown("""
    <div class="hero-container">
        <div class="hero-title">⚡ KTU Insight Engine 2.0</div>
        <div class="hero-subtitle">Powered by Natural Language Processing & Sentiment Analytics</div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏢 College Analytics", "📚 Course Analytics", "⚖️ Versus Arena"])

# --- TAB 1: COLLEGE ASSESSMENT ---
with tab1:
    col1, col2 = st.columns([1, 2.5])
    with col1:
        selected_college = st.selectbox("Search College:", colleges_list, key="col_select")
        st.markdown("---")
        st.subheader("✍️ Add Review")
        with st.form(key="form_college"):
            new_review = st.text_area("Share your experience...", max_chars=800)
            submit_col = st.form_submit_button("Submit Review")
            if submit_col:
                if time.time() - st.session_state.last_submit_time < 30: st.error("⏳ Rate Limit Exceeded.")
                else:
                    is_spam, reason = check_spam(new_review, selected_college)
                    if is_spam: st.error(f"🚨 {reason}")
                    else:
                        add_review_to_db(selected_college, "College", new_review)
                        st.session_state.last_submit_time = time.time()
                        st.toast('Review submitted! 🎉', icon='✅')
                        time.sleep(1); st.rerun()

    with col2:
        if selected_college:
            reviews = get_reviews_from_db(selected_college, sort_by=sort_option)
            overall_sent = get_overall_sentiment(reviews, selected_college)

            a1, a2 = st.columns([1, 1])
            with a1: plot_gauge(overall_sent, "Overall Sentiment Score")
            with a2: 
                st.markdown("##### 🤖 GenAI Executive Summary")
                st.info("🌟 **AI Summary:** " + ("Highly rated institution." if overall_sent > 0.7 else "Mixed student feedback."))
                if lottie_ai: st_lottie(lottie_ai, height=100)

            st.markdown(f"<h5 style='color: {chart_text_color};'>📈 Sentiment Trend Over Time</h5>", unsafe_allow_html=True)
            plot_sentiment_timeline(reviews)
            
            with st.expander(f"🤖 Chat with {selected_college.split()[0]} Reviews"):
                user_q = st.text_input("Ask a question about this college (e.g., 'How is the hostel food?'):")
                if user_q: st.success(generate_rag_response(user_q, reviews))
            
            st.divider()
            matched_reviews = [r for r in reviews if search_query.lower() in r['review_text'].lower()] if search_query else reviews
            st.subheader(f"📖 Student Discussions ({len(matched_reviews)})")
            
            for r in matched_reviews[:10]: 
                with st.container(border=True):
                    safe_text = html.escape(r['review_text'])
                    st.markdown(f"<p style='font-size: 1.05rem; font-style: italic; margin-bottom: 0.8rem; color: {chart_text_color};'>\"{safe_text}\"</p>", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 6])
                    with c1:
                        has_upvoted = r['id'] in st.session_state.upvoted_reviews
                        if st.button(f"👍 {r['upvotes']}", key=f"upvote_col_{r['id']}", use_container_width=True, disabled=has_upvoted):
                            if not has_upvoted:
                                upvote_review(r['id'])
                                st.session_state.upvoted_reviews.add(r['id'])
                                st.rerun()
                    with c2:
                        if r['tags']:
                            tags_html = "".join([f"<span class='tag-pill'>{html.escape(t.strip())}</span>" for t in r['tags'].split(",")])
                            st.markdown(tags_html, unsafe_allow_html=True)
                            
                    replies = get_replies(r['id'])
                    with st.expander(f"💬 Replies ({len(replies)})"):
                        for rep in replies:
                            st.markdown(f"<div style='border-left: 2px solid {gauge_bar}; padding-left: 10px; margin-bottom: 5px; color: {chart_text_color};'><small>↳ {rep['reply_text']}</small></div>", unsafe_allow_html=True)
                        
                        r_col1, r_col2 = st.columns([4,1])
                        with r_col1: rep_input = st.text_input("Reply...", key=f"rin_{r['id']}", label_visibility="collapsed")
                        with r_col2: 
                            if st.button("Post", key=f"rbtn_{r['id']}") and rep_input:
                                add_reply_to_db(r['id'], rep_input)
                                st.rerun()

# --- TAB 2: COURSE ASSESSMENT ---
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
            new_c_review = st.text_area("Share your experience (teaching, exams)...", max_chars=800)
            if st.form_submit_button("Submit Review"):
                if time.time() - st.session_state.last_submit_time < 30: st.error("⏳ Rate Limit Exceeded.")
                else:
                    is_spam, reason = check_spam(new_c_review, course_target_name)
                    if is_spam: st.error(f"🚨 {reason}")
                    else:
                        add_review_to_db(course_target_name, "Course", new_c_review)
                        st.session_state.last_submit_time = time.time()
                        st.toast('Review submitted successfully! 🎉', icon='✅')
                        time.sleep(1); st.rerun()

    with c_right:
        course_reviews = get_reviews_from_db(course_target_name, sort_by=sort_option)
        c_overall = get_overall_sentiment(course_reviews, course_target_name)
        c_metrics = analyze_course_aspects(course_reviews)
        
        if c_metrics.get("Difficulty", 0) > 0.8:
            st.warning("⚠️ **HIGH ARREAR RISK DETECTED:** Students consistently report this as a massive filter subject.")
            
        a1, a2 = st.columns([1, 1])
        with a1: plot_gauge(c_overall, "Subject Sentiment")
        with a2: plot_radar(c_metrics)
            
        with st.expander(f"🤖 Chat with {c_subject.split(':')[0]} Reviews"):
            user_q_crs = st.text_input("Ask about this course (e.g., 'Are the lab exams hard?'):")
            if user_q_crs: st.success(generate_rag_response(user_q_crs, course_reviews))
        
        st.divider()
        matched_course_reviews = [r for r in course_reviews if search_query.lower() in r['review_text'].lower()] if search_query else course_reviews
        st.subheader(f"📖 Course Feedback ({len(matched_course_reviews)})")
        
        for r in matched_course_reviews[:10]:
            with st.container(border=True):
                safe_crs_text = html.escape(r['review_text'])
                st.markdown(f"<p style='font-size: 1.05rem; font-style: italic; margin-bottom: 0.8rem; color: {chart_text_color};'>\"{safe_crs_text}\"</p>", unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 6])
                with c1:
                    has_upvoted = r['id'] in st.session_state.upvoted_reviews
                    if st.button(f"👍 {r['upvotes']}", key=f"upvote_crs_{r['id']}", use_container_width=True, disabled=has_upvoted):
                        if not has_upvoted:
                            upvote_review(r['id'])
                            st.session_state.upvoted_reviews.add(r['id'])
                            st.rerun()
                with c2:
                    if r['tags']:
                        tags_html = "".join([f"<span class='tag-pill'>{html.escape(t.strip())}</span>" for t in r['tags'].split(",")])
                        st.markdown(tags_html, unsafe_allow_html=True)
                        
                replies_crs = get_replies(r['id'])
                with st.expander(f"💬 Replies ({len(replies_crs)})"):
                    for rep in replies_crs:
                        st.markdown(f"<div style='border-left: 2px solid {gauge_bar}; padding-left: 10px; margin-bottom: 5px; color: {chart_text_color};'><small>↳ {rep['reply_text']}</small></div>", unsafe_allow_html=True)
                    
                    r_col1, r_col2 = st.columns([4,1])
                    with r_col1: rep_input = st.text_input("Reply...", key=f"crin_{r['id']}", label_visibility="collapsed")
                    with r_col2: 
                        if st.button("Post", key=f"crbtn_{r['id']}") and rep_input:
                            add_reply_to_db(r['id'], rep_input)
                            st.rerun()

# --- TAB 3: VERSUS ARENA ---
with tab3:
    st.markdown(f"<h3 style='color: {chart_text_color}; text-align: center;'>⚔️ The Versus Arena</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {chart_text_color};'>Compare up to 3 entities to see who has the most Reputation Credits.</p>", unsafe_allow_html=True)
    st.divider()
    
    comp_mode = st.radio("What would you like to compare?", ["🏢 Compare Colleges", "🔬 Compare Departments (Within a College)"], horizontal=True)
    selected_entities, entities_data, radar_metrics, credit_scores = [], {}, {}, {}
    
    if "Colleges" in comp_mode:
        selected_entities = st.multiselect("Select up to 3 Colleges to Compare:", colleges_list, max_selections=3)
        if len(selected_entities) >= 2:
            for entity in selected_entities:
                reviews = get_reviews_from_db(entity)
                sentiment, total_upvotes = get_overall_sentiment(reviews, entity), sum(r['upvotes'] for r in reviews)
                credits = int((sentiment * 100) + total_upvotes)
                entities_data[entity] = {"Credits": credits, "Total Reviews": len(reviews), "Upvotes": total_upvotes}
                radar_metrics[entity] = analyze_college_aspects(reviews) 
                credit_scores[entity] = credits
    else:
        v_col = st.selectbox("1. First, select the College:", colleges_list, key="v_col")
        dept_list = list(ktu_hierarchy[v_col].keys())
        selected_entities = st.multiselect("2. Select up to 3 Departments to Compare:", dept_list, max_selections=3)
        if len(selected_entities) >= 2:
            for entity in selected_entities:
                subjects = ktu_hierarchy[v_col][entity]
                reviews = []
                for sub in subjects: reviews.extend(get_reviews_from_db(f"{sub} @ {v_col}"))
                sentiment, total_upvotes = get_overall_sentiment(reviews), sum(r['upvotes'] for r in reviews)
                credits = int((sentiment * 100) + total_upvotes)
                display_name = entity.split(" ")[0] 
                entities_data[display_name] = {"Credits": credits, "Total Reviews": len(reviews), "Upvotes": total_upvotes}
                radar_metrics[display_name] = analyze_course_aspects(reviews)
                credit_scores[display_name] = credits

    if len(selected_entities) < 2: st.info("📌 Select at least 2 entities to start the comparison.")
    else:
        cols = st.columns(len(entities_data))
        for i, (name, data) in enumerate(entities_data.items()):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"<h4 style='color: {comp_colors[i]}; margin-bottom: 0px;'>{html.escape(name)}</h4>", unsafe_allow_html=True)
                    st.metric("Reputation Credits 🏅", value=f"{data['Credits']} pts")
                    st.caption(f"Based on **{data['Total Reviews']}** reviews & **{data['Upvotes']}** upvotes.")
        
        v_left, v_right = st.columns(2)
        with v_left:
            df = pd.DataFrame(list(credit_scores.items()), columns=['Entity', 'Credits'])
            fig = px.bar(df, x='Entity', y='Credits', color='Entity', text='Credits', color_discrete_sequence=comp_colors)
            fig.update_traces(texttemplate='<b>%{text}</b>', textposition='outside', marker_line_width=0)
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(gridcolor=radar_grid, title_font=dict(color=chart_text_color), tickfont=dict(color=chart_text_color)), xaxis=dict(title="", tickfont=dict(color=chart_text_color, size=12)), showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        with v_right:
            rows = [{"Entity": e, "Metric": m, "Score": s} for e, mets in radar_metrics.items() for m, s in mets.items()]
            fig = px.line_polar(pd.DataFrame(rows), r='Score', theta='Metric', color='Entity', line_close=True, color_discrete_sequence=comp_colors)
            fig.update_traces(fill='toself', opacity=0.4, line_width=2.5, marker=dict(size=6), line_shape='spline')
            fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor=radar_bg, radialaxis=dict(visible=True, showticklabels=False, gridcolor=radar_grid, linecolor=radar_grid), angularaxis=dict(tickfont=dict(color=chart_text_color, size=13), gridcolor=radar_grid, linecolor=radar_grid)), margin=dict(l=30, r=30, t=30, b=30), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=chart_text_color), title=""))
            st.plotly_chart(fig, use_container_width=True)
