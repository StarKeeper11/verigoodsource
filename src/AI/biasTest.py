import time
import requests
from openai import OpenAI
import os

os.environ['OPENAI_API_KEY'] = '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'

client = OpenAI()

def check_bias_with_openai(text):
    """Analyzes text for potential bias using OpenAI's API with retry logic."""

    prompt = """
    Analyze the following text for potential bias.
    Provide a short and concise analysis of any detected bias as well as an overall bias score
    from 1-10, where 1 is completely neutral and 10 is extremely biased.
    You do not need to include anything else in your response.
    You do not need to have any formatting in your response.
    """

    response = client.responses.create(
                model="gpt-4o",
                instructions=prompt,
                input=text
            )
    
    return response.output_text


# Example usage
if __name__ == "__main__":
    with open('src/AI/output.txt', 'r', encoding='utf-8') as file:
        print(check_bias_with_openai(file.read()))

    #result = check_bias_with_openai(text)
    
    #print(result)
