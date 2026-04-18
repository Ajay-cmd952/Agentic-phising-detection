import streamlit as st
import re
import time
import sqlite3
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import urllib.parse
from utils.orchestrator import AIOrchestrator

def init_db():
    conn = sqlite3.connect('scans.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scan_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, url TEXT, status TEXT, risk_score REAL)''')
    conn.commit()
    conn.close()

def log_to_db(url, status, score):
    conn = sqlite3.connect('scans.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scan_logs (timestamp, url, status, risk_score) VALUES (?, ?, ?, ?)", (now, url, status, score))
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Agentic Phishing Detector", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# --- INDESTRUCTIBLE SESSION STATE ---
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'url_threshold' not in st.session_state: st.session_state.url_threshold = 0.80
if 'fusion_threshold' not in st.session_state: st.session_state.fusion_threshold = 0.60
if 'deep_scan' not in st.session_state: st.session_state.deep_scan = True
if 'theme' not in st.session_state: st.session_state.theme = "Crimson Threat (Dark)"

if 'active_target' not in st.session_state: st.session_state.active_target = None
if 'last_target' not in st.session_state: st.session_state.last_target = ""

@st.cache_resource
def load_ai():
    return AIOrchestrator()
orchestrator = load_ai()

@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_scan(url, deep_scan, url_thresh, fusion_thresh):
    return orchestrator.run_detection(
        url, 
        deep_scan=deep_scan,
        url_threshold=url_thresh,
        fusion_threshold=fusion_thresh
    )

# --- THE UNIVERSAL URL EXTRACTOR ---
analyze_target = ""
show_portal = False

try:
    raw_params = st.query_params.to_dict()
except:
    try:
        raw_params = st.experimental_get_query_params()
    except:
        raw_params = {}

if "analyze_target" in raw_params:
    val = raw_params["analyze_target"]
    analyze_target = val[0] if isinstance(val, list) else val
    
if "auth" in raw_params:
    val = raw_params["auth"]
    show_portal = (val[0] if isinstance(val, list) else val) == "portal"

if analyze_target:
    analyze_target = urllib.parse.unquote(analyze_target)

if analyze_target and st.session_state.last_target != analyze_target:
    st.session_state.last_target = analyze_target
    st.session_state.active_target = analyze_target

with st.sidebar:
    # --- UNIFIED TITLE ---
    st.title("🛡️ Agentic Shield")
    st.markdown("**Threat Intelligence Pipeline**")
    st.markdown("---")
    
    if st.session_state.is_admin:
        app_mode = st.radio("Navigation Menu", ["🔍 Threat Scanner", "📊 Global Analytics", "⚙️ Agent Settings"])
    else:
        app_mode = st.radio("Navigation Menu", ["🔍 Threat Scanner", "📊 Global Analytics"])

    st.markdown("---")
    
    st.session_state.theme = st.radio("🎨 UI Theme", ["Crimson Threat (Dark)", "Enterprise Clean (Light)"])
    st.markdown("---")
    
    st.subheader("Live System Status")
    st.success("🟢 URL Agent (RF): Online")
    if st.session_state.deep_scan:
        st.success("🟢 Content Agent (BERT): Online")
    else:
        st.warning("🟡 Content Agent (BERT): Disabled")
    st.success("🟢 Vision Agent (pyzbar): Online")
    
    st.markdown("---")
    
    # Hidden Portal Logic Remains Active
    if not st.session_state.is_admin:
        if show_portal:
            st.markdown("🔒 **Hidden Admin Portal**")
            admin_password = st.text_input("Enter Password to unlock settings:", type="password")
            if st.button("Unlock Modules", use_container_width=True):
                if admin_password == "admin123":
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("❌ Access Denied")
        else:
            st.caption("Current User: Public Guest")
    else:
        if st.button("🔓 Logout Admin", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
        st.caption("Current User: Administrator")
        
    st.caption("System Version: 8.2 (Stable UX)")

# --- CONDITIONAL CSS STYLING ---
if st.session_state.theme == "Crimson Threat (Dark)":
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #1f0000, #3d0000, #140000, #2b0000); background-size: 300% 300%; animation: cyberGradient 15s ease infinite; }
            @keyframes cyberGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
            .block-container { background: rgba(22, 24, 28, 0.95) !important; backdrop-filter: blur(15px) !important; border: 1px solid rgba(255, 70, 70, 0.3) !important; border-radius: 15px !important; box-shadow: 0 0 40px rgba(255, 50, 50, 0.15) !important; padding: 2.5rem 3rem !important; margin: 2rem auto !important; max-width: 95% !important; }
            [data-testid="stSidebar"] { background-color: #0a0101 !important; border-right: 2px solid rgba(255, 70, 70, 0.4); box-shadow: 5px 0 20px rgba(255, 50, 50, 0.15); }
            div.stButton > button:first-child { background: linear-gradient(90deg, rgba(255,70,70,0.1) 0%, rgba(255,100,100,0.1) 100%); color: #FF4444; border: 1px solid #FF4444; border-radius: 6px; padding: 10px 24px; font-weight: bold; letter-spacing: 1px; transition: all 0.3s ease-in-out; box-shadow: 0 0 10px rgba(255, 70, 70, 0.2); }
            div.stButton > button:first-child:hover { background: linear-gradient(90deg, #FF3333 0%, #FF6666 100%); color: #ffffff !important; box-shadow: 0 0 20px rgba(255, 70, 70, 0.6); transform: translateY(-2px); border: 1px solid transparent; }
            .stTextArea textarea { background-color: #000000 !important; color: #FF8888 !important; border: 1px solid rgba(255, 70, 70, 0.4) !important; font-family: 'Courier New', Courier, monospace !important; border-radius: 6px; }
            .stTextArea textarea:focus { border-color: #FF3333 !important; box-shadow: 0 0 15px rgba(255, 70, 70, 0.5) !important; }
            [data-testid="stMetricValue"] { color: #FF4444 !important; text-shadow: 0 0 10px rgba(255, 70, 70, 0.4); }
        </style>
    """, unsafe_allow_html=True)


# --- MAIN APP LOGIC ---

if app_mode == "🔍 Threat Scanner":
    st.title("Deep Scan Engine")
    st.markdown("Choose your input method below to scan for phishing threats.")
    col_input, col_info = st.columns([2, 1])

    with col_info:
        st.info("**Supported Formats:**\n- Raw URLs (http/https)\n- Raw Email Text\n- SMS Message Text\n- QR Code Screenshots")
        st.warning("**Note:** Do not paste passwords or sensitive API keys into the scanner.")

    with col_input:
        input_tab1, input_tab2 = st.tabs(["📝 Text / URL Input", "📷 QR Code Scanner (Quishing)"])
        
        with input_tab1:
            user_input = st.text_area("Target Data Input:", value=analyze_target, height=150, placeholder="Paste raw text, SMS messages, emails, or direct URLs here...")
            
            if st.button("🚀 Initialize Multi-Agent Scan", type="primary", use_container_width=True):
                st.session_state.active_target = user_input.strip()

        with input_tab2:
            st.info("Upload a screenshot of a suspicious QR code. The Vision Agent will extract the hidden link.")
            qr_upload = st.file_uploader("Upload QR Image", type=['png', 'jpg', 'jpeg'])
            if qr_upload is not None:
                image = Image.open(qr_upload)
                st.image(image, caption="Uploaded QR Code", width=200)
                if st.button("🔍 Decode & Scan QR", type="primary", use_container_width=True):
                    with st.spinner("Vision Agent is decoding image..."):
                        try:
                            img_array = np.array(image.convert('RGB'))
                            decoded_objects = decode(img_array)
                            if decoded_objects:
                                st.success("✅ Vision Agent successfully extracted URL from image.")
                                st.session_state.active_target = decoded_objects[0].data.decode('utf-8')
                            else:
                                st.error("❌ Could not detect a valid QR code in this image.")
                        except Exception as e:
                            st.error(f"⚠️ Image Processing Error: {e}")

    # --- THE EXECUTION ENGINE ---
    if st.session_state.active_target:
        raw_input = st.session_state.active_target
        target_url = None
        
        extraction_pattern = r'((?:https?://|upi://|tel:|wifi:|smsto:|mailto:|matmsg:)[^\s]+|(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})(?:/[^\s]*)?)'
        extracted_urls = re.findall(extraction_pattern, raw_input, re.IGNORECASE)
        
        if extracted_urls:
            target_url = extracted_urls[0]
        elif " " not in raw_input and ("." in raw_input or ":" in raw_input):
            target_url = raw_input
            
        if not target_url:
            st.error("⚠️ No clickable URLs or system commands detected in the input payload.")
        else:
            st.markdown("---")
            st.markdown(f"**🔗 Target Locked:** `{target_url}`")
            
            with st.spinner("🤖 Multi-Agent Pipeline is analyzing the threat..."):
                try:
                    result = get_cached_scan(
                        target_url, 
                        st.session_state.deep_scan,
                        st.session_state.url_threshold,
                        st.session_state.fusion_threshold
                    )
                    
                    status = result.get('prediction', 'Unknown')
                    final_score = result.get('final_score', 0.5)
                    url_risk = result.get('url_risk', 0.5)
                    content_risk = result.get('content_risk', 0.0 if not st.session_state.deep_scan else 0.5)
                    real_url = result.get('real_url', 'Unknown Destination')
                    xai_reason = result.get('reason', 'AI analysis complete.')
                    
                    log_to_db(target_url, status, final_score)
                    st.subheader("🚨 Threat Intelligence Report")
                    
                    if status == "Phishing":
                        st.error(f"**CRITICAL ALERT: Payload classified as {status.upper()}** 🛑")
                    elif status == "Trusted Domain":
                        category = result.get('trusted_category', 'Verified Platform')
                        st.success(f"**CLEAN: {category.upper()}** ✅\n\n*System Notice: This domain has been securely verified against the internal enterprise allowlist.*")
                    elif status == "Financial Warning":
                        parsed = urllib.parse.urlparse(target_url)
                        params = urllib.parse.parse_qs(parsed.query)
                        payee_name = params.get('pn', ['Unknown Payee'])[0]
                        payee_vpa = params.get('pa', ['Unknown ID'])[0]
                        st.warning(f"**FINANCIAL INTERCEPTION:** Direct payment link detected. 💸\n\n**Requested Payee:** `{payee_name}`\n**UPI ID:** `{payee_vpa}`\n\n*Security Protocol: Verify the Payee Name and UPI ID.*")
                    elif status == "System Command":
                        st.info("**SYSTEM ACTION: This code connects to a Wi-Fi network or triggers a device action. Verify the network name before connecting!** 📡")
                    elif status == "Shortener Warning":
                        st.warning(f"**OBFUSCATION DETECTED: This is a masked URL shortener.** 🕵️\n\n**Hidden Destination Revealed:** `{real_url}`")
                    else:
                        st.success(f"**CLEAN: Payload classified as {status.upper()}** ✅")
                    
                    st.markdown("""
                    <div style="background-color: rgba(30, 40, 50, 0.6); padding: 15px; border-radius: 8px; border-left: 5px solid #00aaff; margin-top: 15px;">
                        <h4 style="margin-top: 0px; color: #00aaff;">🤖 Explainable AI (XAI) Verdict</h4>
                        <p style="font-size: 16px; margin-bottom: 0px;">{}</p>
                    </div>
                    """.format(xai_reason), unsafe_allow_html=True)
                    
                    st.markdown("---")
                        
                    res_tab1, res_tab2 = st.tabs(["📊 Metric Overview", "🧠 AI Decision Log"])
                    with res_tab1:
                        st.progress(float(final_score), text=f"Final Threat Level: {final_score:.2f}")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Fusion Risk Score", f"{final_score:.2f}")
                        m2.metric("Structural Risk (URL)", f"{url_risk:.2f}")
                        if st.session_state.deep_scan:
                            m3.metric("Semantic Risk (Content)", f"{content_risk:.2f}")
                        else:
                            m3.metric("Semantic Risk (Content)", "Bypassed")
                    
                    with res_tab2:
                        st.write("### Pipeline Execution Trace")
                        st.write("1. **Input Processor:** Target URL isolated successfully.")
                        st.write("2. **URL Agent:** Extracted structural anomalies.")
                        if st.session_state.deep_scan:
                            st.write("3. **Content Agent:** Assessed semantic payload using NLP.")
                        else:
                            st.write("3. **Content Agent:** Bypassed per Admin policy.")
                        st.write("4. **Fusion Module:** Applied dynamic risk thresholds.")
                        st.write("5. **Explainable AI Module:** Generated reasoning rationale.")
                        st.write("6. **Database Module:** Scan saved to `scans.db` 💾")
                except Exception as e:
                    st.error("❌ **Backend Engine Error**")
                    st.code(str(e))

elif app_mode == "📊 Global Analytics":
    st.title("📊 Global Analytics Dashboard")
    st.markdown("Real-time statistics pulled directly from the `scans.db` SQLite database.")
    
    conn = sqlite3.connect('scans.db')
    import pandas as pd
    try:
        df = pd.read_sql_query("SELECT * FROM scan_logs", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    
    if df.empty:
        st.info("No live scans have been recorded yet. Go to the Threat Scanner to run your first test!")
    else:
        total_scans = len(df)
        phishing_count = len(df[df['status'].str.lower() == 'phishing'])
        safe_count = len(df[df['status'].str.lower() == 'safe'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total URLs Scanned", total_scans)
        m2.metric("Phishing Blocked 🛑", phishing_count)
        m3.metric("Safe Sites ✅", safe_count)
        
        st.markdown("---")
        st.subheader("Live Threat Distribution")
        chart_data = pd.DataFrame({"Safe Sites": [safe_count], "Phishing Threats": [phishing_count]})
        st.bar_chart(chart_data, color=["#17B169", "#FF3333"])
        
        st.subheader("Raw Database Logs")
        st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)

elif app_mode == "⚙️ Agent Settings":
    if not st.session_state.is_admin:
        st.error("Authentication required to view this module.")
    else:
        st.title("⚙️ AI Engine Tuning")
        st.success("✅ Administrator access verified. You are live-editing the AI pipeline.")
        
        st.session_state.url_threshold = st.slider("URL Risk Threshold (Sensitivity)", 0.0, 1.0, st.session_state.url_threshold)
        st.session_state.fusion_threshold = st.slider("Fusion Risk Threshold (Final Verdict)", 0.0, 1.0, st.session_state.fusion_threshold)
        st.session_state.deep_scan = st.checkbox("Enable Deep Content Scanning (BERT NLP Engine)", value=st.session_state.deep_scan)
        
        st.info("Notice: Changes made here are instantly pushed to the active `orchestrator.py` engine.")