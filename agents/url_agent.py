import numpy as np
import pickle
import os
import pandas as pd
from urllib.parse import urlparse

class URLAnalysisAgent:
    def __init__(self):
        self.model_path = "Models/rf_model.pkl"
        self.model = None
        
        if os.path.exists(self.model_path):
            print("✅ URL Agent: Successfully connected to rf_model.pkl")
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            print(f"❌ URL Agent Error: Could not find the model at {self.model_path}")

    def extract_features(self, url):
        features = [
            len(url),                         # length_url
            url.count('.'),                   # nb_dots
            url.count('-'),                   # nb_hyphens
            url.count('@'),                   # nb_at
            url.count('?'),                   # nb_qm
            url.count('&'),                   # nb_and
            url.count('|'),                   # nb_or
            url.count('='),                   # nb_eq
            url.count('_'),                   # nb_underscore
            url.count('/'),                   # nb_slash
            1 if 'www' in url.lower() else 0, # nb_www
            1 if '.com' in url.lower() else 0,# nb_com
            sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0, # ratio_digits_url
            1 if len(url) < 20 else 0,        # shortening_service
            url.count('.') - 1,               # nb_subdomains
            1 if '-' in url.split('/')[2] else 0 if len(url.split('/')) > 2 else 0 # prefix_suffix
        ]
        return np.array(features).reshape(1, -1)

    def analyze(self, url):
        # 🌟 V2: Smarter Industry-Standard Trusted Allowlist
        trusted_domains = [
            'openai.com', 'google.com', 'wikipedia.org', 
            'github.com', 'microsoft.com', 'python.org',
            'chatgpt.com', 'tryhackme.com'
        ]
        
        try:
            # Extracts the true network location (e.g., "secure-login.net" instead of "google")
            parsed_domain = urlparse(url).netloc.lower()
            
            # Only marks as safe if the TRUE domain matches the allowlist exactly
            if any(parsed_domain == domain or parsed_domain.endswith('.' + domain) for domain in trusted_domains):
                return 0.05 
        except Exception:
            pass # If it can't parse the URL, let the AI handle it

        # 🚨 NEW: SUSPICIOUS KEYWORD SCANNER (Blocklist)
        # Hackers use these words to create a false sense of urgency
        hacker_keywords = ['login', 'update', 'verify', 'cancel', 'secure', 'account', 'billing']
        
        # Count how many of these sketchy words are in the URL
        url_lower = url.lower()
        sketchy_word_count = sum(1 for word in hacker_keywords if word in url_lower)
        
        # If the URL has 2 or more of these words, it's highly likely to be phishing
        if sketchy_word_count >= 2:
            return 0.88 # Instantly assign a high risk score

        # --- Normal AI processing for unknown URLs ---
        if not self.model:
            return 0.5  
        
        raw_features = self.extract_features(url)
        
        feature_names = [
            'length_url', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm', 'nb_and', 
            'nb_or', 'nb_eq', 'nb_underscore', 'nb_slash', 'nb_www', 'nb_com',
            'ratio_digits_url', 'shortening_service', 'nb_subdomains', 'prefix_suffix'
        ]
        
        features_df = pd.DataFrame(raw_features, columns=feature_names)
        probability = self.model.predict_proba(features_df)[0][1]
        
        return float(probability)







        