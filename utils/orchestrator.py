import requests
import urllib.parse
from agents.preprocessing_agent import PreprocessingAgent
from agents.url_agent import URLAnalysisAgent
from agents.content_agent import ContentAnalysisAgent
from utils.fusion_logic import RiskFusionModule

class AIOrchestrator:
    def __init__(self):
        self.preprocessor = PreprocessingAgent()
        self.url_agent = URLAnalysisAgent()
        self.content_agent = ContentAnalysisAgent()
        self.fusion = RiskFusionModule()

    def run_detection(self, url):
        print(f"\n🔍 Orchestrator starting analysis for: {url}")
        
        url_lower = url.lower()
        
        # --- NEW: SECURE TRUSTED DOMAIN ALLOWLIST ---
        # 1. Safely extract the exact hostname (domain) to prevent spoofing bypasses
        parsed_url = urllib.parse.urlparse(url_lower if url_lower.startswith('http') else 'http://' + url_lower)
        hostname = parsed_url.hostname or ""

        # 2. The Enterprise Allowlist
        trusted_domains = [
            # Tech & Infrastructure
            "google.com", "microsoft.com", "github.com", "linkedin.com", "canva.com", 
            "apple.com", "amazon.com", "aws.amazon.com", "zoom.us", "cisco.com",
            # Indian Financial Institutions
            "hdfcbank.com", "icicibank.com", "sbi.co.in", "axisbank.com", "pnbindia.in", 
            "kotak.com", "billdesk.com", "razorpay.com", "paytm.com",
            # Healthcare & Government
            "gov.in", "nic.in", "who.int", "cowin.gov.in", "mohfw.gov.in",
            # Education
            "vit.ac.in" 
        ]

        # 3. Secure Matching Logic: Must BE the domain or be an official SUBDOMAIN
        is_trusted = any(hostname == domain or hostname.endswith("." + domain) for domain in trusted_domains)

        if is_trusted:
            print(f"-> 🛡️ Trusted Enterprise Domain Detected ({hostname}). Bypassing ML.")
            return {
                "url_risk": 0.0,
                "content_risk": 0.0,
                "final_score": 0.0,
                "prediction": "Safe"
            }

        # --- UNROLL URL SHORTENERS (Option B + C) ---
        shorteners = ["bit.ly", "tinyurl.com", "t.co", "qrs.ly", "is.gd", "ow.ly", "cutt.ly"]
        if any(shortener in url_lower for shortener in shorteners):
            print("-> 🔗 URL Shortener detected! Attempting to unroll...")
            try:
                # Add http:// if missing so the request doesn't crash
                req_url = url if url.startswith("http") else "http://" + url
                # Silently visit the link to find the final destination
                response = requests.head(req_url, allow_redirects=True, timeout=5)
                real_url = response.url
                print(f"-> 📍 Unrolled destination: {real_url}")
            except Exception:
                real_url = "Could not resolve hidden destination."

            return {
                "url_risk": 0.0,
                "content_risk": 0.0,
                "final_score": 0.0,
                "prediction": "Shortener Warning",
                "real_url": real_url  # Send the hidden URL to the frontend!
            }
        
        # --- EDGE CASE INTERCEPTION RULES ---
        
        # 1. Financial Interception (UPI)
        if url_lower.startswith("upi://") or url_lower.startswith("pay"):
            print("-> 💸 Financial Payment Link Detected! Bypassing ML.")
            return {
                "url_risk": 0.0,
                "content_risk": 0.0,
                "final_score": 0.0,
                "prediction": "Financial Warning"
            }
            
        # 2. Local System Commands (Wi-Fi, Phone, Email)
        if url_lower.startswith(("wifi:", "tel:", "smsto:", "mailto:", "matmsg:")):
            print("-> 📱 Local System Command Detected! Bypassing ML.")
            return {
                "url_risk": 0.0,
                "content_risk": 0.0,
                "final_score": 0.0,
                "prediction": "System Command"
            }
        
        # --- STANDARD ML PIPELINE ---
        print("-> Running Preprocessing Agent...")
        cleaned_content = self.preprocessor.clean_url_content(url)
        
        print("-> Running URL Analysis Agent...")
        url_risk_score = self.url_agent.analyze(url)
        
        print("-> Running Content Analysis Agent (BERT)...")
        content_risk_score = self.content_agent.analyze_semantics(cleaned_content)
        
        print("-> Running Risk Fusion & Decision Layer...")
        final_result = self.fusion.aggregate_and_decide(url_risk_score, content_risk_score)
        
        return final_result