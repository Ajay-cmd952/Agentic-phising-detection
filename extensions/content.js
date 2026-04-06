// Listen for EVERY click on the webpage
document.addEventListener('click', function(event) {
    // Check if the thing we clicked was a link (or inside a link button)
    let target = event.target.closest('a'); 
    
    // If it's not a link, or it's just a javascript trigger, ignore it
    if (!target || !target.href || target.href.startsWith('javascript:') || target.href.startsWith('mailto:')) return;

    // 🛑 FREEZE THE BROWSER! Do not open the link yet!
    event.preventDefault();

    // Send the URL to our background script to ask the AI
    chrome.runtime.sendMessage({ action: "checkUrl", url: target.href }, function(response) {
        if (response.status === "Phishing") {
            // It's bad! Redirect to the Red Screen of Death
            window.location.href = chrome.runtime.getURL(`warning.html?url=${encodeURIComponent(target.href)}`);
        } else {
            // It's safe! Let the browser continue to the website normally
            window.location.href = target.href;
        }
    });
});