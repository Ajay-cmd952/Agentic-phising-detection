import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Define the absolute path to your project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'Models')

# CORRECTED PATH: Points to the FILE, not just the folder
DATA_PATH = r"C:\Users\AJAY KARTHICK\OneDrive\Desktop\Agentic_Phising_project\datasets\archive (7)\dataset_phishing.csv"
def train():
    try:
        print(f"Checking for dataset at: {DATA_PATH}")
        
        # Check if the file actually exists before trying to read it
        if not os.path.exists(DATA_PATH):
            print(f"❌ ERROR: Could not find the file at {DATA_PATH}")
            print("Make sure 'dataset_phishing.csv' is in your main project folder.")
            return

        df = pd.read_csv(DATA_PATH)
        
        # Features matching your Presentation's 'URL Analysis Module' [cite: 170, 171]
        features_cols = [
            'length_url', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm', 'nb_and', 
            'nb_or', 'nb_eq', 'nb_underscore', 'nb_slash', 'nb_www', 'nb_com',
            'ratio_digits_url', 'shortening_service', 'nb_subdomains', 'prefix_suffix'
        ]

        X = df[features_cols]
        y = df['status'].apply(lambda x: 1 if x == 'phishing' else 0)

        print("🧠 Training Random Forest... (This matches your literature survey) [cite: 57, 68]")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Create Models folder if it doesn't exist
        if not os.path.exists(MODELS_DIR):
            print(f"Creating directory: {MODELS_DIR}")
            os.makedirs(MODELS_DIR)

        # Save the model
        model_file = os.path.join(MODELS_DIR, 'rf_model.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"✅ SUCCESS! Model saved at: {model_file}")

    except PermissionError:
        print("❌ ERROR: Permission Denied. Try running VS Code as Administrator.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    train()