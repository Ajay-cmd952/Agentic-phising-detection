from agents.preprocessing_agent import PreprocessingAgent
from agents.url_agent import URLAnalysisAgent
from agents.content_agent import ContentAnalysisAgent
from utils.fusion_logic import RiskFusionModule

class AIOrchestrator:
    def __init__(self):
        # Initialize all your agents
        self.preprocessor = PreprocessingAgent()
        self.url_agent = URLAnalysisAgent()
        self.content_agent = ContentAnalysisAgent()
        self.fusion = RiskFusionModule()

    def run_detection(self, url):
        print(f"\n🔍 Orchestrator starting analysis for: {url}")
        
        # --- EDGE CASE INTERCEPTION RULES ---
        url_lower = url.lower()
        
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
        
        # 1. Preprocessing
        print("-> Running Preprocessing Agent...")
        cleaned_content = self.preprocessor.clean_url_content(url)
        
        # 2. Parallel AI Processing
        print("-> Running URL Analysis Agent...")
        url_risk_score = self.url_agent.analyze(url)
        
        print("-> Running Content Analysis Agent (BERT)...")
        content_risk_score = self.content_agent.analyze_semantics(cleaned_content)
        
        # 3. Risk Fusion & Decision
        print("-> Running Risk Fusion & Decision Layer...")
        final_result = self.fusion.aggregate_and_decide(url_risk_score, content_risk_score)
        
        return final_result