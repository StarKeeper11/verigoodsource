## TODO: Make text detection (IN PROGRESS)
## TODO: Make image detection (IN PROGRESS)
## TODO: FIND A WAY TO SCRAPE WEBSITES (IMPORTANT - NOT STARTED), split website in textual and image data

## Really simple stuff
import requests
import json
from pprint import pprint
from urllib.request import Request
from bs4 import BeautifulSoup

## Parameters for sightengine, images
sightparams = {
  'models': 'genai',
  'api_user': '115151825',
  'api_secret': 'nNF32F8fSoNvH5xKjEdsXb3KmjmwSaAN'
}

## Opening images and runnng them
aidogefile = {'media': open('Tests/aidoge.png', 'rb')}
realdogefile = {'media': open('Tests/realdoge.jpg', 'rb')}


def chicken_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


r1 = requests.post('https://api.sightengine.com/1.0/check.json', files=aidogefile, data=sightparams)
r2 = requests.post('https://api.sightengine.com/1.0/check.json', files=realdogefile, data=sightparams)

## Sapling AI text
response = requests.post(
    "https://api.sapling.ai/api/v1/aidetect",
    json={
        "key": "ERCNCCJS75NWG8F37705LVO0Z9M468P6",
        "text": "This is sample text."
    }
)




## Prep outputs
output1 = json.loads(r1.text)
output2 = json.loads(r2.text)

req = Request('https://api.sightengine.com/1.0/check.json', params=sightparams)
## Print outputs
print(output1)
print(output2)
pprint(response.json())