document.addEventListener('DOMContentLoaded', () => {
    // Grab the bad URL from the background
    const urlParams = new URLSearchParams(window.location.search);
    const badUrl = urlParams.get('url') || 'Unknown URL';

    // Button 1: Return to Safety (Closes the red warning tab)
    document.getElementById('go-back').addEventListener('click', () => {
        window.close(); 
    });

    // Button 2: Ignore Risk (Sends them to the danger zone!)
    document.getElementById('proceed').addEventListener('click', () => {
        window.location.href = badUrl; 
    });
});