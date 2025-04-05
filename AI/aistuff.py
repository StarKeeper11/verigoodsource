## TODO: Make text detection
## TODO: Make image detection

import requests
import json

sightparams = {
  'models': 'genai',
  'api_user': '115151825',
  'api_secret': 'nNF32F8fSoNvH5xKjEdsXb3KmjmwSaAN'
}
aidogefile = {'media': open('Tests/aidoge.png', 'rb')}
realdogefile = {'media': open('Tests/realdoge.jpg', 'rb')}
r1 = requests.post('https://api.sightengine.com/1.0/check.json', files=aidogefile, data=sightparams)
r2 = requests.post('https://api.sightengine.com/1.0/check.json', files=realdogefile, data=sightparams)

output1 = json.loads(r1.text)
output2 = json.loads(r2.text)

print(output1)
print(output2)