import time
import requests

def check_bias_with_openai(text: str, api_key: str, max_retries: int = 5, backoff_factor: int = 2) -> dict:
    """Analyzes text for potential bias using OpenAI's API with retry logic."""
    if not api_key:
        return {"success": False, "error": "API key is required"}

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

    payload = {
        "model": "gpt-3.5-turbo",  # You can use gpt-4 if available
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1  # Low temperature for more consistent analysis
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",  # Correct OpenAI API endpoint
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "bias_analysis": analysis,
                    "raw_response": result
                }
            elif response.status_code == 429:
                # Handle rate limit error, retry with backoff
                print(f"Rate limit hit. Retrying in {backoff_factor ** retries} seconds...")
                time.sleep(backoff_factor ** retries)
                retries += 1
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

    # If we reached here, it means we've exceeded max retries
    return {"success": False, "error": "Max retries exceeded due to rate limiting."}

# Example usage
if __name__ == "__main__":
    api_key = "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"  # Replace with your API key
    text = """
    The political debate is often divided. Left-wing ideologies believe in a stronger government, providing social services,
    while right-wing ideologies often advocate for limited government and economic freedom. Both perspectives shape the 
    discourse in different ways, leading to an increasingly polarized society.
    """
    result = check_bias_with_openai(text, api_key)
    
    if result["success"]:
        print("Bias Analysis:\n", result["bias_analysis"])
    else:
        print("Error:", result["error"])
