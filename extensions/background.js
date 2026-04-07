// 🛡️ HEARTBEAT: Keep the brain awake!
console.log("🛡️ Agentic Shield Service Worker: Awake and Monitoring.");

// 1. Master Message Listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "checkUrl") {
        // Send to Local Python API
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: request.url, deep_scan: true })
        })
        .then(res => res.json())
        .then(data => {
            sendResponse({ status: data.prediction });
        })
        .catch(err => {
            console.error("Scanner offline", err);
            sendResponse({ status: "Safe" }); 
        });
        
        return true; // Keep channel open
    }
});

// 2. Setup Context Menus
chrome.runtime.onInstalled.addListener(() => {
    // Standard Link Scanner
    chrome.contextMenus.create({ 
        id: "scan-link", 
        title: "🛡️ Deep Scan Link with Agentic Shield", 
        contexts: ["link"] 
    });
    
    // Nuclear Sniper Scanner
    chrome.contextMenus.create({
        id: "scan-qr-sniper",
        title: "🛡️ Sniper Scan: Check Screen for QR Codes",
        contexts: ["all"] 
    });
});

// 3. Handle Context Menu Clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    // Handle Right-Click on a Link
    if (info.menuItemId === "scan-link") {
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: info.linkUrl, deep_scan: true })
        })
        .then(res => res.json())
        .then(data => {
            if (data.prediction === "Phishing") {
                chrome.tabs.create({ url: chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(info.linkUrl)}`) });
            } else {
                chrome.scripting.executeScript({ 
                    target: { tabId: tab.id }, 
                    func: (msg) => alert(msg), 
                    args: [`✅ Agentic Shield: This link is SAFE!`] 
                });
            }
        }).catch(err => console.error(err));
    } 
    
    // Handle Right-Click anywhere for Sniper Mode
    else if (info.menuItemId === "scan-qr-sniper") {
        // Capture the visible tab and send to content.js
        chrome.tabs.captureVisibleTab(null, { format: "png" }, (screenshotUrl) => {
            if (chrome.runtime.lastError) {
                console.error("Capture failed:", chrome.runtime.lastError.message);
                return;
            }
            
            // Force message to the specific tab that requested it
            chrome.tabs.sendMessage(tab.id, { 
                action: "analyzeScreenshot", 
                image: screenshotUrl 
            }, (response) => {
                if (chrome.runtime.lastError) {
                    console.log("Tab connection slow, but message sent.");
                }
            });
        });
    }
});