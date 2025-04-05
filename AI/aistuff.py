## TODO: Make text detection (IN PROGRESS)
## TODO: Make image detection (IN PROGRESS)
## TODO: FIND A WAY TO SCRAPE WEBSITES (IMPORTANT - NOT STARTED), split website in textual and image data

## Really simple stuff
import requests
import json
from pprint import pprint

## Parameters for sightengine, images
sightparams = {
  'models': 'genai',
  'api_user': '115151825',
  'api_secret': 'nNF32F8fSoNvH5xKjEdsXb3KmjmwSaAN'
}

## Opening images and runnng them
aidogefile = {'media': open('Tests/aidoge.png', 'rb')}
realdogefile = {'media': open('Tests/realdoge.jpg', 'rb')}
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

## Print outputs
print(output1)
print(output2)
pprint(response.json())