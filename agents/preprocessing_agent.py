import requests
from bs4 import BeautifulSoup
import re

class PreprocessingAgent:
    def validate_url(self, url):
        # Validates URL structure
        regex = re.compile(r'^(?:http|ftp)s?://', re.IGNORECASE)
        return re.match(regex, url) is not None

    def clean_url_content(self, url):
        # Webpage Fetching & HTML Cleaning
        if not self.validate_url(url):
            return ""
        try:
            # Fetches webpage content and removes scripts/noise
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cleans HTML and extracts meaningful textual data
            for script in soup(["script", "style"]):
                script.decompose()
                
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Fetch error: {e}")
            return ""