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
    if (!chrome.runtime || !chrome.runtime.sendMessage) return; 

    event.preventDefault();
    showToast("🛡️ Agentic Shield: Scanning payload...");

    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href }, function(response) {
        handleAiResponse(response, target.href, true);
    });
});

// --- 3. AUTO-QR CODE SCANNER ---
function scanImageForQR(imgElement) {
    if (!isShieldActive || !window.jsQR) return;

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d', { willReadFrequently: true });
    
    if (imgElement.width === 0 || imgElement.height === 0) return;

    canvas.width = imgElement.width;
    canvas.height = imgElement.height;
    
    try {
        context.drawImage(imgElement, 0, 0, canvas.width, canvas.height);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        
        // Pass pixels to jsQR
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        
        if (code && code.data.startsWith('http')) {
            console.log("Agentic Shield found a hidden QR URL:", code.data);
            showToast("🛡️ Agentic Shield: Secret QR Code detected. Scanning...");
            
            // Send the hidden URL to your Python API!
            chrome.runtime.sendMessage({ action: "checkUrl", url: code.data }, function(response) {
                handleAiResponse(response, code.data, false); // false = don't auto-redirect if safe
            });
        }
    } catch (e) {
        // Ignore cross-origin image blocks
    }
}

// Invisible watcher for new images
const observer = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
            if (node.tagName === 'IMG') {
                node.onload = () => scanImageForQR(node);
            } else if (node.querySelectorAll) {
                const imgs = node.querySelectorAll('img');
                imgs.forEach(img => { img.onload = () => scanImageForQR(img); });
            }
        });
    });
});

observer.observe(document.body, { childList: true, subtree: true });


// --- 4. HELPER FUNCTIONS ---
let activeToast = null;

function showToast(message) {
    if (activeToast) activeToast.remove();
    activeToast = document.createElement('div');
    activeToast.innerText = message;
    activeToast.style.cssText = "position:fixed; bottom:20px; right:20px; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; z-index:999999; font-family:system-ui; font-size:14px; font-weight:bold; box-shadow:0 10px 25px rgba(0,0,0,0.5); transition: all 0.3s ease;";
    document.body.appendChild(activeToast);
}

function handleAiResponse(response, targetUrl, isClick) {
    if (chrome.runtime.lastError || !response) {
        if (activeToast) activeToast.remove();
        if (isClick) window.location.href = targetUrl;
        return;
    }
    if (response.status === "Phishing") {
        if (activeToast) activeToast.remove();
        // Redirect to Red Screen of Death
        window.location.href = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(targetUrl)}`);
    } else {
        if (activeToast) {
            activeToast.innerText = "✅ Verified Safe.";
            activeToast.style.background = "#10b981";
            setTimeout(() => {
                activeToast.remove(); 
                if (isClick) window.location.href = targetUrl; 
            }, 500); 
        }
    }
}