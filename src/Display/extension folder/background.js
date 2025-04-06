// Initialize extension when installed
chrome.runtime.onInstalled.addListener(function() {
    console.log("TrueScan Verifier extension installed");
    
    // Initialize default settings
    chrome.storage.sync.get({
        credibilityThreshold: '50',
        autoAnalyze: true,
        showNotifications: true,
        contextualMenu: true,
        highlightClaims: false,
        saveHistory: true
    }, function(items) {
        chrome.storage.sync.set(items);
    });
});