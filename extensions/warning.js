document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const badUrl = urlParams.get('url') || 'Unknown URL';

    document.getElementById('go-back').addEventListener('click', () => {
        window.close(); 
    });

    // The Foolproof Copy & Paste Handoff
    document.getElementById('analyze-threat').addEventListener('click', () => {
        // 1. Copy the malicious URL to the clipboard
        navigator.clipboard.writeText(badUrl).then(() => {
            // 2. Alert the user on what to do next
            alert("✅ Malicious URL copied to clipboard!\n\nRedirecting to Admin Console. Please paste (Ctrl+V) the URL into the Deep Scan Engine to view the full threat report.");
            
            // 3. Open the clean Streamlit URL (no parameters to break the iframe)
            const streamlitAppUrl = "https://agentic-phising-detection-xikuqb8mecesbqbmetkvgu.streamlit.app/"; 
            window.open(streamlitAppUrl, '_blank');
        }).catch(err => {
            alert("Failed to copy URL. Please copy it manually and proceed to the Admin Console.");
            window.open("https://agentic-phising-detection-xikuqb8mecesbqbmetkvgu.streamlit.app/", '_blank');
        });
    });

    document.getElementById('proceed').addEventListener('click', () => {
        if (confirm("⚠️ You are bypassing Agentic Shield. If you are 100% sure this is a safe link, click OK to proceed.")) {
            window.location.href = badUrl; 
        }
    });
});