document.addEventListener('DOMContentLoaded', function() {
    const resultDiv = document.getElementById('result');
    const loadingView = document.getElementById('loading-view');
    const loadingText = document.querySelector('.loading-text');
    const toggle = document.getElementById('master-toggle');
    const statusText = document.getElementById('status-text');

    // 1. Load Toggle State
    chrome.storage.local.get(['shieldActive'], function(result) {
        if (result.shieldActive === false) {
            toggle.checked = false;
            statusText.innerText = "Shield is OFF";
            statusText.style.color = "#94a3b8";
        }
    });

    // 2. Save Toggle State when clicked
    toggle.addEventListener('change', function() {
        chrome.storage.local.set({ shieldActive: this.checked });
        if (this.checked) {
            statusText.innerText = "Shield is ON";
            statusText.style.color = "#f8fafc";
        } else {
            statusText.innerText = "Shield is OFF";
            statusText.style.color = "#94a3b8";
        }
    });

    // 3. Auto-Trigger the AI Scan for the popup UI
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let currentTabUrl = tabs[0].url;
        
        setTimeout(() => loadingText.innerText = "Extracting semantic payload...", 800);
        setTimeout(() => loadingText.innerText = "Fusing risk metrics...", 1600);

        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: currentTabUrl, deep_scan: true })
        })
        .then(response => response.json())
        .then(data => {
            loadingView.style.display = 'none';
            resultDiv.style.display = 'block';
            
            if (data.prediction === "Phishing") {
                resultDiv.innerHTML = `
                    <div class="result-title" style="color: var(--danger);">🛑 Threat Detected</div>
                    <div class="metric">Risk Score: <span>${data.final_score.toFixed(2)} / 1.0</span></div>
                    <div class="reason">${data.reason}</div>
                `;
                resultDiv.style.borderLeft = "4px solid var(--danger)";
            } else if (data.prediction === "Trusted Domain") {
                resultDiv.innerHTML = `
                    <div class="result-title" style="color: var(--accent);">💎 Verified Safe</div>
                    <div class="metric">Category: <span>${data.trusted_category}</span></div>
                    <div class="reason">${data.reason}</div>
                `;
                resultDiv.style.borderLeft = "4px solid var(--accent)";
            } else {
                resultDiv.innerHTML = `
                    <div class="result-title" style="color: var(--safe);">✅ Clean Baseline</div>
                    <div class="metric">Risk Score: <span>${data.final_score.toFixed(2)} / 1.0</span></div>
                    <div class="reason">${data.reason}</div>
                `;
                resultDiv.style.borderLeft = "4px solid var(--safe)";
            }
            setTimeout(() => resultDiv.classList.add('fade-in'), 10);
        })
        .catch((error) => {
            loadingView.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<div class="result-title" style="color: #f59e0b;">⚠️ Engine Offline</div><div class="reason">Could not connect to the local API on Port 8080.</div>`;
            resultDiv.classList.add('fade-in');
        });
    });
});