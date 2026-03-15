# application.py
from utils.orchestrator import AIOrchestrator

def start_system():
    print("🛡️ Loading Agentic Phishing Detection System... 🛡️")
    print("Please wait while the AI Models load...")
    
    # This single line wakes up the Orchestrator, which loads all 3 Agents!
    orchestrator = AIOrchestrator()
    
    print("\n✅ System Ready!")
    
    while True:
        # This is your URL Input Interface
        print("\n" + "="*50)
        url = input("🌐 Enter a URL to check (or type 'quit' to exit): ")
        
        if url.lower() == 'quit':
            print("Shutting down system. Goodbye!")
            break
            
        if not url.startswith("http"):
            print("⚠️ Please include 'http://' or 'https://' in your URL.")
            continue
            
        # Send the URL to the AI Orchestration Layer
        result = orchestrator.run_detection(url)
        
        # Display the Final Prediction
        print("\n--- 🚨 FINAL AI PREDICTION 🚨 ---")
        print(f"Status:      {result['prediction']}")
        print(f"Risk Score:  {result['final_score']} (Scale 0 to 1)")
        print(f"URL Risk:    {result['url_risk']}")
        print(f"Content Risk:{result['content_risk']}")
        print("="*50)

if __name__ == "__main__":
    start_system()