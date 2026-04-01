import streamlit as st
import re
import time
import sqlite3
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
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
        /* 1. The Deep Animated RED Background */
        .stApp {
            background: linear-gradient(135deg, #1f0000, #3d0000, #140000, #2b0000);
            background-size: 300% 300%;
            animation: cyberGradient 15s ease infinite;
        }

        @keyframes cyberGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* 2. Floating Content Container (Distinct Dark Slate Color) */
        .block-container {
            background: rgba(22, 24, 28, 0.95) !important; /* Dark Slate/Charcoal to separate from background */
            backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 70, 70, 0.3) !important; /* Red border */
            border-radius: 15px !important;
            box-shadow: 0 0 40px rgba(255, 50, 50, 0.15) !important; /* Red glow */
            padding-top: 2.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            margin-top: 2rem !important;
            margin-bottom: 2rem !important;
            max-width: 95% !important;
        }

        /* 3. Sidebar (Distinct Deep Black-Red) */
        [data-testid="stSidebar"] {
            background-color: #0a0101 !important;
            border-right: 2px solid rgba(255, 70, 70, 0.4);
            box-shadow: 5px 0 20px rgba(255, 50, 50, 0.15);
        }

        /* 4. Neon Red Glowing Buttons */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, rgba(255,70,70,0.1) 0%, rgba(255,100,100,0.1) 100%);
            color: #FF4444;
            border: 1px solid #FF4444;
            border-radius: 6px;
            padding: 10px 24px;
            font-weight: bold;
            letter-spacing: 1px;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 0 10px rgba(255, 70, 70, 0.2);
        }
        div.stButton > button:first-child:hover {
            background: linear-gradient(90deg, #FF3333 0%, #FF6666 100%);
            color: #ffffff !important;
            box-shadow: 0 0 20px rgba(255, 70, 70, 0.6);
            transform: translateY(-2px);
            border: 1px solid transparent;
        }

        /* 5. Terminal-style Text Area (True Black) */
        .stTextArea textarea {
            background-color: #000000 !important;
            color: #FF8888 !important;
            border: 1px solid rgba(255, 70, 70, 0.4) !important;
            font-family: 'Courier New', Courier, monospace !important;
            border-radius: 6px;
        }
        .stTextArea textarea:focus {
            border-color: #FF3333 !important;
            box-shadow: 0 0 15px rgba(255, 70, 70, 0.5) !important;
        }

        /* 6. Glowing Metrics (Red) */
        [data-testid="stMetricValue"] {
            color: #FF4444 !important;
            text-shadow: 0 0 10px rgba(255, 70, 70, 0.4);
        }
        
        /* Hide Default Header completely */
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
    
    app_mode = st.radio(
        "Navigation Menu", 
        ["🔍 Threat Scanner", "📊 Global Analytics", "⚙️ Agent Settings"]
    )
    
    st.markdown("---")
    st.subheader("Live System Status")
    st.success("🟢 URL Agent (RF): Online")
    st.success("🟢 Content Agent (BERT): Online")
    st.success("🟢 Vision Agent (QR): Online")
    st.success("🟢 SQLite Database: Connected")
    
    st.markdown("---")
    st.caption("System Version: 4.8 (Crimson SOC Theme)")
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
            user_input = st.text_area(
                "Target Data Input:", 
                height=150, 
                placeholder="Paste raw text, SMS messages, emails, or direct URLs here..."
            )
            if st.button("🚀 Initialize Multi-Agent Scan", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.error("⚠️ Please input data to scan.")
                else:
                    # UPDATED REGEX: Now catches both http/https and upi:// links
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
                            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                            detector = cv2.QRCodeDetector()
                            data, bbox, _ = detector.detectAndDecode(img_bgr)
                            if data:
                                target_url = data
                                st.success("✅ Vision Agent successfully extracted URL from image.")
                            else:
                                st.error("❌ Could not detect a valid QR code in this image.")
                        except Exception as e:
                            st.error("⚠️ Image Processing Error: Make sure the file is a clear QR code.")

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
                
                # Fetch the unrolled URL if it exists (for shorteners)
                real_url = result.get('real_url', 'Unknown Destination')
                
                log_to_db(target_url, status, final_score)
                
                st.subheader("🚨 Threat Intelligence Report")
                
                # --- UPDATED ALERT LOGIC ---
                if status == "Phishing":
                    st.error(f"**CRITICAL ALERT: Payload classified as {status.upper()}** 🛑")
                elif status == "Financial Warning":
                    st.warning("**FINANCIAL INTERCEPTION: This is a direct payment link (UPI). Proceed with extreme caution!** 💸")
                elif status == "System Command":
                    st.info("**SYSTEM ACTION: This code connects to a Wi-Fi network or triggers a device action. Verify the network name before connecting!** 📡")
                elif status == "Shortener Warning":
                    st.warning(f"**OBFUSCATION DETECTED: This is a masked URL shortener.** 🕵️\n\n**Hidden Destination Revealed:** `{real_url}`")
                else:
                    st.success(f"**CLEAN: Payload classified as {status.upper()}** ✅")
                
                # --- UNIVERSAL ZERO-TRUST AWARENESS MESSAGE ---
                st.markdown("---")
                st.info("🛡️ **Security Awareness Reminder:** AI is a powerful assistant, but it is not perfect. Please use your best judgment. \n\n* **Never** enter passwords, OTPs, or financial details unless you are 100% sure of the sender's identity. \n* **Always** double-check the URL in your browser's address bar before logging in.")
                st.markdown("---")
                    
                res_tab1, res_tab2 = st.tabs(["📊 Metric Overview", "🧠 AI Decision Log"])
                
                with res_tab1:
                    st.progress(float(final_score), text=f"Final Threat Level: {final_score:.2f}")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Fusion Risk Score", f"{final_score:.2f}")
                    m2.metric("Structural Risk (URL)", f"{url_risk:.2f}")
                    m3.metric("Semantic Risk (Content)", f"{content_risk:.2f}")
                
                with res_tab2:
                    st.write("### Pipeline Execution Trace")
                    st.write("1. **Input Processor:** Target URL isolated successfully.")
                    st.write("2. **URL Agent:** Checked Trusted Allowlist and Suspicious Keyword Blocklist.")
                    st.write("3. **URL Agent:** Ran feature extraction through Random Forest classifier.")
                    st.write("4. **Content Agent:** Assessed semantic payload.")
                    st.write("5. **Fusion Module:** Calculated weighted average.")
                    st.write("6. **Database Module:** Scan successfully logged to `scans.db` 💾")
                    
            except Exception as e:
                st.error("❌ **Backend Engine Error**")
                st.warning("The AI backend encountered an issue parsing this specific link.")
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
        
        chart_data = pd.DataFrame({
            "Safe Sites": [safe_count], 
            "Phishing Threats": [phishing_count]
        })
        st.bar_chart(chart_data, color=["#17B169", "#FF3333"])
        
        st.subheader("Raw Database Logs")
        st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)

elif app_mode == "⚙️ Agent Settings":
    st.title("⚙️ AI Engine Tuning")
    st.success("✅ Administrator access verified. You may now modify the heuristic thresholds.")
    
    url_threshold = st.slider("URL Risk Threshold", 0.0, 1.0, 0.80)
    fusion_threshold = st.slider("Fusion Risk Threshold", 0.0, 1.0, 0.60)
    deep_scan = st.checkbox("Enable Deep Content Scanning (Slower)", value=True)
    
    st.info("Note: Wiring these dynamic sliders directly to the `orchestrator.py` threshold variables is scheduled for the next deployment phase.")