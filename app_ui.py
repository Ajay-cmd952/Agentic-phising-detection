import streamlit as st
import re
import time
from utils.orchestrator import AIOrchestrator

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Agentic Phishing Detector",
    page_icon="🛡️",
    layout="centered"
)

# Custom CSS for a sleek, modern look
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #1E88E5;
        color: white;
        width: 100%;
        border-radius: 8px;
        padding: 12px;
        font-weight: bold;
        font-size: 16px;
    }
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Load the AI Engine ---
@st.cache_resource
def load_ai():
    return AIOrchestrator()

orchestrator = load_ai()

# --- 3. UI Header ---
st.title("🛡️ Agentic Phishing Detection System")
st.markdown("""
**Upload your suspicious content below.** Our Multi-Agent AI System will scan your emails, SMS messages, or raw URLs. It automatically extracts links and analyzes the structural risk, domain reputation, and semantic content.
""")
st.markdown("---")

# --- 4. The Email/SMS/URL Input Area ---
st.subheader("📩 Input Data")
user_input = st.text_area(
    "Paste an Email, SMS message, or a URL here:", 
    height=150, 
    placeholder="Example: 'URGENT: Your PayPal account has been locked. Click here to verify your identity: http://paypal-update-account.com/login'"
)

# --- 5. Analysis Logic ---
if st.button("🔍 Scan & Analyze"):
    if not user_input.strip():
        st.warning("⚠️ Please paste some text or a URL to analyze.")
    else:
        # Regex to automatically extract URLs from a block of text
        extracted_urls = re.findall(r'(https?://[^\s]+)', user_input)
        
        if not extracted_urls:
            st.info("✅ No clickable URLs were found in this message. It is generally safe from link-based phishing, but do not share personal info!")
        else:
            target_url = extracted_urls[0] # Grab the first link found
            
            # Show the user what the system extracted
            st.markdown(f"**🔗 Extracted Target URL:** `{target_url}`")
            
            with st.spinner("🤖 Multi-Agent Pipeline is scanning the threat..."):
                time.sleep(1.5) # Smooth UI transition
                
                # Feed the extracted URL to your backend orchestrator!
                result = orchestrator.run_detection(target_url)
                
                status = result['prediction']
                final_score = result['final_score']
                url_risk = result['url_risk']
                content_risk = result['content_risk']
                
                # --- 6. The Results Dashboard ---
                st.markdown("---")
                st.subheader("🚨 AI Analysis Results")
                
                if status == "Phishing":
                    st.error(f"**DANGER: This content is classified as {status}** 🛑")
                else:
                    st.success(f"**SAFE: This content is classified as {status}** ✅")
                    
                # Display metrics side-by-side
                col1, col2, col3 = st.columns(3)
                col1.metric("Overall Risk Score", f"{final_score:.2f}")
                col2.metric("URL Risk Score", f"{url_risk:.2f}")
                col3.metric("Content Risk Score", f"{content_risk:.2f}")
                
                # Visual Progress Bar
                st.markdown("### Threat Level Meter")
                st.progress(float(final_score))
                
                # Explain the "Why" (Great for presentations!)
                with st.expander("📊 How did the AI make this decision?"):
                    st.write("""
                    - **URL Agent (Random Forest):** Checked for typosquatting, subdomain spoofing, missing HTTPS, and malicious keyword stuffing.
                    - **Content Agent (BERT):** Checked the readability and semantic safety of the destination webpage.
                    - **Risk Fusion:** Applied weighted threshold logic to combine the scores into a final verdict.
                    """)