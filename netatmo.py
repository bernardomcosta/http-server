# This code is heavly based on the sample provided at https://dev.netatmo.com/resources/technical/samplessdks/codesamples#authcode

#TODO: Check state in response
#TODO: Encapsulate API handling in classes, e.g. generic devices class

from flask import Flask, render_template, redirect
from flask import request as r
import requests
import uuid
import sys

CLIENT_ID = None
CLIENT_SECRET = None

app = Flask(__name__)

def print_thermostats(device):
    return "Thermostat %s @ %s" % (device["station_name"], device["_id"])

def print_stations(device):
    return "Weather Station @ %s" % (device["_id"])

def get_user_devices(access_token):
    devices = get_stations_data(access_token)

    if (devices != None):
        devices += "\r\n"
    
    devices += get_thermostats_data(access_token)

    return "Available devices:\r\n" + devices

def get_thermostats_data(access_token, device_id = None):
    payload = {"access_token" : access_token}

    if (device_id != None):
        payload["device_id"] = device_id

    response = requests.post("https://api.netatmo.com/api/getthermostatsdata", data=payload)
    response.raise_for_status()
    
    return "\r\n".join([print_thermostats(device) for device in response.json()["body"]["devices"]])

def get_stations_data(access_token, device_id = None):
    payload = {"access_token" : access_token}

    if (device_id != None):
        payload["device_id"] = device_id

    response = requests.post("https://api.netatmo.com/api/getstationsdata", data=payload)
    response.raise_for_status()

    return "\r\n".join([print_thermostats(device) for device in response.json()["body"]["devices"]])

def user_accepted_app():
    code = r.args.get('code')
    payload = {'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': 'http://localhost:5000/signin'}
    try:
        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        response.raise_for_status()
        access_token=response.json()["access_token"]
        refresh_token=response.json()["refresh_token"]
        scope=response.json()["scope"]

        return get_user_devices(access_token)

    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)

def ask_user_permission():
    payload = {'client_id': CLIENT_ID,
        'redirect_uri': "http://localhost:5000/signin",
        'scope': 'read_station read_thermostat',
        'state': uuid.uuid4().hex}
    try:
        response = requests.post("https://api.netatmo.com/oauth2/authorize", params=payload)
        response.raise_for_status()
        return redirect(response.url, code=302)
    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)

@app.route('/')
def sign():
    return "<form action='/signin' method='get'><button type='submit'>Sign in</button></form>"

#Authorization Code type authentication flow
@app.route('/signin', methods=['GET'])
def signin():
    # Test if "code" is provided in get parameters (that would mean that user has already accepted the app and has been redirected here)
    if r.args.get('code'):
        return user_accepted_app()
    # Test if "error" is provided in get parameters (that would mean that the user has refused the app)
    elif r.args.get('error') == 'access_denied':
        return "The user refused to give access to his Netatmo data"
    # If "error" and "code" are not provided in get parameters: the user should be prompted to authorize your app
    else:
        return ask_user_permission()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please give client id and client secret as arguments. The order matters!")
    else:
        CLIENT_ID = sys.argv[1]
        CLIENT_SECRET = sys.argv[2]

        app.run()
