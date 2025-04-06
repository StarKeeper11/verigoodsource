// Add a console log to verify the content script is loading
console.log("TrueScan content script loaded");

// Listen for messages from the popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log("Message received in content script:", request);
    
    if (request.action === "analyzeWebsite") {
        try {
            // Get the current URL
            const currentUrl = window.location.href;
            const domain = window.location.hostname;
            
            console.log("Analyzing website:", domain);
            
            // Perform website analysis
            const analysisResult = analyzeWebsite(currentUrl, document);
            
            console.log("Analysis result:", analysisResult);
            
            // Send the results back to the popup
            sendResponse(analysisResult);
        } catch (error) {
            console.error("Analysis error:", error);
            sendResponse({ error: "Analysis failed: " + error.message });
        }
        
        return true; // Required to use sendResponse asynchronously
    }
});

// Function to analyze the website
function analyzeWebsite(url, document) {
    // In a real implementation, you would make API calls to credibility services
    // This is a simplified mock implementation
    
    // Extract domain
    const domain = new URL(url).hostname;
    
    // Analyze content on the page
    const textContent = document.body.innerText;
    const headings = document.querySelectorAll('h1, h2, h3');
    const links = document.querySelectorAll('a');
    const images = document.querySelectorAll('img');
    
    // Calculate mock scores
    const contentLength = textContent.length;
    const wordCount = textContent.split(/\s+/).length;
    const headingCount = headings.length;
    const linkCount = links.length;
    const imageCount = images.length;
    
    // These would normally be based on real analysis
    const contentQualityScore = calculateContentQuality(wordCount, headingCount, linkCount, imageCount);
    const domainAgeScore = calculateDomainAge(domain);
    const reliabilityScore = calculateReliability(domain, linkCount);
    
    // Calculate overall score
    const overallScore = Math.round((contentQualityScore + domainAgeScore + reliabilityScore) / 3);
    
    // Generate a summary
    const summary = generateSummary(domain, overallScore, contentQualityScore, domainAgeScore, reliabilityScore);
    
    return {
        overallScore: overallScore,
        domainAge: domainAgeScore + "/100",
        contentQuality: contentQualityScore + "/100",
        sourceReliability: reliabilityScore + "/100",
        summary: summary
    };
}

// Helper functions for calculating scores
function calculateContentQuality(wordCount, headingCount, linkCount, imageCount) {
    // Mock algorithm - in a real extension, this would be more sophisticated
    let score = 50; // Base score
    
    // Content length factor
    if (wordCount > 1000) score += 15;
    else if (wordCount > 500) score += 10;
    else if (wordCount > 200) score += 5;
    
    // Heading structure factor
    if (headingCount > 5) score += 10;
    else if (headingCount > 2) score += 5;
    
    // Media richness factor
    if (imageCount > 5 && linkCount > 10) score += 15;
    else if (imageCount > 2 && linkCount > 5) score += 10;
    
    // Cap the score at 100
    return Math.min(100, Math.max(0, score));
}

function calculateDomainAge(domain) {
    // In a real extension, you would use WHOIS data or a domain age API
    // This is just a mock implementation based on known domains
    
    const knownDomains = {
        "google.com": 95,
        "wikipedia.org": 90,
        "amazon.com": 85,
        "facebook.com": 80,
        "twitter.com": 75,
        "reddit.com": 70,
        "nytimes.com": 85,
        "bbc.co.uk": 85,
        "cnn.com": 80,
        "nature.com": 88 // Adding nature.com explicitly
    };
    
    // Check if the domain or its parent is in our known list
    for (const knownDomain in knownDomains) {
        if (domain === knownDomain || domain.endsWith('.' + knownDomain)) {
            return knownDomains[knownDomain];
        }
    }
    
    // For unknown domains, generate a semi-random score
    // In a real implementation, this would be based on actual domain registration data
    const hash = simpleHash(domain);
    return 40 + (hash % 40); // Score between 40-79 for unknown domains
}

function calculateReliability(domain, linkCount) {
    // In a real extension, you would check against known reliable sources databases
    // This is just a mock implementation
    
    const highlyReliableDomains = [
        "edu", "gov", "wikipedia.org", "bbc.co.uk", "reuters.com", 
        "nature.com", "science.org", "nejm.org", "mayoclinic.org"
    ];
    
    const moderatelyReliableDomains = [
        "nytimes.com", "washingtonpost.com", "theguardian.com", 
        "economist.com", "scientificamerican.com", "nationalgeographic.com"
    ];
    
    // Check domain TLD and known reliable domains
    for (const reliableDomain of highlyReliableDomains) {
        if (domain.endsWith(reliableDomain)) {
            return 85 + (Math.random() * 15); // 85-100 score
        }
    }
    
    for (const reliableDomain of moderatelyReliableDomains) {
        if (domain.endsWith(reliableDomain)) {
            return 70 + (Math.random() * 15); // 70-85 score
        }
    }
    
    // Default score based on domain and outbound links
    let score = 50;
    
    // More outbound links might indicate better sourcing
    if (linkCount > 20) score += 10;
    else if (linkCount > 10) score += 5;
    
    // Adjust based on TLD
    if (domain.endsWith('.org')) score += 5;
    if (domain.endsWith('.com')) score += 0;
    if (domain.endsWith('.info')) score -= 5;
    
    return Math.min(100, Math.max(0, score));
}

function generateSummary(domain, overallScore, contentScore, ageScore, reliabilityScore) {
    // Generate a summary based on the scores
    let summary = `This website (${domain}) has an overall credibility score of ${overallScore}/100. `;
    
    if (overallScore >= 80) {
        summary += "This indicates a highly credible source. ";
    } else if (overallScore >= 60) {
        summary += "This indicates a moderately credible source. ";
    } else {
        summary += "This indicates a source that may require additional verification. ";
    }
    
    // Add details about the strongest and weakest aspects
    const scores = [
        { name: "content quality", value: contentScore },
        { name: "domain age", value: ageScore },
        { name: "source reliability", value: reliabilityScore }
    ];
    
    scores.sort((a, b) => b.value - a.value);
    summary += `The strongest aspect is ${scores[0].name} (${scores[0].value}/100), `;
    summary += `while ${scores[2].name} (${scores[2].value}/100) could be improved.`;
    
    return summary;
}

function simpleHash(str) {
    // Simple string hash function for mock scoring
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
}