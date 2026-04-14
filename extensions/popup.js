document.addEventListener('DOMContentLoaded', function() {
    const resultDiv = document.getElementById('result');
    const loadingView = document.getElementById('loading-view');
    const toggle = document.getElementById('master-toggle');
    const statusText = document.getElementById('status-text');

    chrome.storage.local.get(['shieldActive'], function(result) {
        const isActive = result.shieldActive !== false;
        toggle.checked = isActive;
        updateUI(isActive);
        
        if (isActive) {
            startScan();
        } else {
            showDisabledUI();
        }
    });

    function updateUI(isActive) {
        statusText.innerText = isActive ? "Shield is ON" : "Shield is OFF";
        statusText.style.color = isActive ? "#f8fafc" : "#52525b";
    }

    toggle.addEventListener('change', function() {
        chrome.storage.local.set({ shieldActive: this.checked });
        updateUI(this.checked);
        if (this.checked) location.reload(); else showDisabledUI();
    });

    function startScan() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let url = tabs[0].url;

            // FIX: Whitelist New Tab and Google Search to avoid false 0.81 scores
            if (!url || url.startsWith("chrome://") || url.includes("google.com/search") || url.includes("newtab")) {
                showSafeUI("Internal Page", "This is a secure system or search page. No risk identified.");
                return;
            }

            fetch('https://ajay0006-agentic-shield-api.hf.space/api/v1/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, deep_scan: true })
            })
            .then(res => res.json())
            .then(data => displayResult(data))
            .catch(() => showErrorUI());
        });
    }

    function showSafeUI(cat, reason) {
        loadingView.style.display = 'none';
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `<div class="result-title" style="color: #10b981;">💎 Verified Safe</div><div class="metric">Category: <span>${cat}</span></div><div class="reason">${reason}</div>`;
        resultDiv.style.borderLeft = "4px solid #10b981";
        resultDiv.classList.add('fade-in');
    }

    function displayResult(data) {
        loadingView.style.display = 'none';
        resultDiv.style.display = 'block';
        if (data.prediction === "Phishing") {
            resultDiv.innerHTML = `<div class="result-title" style="color: #e11d48;">🛑 Threat Detected</div><div class="metric">Risk Score: <span>${data.final_score.toFixed(2)}</span> / 1.0</div><div class="reason">${data.reason}</div>`;
            resultDiv.style.borderLeft = "4px solid #e11d48";
        } else {
            showSafeUI("Clean Baseline", data.reason);
        }
        resultDiv.classList.add('fade-in');
    }

    function showDisabledUI() {
        loadingView.style.display = 'none';
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `<div class="result-title" style="color: #52525b;">🛡️ System Standby</div><div class="reason">Enable Shield to scan this active tab.</div>`;
        resultDiv.classList.add('fade-in');
    }

    function showErrorUI() {
        loadingView.style.display = 'none';
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `<div class="result-title" style="color: #fbbf24;">💤 Engine Asleep</div><div class="reason">The server is waking up. Please wait 30s.</div>`;
    }
});