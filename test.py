## Import different libraries
import json
import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
import requests
import xmltodict

## Store some constants
client_id = 'D50E0C06-32D1-4B41-A137-A9A850C892C2'
SCHOOL_UUID = "e216edc3-331c-4880-8815-d1fe03f164cc"

## Token flow
def get_organisation(uuid):
    response = requests.get('https://servers.somtoday.nl/organisaties.json')
    data = response.json()
    school = next((instelling for instelling in data[0]['instellingen'] if instelling['uuid'] == uuid), None)
    if school:
        return school
    else:
        raise ValueError('No school found')

school = get_organisation(SCHOOL_UUID)
base_url = "https://somtoday.nl/oauth2/authorize?redirect_uri=somtodayleerling://oauth/callback&client_id=D50E0C06-32D1-4B41-A137-A9A850C892C2&response_type=code&prompt=login&scope=openid&code_challenge=tCqjy6FPb1kdOfvSa43D8a7j8FLDmKFCAz8EdRGdtQA&code_challenge_method=S256&tenant_uuid={TENANT_UUID}".format(TENANT_UUID=school['uuid'])

print(f"Logging into {school['naam']} with ID: {school['uuid']}")

browser = webdriver.Chrome()
browser.get(base_url)

start_time = time.time()
while True:
    elapsed_time = time.time() - start_time
    if elapsed_time >= 60:  # Can be modified
        print("Timeout: 1 minute elapsed")
        break
    
    console_logs = browser.get_log('browser')
    for log_entry in console_logs:
        if 'Failed to launch' in log_entry['message']:
            url = log_entry['message'].split("'")[1]
            code = parse_qs(urlparse(url).query)['code'][0]

            payload = {
                'grant_type': 'authorization_code',
                'redirect_uri': 'somtodayleerling://oauth/callback',
                'code_verifier': 't9b9-QCBB3hwdYa3UW2U2c9hhrhNzDdPww8Xp6wETWQ',
                'code': code,
                'scope': 'openid',
                'client_id': 'D50E0C06-32D1-4B41-A137-A9A850C892C2'
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post('https://somtoday.nl/oauth2/token', data=payload, headers=headers)
            token_data = response.json()
            # optional -- with open('token.json', 'w') as token_file:
            # optional -- json.dump(token_data, token_file)
            print('Saved token.')
            browser.quit()
            break
    else:
        time.sleep(1)
        continue
    break

# Refresh token
refresh = token_data['refresh_token']
print("Refresh Token:")
print(refresh)