// 1. Listen for the "checkUrl" message from our content.js click freezer
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "checkUrl") {
        
        // Ask the Python API
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: request.url, deep_scan: true })
        })
        .then(res => res.json())
        .then(data => {
            // Send the verdict back to content.js
            sendResponse({ status: data.prediction });
        })
        .catch(err => {
            console.error("Scanner offline", err);
            sendResponse({ status: "Safe" }); // Fail open if API is down
        });
        
        return true; // Keep the message channel open while we wait for the AI!
    }
});

// 2. Keep the Right-Click Menu active just in case!
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({ id: "scan-link", title: "🛡️ Deep Scan Link with Agentic Shield", contexts: ["link"] });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
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
                chrome.scripting.executeScript({ target: { tabId: tab.id }, func: (msg) => alert(msg), args: [`✅ Agentic Shield: This link is SAFE!`] });
            }
        }).catch(err => console.error(err));
    }
});