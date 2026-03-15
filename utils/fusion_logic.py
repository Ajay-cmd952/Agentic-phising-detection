class RiskFusionModule:
    def aggregate_and_decide(self, url_score, content_score):
        # We give the URL model 70% weight and Content 30%
        final_risk_score = (url_score * 0.7) + (content_score * 0.3)
        
        # TUNED THRESHOLDS: Reduced sensitivity to prevent False Positives
        
        # 1. If URL is EXTREMELY bad (> 0.80), flag it immediately
        if url_score > 0.80:
            prediction = "Phishing"
            
        # 2. Otherwise, require a higher combined score (> 0.60) to flag as phishing
        elif final_risk_score > 0.60:
            prediction = "Phishing"
            
        # 3. If it doesn't meet those high thresholds, it is Safe
        else:
            prediction = "Safe"
            
        return {
            "url_risk": round(url_score, 4),
            "content_risk": round(content_score, 4),
            "final_score": round(final_risk_score, 4),
            "prediction": prediction
        }