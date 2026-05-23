# 📈 Professional Swing Score & Market Sentiment Dashboard

Dieses interaktive Dashboard wurde für Swing-Trader entwickelt, um die wichtigsten globalen Indizes auf dem 1-Tages-Chart (Daily) nach einem mathematischen **Swing Score** zu analysieren. Es kombiniert Trend-, Momentum- und Volatilitätsindikatoren im Stil von TradingView.

## 🚀 Features
- **Live-Daten:** Abruf über Yahoo Finance (SPY, QQQ, ^GSPC, ^IXIC, ^RUT, ^DJI, ^GDAXI, ^N225).
- **Profi Swing Score (-100 bis +100):** Dynamische Berechnung basierend auf EMA 21 vs. SMA 50, RSI (14) und MACD.
- **VIX Volatilitäts-Indikator:** Live-Auswertung der Markt-Angst.
- **Fear & Greed Proxy:** Berechnet aus der relativen Stärke der Indizes und der VIX-Lage.
- **Stream-Optimiert:** Perfekt als schmale Sidebar (rechte Bildschirmseite) im Livestream nutzbar.

## 🛠️ Installation & Start
1. Repository klonen: `git clone <dein-repo-link>`
2. Abhängigkeiten installieren: `pip install -r requirements.txt`
3. App starten: `streamlit run app.py`
