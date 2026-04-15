let isShieldActive = true; 
chrome.storage.local.get(['shieldActive'], (res) => { if (res.shieldActive === false) isShieldActive = false; });
chrome.storage.onChanged.addListener((changes) => { if (changes.shieldActive) isShieldActive = changes.shieldActive.newValue; });

let activeToast = null;
function showToast(message, color = "#D4AF37") {
    if (activeToast) activeToast.remove();
    activeToast = document.createElement('div');
    activeToast.innerText = message;
    activeToast.style.cssText = `position:fixed; bottom:30px; right:30px; width: 300px; background:#050505; color:${color}; padding:16px; border-radius:12px; z-index:2147483647; font-family: sans-serif; font-size:14px; font-weight:bold; line-height: 1.4; box-shadow:0 10px 40px rgba(0,0,0,0.8); border: 1px solid ${color}; backdrop-filter: blur(10px); transition: all 0.3s ease;`;
    document.body.appendChild(activeToast);
}

document.addEventListener('click', function(event) {
    let target = event.target.closest('a'); 
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;
    if (!isShieldActive) return;
    event.preventDefault(); 
    showToast("🛡️ Agentic Shield: Checking link safety...", "#D4AF37");
    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href });
});

chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "clearToast") if (activeToast) activeToast.remove();

    if (request.action === "showSimpleAdvice") {
        if (activeToast) {
            activeToast.innerText = request.message;
            activeToast.style.color = "#10b981";
            activeToast.style.borderColor = "#10b981";
            if (request.shouldRedirect && request.targetUrl) {
                setTimeout(() => { window.location.href = request.targetUrl; }, 1000);
            } else {
                setTimeout(() => { if (activeToast) activeToast.remove(); }, 6000);
            }
        }
    }

    if (request.action === "analyzeScreenshot") {
        showToast("🛡️ Sniper Mode: Searching for QR...", "#D4AF37");
        const img = new Image();
        img.src = request.image;
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            canvas.width = img.width; canvas.height = img.height;
            
            // --- PASS 1: NATURAL SCAN ---
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            let code = (typeof jsQR !== 'undefined') ? jsQR(imageData.data, imageData.width, imageData.height) : null;

            if (!code) {
                // --- PASS 2: HIGH CONTRAST (For shadows) ---
                ctx.filter = 'contrast(150%) grayscale(100%)';
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                code = jsQR(imageData.data, imageData.width, imageData.height);
            }

            if (!code) {
                // --- PASS 3: AGGRESSIVE BLACK/WHITE (For Watermarks) ---
                ctx.filter = 'threshold(0.5) contrast(200%) grayscale(100%)';
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                code = jsQR(imageData.data, imageData.width, imageData.height);
            }

            if (code) {
                showToast("🛡️ QR Found. Scanning content...", "#D4AF37");
                chrome.runtime.sendMessage({ action: "qrResult", url: code.data });
            } else {
                showToast("❌ Scanning Failed. Please zoom in or ensure the QR is clear of watermarks.", "#ef4444");
                setTimeout(() => { if (activeToast) activeToast.remove(); }, 4000);
            }
        };
    }
});