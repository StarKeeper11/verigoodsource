import os
import requests
import json
from pprint import pprint
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def chicken_soup(url: str) -> Optional[BeautifulSoup]:
    """
    Fetch a webpage and parse it with BeautifulSoup.
    
    Parameters:
    - url (str): The URL to fetch
    
    Returns:
    - BeautifulSoup object or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def extract_main_content(soup: BeautifulSoup) -> str:
    """
    Extract the main textual content from a BeautifulSoup object.
    
    Parameters:
    - soup (BeautifulSoup): Parsed HTML
    
    Returns:
    - str: Extracted main content text
    """
    main_content = (soup.find('main') or 
                   soup.find('article') or 
                   soup.find('div', {'id': 'content'}) or
                   soup.find('div', {'class': 'content'}))
    
    if main_content:
        # Extract text and add line breaks between paragraphs
        return '\n\n'.join(p.get_text(strip=True) for p in main_content.find_all(['p', 'div']))
    else:
        # Fallback to extracting all text with line breaks
        return '\n\n'.join(soup.stripped_strings)

def check_bias(text: str, api_key: Optional[str] = None, max_tokens: int = 500) -> Dict[str, Any]:
    """
    Analyze text for potential bias using an LLM API.
    
    Parameters:
    - text (str): The article text to analyze
    - api_key (str, optional): API key for the LLM service
    - max_tokens (int): Maximum length of text to analyze
    
    Returns:
    - dict: Analysis results containing bias assessment
    """
    # Truncate text if needed
    if len(text) > max_tokens * 4:  # Rough character-to-token ratio estimation
        text = text[:max_tokens * 4] + "..."
    
    # Using OpenAI's API (could be replaced with another LLM API)
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "No API key provided. Set OPENAI_API_KEY environment variable or pass as parameter."
            }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"""
    Analyze the following article text for potential bias. Consider:
    1. Political leaning (left, right, center)
    2. Use of loaded language or emotional appeal
    3. Selection of facts (what's included vs. omitted)
    4. Tone (neutral, inflammatory, promotional)
    5. Citation of sources (balanced, one-sided, missing)
    
    Provide a concise analysis of any detected bias and an overall bias score 
    from 1-10 where 1 is extremely neutral and 10 is extremely biased.
    
    ARTICLE TEXT:
    {text}
    """
    
    try:
        payload = {
            "model": "gpt-4o",  # Or another appropriate model
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1  # Low temperature for more consistent analysis
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            
            # Extract and format the results
            return {
                "success": True,
                "bias_analysis": analysis,
                "raw_response": result
            }
        else:
            return {
                "success": False,
                "error": f"API error: {response.status_code}",
                "details": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }

def analyze_article_bias(url: str) -> Dict[str, Any]:
    """
    Extract content from a URL and analyze it for bias.
    
    Parameters:
    - url (str): URL of the article to analyze
    
    Returns:
    - dict: Analysis results containing bias assessment
    """
    # Get the article content
    soup = chicken_soup(url)
    
    if not soup:
        return {"success": False, "error": "Failed to retrieve the webpage"}
    
    # Extract the main content
    article_text = extract_main_content(soup)
    
    if not article_text:
        return {"success": False, "error": "Failed to extract article text"}
    
    # Get the title if available
    title = soup.title.string if soup.title else "Untitled Article"
    
    # Check for bias in the extracted text
    bias_results = check_bias(article_text)
    
    # Return combined results
    return {
        "url": url,
        "title": title,
        "content_length": len(article_text),
        "bias_analysis": bias_results
    }

def save_bias_analysis(results: Dict[str, Any], output_file: str = "bias_analysis.json") -> None:
    """
    Save bias analysis results to a JSON file.
    
    Parameters:
    - results (dict): Analysis results from analyze_article_bias
    - output_file (str): Path to save the results
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Analysis saved to {output_file}")
    except Exception as e:
        print(f"Error saving analysis: {e}")

# Example usage when run as a script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze article bias using LLM")
    parser.add_argument("url", help="URL of the article to analyze")
    parser.add_argument("--output", "-o", help="Output file for analysis results", default="bias_analysis.json")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY environment variable)")
    
    args = parser.parse_args()
    
    print(f"Analyzing article bias for: {args.url}")
    results = analyze_article_bias(args.url)
    
    # Print a summary to console
    if results.get("success", True):
        print(f"\nArticle: {results.get('title', 'Unknown Title')}")
        print(f"Content length: {results.get('content_length', 0)} characters")
        
        bias_data = results.get("bias_analysis", {})
        if bias_data.get("success", False):
            print("\nBias Analysis:")
            print(bias_data.get("bias_analysis", "No analysis available"))
        else:
            print(f"\nBias analysis failed: {bias_data.get('error', 'Unknown error')}")
    else:
        print(f"Analysis failed: {results.get('error', 'Unknown error')}")
    
    # Save full results to file
    save_bias_analysis(results, args.output)