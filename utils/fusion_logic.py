class RiskFusionModule:
    def aggregate_and_decide(self, url_score, content_score):
        # We give the URL model 70% weight and Content 30%
        final_risk_score = (url_score * 0.7) + (content_score * 0.3)
        
        # TUNED THRESHOLDS: Increased sensitivity to catch SMS Phishing
        
        # 1. If URL is highly suspicious (> 0.80), flag it immediately
        if url_score > 0.80:
            prediction = "Phishing"
            
        # 2. LOWERED THRESHOLD: Require a combined score of only > 0.40 to flag as phishing
        elif final_risk_score >= 0.40:
            prediction = "Phishing"
            
        # 3. If it doesn't meet those thresholds, it is Safe
        else:
            prediction = "Safe"
            
        return {
            "url_risk": round(url_score, 4),
            "content_risk": round(content_score, 4),
            "final_score": round(final_risk_score, 4),
            "prediction": prediction
        }