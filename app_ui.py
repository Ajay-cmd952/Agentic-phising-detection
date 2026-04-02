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

# --- 1. Database Initialization ---
def init_db():
    conn = sqlite3.connect('scans.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            url TEXT,
            status TEXT,
            risk_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_to_db(url, status, score):
    conn = sqlite3.connect('scans.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scan_logs (timestamp, url, status, risk_score) VALUES (?, ?, ?, ?)", 
              (now, url, status, score))
    conn.commit()
    conn.close()

init_db()

# --- 2. Page Configuration ---
st.set_page_config(
    page_title="Agentic Phishing Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🚨 THE "CRIMSON THREAT" MULTI-COLOR THEME 🚨 ---
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
        header {visibility: hidden !important;}
    </style>
""", unsafe_allow_html=True)

# --- 3. Load the AI Engine ---
@st.cache_resource
def load_ai():
    return AIOrchestrator()

orchestrator = load_ai()

# --- 4. THE SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Admin Console")
    st.markdown("**Agentic Threat Pipeline**")
    st.markdown("---")
    app_mode = st.radio("Navigation Menu", ["🔍 Threat Scanner", "📊 Global Analytics", "⚙️ Agent Settings"])
    st.markdown("---")
    st.subheader("Live System Status")
    st.success("🟢 URL Agent (RF): Online")
    st.success("🟢 Content Agent (BERT): Online")
    st.success("🟢 Vision Agent (pyzbar): Online")
    st.success("🟢 SQLite Database: Connected")
    st.markdown("---")
    st.caption("System Version: 6.0 (XAI Enabled)")
    st.caption("Current User: Administrator")

# --- 5. MAIN PAGE CONTENT ---

if app_mode == "🔍 Threat Scanner":
    st.title("Deep Scan Engine")
    st.markdown("Choose your input method below to scan for phishing threats.")
    
    col_input, col_info = st.columns([2, 1])
    target_url = None

    with col_info:
        st.info("**Supported Formats:**\n- Raw URLs (http/https)\n- Raw Email Text\n- SMS Message Text\n- QR Code Screenshots")
        st.warning("**Note:** Do not paste passwords or sensitive API keys into the scanner.")

    with col_input:
        input_tab1, input_tab2 = st.tabs(["📝 Text / URL Input", "📷 QR Code Scanner (Quishing)"])
        
        with input_tab1:
            user_input = st.text_area("Target Data Input:", height=150, placeholder="Paste raw text, SMS messages, emails, or direct URLs here...")
            if st.button("🚀 Initialize Multi-Agent Scan", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.error("⚠️ Please input data to scan.")
                else:
                    extracted_urls = re.findall(r'((?:https?|upi)://[^\s]+)', user_input)
                    if not extracted_urls:
                        st.success("✅ No clickable URLs detected in the payload.")
                    else:
                        target_url = extracted_urls[0]

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
                                target_url = decoded_objects[0].data.decode('utf-8')
                                st.success("✅ Vision Agent successfully extracted URL from image.")
                            else:
                                st.error("❌ Could not detect a valid QR code in this image.")
                        except Exception as e:
                            st.error(f"⚠️ Image Processing Error: {e}")

    # --- Centralized AI Analysis Logic ---
    if target_url:
        st.markdown("---")
        st.markdown(f"**🔗 Target Locked:** `{target_url}`")
        
        with st.spinner("🤖 Multi-Agent Pipeline is analyzing the threat..."):
            time.sleep(1.0) 
            
            try:
                result = orchestrator.run_detection(target_url)
                
                status = result.get('prediction', 'Unknown')
                final_score = result.get('final_score', 0.5)
                url_risk = result.get('url_risk', 0.5)
                content_risk = result.get('content_risk', 0.5)
                real_url = result.get('real_url', 'Unknown Destination')
                xai_reason = result.get('reason', 'AI analysis complete.')
                
                log_to_db(target_url, status, final_score)
                
                st.subheader("🚨 Threat Intelligence Report")
                
                # --- UPDATED ALERT LOGIC ---
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
                    st.warning(f"**FINANCIAL INTERCEPTION:** Direct payment link detected. 💸\n\n**Requested Payee:** `{payee_name}`\n**UPI ID:** `{payee_vpa}`\n\n*Security Protocol: Verify the Payee Name and UPI ID. Note that corporate payment gateways may display generic merchant tags. Always confirm the final recipient identity within your secure banking application before authorizing any transaction.*")
                
                elif status == "System Command":
                    st.info("**SYSTEM ACTION: This code connects to a Wi-Fi network or triggers a device action. Verify the network name before connecting!** 📡")
                
                elif status == "Shortener Warning":
                    st.warning(f"**OBFUSCATION DETECTED: This is a masked URL shortener.** 🕵️\n\n**Hidden Destination Revealed:** `{real_url}`")
                
                else:
                    st.success(f"**CLEAN: Payload classified as {status.upper()}** ✅")
                
                # --- NEW: XAI REASONING BLOCK ---
                st.markdown("""
                <div style="background-color: rgba(30, 40, 50, 0.6); padding: 15px; border-radius: 8px; border-left: 5px solid #00aaff; margin-top: 15px;">
                    <h4 style="margin-top: 0px; color: #00aaff;">🤖 Explainable AI (XAI) Verdict</h4>
                    <p style="font-size: 16px; margin-bottom: 0px;">{}</p>
                </div>
                """.format(xai_reason), unsafe_allow_html=True)
                
                # --- NEW STRONGER ZERO-TRUST MESSAGE ---
                st.markdown("---")
                st.info("🛡️ **System Notice:** The scores below are generated by an Artificial Intelligence model based on pattern recognition. AI is a powerful assistant, but it is not infallible. \n\n**Please ensure your own safety:** Verify the sender's identity and double-check URLs manually before proceeding.")
                st.markdown("---")
                    
                res_tab1, res_tab2 = st.tabs(["📊 Metric Overview", "🧠 AI Decision Log"])
                
                with res_tab1:
                    st.progress(float(final_score), text=f"Final Threat Level: {final_score:.2f}")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Fusion Risk Score", f"{final_score:.2f}")
                    m2.metric("Structural Risk (URL)", f"{url_risk:.2f}")
                    m3.metric("Semantic Risk (Content)", f"{content_risk:.2f}")
                    
                    if status in ["Financial Warning", "System Command", "Trusted Domain"]:
                        st.caption("*(Note: Machine Learning scoring is intentionally bypassed for trusted domains and direct system/payment protocols to prevent false calculations.)*")
                
                with res_tab2:
                    st.write("### Pipeline Execution Trace")
                    st.write("1. **Input Processor:** Target URL isolated successfully.")
                    st.write("2. **URL Agent:** Checked Trusted Allowlist and Suspicious Keyword Blocklist.")
                    st.write("3. **URL Agent:** Ran feature extraction through Random Forest classifier.")
                    st.write("4. **Content Agent:** Assessed semantic payload.")
                    st.write("5. **Fusion Module:** Calculated weighted average.")
                    st.write("6. **Explainable AI Module:** Generated human-readable logic rationale.")
                    st.write("7. **Database Module:** Scan successfully logged to `scans.db` 💾")
                    
            except Exception as e:
                st.error("❌ **Backend Engine Error**")
                st.warning("The AI backend encountered an issue parsing this specific link.")
                st.code(str(e))

# ... [Global Analytics and Agent Settings blocks remain the same below this line] ...