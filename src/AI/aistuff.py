## TODO: Make text detection (IN PROGRESS)
## TODO: Make image detection (IN PROGRESS)
## TODO: FIND A WAY TO SCRAPE WEBSITES (IMPORTANT - NOT STARTED), split website in textual and image data



## Really simple stuff
import requests
import json
from pprint import pprint
from urllib.request import Request
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import cairosvg 
from openai import OpenAI

os.environ['SIGHTENGINE_PRIVATE'] = 'nNF32F8fSoNvH5xKjEdsXb3KmjmwSaAN'
os.environ['OPENAI_API_KEY'] = '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'

client = OpenAI()

## Parameters for sightengine, images
sightparams = {
  'models': 'genai',
  'api_user': '115151825',
  'api_secret': os.getenv('SIGHTENGINE_PRIVATE'),
}



# ## Opening images and runnng them
# aidogefile = {'media': open('Tests/aidoge.png', 'rb')}
# realdogefile = {'media': open('Tests/realdoge.jpg', 'rb')}


def chicken_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

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
                png_data = cairosvg.svg2png(bytestring=response.content)
                
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

# ## Sapling AI text
# response = requests.post(
#     "https://api.sapling.ai/api/v1/aidetect",
#     json={
#         "key": "ERCNCCJS75NWG8F37705LVO0Z9M468P6",
#         "text": "This is sample text."
#     }
# )
url = 'https://sapling.ai/ai-detection-apis'
soup = chicken_soup(url)

if soup:
    print('---')
    with open('src/AI/output.txt', 'w', encoding='utf-8') as file:
        rawText = extract_main_content(soup)
        response = client.responses.create(
            model = "gpt-4oturbo",
            instructions = "This text is the raw text of a website. Clean it up, but DO NOT CHANGE THE CONTENT IN ANY WAY. Remove all formatting from your output. Return only the text, you don't need to say anything else.",
            input = rawText
        )
        #answer = json.loads(response.text)
        file.write(response.text)

    imgs = extract_images(soup, url)
    imgresults = []

    for i in imgs:
        download_as_webp(i, f'src/dump/tempimg.webp')
        file = {'media': open('src/dump/tempimg.webp', 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/check.json', files=file, data=sightparams)
        result = json.loads(r.text)
        if result['status'] == 'success':
            imgresults.append(result["type"]["ai_generated"])
    
    print(imgresults)
        

