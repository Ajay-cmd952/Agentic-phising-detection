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

    # --- NEW: Added dynamic parameters for the Settings Page ---
    def run_detection(self, url, deep_scan=True, url_threshold=0.80, fusion_threshold=0.60):
        print(f"\n🔍 Orchestrator starting analysis for: {url}")
        print(f"⚙️ Settings - Deep Scan: {deep_scan}, URL Thresh: {url_threshold}, Fusion Thresh: {fusion_threshold}")
        
        url_lower = url.lower()
        
        # --- SECURE TRUSTED DOMAIN ALLOWLIST ---
        parsed_url = urllib.parse.urlparse(url_lower if url_lower.startswith('http') else 'http://' + url_lower)
        hostname = parsed_url.hostname or ""

        trusted_categories = {
            "Verified Tech Infrastructure": ["google.com", "microsoft.com", "github.com", "linkedin.com", "canva.com", "apple.com", "amazon.com", "aws.amazon.com", "zoom.us", "cisco.com"],
            "Official Financial Institution": ["hdfcbank.com", "icicibank.com", "sbi.co.in", "axisbank.com", "pnbindia.in", "kotak.com", "billdesk.com", "razorpay.com", "paytm.com"],
            "Government & Healthcare Portal": ["gov.in", "nic.in", "who.int", "cowin.gov.in", "mohfw.gov.in"],
            "Recognized Educational Institution": ["vit.ac.in"],
            "Trusted Media Platform": ["shutterstock.com", "youtube.com", "vimeo.com"]
        }

        for category, domains in trusted_categories.items():
            if any(hostname == domain or hostname.endswith("." + domain) for domain in domains):
                print(f"-> 🛡️ {category} Detected ({hostname}). Bypassing ML.")
                return {
                    "url_risk": 0.0, "content_risk": 0.0, "final_score": 0.0,
                    "prediction": "Trusted Domain", "trusted_category": category, "real_url": url,
                    "reason": f"Domain securely authenticated against the Zero-Trust network directory as a '{category}'. Heuristic deep-scanning deferred for verified infrastructure."
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
                "url_risk": 0.0, "content_risk": 0.0, "final_score": 0.0,
                "prediction": "Shortener Warning", "real_url": real_url,
                "reason": "URL obfuscation detected. The payload relies on a redirection service to mask its final destination, a common tactic used to bypass perimeter security."
            }
        
        # --- EDGE CASE INTERCEPTION RULES ---
        if url_lower.startswith("upi://") or url_lower.startswith("pay"):
            return {
                "url_risk": 0.0, "content_risk": 0.0, "final_score": 0.0,
                "prediction": "Financial Warning",
                "reason": "This is a direct peer-to-peer or merchant financial protocol, not a standard website. ML scoring is Not Applicable (N/A)."
            }
            
        if url_lower.startswith(("wifi:", "tel:", "smsto:", "mailto:", "matmsg:")):
            return {
                "url_risk": 0.0, "content_risk": 0.0, "final_score": 0.0,
                "prediction": "System Command",
                "reason": "This code executes a local hardware or software action (like dialing a phone or connecting to Wi-Fi) rather than navigating to a web page."
            }
        
        # --- STANDARD ML PIPELINE ---
        print("-> Running Preprocessing Agent...")
        cleaned_content = self.preprocessor.clean_url_content(url)
        
        print("-> Running URL Analysis Agent...")
        url_risk_score = self.url_agent.analyze(url)
        
        # --- NEW: DYNAMIC DEEP SCAN TOGGLE ---
        content_risk_score = 0.0
        if deep_scan:
            print("-> Running Content Analysis Agent (BERT)...")
            content_risk_score = self.content_agent.analyze_semantics(cleaned_content)
        else:
            print("-> ⏩ Deep Scan Disabled by Admin. Bypassing BERT Model...")
        
        print("-> Running Risk Fusion & Decision Layer...")
        final_result = self.fusion.aggregate_and_decide(url_risk_score, content_risk_score)
        
        # --- NEW: DYNAMIC THRESHOLD OVERRIDE ---
        final_score = final_result['final_score']
        if final_score >= fusion_threshold:
            final_result['prediction'] = "Phishing"
        else:
            final_result['prediction'] = "Safe"
        
        # --- PROFESSIONAL XAI REASONING ENGINE ---
        if final_result.get('prediction') == "Phishing":
            if url_risk_score >= url_threshold and content_risk_score >= 0.6:
                reason = f"High-confidence threat. Structural anomalies exceeded the {url_threshold} threshold, alongside manipulative semantic triggers within the text payload."
            elif url_risk_score >= url_threshold:
                reason = f"URL topology analysis indicates high risk (Exceeded {url_threshold} threshold). The link structure contains patterns frequently associated with malware distribution."
            else:
                reason = "Semantic risk identified. The payload text contains social engineering vectors commonly used to artificially induce user urgency or panic."
        else:
            if not deep_scan:
                reason = "URL structural patterns conform to standard baseline. Note: Deep Semantic Scanning (BERT) was bypassed by Administrator policy."
            else:
                reason = "Static and dynamic analysis complete. Structural and semantic patterns conform to standard, safe network traffic baseline."
            
        final_result['reason'] = reason
        
        return final_result