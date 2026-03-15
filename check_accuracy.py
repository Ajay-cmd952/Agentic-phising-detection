import pandas as pd
import pickle
from sklearn.metrics import accuracy_score, classification_report
import os

def check_model_accuracy():
    print("📊 Evaluating Model Accuracy...")
    
    # 1. Load the dataset
    dataset_path = r"C:\Users\AJAY KARTHICK\OneDrive\Desktop\Agentic_Phising_project\datasets\archive (7)\dataset_phishing.csv"
    if not os.path.exists(dataset_path):
        print(f"❌ Error: Cannot find {dataset_path} in the main folder.")
        return

    df = pd.read_csv(dataset_path)
    
    # 2. Extract the exact same 16 features used in training
    feature_names = [
        'length_url', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm', 'nb_and', 
        'nb_or', 'nb_eq', 'nb_underscore', 'nb_slash', 'nb_www', 'nb_com',
        'ratio_digits_url', 'shortening_service', 'nb_subdomains', 'prefix_suffix'
    ]
    
    try:
        X = df[feature_names]
        y_true = df['status'].apply(lambda x: 1 if x == 'phishing' else 0)
    except KeyError as e:
        print(f"❌ Error reading dataset columns: {e}")
        return

    # 3. Load your trained model using the absolute path
    model_path = r"C:\Users\AJAY KARTHICK\OneDrive\Desktop\Agentic_Phising_project\Models\rf_model.pkl"
    if not os.path.exists(model_path):
        print(f"❌ Error: Cannot find the model at {model_path}")
        return

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # 4. Make predictions on the entire dataset
    print("🧠 AI is taking the test... please wait.")
    y_pred = model.predict(X)

    # 5. Calculate and print the results!
    accuracy = accuracy_score(y_true, y_pred)
    
    print("\n" + "="*50)
    print(f"🎯 OVERALL ACCURACY: {accuracy * 100:.2f}%")
    print("="*50)
    print("\nDetailed Report:")
    print(classification_report(y_true, y_pred, target_names=["Safe (0)", "Phishing (1)"]))

if __name__ == "__main__":
    check_model_accuracy()