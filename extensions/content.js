// Listen for EVERY click on the webpage
document.addEventListener('click', function(event) {
    let target = event.target.closest('a'); 
    
    // Ignore non-links or javascript triggers
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;

    // 🛡️ SAFETY CHECK: If the extension was reloaded but the page wasn't refreshed, let the click happen normally to prevent crashes.
    if (!chrome.runtime || !chrome.runtime.sendMessage) {
        return; 
    }

    // 🛑 FREEZE THE BROWSER!
    event.preventDefault();

    // --- PRESENTATION MODE: Inject a sleek scanning popup ---
    let toast = document.createElement('div');
    toast.innerText = "🛡️ Agentic Shield: Scanning payload...";
    toast.style.cssText = "position:fixed; bottom:20px; right:20px; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; z-index:999999; font-family:system-ui, sans-serif; font-size:14px; font-weight:bold; box-shadow:0 10px 25px rgba(0,0,0,0.5); transition: all 0.3s ease;";
    document.body.appendChild(toast);
    // ---------------------------------------------------------

    // Send the URL to the AI
    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href }, function(response) {
        
        // Safety catch if the API connection drops
        if (chrome.runtime.lastError || !response) {
            toast.remove();
            window.location.href = target.href;
            return;
        }

        if (response.status === "Phishing") {
            // It's bad! Clean up popup and Redirect to the Red Screen of Death
            toast.remove(); 
            window.location.href = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(target.href)}`);
        } else {
            // It's safe! Update the popup to Green for 1 second so the professors can see it
            toast.innerText = "✅ Verified Safe. Redirecting...";
            toast.style.background = "#10b981";
            
            setTimeout(() => {
                toast.remove(); // 🧹 THIS FIXES THE STICKY POPUP ON THE BACK BUTTON!
                window.location.href = target.href; // Now actually open the link
            }, 1000); // 1 second delay
        }
    });
});