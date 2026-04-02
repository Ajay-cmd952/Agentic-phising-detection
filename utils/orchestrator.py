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
        
        # --- SECURE TRUSTED DOMAIN ALLOWLIST (CATEGORIZED) ---
        parsed_url = urllib.parse.urlparse(url_lower if url_lower.startswith('http') else 'http://' + url_lower)
        hostname = parsed_url.hostname or ""

        trusted_categories = {
            "Verified Tech Infrastructure": ["google.com", "microsoft.com", "github.com", "linkedin.com", "canva.com", "apple.com", "amazon.com", "aws.amazon.com", "zoom.us", "cisco.com"],
            "Official Financial Institution": ["hdfcbank.com", "icicibank.com", "sbi.co.in", "axisbank.com", "pnbindia.in", "kotak.com", "billdesk.com", "razorpay.com", "paytm.com"],
            "Government & Healthcare Portal": ["gov.in", "nic.in", "who.int", "cowin.gov.in", "mohfw.gov.in"],
            "Recognized Educational Institution": ["vit.ac.in"] 
        }

        for category, domains in trusted_categories.items():
            if any(hostname == domain or hostname.endswith("." + domain) for domain in domains):
                print(f"-> 🛡️ {category} Detected ({hostname}). Bypassing ML.")
                return {
                    "url_risk": 0.0,
                    "content_risk": 0.0,
                    "final_score": 0.0,
                    "prediction": "Trusted Domain",
                    "trusted_category": category,
                    "real_url": url,
                    "reason": f"Domain perfectly matches the internal enterprise allowlist for '{category}'. Machine learning math is bypassed to ensure seamless operation for official platforms."
                }

        # --- UNROLL URL SHORTENERS ---
        shorteners = ["bit.ly", "tinyurl.com", "t.co", "qrs.ly", "is.gd", "ow.ly", "cutt.ly"]
        if any(shortener in url_lower for shortener in shorteners):
            print("-> 🔗 URL Shortener detected! Attempting to unroll...")
            try:
                req_url = url if url.startswith("http") else "http://" + url
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
                "real_url": real_url,
                "reason": "The link relies on a redirection service to obscure its final destination. Hackers frequently use this to bypass basic security filters."
            }
        
        # --- EDGE CASE INTERCEPTION RULES ---
        
        if url_lower.startswith("upi://") or url_lower.startswith("pay"):
            print("-> 💸 Financial Payment Link Detected! Bypassing ML.")
            return {
                "url_risk": 0.0,
                "content_risk": 0.0,
                "final_score": 0.0,
                "prediction": "Financial Warning",
                "reason": "This is a direct peer-to-peer or merchant financial protocol, not a standard website. ML scoring is Not Applicable (N/A)."
            }
            
        if url_lower.startswith(("wifi:", "tel:", "smsto:", "mailto:", "matmsg:")):
            print("-> 📱 Local System Command Detected! Bypassing ML.")
            return {
                "url_risk": 0.0,
                "content_risk": 0.0,
                "final_score": 0.0,
                "prediction": "System Command",
                "reason": "This code executes a local hardware or software action (like dialing a phone or connecting to Wi-Fi) rather than navigating to a web page."
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
        
        # --- EXPLAINABLE AI (XAI) REASONING ENGINE ---
        if final_result.get('prediction') == "Phishing":
            if url_risk_score >= 0.6 and content_risk_score >= 0.6:
                reason = "Both the URL structure is highly suspicious (e.g., unusual characters, extreme length) and the semantic payload contains strong psychological triggers (urgency, threats)."
            elif url_risk_score >= 0.6:
                reason = "The text appears benign, but the URL structure is mathematically irregular, strongly suggesting a disguised malicious link."
            else:
                reason = "The URL looks relatively normal, but the semantic content contains severe social engineering triggers attempting to manipulate the user."
        else:
            reason = "The structural layout of the URL and the semantic meaning of the text conform to standard, safe internet patterns with no detected anomalies."
            
        final_result['reason'] = reason
        
        return final_result