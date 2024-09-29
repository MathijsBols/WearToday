import json
import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
import requests
from datetime import datetime, timedelta
import pytz
import threading
from flask import Flask, request, abort
import os

REFRESH_TOKEN_FILE = 'refresh_token.txt'

VALID_TOKEN = "PUT CUSTOM HERE"

def load_refresh_token():
    if os.path.exists(REFRESH_TOKEN_FILE):
        with open(REFRESH_TOKEN_FILE, 'r') as file:
            return file.read().strip()
    return None

def save_refresh_token(refresh_token):
    with open(REFRESH_TOKEN_FILE, 'w') as file:
        file.write(refresh_token)


def refreshToken():
    client_id = 'D50E0C06-32D1-4B41-A137-A9A850C892C2'
    refresh = load_refresh_token()  # Load the refresh token from file
    
    if not refresh:
        print("Error: No refresh token found.")
        return None

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh,
        'client_id': client_id
    }
    
    refresh_req = requests.post('https://somtoday.nl/oauth2/token', data=payload)
    
    if refresh_req.status_code == 200:
        access_json = refresh_req.text
        access_dict = json.loads(access_json)
        
        if 'access_token' in access_dict:
            # Returning the new access token
            new_access_token = access_dict['access_token']
            # Update the refresh token if available
            if 'refresh_token' in access_dict:
                save_refresh_token(access_dict['refresh_token'])  # Save the new refresh token
            return new_access_token
        else:
            print("Error: 'access_token' not found in response.")
            print("JSON response: ", access_dict)
    else:
        print("Error: HTTP Status Code", refresh_req.status_code)
        print("Response: ", refresh_req.text)

    return None



code = ""
code = "Bearer "+code
headers = {'authorization': code, 'Accept': 'application/json'}



def getAfspreken():
    today = datetime.now()
    parameters = {
        'begindatum': today.strftime('%Y-%m-%d'),
        'einddatum': (today + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    afspraken = requests.get('https://api.somtoday.nl/rest/v1/afspraken',headers=headers, params=parameters)
    if afspraken.status_code in [200, 206]:
        return afspraken.json()
    else:
        print(f"Error: {afspraken.status_code} - {afspraken.text}")
    

def get_next_lesson(data):

    if data is None:
        return "No data available to retrieve lessons."
    # Get the current date and time and make it aware
    local_tz = pytz.timezone('Europe/Amsterdam')  # Use the appropriate timezone
    current_time = datetime.now(local_tz)

    # Access the list of lessons from the response
    lessons = data.get("items", [])

    # Convert lesson start times to datetime objects and check the next one
    for lesson in lessons:
        lesson_time = datetime.fromisoformat(lesson["beginDatumTijd"].replace("Z", "+00:00"))  # Convert to aware datetime
        
        if lesson_time > current_time:
            return f"{lesson['omschrijving']} in {lesson['locatie']} om {lesson_time.strftime('%H:%M')}."

    return "No upcoming lessons today!"


next_lesson = "No lessons available"

def update_next_lesson():
    global next_lesson
    while True:
        try:
            token = refreshToken()
            code = "Bearer "+token
            headers['authorization'] = code
            afspraken = getAfspreken()
            next_lesson = get_next_lesson(afspraken)
            print(f"Updated next lesson: {next_lesson}")
        except Exception as e:
            print(f'error updating lesson: {e}')
        time.sleep(600)

def check_auth(token):
    return token == VALID_TOKEN

def authenticate_error():
    return "error Unauthorized access"


app = Flask(__name__)

@app.route('/', methods=['GET'])
def display_next_lesson():
    # Get the Authorization header from the request
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith("Bearer "):
        # Extract the token from the Authorization header
        token = auth_header.split(" ")[1]
        
        # Check if the token is valid
        if check_auth(token):
            return next_lesson
        else:
            return authenticate_error()
    else:
        return authenticate_error()

def run_flask():
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    # Start the lesson updater in a separate thread
    lesson_thread = threading.Thread(target=update_next_lesson)
    lesson_thread.daemon = True  # Daemonize thread to close with the main program
    lesson_thread.start()

    # Start the Flask app in the main thread
    run_flask()