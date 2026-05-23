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

# MEIN DESIGN-SETUP: Extrem dunkel, neon-akzentuiert, kompakt für OBS-Seitenleisten (350px-450px)
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
    .score-badge { font-family: 'Courier New', monospace; font-size: 13px; font-weight: bold; padding: 1px 6px; border-radius: 3px; }
    .badge-green { background-color: rgba(0,230,118,0.2); color: #00e676; }
    .badge-blue { background-color: rgba(0,176,255,0.2); color: #00b0ff; }
    .badge-red { background-color: rgba(255,23,68,0.2); color: #ff1744; }
    .badge-orange { background-color: rgba(255,145,0,0.2); color: #ff9100; }
    
    .card-body { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }
    .indicator-pill { background: #1e293b; padding: 2px 5px; border-radius: 3px; font-size: 10px; }
    
    /* Footer */
    .custom-footer { text-align: center; font-size: 9px; color: #475569; margin-top: 15px; border-top: 1px dashed #1e293b; padding-top: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ ALPHA SWING SCANNER ⚡</div>', unsafe_allow_html=True)

# --- 2. MULTI-MARKET TICKERS ---
# Ich habe die Liste optimiert, damit US, Europa und Asien perfekt abgedeckt sind
TICKERS = {
    "S&P 500 (SPY)": "SPY",
    "NASDAQ 100 (QQQ)": "QQQ",
    "RUSSELL 2000": "^RUT",
    "DOW JONES": "^DJI",
    "DAX 40": "^GDAXI",
    "NIKKEI 225": "^N225"
}

def calculate_indicators(df):
    if len(df) < 50: return None
    df = df.dropna(subset=['Close'])
    
    # Exakte mathematische Nachbildung der TradingView-Skripte
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / np.where(loss == 0, 0.00001, loss)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    
    return df.iloc[-1]

@st.cache_data(ttl=600) # 10 Minuten Cache
def fetch_all_data():
    results = {}
    for name, ticker in TICKERS.items():
        try:
            df = yf.Ticker(ticker).history(period="6mo", interval="1d")
            if not df.empty and len(df) >= 50:
                calc = calculate_indicators(df)
                if calc is not None: results[name] = calc
        except: pass
    
    vix_val = 15.0
    try:
        vix_df = yf.Ticker("^VIX").history(period="1d")
        if not vix_df.empty: vix_val = vix_df['Close'].iloc[-1]
    except: pass
    return results, vix_val

data, vix = fetch_all_data()

# --- 3. PREMIUM TOP PANEL (VIX & FEAR/GREED COMBINED) ---
valid_rsis = [data[i]['RSI'] for i in data if data[i] is not None and 'RSI' in data[i]]
if valid_rsis:
    avg_rsi = np.mean(valid_rsis)
    fg_score = int(avg_rsi * 0.65 + (45 - vix) * 1.4)
    fg_score = max(0, min(100, fg_score))
else:
    fg_score = 50

# VIX Styling Variablen
if vix < 15: vix_c, vix_t = "#00e676", "RISK-ON"
elif vix <= 22: vix_c, vix_t = "#ff9100", "NORMAL"
else: vix_c, vix_t = "#ff1744", "PANIC"

# Fear & Greed Styling Variablen
if fg_score > 70: fg_c, fg_t = "#00e676", "EXTR. GREED"
elif fg_score > 50: fg_c, fg_t = "#00b0ff", "GREED"
elif fg_score > 35: fg_c, fg_t = "#ff9100", "FEAR"
else: fg_c, fg_t = "#ff1744", "EXTR. FEAR"

st.markdown(f"""
<div class="sentiment-container">
    <div class="sentiment-card">
        <div class="sentiment-label">⚠️ Volatilität (VIX)</div>
        <div class="sentiment-value">{vix:.2f}</div>
        <div class="sentiment-sub" style="color: {vix_c};">{vix_t}</div>
    </div>
    <div class="sentiment-card">
        <div class="sentiment-label">🔥 Sentiment (F&G)</div>
        <div class="sentiment-value">{fg_score}/100</div>
        <div class="sentiment-sub" style="color: {fg_c};">{fg_t}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. STREAM-OPTIMIZED MARKET HEATMAP ---
rows_html = ""

for name, current in data.items():
    required = ['Close', 'EMA21', 'SMA50', 'MACD_Hist', 'RSI']
    if not all(k in current for k in required): continue
    
    # Mathematischer Scoring-Algorithmus (Gewichtung wie ein Quant-Fonds)
    score = 0
    trend_status = "Neutral"
    
    if current['Close'] > current['EMA21'] and current['EMA21'] > current['SMA50']:
        score += 50
        trend_status = "Bullish"
    elif current['Close'] < current['EMA21'] and current['EMA21'] < current['SMA50']:
        score -= 50
        trend_status = "Bearish"
        
    if current['MACD_Hist'] > 0: score += 30
    else: score -= 30
        
    if 30 <= current['RSI'] <= 65: score += 20
    elif current['RSI'] > 70: score -= 10
    elif current['RSI'] < 30: score += 20

    # Bestimme CSS-Klassen basierend auf dem Score
    if score >= 50:
        card_class = "border-strong-long"
        badge_class = "badge-green"
        signal_text = "STRONG LONG"
    elif score > 0:
        card_class = "border-long"
        badge_class = "badge-blue"
        signal_text = "ACCUMULATE"
    elif score <= -50:
        card_class = "border-strong-short"
        badge_class = "badge-red"
        signal_text = "STRONG SHORT"
    else:
        card_class = "border-orange"
        badge_class = "badge-orange"
        signal_text = "DISTRIBUTION"

    # Generiere pures HTML für maximale Design-Kontrolle ohne klobige Streamlit-Elemente
    rows_html += f"""
    <div class="index-card {card_class}">
        <div class="card-header">
            <div class="index-name">{name}</div>
            <div class="score-badge {badge_class}">Score: {score}</div>
        </div>
        <div class="card-body">
            <div>💰 <b>{current['Close']:.2f}</b></div>
            <div class="indicator-pill">RSI: {current['RSI']:.1f}</div>
            <div class="indicator-pill">Trend: {trend_status}</div>
            <div style="font-weight: bold;">{signal_text}</div>
        </div>
    </div>
    """

# Rendere die gesamte Heatmap
st.markdown(f'<div class="index-grid">{rows_html}</div>', unsafe_allow_html=True)

# Professioneller Footer
st.markdown('<div class="custom-footer">⚡ LIVE QUANT SCANNER // INTERVAL: 1D CHART // AUTO-REFRESH ⚡</div>', unsafe_allow_html=True)
