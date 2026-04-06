// --- 1. THE SILENT LEFT-CLICK INTERCEPTOR ---
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Only scan the main website frame (ignore invisible background trackers)
    if (details.frameId === 0) {
        const targetUrl = details.url;

        // Ignore internal Chrome pages and our own warning page
        if (targetUrl.startsWith('chrome://') || targetUrl.includes('warning.html')) return;

        try {
            // Silently send the URL to the AI
            const response = await fetch('http://127.0.0.1:8080/api/v1/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: targetUrl, deep_scan: true })
            });
            const data = await response.json();

            // IF PHISHING: Hijack the tab immediately!
            if (data.prediction === "Phishing") {
                const warningUrl = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(targetUrl)}`);
                chrome.tabs.update(details.tabId, { url: warningUrl });
            }
            // IF SAFE: Do absolutely nothing. The user browses with zero interruption!

        } catch (error) {
            console.error("Scanner offline", error);
        }
    }
});

// --- 2. KEEP THE RIGHT-CLICK MENU (Optional backup) ---
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scan-link",
        title: "🛡️ Deep Scan Link with Agentic Shield",
        contexts: ["link"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-link") {
        const targetUrl = info.linkUrl;
        fetch('http://127.0.0.1:8080/api/v1/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: targetUrl, deep_scan: true })
        })
        .then(res => res.json())
        .then(data => {
            if (data.prediction === "Phishing") {
                const warningUrl = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(targetUrl)}`);
                chrome.tabs.create({ url: warningUrl });
            } else {
                chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: (msg) => alert(msg),
                    args: [`✅ Agentic Shield: This link is SAFE!\n\nCategory: ${data.trusted_category || 'Clean Baseline'}`]
                });
            }
        }).catch(err => console.error(err));
    }
});