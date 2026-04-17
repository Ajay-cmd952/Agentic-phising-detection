let isShieldActive = true; 
chrome.storage.local.get(['shieldActive'], (res) => { if (res.shieldActive === false) isShieldActive = false; });
chrome.storage.onChanged.addListener((changes) => { if (changes.shieldActive) isShieldActive = changes.shieldActive.newValue; });

let activeToast = null;
function showToast(message, color = "#D4AF37", border = "#D4AF37") {
    if (activeToast) activeToast.remove();
    activeToast = document.createElement('div');
    activeToast.id = "agentic-toast"; 
    activeToast.innerText = message;
    activeToast.style.cssText = `position:fixed; bottom:30px; right:30px; width: 300px; background:#050505; color:${color}; padding:16px; border-radius:12px; z-index:2147483647; font-family: sans-serif; font-size:14px; font-weight:bold; line-height: 1.4; box-shadow:0 10px 40px rgba(0,0,0,0.8); border: 2px solid ${border}; backdrop-filter: blur(10px); transition: all 0.3s ease;`;
    document.body.appendChild(activeToast);
}

window.addEventListener('load', () => {
    const oldToast = document.getElementById("agentic-toast");
    if (oldToast) oldToast.remove();
});

document.addEventListener('click', function(event) {
    let target = event.target.closest('a'); 
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;
    if (!isShieldActive) return;
    event.preventDefault(); 
    
    showToast("🛡️ Agentic Shield: Checking link safety...", "#D4AF37", "#D4AF37");
    
    // FIXED: Ultimate fallback timer. Toast dies after 8 seconds no matter what happens.
    setTimeout(() => { if (activeToast) activeToast.remove(); }, 8000); 
    
    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href });
});

chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "clearToast") { 
        if (activeToast) activeToast.remove(); 
    }

    // Handles normal URL clicks
    if (request.action === "showSimpleAdvice") {
        if (activeToast) {
            activeToast.innerText = request.message;
            activeToast.style.color = "#10b981";
            activeToast.style.borderColor = "#10b981";
            
            if (request.shouldRedirect && request.targetUrl) {
                setTimeout(() => { 
                    const url = request.targetUrl;
                    if (activeToast) activeToast.remove(); 
                    window.location.href = url; 
                }, 800);
            } else {
                setTimeout(() => { if (activeToast) activeToast.remove(); }, 5000);
            }
        }
    }

    // NEW: Specifically handles the Download Warning (distinct styling)
    if (request.action === "showDownloadAdvice") {
        showToast(request.message, "#ef4444", "#ef4444"); // Bright Red Warning
        setTimeout(() => { if (activeToast) activeToast.remove(); }, 7000);
    }

    // Handles QR Snipping
    if (request.action === "analyzeScreenshot") {
        showToast("🛡️ Sniper Mode: Searching for QR...", "#D4AF37", "#D4AF37");
        const img = new Image();
        img.src = request.image;
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            canvas.width = img.width; canvas.height = img.height;
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            let code = (typeof jsQR !== 'undefined') ? jsQR(imageData.data, imageData.width, imageData.height) : null;

            if (!code) {
                ctx.filter = 'contrast(150%) grayscale(100%)';
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                code = jsQR(imageData.data, imageData.width, imageData.height);
            }

            if (!code) {
                ctx.filter = 'threshold(0.5) contrast(200%) grayscale(100%)';
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                code = jsQR(imageData.data, imageData.width, imageData.height);
            }

            if (code) {
                showToast("🛡️ QR Found. Scanning content...", "#D4AF37", "#D4AF37");
                chrome.runtime.sendMessage({ action: "qrResult", url: code.data });
            } else {
                showToast("❌ No QR detected. Try zooming in.", "#ef4444", "#ef4444");
                setTimeout(() => { if (activeToast) activeToast.remove(); }, 3000);
            }
        };
    }
});