import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. PREMIUM PRO TRADER CONFIG ---
st.set_page_config(
    page_title="ALPHA SWING SCANNER",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# DESIGN-SETUP: Extrem dunkel, neon-akzentuiert, kompakt für OBS-Seitenleisten (350px-450px)
st.markdown("""
<style>
    /* Hintergrund & Globales Styling */
    .stApp { background-color: #0b0e14; color: #bc9ec1; }
    .block-container { padding-top: 1rem; padding-bottom: 0.5rem; padding-left: 0.75rem; padding-right: 0.75rem; }
    
    /* Header */
    .main-title { font-family: 'Courier New', monospace; font-size: 19px; font-weight: 900; letter-spacing: 2px; text-align: center; color: #00e676; margin-bottom: 12px; text-shadow: 0 0 10px rgba(0,230,118,0.3); }
    
    /* Markt-Stimmungs-Boxen */
    .sentiment-container { display: flex; gap: 8px; margin-bottom: 15px; }
    .sentiment-card { flex: 1; background: linear-gradient(135deg, #121824, #1a2333); border: 1px solid #243249; border-radius: 6px; padding: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .sentiment-label { font-size: 10px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; margin-bottom: 2px; }
    .sentiment-value { font-size: 18px; font-weight: bold; color: #ffffff; }
    .sentiment-sub { font-size: 9px; margin-top: 2px; font-weight: bold; }

    /* Index Heatmap Kacheln */
    .index-grid { display: flex; flex-direction: column; gap: 8px; }
    .index-card { background: #121824; border-left: 5px solid #475569; border-top: 1px solid #1e293b; border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b; border-radius: 4px; padding: 10px; transition: all 0.2s; }
    
    /* Dynamische Signal-Rahmen */
    .border-strong-long { border-left-color: #00e676 !important; background: linear-gradient(90deg, #13251d, #121824); }
    .border-long { border-left-color: #00b0ff !important; background: linear-gradient(90deg, #112233, #121824); }
    .border-strong-short { border-left-color: #ff1744 !important; background: linear-gradient(90deg, #2d141a, #121824); }
    .border-short { border-left-color: #ff9100 !important; background: linear-gradient(90deg, #281e15, #121824); }

    /* Kachelinhalt */
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .index-name { font-weight: bold; font-size: 13px; color: #ffffff; }
    .score-badge { font-family: 'Courier
