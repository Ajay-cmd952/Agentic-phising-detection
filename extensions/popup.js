document.addEventListener('DOMContentLoaded', function() {
    const resultDiv = document.getElementById('result');
    const urlDisplay = document.getElementById('current-url');
    const loadingView = document.getElementById('loading-view');
    const loadingText = document.querySelector('.loading-text');

    // 1. Instantly grab the URL when popup opens
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let currentTabUrl = tabs[0].url;
        urlDisplay.innerText = currentTabUrl.length > 45 ? currentTabUrl.substring(0, 45) + '...' : currentTabUrl;
        
        // 2. Change loading text dynamically to look highly technical
        setTimeout(() => loadingText.innerText = "Extracting semantic payload...", 800);
        setTimeout(() => loadingText.innerText = "Fusing risk metrics...", 1600);

        // 3. Auto-Trigger the AI Scan
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: currentTabUrl, deep_scan: true })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader, show results
            loadingView.style.display = 'none';
            resultDiv.style.display = 'block';
            
            // Format dynamic UI based on prediction
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
            
            // Trigger CSS fade-in animation
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