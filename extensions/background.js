// 🛡️ Agentic Shield: Silent Operational Core
console.log("🛡️ Agentic Shield: Monitoring Silently.");

function wakeUpServer() {
    fetch('https://ajay0006-agentic-shield-api.hf.space/').catch(() => {});
}
chrome.runtime.onStartup.addListener(wakeUpServer);
chrome.runtime.onInstalled.addListener(wakeUpServer);

async function performScan(url, tabId, sendResponse) {
    // Advanced Protocols (Mail, Tel, UPI)
    if (url.startsWith('mailto:') || url.startsWith('tel:') || url.startsWith('upi://')) {
        if (sendResponse) sendResponse({ status: "Safe" });
        return;
    }

    fetch('https://ajay0006-agentic-shield-api.hf.space/api/v1/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, deep_scan: true })
    })
    .then(res => res.json())
    .then(data => {
        if (data.prediction === "Phishing") {
            chrome.tabs.create({ url: chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(url)}`) });
        }
        // SILENT: We just send the result back to content.js without alerts
        if (sendResponse) sendResponse({ status: data.prediction });
    })
    .catch(err => {
        if (sendResponse) sendResponse({ status: "Safe" });
    });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "checkUrl") {
        performScan(request.url, sender.tab.id, sendResponse);
        return true; 
    }
    if (request.action === "qrResult") {
        performScan(request.url, sender.tab.id);
        return true;
    }
});

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({ id: "scan-link", title: "🛡️ Deep Scan Link", contexts: ["link"] });
    chrome.contextMenus.create({ id: "scan-qr-sniper", title: "🛡️ Sniper Scan", contexts: ["all"] });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-link") performScan(info.linkUrl, tab.id);
    else if (info.menuItemId === "scan-qr-sniper") {
        chrome.tabs.captureVisibleTab(null, { format: "png" }, (img) => {
            chrome.tabs.sendMessage(tab.id, { action: "analyzeScreenshot", image: img });
        });
    }
});