import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

print("🚀 Starting local model training...")

# 1. Load your local dataset
dataset_path = r"C:\Users\AJAY KARTHICK\OneDrive\Desktop\Agentic_Phising_project\datasets\archive (7)\dataset_phishing.csv"

if not os.path.exists(dataset_path):
    print(f"❌ Error: Cannot find dataset at {dataset_path}")
    exit()

df = pd.read_csv(dataset_path)

# 2. Extract the exact 16 features your extension requires
feature_names = [
    'length_url', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm', 'nb_and', 
    'nb_or', 'nb_eq', 'nb_underscore', 'nb_slash', 'nb_www', 'nb_com',
    'ratio_digits_url', 'shortening_service', 'nb_subdomains', 'prefix_suffix'
]

X = df[feature_names]
y = df['status'].apply(lambda x: 1 if x == 'phishing' else 0)

# 3. Train the model
print("🧠 Training the Random Forest model (this will only take a few seconds)...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# 4. Save the freshly trained model overwriting the corrupted one
model_path = r"C:\Users\AJAY KARTHICK\OneDrive\Desktop\Agentic_Phising_project\Models\rf_model.pkl"

# Make sure the Models folder exists
os.makedirs(os.path.dirname(model_path), exist_ok=True)

with open(model_path, 'wb') as f:
    pickle.dump(rf_model, f)

print(f"✅ SUCCESS! A fresh, working rf_model.pkl has been created at:\n{model_path}")
print("🎉 You can now run check_accuracy.py and start your backend!")