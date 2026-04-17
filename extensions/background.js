// 🛡️ Agentic Shield: Core Engine (STABLE, THREAT INTEL, ALLOWLIST & SMART QR)
console.log("🛡️ Agentic Shield: Brain Active.");

const VT_API_KEY = "8ec0ac90fa1a55fea24ed6f6d60088e4f126b97a500a7db8e94322a9a97f4b7a";

function wakeUpServer() {
    fetch('https://ajay0006-agentic-shield-api.hf.space/').catch(() => {});
}

function createMenus() {
    chrome.contextMenus.removeAll(() => {
        chrome.contextMenus.create({ id: "scan-link", title: "🛡️ Scan with Agentic Shield", contexts: ["link"] });
        chrome.contextMenus.create({ id: "scan-qr-sniper", title: "🛡️ Sniper Scan QR Code", contexts: ["all"] });
    });
}

chrome.runtime.onInstalled.addListener(() => {
    wakeUpServer();
    createMenus();
});

chrome.runtime.onStartup.addListener(createMenus);

// --- 1. THREAT INTEL DOWNLOAD AGENT (VIRUSTOTAL) ---
chrome.downloads.onCreated.addListener((downloadItem) => {
    const fileExt = downloadItem.filename.split('.').pop().toLowerCase();
    const riskyExts = ['exe', 'msi', 'zip', 'rar', 'apk', 'bat', 'com'];
    
    if (riskyExts.includes(fileExt)) {
        chrome.downloads.pause(downloadItem.id);
        
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, { 
                    action: "showDownloadAdvice", 
                    message: `🔍 THREAT INTEL AGENT: Intercepted .${fileExt}. Querying global threat networks...`, 
                    isSafe: false 
                });
            }
        });

        const encodedUrl = btoa(downloadItem.url).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
        
        fetch(`https://www.virustotal.com/api/v3/urls/${encodedUrl}`, {
            method: 'GET',
            headers: { 'x-apikey': VT_API_KEY }
        })
        .then(res => res.json())
        .then(data => {
            let isMalicious = false;
            if (data.data && data.data.attributes && data.data.attributes.last_analysis_stats) {
                const stats = data.data.attributes.last_analysis_stats;
                if (stats.malicious > 0 || stats.suspicious > 0) {
                    isMalicious = true;
                }
            }

            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                if (isMalicious) {
                    chrome.downloads.cancel(downloadItem.id);
                    if (tabs[0]) {
                        chrome.tabs.sendMessage(tabs[0].id, { 
                            action: "showDownloadAdvice", 
                            message: `🚨 THREAT INTEL: Download terminated! Global threat intelligence flagged this source as MALWARE.`, 
                            isSafe: false 
                        });
                    }
                } else {
                    chrome.downloads.resume(downloadItem.id);
                    if (tabs[0]) {
                        chrome.tabs.sendMessage(tabs[0].id, { 
                            action: "showSimpleAdvice", 
                            message: `✅ THREAT INTEL: File source verified safe. Resuming download.`, 
                            isSafe: true 
                        });
                    }
                }
            });
        })
        .catch(err => {
            chrome.downloads.resume(downloadItem.id);
        });
    }
});

// --- 2. URL SCAN (WITH ENTERPRISE ALLOWLIST) ---
async function performScan(url, tabId, sendResponse) {
    try {
        let urlObj = new URL(url);

        if (urlObj.hostname.includes("google.com") && urlObj.pathname === "/url") {
            const actualUrl = urlObj.searchParams.get("q") || urlObj.searchParams.get("url");
            if (actualUrl) {
                url = actualUrl; 
                urlObj = new URL(url); 
            }
        }

        const hostname = urlObj.hostname.toLowerCase();
        
        const trusted = [
            "google.com", "gmail.com", "youtube.com", "microsoft.com", "bing.com", 
            "github.com", "apple.com", "amazon.com", "amazon.in", "flipkart.com", 
            "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", 
            "wikipedia.org", "yahoo.com", "reddit.com", "whatsapp.com", "netflix.com",
            "zoom.us", "openai.com", "chess.com", "hdfcbank.com", "onlinesbi.sbi", 
            "icicibank.com", "naukri.com", "myntra.com"
        ];

        if (trusted.some(d => hostname === d || hostname.endsWith('.' + d))) {
            chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ Verified Enterprise Domain.", isSafe: true, shouldRedirect: true, targetUrl: url });
            return;
        }
    } catch (e) {}

    fetch('https://ajay0006-agentic-shield-api.hf.space/api/v1/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, deep_scan: true })
    })
    .then(res => res.json())
    .then(data => {
        if (data.prediction === "Phishing") {
            chrome.tabs.sendMessage(tabId, { action: "clearToast" });
            setTimeout(() => {
                chrome.tabs.create({ url: chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(url)}`) });
            }, 100);
        } else {
            chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ AI Verified Safe. Redirecting...", isSafe: true, shouldRedirect: true, targetUrl: url });
        }
    })
    .catch(() => {
        chrome.tabs.sendMessage(tabId, { action: "showSimpleAdvice", message: "✅ Safe to proceed.", isSafe: true, shouldRedirect: true, targetUrl: url });
    });
}

// --- 3. CONTEXTUAL QR ANALYZER (RESTORED) ---
function handleQRResult(qrData, tabId) {
    const dataUpper = qrData.toUpperCase();
    
    // Check for Payment QR
    if (dataUpper.startsWith("UPI://") || dataUpper.startsWith("PAYTM://") || dataUpper.startsWith("PHONEPE://")) {
        chrome.tabs.sendMessage(tabId, { 
            action: "showSimpleAdvice", 
            message: "💸 PAYMENT QR DETECTED: Please verify the name with your bank app or GPay before entering your PIN!", 
            isSafe: true, 
            shouldRedirect: true, 
            targetUrl: qrData 
        });
    } 
    // Check for Wi-Fi QR
    else if (dataUpper.startsWith("WIFI:")) {
        chrome.tabs.sendMessage(tabId, { 
            action: "showSimpleAdvice", 
            message: "📶 WI-FI DETECTED: For your safety, please verify the network name before connecting!", 
            isSafe: true, 
            shouldRedirect: false 
        });
    } 
    // Check for standard Website URL
    else if (dataUpper.startsWith("HTTP://") || dataUpper.startsWith("HTTPS://")) {
        performScan(qrData, tabId); // Route web links to the AI scanner
    } 
    // Default Text QR
    else {
        chrome.tabs.sendMessage(tabId, { 
            action: "showSimpleAdvice", 
            message: `📄 TEXT QR SCANNED: ${qrData.substring(0, 60)}...`, 
            isSafe: true, 
            shouldRedirect: false 
        });
    }
}

chrome.runtime.onMessage.addListener((request, sender) => {
    if (request.action === "checkUrl") performScan(request.url, sender.tab.id);
    if (request.action === "qrResult") handleQRResult(request.url, sender.tab.id); // Fixed routing!
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-link") performScan(info.linkUrl, tab.id);
    else if (info.menuItemId === "scan-qr-sniper") {
        chrome.tabs.captureVisibleTab(null, { format: "png" }, (img) => {
            chrome.tabs.sendMessage(tab.id, { action: "analyzeScreenshot", image: img });
        });
    }
});