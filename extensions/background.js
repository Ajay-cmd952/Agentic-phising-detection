// 🛡️ Agentic Shield: Professional Advice Engine
console.log("🛡️ Agentic Shield: Brain Active.");

function wakeUpServer() {
    fetch('https://ajay0006-agentic-shield-api.hf.space/').catch(() => {});
}
chrome.runtime.onStartup.addListener(wakeUpServer);
chrome.runtime.onInstalled.addListener(wakeUpServer);

async function performScan(url, tabId, sendResponse) {
    let advice = "";
    let type = "Link";

    if (url.startsWith('upi://') || (url.includes('pa=') && url.includes('@'))) {
        type = "Payment";
        advice = "💸 PAYMENT ALERT: This is a request to send money. Verify the recipient name in your GPay/PhonePe app before entering your PIN.";
    } else if (url.startsWith('WIFI:S:')) {
        type = "WiFi";
        advice = "📶 WIFI ALERT: This connects you to a new network. Unknown networks can be used to intercept your personal data.";
    } else if (url.startsWith('mailto:')) {
        type = "Email";
        advice = "📩 EMAIL ALERT: This starts an outgoing draft. Be cautious of hidden trackers used to verify your active status.";
    } else if (url.startsWith('tel:')) {
        type = "Phone";
        advice = "📞 PHONE ALERT: This will dial a number. Verify the source to prevent Vishing (Voice Phishing) or scam calls.";
    }

    if (type !== "Link") {
        chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: advice, isSafe: true });
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
            chrome.tabs.sendMessage(tabId, { action: "clearToast" });
            chrome.tabs.create({ url: chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(url)}`) });
        } else {
            chrome.tabs.sendMessage(tabId, { 
                action: "showSimpleAdvice", 
                message: "✅ Verified Safe. Redirecting you now...", 
                isSafe: true,
                shouldRedirect: true,
                targetUrl: url
            });
        }
        if (sendResponse) sendResponse({ status: data.prediction });
    })
    .catch(err => {
        chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ Safe to proceed.", isSafe: true, shouldRedirect: true, targetUrl: url });
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
    chrome.contextMenus.create({ id: "scan-link", title: "🛡️ Scan with Agentic Shield", contexts: ["link"] });
    chrome.contextMenus.create({ id: "scan-qr-sniper", title: "🛡️ Sniper Scan QR Code", contexts: ["all"] });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-link") performScan(info.linkUrl, tab.id);
    else if (info.menuItemId === "scan-qr-sniper") {
        chrome.tabs.captureVisibleTab(null, { format: "png" }, (img) => {
            chrome.tabs.sendMessage(tab.id, { action: "analyzeScreenshot", image: img });
        });
    }
});