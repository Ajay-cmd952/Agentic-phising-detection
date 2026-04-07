// Check the Master Toggle Switch State!
let isShieldActive = true; 
chrome.storage.local.get(['shieldActive'], function(result) {
    if (result.shieldActive === false) isShieldActive = false;
});

// Listen in real-time if the user flips the switch
chrome.storage.onChanged.addListener(function(changes) {
    if (changes.shieldActive) isShieldActive = changes.shieldActive.newValue;
});

// Listen for EVERY click on the webpage
document.addEventListener('click', function(event) {
    let target = event.target.closest('a'); 
    
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;

    // 🛑 MASTER KILL SWITCH: If Shield is OFF, let the user browse normally!
    if (!isShieldActive) return;

    // 🛡️ SAFETY CHECK: Prevent crashes if extension reloaded
    if (!chrome.runtime || !chrome.runtime.sendMessage) {
        return; 
    }

    event.preventDefault();

    // --- PRESENTATION MODE: Inject a sleek scanning popup ---
    let toast = document.createElement('div');
    toast.innerText = "🛡️ Agentic Shield: Scanning payload...";
    toast.style.cssText = "position:fixed; bottom:20px; right:20px; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; z-index:999999; font-family:system-ui, sans-serif; font-size:14px; font-weight:bold; box-shadow:0 10px 25px rgba(0,0,0,0.5); transition: all 0.3s ease;";
    document.body.appendChild(toast);
    // ---------------------------------------------------------

    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href }, function(response) {
        
        if (chrome.runtime.lastError || !response) {
            toast.remove();
            window.location.href = target.href;
            return;
        }

        if (response.status === "Phishing") {
            toast.remove(); 
            window.location.href = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(target.href)}`);
        } else {
            toast.innerText = "✅ Verified Safe.";
            toast.style.background = "#10b981";
            
            setTimeout(() => {
                toast.remove(); 
                window.location.href = target.href; 
            }, 200); // 200ms delay - fast enough for real life, but visible for presentation!
        }
    });
});