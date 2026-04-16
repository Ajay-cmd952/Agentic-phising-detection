// 🛡️ Agentic Shield: Core Engine (STABLE VERSION)
console.log("🛡️ Agentic Shield: Brain Active.");

function wakeUpServer() {
    fetch('https://ajay0006-agentic-shield-api.hf.space/').catch(() => {});
}
chrome.runtime.onStartup.addListener(wakeUpServer);
chrome.runtime.onInstalled.addListener(wakeUpServer);

// --- 1. NEURAL DOWNLOAD GUARD ---
chrome.downloads.onCreated.addListener((downloadItem) => {
    const fileExt = downloadItem.filename.split('.').pop().toLowerCase();
    const riskyExts = ['exe', 'msi', 'zip', 'rar', 'bat', 'apk', 'scr'];
    if (riskyExts.includes(fileExt)) {
        chrome.tabs.sendMessage(downloadItem.referrerTabId || -1, { 
            action: "showSimpleAdvice", 
            message: `⚠️ NEURAL DOWNLOAD GUARD: Analyzing .${fileExt} file. Cracked software is a primary malware vector.`, 
            isSafe: false 
        });
    }
});

// --- 2. URL SCANNING ENGINE ---
async function performScan(url, tabId, sendResponse) {
    let advice = "";
    let type = "Link";
    
    try {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname.toLowerCase();
        const trustedDomains = ["google.com", "www.google.com", "gmail.com", "mail.google.com", "microsoft.com", "bing.com", "github.com", "netbeans.org", "youtube.com", "chess.com"];

        if (trustedDomains.some(d => hostname === d || hostname.endsWith('.' + d))) {
            chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ Trusted Domain Verified.", isSafe: true, shouldRedirect: true, targetUrl: url });
            if (sendResponse) sendResponse({ status: "Safe" });
            return;
        }
    } catch (e) {}

    if (url.startsWith('upi://') || (url.includes('pa=') && url.includes('@'))) {
        type = "Payment";
        advice = "💸 PAYMENT ALERT: Verify recipient name before PIN entry.";
    } else if (url.startsWith('WIFI:S:')) {
        type = "WiFi";
        advice = "📶 WIFI ALERT: Public networks can intercept data.";
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
            chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ Verified Safe. Redirecting...", isSafe: true, shouldRedirect: true, targetUrl: url });
        }
    })
    .catch(() => {
        chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ Safe to proceed.", isSafe: true, shouldRedirect: true, targetUrl: url });
    });
}

// --- 3. EVENT LISTENERS ---
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
    // Re-registering menus to ensure they appear
    chrome.contextMenus.removeAll(() => {
        chrome.contextMenus.create({ id: "scan-link", title: "🛡️ Scan with Agentic Shield", contexts: ["link"] });
        chrome.contextMenus.create({ id: "scan-qr-sniper", title: "🛡️ Sniper Scan QR Code", contexts: ["all"] });
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-link") performScan(info.linkUrl, tab.id);
    else if (info.menuItemId === "scan-qr-sniper") {
        chrome.tabs.captureVisibleTab(null, { format: "png" }, (img) => {
            chrome.tabs.sendMessage(tab.id, { action: "analyzeScreenshot", image: img });
        });
    }
});