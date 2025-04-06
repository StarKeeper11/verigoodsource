document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const credibilityThreshold = document.getElementById('credibility-threshold');
    const autoAnalyze = document.getElementById('auto-analyze');
    const showNotifications = document.getElementById('show-notifications');
    const contextualMenu = document.getElementById('contextual-menu');
    const highlightClaims = document.getElementById('highlight-claims');
    const saveHistory = document.getElementById('save-history');
    const saveBtn = document.getElementById('save-btn');
    const statusMessage = document.getElementById('status-message');
    
    // Load saved settings
    loadSettings();
    
    // Add event listener for save button
    saveBtn.addEventListener('click', saveSettings);
    
    function loadSettings() {
        chrome.storage.sync.get({
            // Default values
            credibilityThreshold: '50',
            autoAnalyze: true,
            showNotifications: true,
            contextualMenu: true,
            highlightClaims: false,
            saveHistory: true
        }, function(items) {
            // Set form values based on saved settings
            credibilityThreshold.value = items.credibilityThreshold;
            autoAnalyze.checked = items.autoAnalyze;
            showNotifications.checked = items.showNotifications;
            contextualMenu.checked = items.contextualMenu;
            highlightClaims.checked = items.highlightClaims;
            saveHistory.checked = items.saveHistory;
        });
    }
    
    function saveSettings() {
        // Get current values
        const settings = {
            credibilityThreshold: credibilityThreshold.value,
            autoAnalyze: autoAnalyze.checked,
            showNotifications: showNotifications.checked,
            contextualMenu: contextualMenu.checked,
            highlightClaims: highlightClaims.checked,
            saveHistory: saveHistory.checked
        };
        
        // Save to Chrome storage
        chrome.storage.sync.set(settings, function() {
            // Show success message
            statusMessage.textContent = 'Settings saved successfully!';
            statusMessage.className = 'status success';
            statusMessage.style.display = 'block';
            
            // Hide message after a few seconds
            setTimeout(function() {
                statusMessage.style.display = 'none';
            }, 3000);
        });
    }
});