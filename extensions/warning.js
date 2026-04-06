document.addEventListener('DOMContentLoaded', () => {
    // Grab the bad URL from the address bar
    const urlParams = new URLSearchParams(window.location.search);
    const badUrl = urlParams.get('url') || 'Unknown URL';
    
    // Display it on the screen so the user knows what we blocked
    document.getElementById('bad-url').innerText = "Target: " + badUrl;

    // Button 1: Go Back (Closes the red warning tab)
    document.getElementById('go-back').addEventListener('click', () => {
        window.close(); 
    });

    // Button 2: Proceed Anyway (Sends them to the danger zone!)
    document.getElementById('proceed').addEventListener('click', () => {
        window.location.href = badUrl; 
    });
});