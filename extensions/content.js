let isShieldActive = true; 
chrome.storage.local.get(['shieldActive'], (res) => { if (res.shieldActive === false) isShieldActive = false; });
chrome.storage.onChanged.addListener((changes) => { if (changes.shieldActive) isShieldActive = changes.shieldActive.newValue; });

// --- 1. SEAMLESS LINK INTERCEPTOR ---
document.addEventListener('click', function(event) {
    let target = event.target.closest('a'); 
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;
    if (!isShieldActive) return;

    event.preventDefault(); 
    showToast("🛡️ Agentic Shield: Scanning payload...", "#D4AF37");

    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href }, (response) => {
        if (response && response.status !== "Phishing") {
            // SUCCESS: Change the color of the toast to green and redirect automatically
            if (activeToast) {
                activeToast.innerText = "✅ Link Verified Safe. Redirecting...";
                activeToast.style.color = "#10b981";
                activeToast.style.borderColor = "#10b981";
            }
            setTimeout(() => {
                window.location.href = target.href; 
            }, 800); // 0.8 second pause so the user sees the "Safe" message
        } else {
            if (activeToast) activeToast.remove();
        }
    });
});

// --- 2. THE GOLDEN TOAST HELPER ---
let activeToast = null;
function showToast(message, color = "#D4AF37") {
    if (activeToast) activeToast.remove();
    activeToast = document.createElement('div');
    activeToast.innerText = message;
    activeToast.style.cssText = `position:fixed; bottom:30px; right:30px; background:#050505; color:${color}; padding:14px 28px; border-radius:12px; z-index:2147483647; font-family:sans-serif; font-size:14px; font-weight:600; box-shadow:0 10px 40px rgba(0,0,0,0.8); border: 1px solid ${color}; backdrop-filter: blur(10px); transition: all 0.3s ease;`;
    document.body.appendChild(activeToast);
}

// --- 3. QR LOGIC (Preserved for later) ---
chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "analyzeScreenshot") {
        showToast("🛡️ Sniper Mode: Scanning...", "#D4AF37");
        const img = new Image();
        img.src = request.image;
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = img.width; canvas.height = img.height;
            context.drawImage(img, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR ? jsQR(imageData.data, imageData.width, imageData.height) : null;
            if (code) {
                chrome.runtime.sendMessage({ action: "qrResult", url: code.data });
            } else {
                showToast("❌ No QR found", "#ef4444");
                setTimeout(() => activeToast?.remove(), 2000);
            }
        };
    }
});