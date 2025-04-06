from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from urllib.parse import urlparse
import requests
import json
from urllib.request import Request
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
#import cairosvg 
import math
from openai import OpenAI
import random

os.environ['SIGHTENGINE_PRIVATE'] = 'JF2JSXgtDUBWk5gZKfZp5JyAWKp46jW2'
os.environ['OPENAI_API_KEY'] = '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'
client = OpenAI()

sightparams = {
  'models': 'genai',
  'api_user': '384942881',
  'api_secret': '{api_secret}'
}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def chicken_soup(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    response.raise_for_status()  # Raise an error for bad status codes
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def extract_main_content(soup):
    main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'content'})

    if main_content:
        # Extract text and add line breaks between paragraphs
        return '\n\n'.join(p.get_text(strip=True) for p in main_content.find_all(['p', 'div']))
    else:
        # Fallback to extracting all text with line breaks
        return '\n\n'.join(soup.stripped_strings)

def extract_images(soup, base_url):
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            # Resolve relative URLs to absolute URLs
            full_url = requests.compat.urljoin(base_url, src)
            images.append(full_url)
    return images

def download_as_webp(url, output_path, quality=100):
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Download image
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()

        # Determine if SVG
        is_svg = ('svg' in response.headers.get('Content-Type', '').lower() or 
                 url.lower().endswith('.svg'))

        if is_svg:
            # Handle SVG with cairosvg
            try:
                # Convert SVG to PNG in memory
                #png_data = cairosvg.svg2png(bytestring=response.content)

                # Open the PNG data with PIL
                img = Image.open(BytesIO(png_data))

                # Save as WebP
                img.save(output_path, 'WEBP', quality=quality)
                return True
            except Exception as e:
                print(f"SVG conversion failed: {e}")
                return False
        else:
            # For non-SVG images, use PIL directly
            try:
                img = Image.open(BytesIO(response.content))

                # Convert to RGB if mode is not supported for WebP
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')

                # Save as WebP
                img.save(output_path, 'WEBP', quality=quality)
                return True
            except Exception as e:
                print(f"Image conversion failed: {e}")
                return False

    except Exception as e:
        print(f"Error: {e}")
        return False

def check_bias_with_openai(text):
    """Analyzes text for potential bias using OpenAI's API with retry logic."""

    prompt = """
    Analyze the following text for potential bias.
    Provide a short and concise analysis of any detected bias as well as an overall numbered bias score from 1-10, where 1 is completely neutral and 10 is extremely biased. End your response with "BIAS SCORE:" and then the bias rating number.
    You do not need to include anything else in your response.
    You do not need to have any formatting in your response.
    """

    response = client.responses.create(
                model="gpt-4o",
                instructions=prompt,
                input=text
            )

    return response.output_text



def run_url(url):

    output = ""

    alltext = ""

    soup = chicken_soup(url)

    if soup:
        rawText = extract_main_content(soup
                                      )
        response = client.responses.create(
            model = "gpt-4o",
            instructions = "This text is the raw text of a website. Clean it up, but DO NOT CHANGE THE CONTENT IN ANY WAY. Remove all potential footers. Remove all formatting from your output. Return only the text, you don't need to say anything else.",
            input = rawText
        )

        biasedOutput = str(check_bias_with_openai(response.output_text))
        biasScore = float((biasedOutput.split("BIAS SCORE: ")[1]).strip('.'))
        output += "\nInformation Bias Score: " + str(biasScore)
        biasExplanation = (biasedOutput.split("BIAS SCORE: ")[0])
        
        aiTextScore = 0
        
        try:
            textresponse = requests.post(
                "https://api.sapling.ai/api/v1/aidetect",
                json={
                    "key": "E00YARC4QHFDBOT8LAIUVMONOAO3PX87",
                    "text": rawText
                }
            )
            textresult = textresponse.json()
            aiTextScore = round(float(textresult['score'])*10, 1)
            output += "\nAI Text Score: " + str(aiTextScore)
        except:
            output += "\nText API failed"
            aiTextScore = float(0)

        imgs = extract_images(soup, url)
        imgresults = []

        for i in imgs:
            download_as_webp(i, f'src/dump/tempimg.webp')
            file = {'media': open('src/dump/tempimg.webp', 'rb')}
            r = requests.post('https://api.sightengine.com/1.0/check.json', files=file, data=sightparams)
            result = json.loads(r.text)
            if result['status'] == 'success':
                imgresults.append(result["type"]["ai_generated"])


        aiImgScore = None
        if len(imgresults) == 0:
            aiImgScore = float("0")
            output += 'AI Images Failed'
        else:
            aiImgScore = str(sum(imgresults)/len(imgresults))
            aiImgScore = round(float(aiImgScore)*10, 1)
            output += '\nAI Image Score: ' + str(aiImgScore)
        
        

        finalScore = 0
        valuesFound = 0
        
        if biasScore != 0 and biasScore != None:
            finalScore += biasScore
            valuesFound += 1
        if aiTextScore != 0 and aiTextScore != None:
            finalScore += aiTextScore
            valuesFound += 1
        if aiImgScore != 0 and aiImgScore != None:
            finalScore += aiImgScore
            valuesFound += 1

        finalScore = round(finalScore/float(valuesFound), 1)
        
        output += '\nFinal Score: ' + str(finalScore)
        output += '\n---\n'
        output += biasExplanation
        
        print(output)
        return output
    else:
        return "Error: Could not retrieve content from the URL. Sorry about that."

@app.route('/process-url', methods=['POST'])
def process_url():
    print("Processing URL")
    data = request.json

    print("Data received")
    if not data or 'url' not in data:
        print("error of url")
        return jsonify({'error': 'URL is required'}), 400

    url = str(data['url'])

    print("about to run url")
    response_string = run_url(url)
    print("url run")

    return jsonify({'result': response_string})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
