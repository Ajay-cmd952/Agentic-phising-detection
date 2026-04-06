// 1. Create the right-click menu item when the extension installs
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scan-link",
        title: "🛡️ Scan Link with Agentic Shield",
        contexts: ["link"] // Only show up when right-clicking a hyperlink!
    });
});

// 2. Listen for when the user clicks our new menu item
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-link") {
        const targetUrl = info.linkUrl; // This extracts the hidden URL behind the button/text!

        // Send to our local API silently
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: targetUrl, deep_scan: true })
        })
        .then(response => response.json())
        .then(data => {
            if (data.prediction === "Phishing") {
                // IT IS BAD! Open the massive red warning page
                const warningUrl = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(targetUrl)}`);
                chrome.tabs.create({ url: warningUrl });
            } else {
                // IT IS SAFE! Inject a quick native pop-up alert so the user knows
                chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: (msg) => alert(msg),
                    args: [`✅ Agentic Shield: This link is SAFE!\n\nCategory: ${data.trusted_category || 'Clean Baseline'}`]
                });
            }
        })
        .catch(error => {
            console.error("Scanner offline", error);
        });
    }
});