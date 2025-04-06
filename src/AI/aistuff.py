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
import subprocess
import tempfile
import shutil
import os


## from PIL import Image

## Parameters for sightengine, images
sightparams = {
  'models': 'genai',
  'api_user': '115151825',
  'api_secret': 'nNF32F8fSoNvH5xKjEdsXb3KmjmwSaAN'
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

def download_as_webp(url, output_path, quality=80):
    """
    Downloads an image from URL and saves as WebP, handling SVGs and other formats.
    
    Args:
        url (str): Image URL to download
        output_path (str): Where to save the WebP file
        quality (int): WebP quality (0-100)
    
    Returns:
        bool: Success or failure
    """
    try:
        print("start")
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Download image
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        print("no error from response")
        
        # Determine if SVG
        is_svg = ('svg' in response.headers.get('Content-Type', '').lower() or 
                 url.lower().endswith('.svg'))
        
        print("svg check complete")
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            temp_path = temp_file.name
            temp_file.write(response.content)

        print("temp file created")
        
        success = False
        
        # Handle SVG conversion via external tools
        if is_svg:
            # Try converting SVG to PNG first
            png_path = f"{temp_path}.png"
            
            # Try librsvg or Inkscape
            if shutil.which('rsvg-convert'):
                subprocess.run(['rsvg-convert', '-o', png_path, temp_path], capture_output=True)
                if os.path.exists(png_path):
                    temp_path = png_path  # Use PNG for next step
                    success = True
            elif shutil.which('inkscape') and not success:
                subprocess.run(['inkscape', '--export-filename', png_path, temp_path], capture_output=True)
                if os.path.exists(png_path):
                    temp_path = png_path  # Use PNG for next step
                    success = True
        
        # Try PIL first for non-SVGs or when SVG was converted to PNG
        if not is_svg or (is_svg and success):
            try:
                img = Image.open(temp_path if is_svg else BytesIO(response.content))
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                img.save(output_path, 'WEBP', quality=quality)
                success = True
            except Exception:
                success = False
        
        # ImageMagick as fallback
        if not success and shutil.which('convert'):
            subprocess.run(['convert', temp_path, '-quality', str(quality), output_path], capture_output=True)
            success = os.path.exists(output_path)
        
        # Clean up temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'png_path' in locals() and os.path.exists(png_path):
            os.remove(png_path)
            
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        # Clean up any temp files that might exist
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        if 'png_path' in locals() and os.path.exists(png_path):
            os.remove(png_path)
        return False

# ## Sapling AI text
# response = requests.post(
#     "https://api.sapling.ai/api/v1/aidetect",
#     json={
#         "key": "ERCNCCJS75NWG8F37705LVO0Z9M468P6",
#         "text": "This is sample text."
#     }
# )

soup = chicken_soup('https://sapling.ai/ai-detection-apis')

if soup:
    print('---')
    with open('src/AI/output.txt', 'w', encoding='utf-8') as file:
        file.write(extract_main_content(soup))

    imgs = extract_images(soup, 'https://sapling.ai/ai-detection-apis')

    download_as_webp(imgs[0], 'src/dumb/', quality=80)

    # for i in imgs:
    #     download_image_as_webp(i, )
        # response = requests.get(i, stream=True)
        
        # if 'image' in response.headers.get('Content-Type', ''):
        #     # Save the image to a temporary file
        #     print('---')
        #     print("Image at url " + i)
        #     temp_file_path = f'src/dump/temp_image_{i.split("/")[-1]}'
        #     with open(temp_file_path, 'wb') as temp_file:
        #         temp_file.write(response.content)

        #     print(f"Image saved to {temp_file_path}")
        #     result = cwebp(input_image=temp_file_path, output_image=temp_file_path, option=f"-q {100}")