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

os.environ['SIGHTENGINE_PRIVATE'] = 'LtBVMFAQUeKUkjGgfvFMfkvaUgf9QB9j'
os.environ['OPENAI_API_KEY'] = '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'
client = OpenAI()


## Parameters for sightengine, images
sightparams = {
  'models': 'genai',
  'api_user': '207914551',
  'api_secret': os.getenv('SIGHTENGINE_PRIVATE'),
}



# ## Opening images and runnng them
# aidogefile = {'media': open('Tests/aidoge.png', 'rb')}
# realdogefile = {'media': open('Tests/realdoge.jpg', 'rb')}


def chicken_soup(url):
    # response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    # response.raise_for_status()  # Raise an error for bad status codes
    # soup = None
    # if url.endswith('.html'):
    #     pprint(response)
    #     soup = BeautifulSoup(response.text.replace(".html", ""), 'html.parser')
    # else:
    #     soup = BeautifulSoup(response.text, 'html.parser')
    soup = None
    with open("src/Main/Tests/fakeBlogPost.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
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



def run_url(url):

    soup = chicken_soup(url)

    if soup:
        print('---')
        with open('src/AI/output.txt', 'w', encoding='utf-8') as file:
            rawText = extract_main_content(soup)
            response = client.responses.create(
                model = "gpt-4o",
                instructions = "This text is the raw text of a website. Clean it up, but DO NOT CHANGE THE CONTENT IN ANY WAY. Remove all potential footers. Remove all formatting from your output. Return only the text, you don't need to say anything else.",
                input = rawText
            )
            #answer = json.loads(response.text)
            file.write(response.output_text)
            print("File write sucess!")
            print('---')
            print(check_bias_with_openai(response.output_text))
            print('---')
            textresponse = requests.post(
                "https://api.sapling.ai/api/v1/aidetect",
                json={
                    "key": "G108GEIPFKTLI0SW8P1WTGZ9ZBNQOKF1",
                    "text": rawText
                }
            )
            textresult = textresponse.json()
            print("AI Text Score: " + str(textresult['score']))

        print("---")    

        imgs = extract_images(soup, url)
        imgresults = []

        pprint(imgs)

        for i in imgs:
            download_as_webp(i, f'src/dump/tempimg.webp')
            file = {'media': open('src/dump/tempimg.webp', 'rb')}
            r = requests.post('https://api.sightengine.com/1.0/check.json', files=file, data=sightparams)
            result = json.loads(r.text)
            if result['status'] == 'success':
                pprint(result)
                imgresults.append(result["type"]["ai_generated"])
        
        print('Image scores:')
        print(imgresults)
        print('---')
            

run_url('https://www.opensourceshakespeare.org/views/plays/play_view.php')