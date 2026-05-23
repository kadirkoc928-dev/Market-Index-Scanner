import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- STREAMLIT PAGE CONFIG (Optimiert für Sidebar/Rechte Bildschirmseite) ---
st.set_page_config(
    page_title="Swing Score Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS für einen professionellen Dark-Trader-Look und kompakte Darstellung
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    h1 { font-size: 22px !important; font-weight: bold; color: #f0f2f6; text-align: center; margin-bottom: 20px;}
    h2 { font-size: 16px !important; color: #10b981;}
    .metric-box { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; text-align: center; }
    .score-long { color: #00e676; font-weight: bold; font-size: 18px; }
    .score-short { color: #ff1744; font-weight: bold; font-size: 18px; }
    .score-neutral { color: #b0bec5; font-weight: bold; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ PRO SWING TRADER DASHBOARD")

# --- INDIZES DEFINIEREN ---
TICKERS = {
    "S&P 500 (SPY)": "SPY",
    "Nasdaq 100 (QQQ)": "QQQ",
    "S&P 500 Index": "^GSPC",
    "Nasdaq 100 Index": "^IXIC",
    "Russell 2000": "^RUT",
    "Dow Jones": "^DJI",
    "DAX 40": "^GDAXI",
    "Nikkei 225": "^N225"
}

# --- FUNKTION: INDIKATOREN BERECHNEN ---
def calculate_indicators(df):
    if len(df) < 50:
        return None
    
    df = df.dropna(subset=['Close'])
    
    # 1. Gleitende Durchschnitte (Trend)
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    
    # 2. RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / np.where(loss == 0, 0.00001, loss)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    
    return df.iloc[-1]

# --- DATA FETCHING ---
@st.cache_data(ttl=900)
def get_market_data():
    data_results = {}
    for name, ticker in TICKERS.items():
        try:
            asset = yf.Ticker(ticker)
            df = asset.history(period="6mo", interval="1d")
            if not df.empty and len(df) >= 50:
                calculated = calculate_indicators(df)
                if calculated is not None:
                    data_results[name] = calculated
        except Exception:
            pass
            
    vix_val = 15.0
    try:
        vix_df = yf.Ticker("^VIX").history(period="1d")
        if not vix_df.empty:
            vix_val = vix_df['Close'].iloc[-1]
    except:
        pass
        
    return data_results, vix_val

# Daten laden
data, vix = get_market_data()

# --- SIDEBAR / GLOBAL METRICS ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    if vix < 15:
        vix_status = "🟢 Risk-On (Niedrige Angst)"
    elif vix <= 23:
        vix_status = "🟡 Moderates Risiko"
    else:
        vix_status = "🔴 Risk-Off (Hohe Panik!)"
    st.metric(label="VIX (S&P 500 Volatilität)", value=f"{vix:.2f}", delta=vix_status, delta_color="normal")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    valid_rsis = [data[idx]['RSI'] for idx in data if data[idx] is not None and 'RSI' in data[idx]]
    if valid_rsis:
        avg_rsi = np.mean(valid_rsis)
        fg_score = int(avg_rsi * 0.7 + (40 - vix) * 1.5)
        fg_score = max(0, min(100, fg_score))
    else:
        fg_score = 50
        
    if fg_score < 30: fg_text = "😨 Extreme Angst"
    elif fg_score < 45: fg_text = "😰 Angst"
    elif fg_score < 55: fg_text = "😐 Neutral"
    elif fg_score < 75: fg_text = "🤑 Gier"
    else: fg_text = "🚨 Extreme Gier"
    
    st.metric(label="Fear & Greed Index", value=f"{fg_score} / 100", delta=fg_text)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# --- SWING SCORE BERECHNUNG & TABELLE ---
st.subheader("📊 Index Swing-Scores (1D Chart)")

rows = []
for name, current in data.items():
    if current is None: 
        continue
    
    required_keys = ['Close', 'EMA21', 'SMA50', 'MACD_Hist', 'RSI']
    if not all(key in current for key in required_keys):
        continue
        
    score = 0
    
    # 1. Trend Filter
    if current['Close'] > current['EMA21'] and current['EMA21'] > current['SMA50']:
        score += 50
    elif current['Close'] < current['EMA21'] and current['EMA21'] < current['SMA50']:
        score -= 50
        
    # 2. Momentum Filter
    if current['MACD_Hist'] > 0:
        score += 30
    else:
        score -= 30
        
    # 3. RSI Erschöpfung
    if 30 <= current['RSI'] <= 65:
        score += 20
    elif current['RSI'] > 70:
        score -= 10
    elif current['RSI'] < 30:
        score += 20
        
    if score >= 40:
        signal = "🚀 STRONG LONG"
    elif score > 0:
        signal = "📈 Lichte Long-Tendenz"
    elif score <= -40:
        signal = "💥 STRONG SHORT"
    else:
        signal = "📉 Lichte Short-Tendenz"

    # 🛡️ FIX: Die Spaltennamen hier stimmen jetzt 1:1 mit den Ausgabevariablen überein
    rows.append({
        "Index": name,
        "Preis": f"{current['Close']:.2f}",
        "RSI": f"{current['RSI']:.1f}",
        "Swing Score": score,
        "Signal Setup": signal
    })

if rows:
    df_display = pd.DataFrame(rows)
    for index, row in df_display.iterrows():
        score_val = row['Swing Score']
        if score_val >= 40:
            score_class = "score-long"
        elif score_val <= -40:
            score_class = "score-short"
        else:
            score_class = "score-neutral"
            
        with st.expander(f"**{row['Index']}** | Score: {score_val} | {row['Signal Setup']}", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.write(f"**Kurs:** {row['Preis']}")
            col_b.write(f"**RSI (14):** {row['RSI']}") # 🛡️ Hier greift es jetzt sauber auf row['RSI'] zu
            col_c.markdown(f"**Score:** <span class='{score_class}'>{score_val}</span>", unsafe_allow_html=True)
else:
    st.info("Warte auf Marktdaten... Bitte Seite in Kürze neu laden.")

st.caption("Live-Daten aktualisieren sich automatisch alle 15 Minuten. Basis: TradingView Standard-Indikatoren-Setups.")
