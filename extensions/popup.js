document.addEventListener('DOMContentLoaded', function() {
    const scanBtn = document.getElementById('scan-btn');
    const resultDiv = document.getElementById('result');
    const urlDisplay = document.getElementById('current-url');
    const loader = document.getElementById('loading');
    let currentTabUrl = '';

    // Get the URL of the active tab
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        currentTabUrl = tabs[0].url;
        // Truncate the URL for display if it's too long
        let displayUrl = currentTabUrl.length > 50 ? currentTabUrl.substring(0, 50) + '...' : currentTabUrl;
        urlDisplay.innerText = "Target: " + displayUrl;
    });

    scanBtn.addEventListener('click', function() {
        // Hide previous results, show loading animation
        resultDiv.style.display = 'none';
        scanBtn.style.display = 'none';
        loader.style.display = 'block';

        // Send the URL to our local API!
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: currentTabUrl,
                deep_scan: true
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading, show results
            loader.style.display = 'none';
            scanBtn.style.display = 'block';
            scanBtn.innerText = "Scan Again";
            resultDiv.style.display = 'block';

            // Format the result box based on the AI's prediction
            if (data.prediction === "Phishing") {
                resultDiv.innerHTML = `
                    <strong style="color: #ff4444;">🛑 CRITICAL ALERT: Phishing</strong><br><br>
                    <strong>Risk Score:</strong> ${data.final_score.toFixed(2)}<br>
                    <strong>Reason:</strong> ${data.reason}
                `;
                resultDiv.style.borderLeft = "4px solid #ff4444";
            } else if (data.prediction === "Trusted Domain") {
                 resultDiv.innerHTML = `
                    <strong style="color: #17B169;">✅ SAFE: Trusted Domain</strong><br><br>
                    <strong>Category:</strong> ${data.trusted_category}<br>
                    <strong>Reason:</strong> ${data.reason}
                `;
                resultDiv.style.borderLeft = "4px solid #17B169";
            }
             else {
                resultDiv.innerHTML = `
                    <strong style="color: #17B169;">✅ SAFE: Clean Baseline</strong><br><br>
                    <strong>Risk Score:</strong> ${data.final_score.toFixed(2)}<br>
                    <strong>Reason:</strong> ${data.reason}
                `;
                resultDiv.style.borderLeft = "4px solid #17B169";
            }
        })
        .catch((error) => {
            // If the API is offline or crashes
            loader.style.display = 'none';
            scanBtn.style.display = 'block';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<strong style="color: #ffaa00;">⚠️ Connection Error</strong><br>Could not reach the AI Engine. Make sure the API is running on Port 8080.`;
            console.error('Error:', error);
        });
    });
});