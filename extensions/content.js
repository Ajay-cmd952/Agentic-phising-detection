// --- 1. MASTER KILL SWITCH LOGIC ---
let isShieldActive = true; 
chrome.storage.local.get(['shieldActive'], function(result) {
    if (result.shieldActive === false) isShieldActive = false;
});
chrome.storage.onChanged.addListener(function(changes) {
    if (changes.shieldActive) isShieldActive = changes.shieldActive.newValue;
});

// --- 2. REGULAR LINK INTERCEPTOR ---
document.addEventListener('click', function(event) {
    let target = event.target.closest('a'); 
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;
    if (!isShieldActive) return;

    event.preventDefault();
    showToast("🛡️ Agentic Shield: Scanning payload...");

    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href }, function(response) {
        handleAiResponse(response, target.href, true);
    });
});

// --- 3. AUTO-QR CODE SCANNER ---
function scanImageForQR(imgElement) {
    if (!isShieldActive || !window.jsQR) return;

    imgElement.crossOrigin = "Anonymous";
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d', { willReadFrequently: true });
    
    if (imgElement.width === 0 || imgElement.height === 0) return;
    canvas.width = imgElement.width;
    canvas.height = imgElement.height;
    
    try {
        context.drawImage(imgElement, 0, 0, canvas.width, canvas.height);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        
        if (code && code.data.startsWith('http')) {
            showToast("🛡️ Agentic Shield: Secret QR Code detected. Scanning...");
            chrome.runtime.sendMessage({ action: "checkUrl", url: code.data }, function(response) {
                handleAiResponse(response, code.data, false); 
            });
        }
    } catch (e) {}
}

function scanExistingImages() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (img.complete && img.naturalHeight !== 0) scanImageForQR(img);
        else img.onload = () => scanImageForQR(img);
    });
}

if (document.readyState === 'complete') scanExistingImages();
else window.addEventListener('load', scanExistingImages);

const observer = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
            if (node.tagName === 'IMG') node.onload = () => scanImageForQR(node);
            else if (node.querySelectorAll) {
                node.querySelectorAll('img').forEach(img => { img.onload = () => scanImageForQR(img); });
            }
        });
    });
});
observer.observe(document.body, { childList: true, subtree: true });

// --- 4. THE ORIGINAL TOAST HELPER ---
let activeToast = null;

function showToast(message) {
    if (activeToast) activeToast.remove();
    activeToast = document.createElement('div');
    activeToast.innerText = message;
    activeToast.style.cssText = "position:fixed; bottom:20px; right:20px; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; z-index:999999; font-family:system-ui; font-size:14px; font-weight:bold; box-shadow:0 10px 25px rgba(0,0,0,0.5); transition: all 0.3s ease;";
    document.body.appendChild(activeToast);
}

// --- 🛠️ UPDATED: FULL-SCREEN OVERLAY ---
function handleAiResponse(response, targetUrl, isClick) {
    if (chrome.runtime.lastError || !response) {
        if (activeToast) activeToast.remove();
        if (isClick) window.location.href = targetUrl;
        return;
    }
    
    if (response.status === "Phishing") {
        if (activeToast) activeToast.remove();
        
        let overlay = document.createElement('div');
        overlay.id = 'agentic-shield-warning-overlay';
        overlay.style.cssText = `
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: rgba(15, 23, 42, 0.95) !important;
            backdrop-filter: blur(10px) !important;
            z-index: 2147483647 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            color: white !important;
        `;
        
        overlay.innerHTML = `
            <div style="background: #1e293b; padding: 40px; border-radius: 16px; border-top: 5px solid #ef4444; max-width: 500px; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);">
                <h1 style="color: #ef4444; font-size: 24px; margin-bottom: 16px; margin-top: 0;">🛡️ Connection Intercepted</h1>
                <p style="color: #cbd5e1; font-size: 16px; margin-bottom: 30px; line-height: 1.5;">Agentic Shield has blocked this navigation. The destination has been identified as a highly probable phishing or malware distribution vector.</p>
                
                <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin-bottom: 30px; word-break: break-all; color: #94a3b8; font-size: 14px;">
                    <strong>Blocked Target:</strong><br>${targetUrl}
                </div>

                <button id="agentic-return-btn" style="background: #ef4444; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-right: 15px; font-size: 16px; transition: background 0.2s;">Return to Safety</button>
                <button id="agentic-ignore-btn" style="background: transparent; color: #94a3b8; border: 1px solid #475569; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; transition: all 0.2s;">Ignore Risk (Unsafe)</button>
            </div>
        `;
        
        document.documentElement.appendChild(overlay);
        
        document.getElementById('agentic-return-btn').addEventListener('click', () => {
            overlay.remove(); 
        });
        
        document.getElementById('agentic-ignore-btn').addEventListener('click', () => {
            overlay.remove();
            window.location.href = targetUrl; 
        });

    } else {
        if (activeToast) {
            activeToast.innerText = "✅ Verified Safe.";
            activeToast.style.background = "#10b981";
            setTimeout(() => {
                activeToast.remove(); 
                if (isClick) window.location.href = targetUrl; 
            }, 1000); 
        }
    }
}

// --- 5. THE ORIGINAL SNIPER RECEIVER ---
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "analyzeScreenshot") {
        showToast("🛡️ Sniper Mode: Scanning screen...");
        
        const img = new Image();
        img.src = request.image;
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = img.width; canvas.height = img.height;
            context.drawImage(img, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height);
            
            if (code) {
                if (code.data.startsWith('http')) {
                    showToast("🛡️ Target acquired. Analyzing...");
                    chrome.runtime.sendMessage({ action: "checkUrl", url: code.data }, (res) => handleAiResponse(res, code.data, false));
                } else if (code.data.startsWith('upi://')) {
                    showToast("💸 UPI Payment QR Detected.");
                    setTimeout(() => { if(activeToast) activeToast.remove(); }, 3000);
                } else {
                    showToast("✅ Safe text found in QR.");
                    setTimeout(() => { if(activeToast) activeToast.remove(); }, 3000);
                }
            } else {
                showToast("❌ No QR detected on screen.");
                setTimeout(() => { if(activeToast) activeToast.remove(); }, 2500);
            }
        };
    }
});