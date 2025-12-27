import streamlit as st
import pandas as pd
import yfinance as yf

# --- AYARLAR & TASARIM (Hacker Teması - Sadece Emoji Logolu) ---
st.set_page_config(page_title="MirZ Scanner", layout="wide", page_icon="🐰")

st.markdown("""
<style>
    /* Ana Arka Plan: KAPKARA */
    .stApp { background-color: #0e1117; color: #00ff41; }
    
    /* Yan Menü: Siyah ve Yeşil Çizgili */
    [data-testid="stSidebar"] { background-color: #000000; border-right: 2px solid #00ff41; }
    
    /* Butonlar: Neon Yeşil */
    .stButton > button { 
        color: #000000; 
        background-color: #00ff41; 
        border: none; 
        font-weight: bold; 
        font-size: 18px; 
        padding: 10px;
        width: 100%;
        text-transform: uppercase;
        border-radius: 0px; /* Keskin köşeler */
    }
    .stButton > button:hover { background-color: #00cc33; color: white; box-shadow: 0 0 10px #00ff41; }
    
    /* Yazı Tipleri: Terminal Havası */
    h1, h2, h3 { color: #00ff41 !important; font-family: 'Courier New', monospace; font-weight: bold; }
    p, div, span { font-family: 'Courier New', monospace; }
    
    /* Tablo Tasarımı */
    div[data-testid="stDataFrame"] { border: 1px solid #00ff41; }
    
    /* Radyo Butonları */
    .stRadio > div { color: #00ff41; background-color: #111; padding: 10px; border: 1px solid #333; }
    
    /* LOGO ALANI (Sadece Emoji) */
    .logo-box { text-align: center; padding: 20px; border-bottom: 2px dashed #00ff41; margin-bottom: 20px; }
    .emoji-logo { font-size: 80px; margin: 0; letter-spacing: -10px; } /* Emojileri büyüttüm ve yaklaştırdım */
</style>
""", unsafe_allow_html=True)

# --- HIZLI VERİ MOTORU ---
@st.cache_data(ttl=900)
def get_data_scan(symbol):
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        df.columns = [str(c[0]).lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
        if 'close' in df.columns and len(df) > 200:
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            return df
    except: pass
    return pd.DataFrame()

# --- TARAMA MOTORU ---
def stratejik_tarama(hisse_listesi, strateji):
    sonuclar = []
    bar = st.progress(0)
    durum = st.empty()
    toplam = len(hisse_listesi)
    
    for i, hisse in enumerate(hisse_listesi):
        hisse = hisse.strip()
        durum.code(f"SCANNING >> {hisse} ({i+1}/{toplam})")
        df = get_data_scan(hisse)
        
        if not df.empty and 'close' in df.columns:
            try:
                son = df['close'].iloc[-1]
                rsi = df['rsi'].iloc[-1]
                sma50 = df['sma_50'].iloc[-1]
                sma200 = df['sma_200'].iloc[-1]
                ekle = False
                sinyal = ""
                
                if strateji == "🎯 DİP AVCISI (RSI < 30)":
                    if rsi < 32: ekle = True; sinyal = "AŞIRI UCUZ"
                elif strateji == "🏆 GOLDEN CROSS (50 > 200)":
                    if sma50 > sma200 and son > sma50 and ((sma50-sma200)/sma200)*100 < 5: ekle = True; sinyal = "YENİ RALLİ"
                elif strateji == "🚀 KIRILIM (Trend Start)":
                    if rsi > 50 and rsi < 60 and son > sma50 and son < (sma50 * 1.05): ekle = True; sinyal = "TREND BAŞLANGICI"
                elif strateji == "🐂 MOMENTUM (Güçlü)":
                    if rsi > 60 and rsi < 75 and son > sma50: ekle = True; sinyal = "GÜÇLÜ AL"

                if ekle:
                    sonuclar.append({"HİSSE": hisse.replace(".IS",""), "FİYAT": f"{son:.2f}", "RSI": f"{rsi:.1f}", "SİNYAL": sinyal})
            except: pass
        bar.progress((i+1)/toplam)
    bar.empty(); durum.empty()
    return pd.DataFrame(sonuclar)

# --- LİSTE ---
def get_list():
    raw = "THYAO, GARAN, AKBNK, ISCTR, YKBNK, VAKBN, HALKB, TSKB, SKBNK, ALBRK, SAHOL, KCHOL, SISE, EREGL, KRDMD, TUPRS, PETKM, ASELS, TCELL, TTKOM, BIMAS, MGROS, SOKM, AEFES, CCOLA, FROTO, TOASO, TTRAK, OTKAR, DOAS, ARCLK, VESTL, ENKAI, TEKFEN, PGSUS, TAVHL, GUBRF, HEKTS, KOZAL, KOZAA, IPEKE, OYAKC, CIMSA, AKCNS, EKGYO, ISGYO, TRGYO, SNGYO, ALARK, ODAS, ZOREN, AKSA, AKSEN, AYDEM, GWIND, SMRTG, KONTR, EUPWR, GESAN, ASTOR, ALFA, CWENE, MIATK, SDTTR, YEOTK, KMPUR, BRSAN, TUKAS, ULKER, TATGD, LOGO, INDES, SELEC, ECILC, GENIL, TRILC, TURSG, ANHYT, MAVI, YATAS, KORDS, SARTKY, KLKIM, CEMTS, GOODY, BRISA, JANTS, KCAER, QUAGR, BERA, KONKA, KARTN, BFREN, EGEEN"
    return [f"{h.strip()}.IS" for h in raw.split(',')]

# --- ARAYÜZ (Yan Menü - Sadece Emoji) ---
with st.sidebar:
    # MirZ yazısı kaldırıldı, sadece emojiler kaldı
    st.markdown("<div class='logo-box'><p class='emoji-logo'>🐰🐥</p></div>", unsafe_allow_html=True)
    st.write("")
    st.header("STRATEJİ SEÇ:")
    mod = st.radio("", ["🎯 DİP AVCISI (RSI < 30)", "🏆 GOLDEN CROSS (50 > 200)", "🚀 KIRILIM (Trend Start)", "🐂 MOMENTUM (Güçlü)"])
    st.write("")
    st.write("")
    if st.button("TARAMAYI BAŞLAT 🚀"): st.session_state['run'] = True

# --- ANA EKRAN ---
st.title(f"📊 {mod}")
if st.session_state.get('run'):
    st.info("Sistem çalışıyor... Veriler işleniyor...")
    df = stratejik_tarama(get_list(), mod)
    if not df.empty:
        st.success(f"{len(df)} Fırsat Yakalandı!")
        st.dataframe(df, use_container_width=True, height=600, hide_index=True)
    else: st.warning("Bu kriterde hisse bulunamadı.")
else: st.info("👈 Sol menüden stratejini seç ve butona bas.")
